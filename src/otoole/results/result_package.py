import logging
from collections.abc import Mapping
from typing import Dict, Iterable, Optional, Tuple

import pandas as pd
from pandas_datapackage_reader import read_datapackage

LOGGER = logging.getLogger(__name__)


class ResultsPackage(Mapping):
    """A package of OSeMOSYS results

    Internal data structure is a dictionary of pandas DataFrames

    A crude caching function is implemented whereby calculated results are stored in the
    internal data structure so that each result is only calculated once.

    Arguments
    ---------
    data : dict
        A dictionary of results data
    input_data: str, default=None
        Path to the datapackage of input data
    """

    def __init__(self, data: Dict[str, pd.DataFrame], input_data: Optional[str] = None):
        super().__init__()
        self._data = data
        if input_data:
            self._package = read_datapackage(
                input_data
            )  # typing: Dict[str, pd.DataFrame]
        else:
            self._package = {}
        self._result_mapper = {
            "AccumulatedNewCapacity": self.accumulated_new_capacity,
            "AnnualEmissions": self.annual_emissions,
            "AnnualFixedOperatingCost": self.annual_fixed_operating_cost,
            "AnnualTechnologyEmission": self.annual_technology_emissions,
            "AnnualTechnologyEmissionByMode": self.annual_technology_emission_by_mode,
            "AnnualVariableOperatingCost": self.annual_variable_operating_cost,
            "CapitalInvestment": self.capital_investment,
            "Demand": self.demand,
            "ProductionByTechnology": self.production_by_technology,
            "ProductionByTechnologyAnnual": self.production_by_technology_annual,
            "RateOfProductionByTechnology": self.rate_of_product_technology,
            "RateOfProductionByTechnologyByMode": self.rate_of_production_tech_mode,
            "TotalCapacityAnnual": self.total_capacity_annual,
        }
        self._result_cache = {}  # type: Dict[str, pd.DataFrame]

    @property
    def data(self) -> Dict[str, pd.DataFrame]:
        """View the results dictionary
        """
        return self._data

    @property
    def result_mapper(self) -> Dict[str, pd.DataFrame]:
        return self._result_mapper

    @property
    def result_cache(self) -> Dict[str, pd.DataFrame]:
        return self._result_cache

    @result_cache.setter
    def result_cache(self, value: Iterable[Tuple[str, pd.DataFrame]]):
        self._result_cache.update(value)

    def __getitem__(self, name: str) -> pd.DataFrame:
        if name in self.data.keys():
            return self.data[name]
        elif name in self._package.keys():
            return self._package[name]
        elif name in self.result_cache.keys():
            return self.result_cache[name]
        elif name in self.result_mapper.keys():
            # Implements a crude form of caching, where calculated results are
            # first stored in the internal dict, and then returned
            results = self.result_mapper[name]()
            self.result_cache[name] = results
            return self.result_cache[name]
        else:
            raise KeyError("'{}' is not accessible or available".format(name))
        return self.data[name]

    def __iter__(self):
        raise NotImplementedError()

    def __len__(self):
        raise NotImplementedError()

    def accumulated_new_capacity(self) -> pd.DataFrame:
        """
        Arguments
        ---------
        operational_life: pandas.DataFrame

        new_capacity: pandas.DataFrame

        year: pandas.Index

        Notes
        -----
        table AccumulatedNewCapacity
        {r in REGION, t in TECHNOLOGY, y in YEAR:
            sum{yy in YEAR: y-yy < OperationalLife[r,t] && y-yy>=0}
            NewCapacity[r,t,yy] > 0}
        OUT "CSV"
        ResultsPath & "/AccumulatedNewCapacity.csv" :
        r~REGION, t~TECHNOLOGY, y~YEAR,
        sum{yy in YEAR: y-yy < OperationalLife[r,t] && y-yy>=0}
            NewCapacity[r,t,yy] ~VALUE;
        """
        new_capacity = self["NewCapacity"].copy()
        year = pd.Index(self["YEAR"]["VALUE"].to_list())

        new_capacity["OperationalLife"] = self["OperationalLife"].copy()

        regions = new_capacity.reset_index()["REGION"].unique()
        technologies = new_capacity.reset_index()["TECHNOLOGY"].unique()

        index = pd.MultiIndex.from_product(
            [regions, technologies, year.to_list()],
            names=["REGION", "TECHNOLOGY", "YEAR"],
        )

        acc_capacity = new_capacity.reindex(index, copy=True)

        for index, data in new_capacity.reset_index().groupby(
            by=["REGION", "TECHNOLOGY"]
        ):
            region, technology = index
            for yr in year:
                mask = (yr - data["YEAR"] < data["OperationalLife"]) & (
                    yr - data["YEAR"] >= 0
                )
                acc_capacity.loc[region, technology, yr] = data[mask].sum()

        acc_capacity = acc_capacity.drop(columns="OperationalLife")
        return acc_capacity[(acc_capacity != 0).all(1)]

    def annual_emissions(self) -> pd.DataFrame:
        """Calculates the annual emissions

        Annual Emission are found by multiplying the emission activity ratio
        (emissions per unit activity) by the rate of activity and the yearsplit

        Notes
        -----

        sum{t in TECHNOLOGY, l in TIMESLICE, m in MODE_OF_OPERATION:
                EmissionActivityRatio[r,t,e,m,y]<>0}
            RateOfActivity[r,l,t,m,y] * EmissionActivityRatio[r,t,e,m,y]
                * YearSplit[l,y]~VALUE;
        """
        emission_activity_ratio = self["EmissionActivityRatio"]
        yearsplit = self["YearSplit"]
        rate_of_activity = self["RateOfActivity"]

        data = emission_activity_ratio.mul(yearsplit, fill_value=0.0)
        data = data.mul(rate_of_activity, fill_value=0.0)

        if not data.empty:
            data = data.groupby(by=["REGION", "EMISSION", "YEAR"]).sum()

            return data

        else:
            return pd.DataFrame()

    def annual_fixed_operating_cost(self) -> pd.DataFrame:
        """Compute AnnualFixedOperatingCost result

        Notes
        -----
        r~REGION, t~TECHNOLOGY, y~YEAR,
        FixedCost[r,t,y] *
        ((sum{yy in YEAR: y-yy < OperationalLife[r,t] && y-yy>=0}
            NewCapacity[r,t,yy]) + ResidualCapacity[r,t,y]) ~VALUE;

        """
        total_capacity = self["TotalCapacityAnnual"]
        fixed_cost = self["FixedCost"]
        total_fixed_costs = total_capacity.mul(fixed_cost, fill_value=0.0)
        return total_fixed_costs[(total_fixed_costs != 0).all(1)].dropna()

    def annual_technology_emissions(self) -> pd.DataFrame:
        """Annual emissions by technology

        Notes
        -----
        REGION, TECHNOLOGY, EMISSION, YEAR,
        sum{l in TIMESLICE, m in MODE_OF_OPERATION:
            EmissionActivityRatio[r,t,e,m,y]<>0}
        EmissionActivityRatio[r,t,e,m,y] * RateOfActivity[r,l,t,m,y]
            * YearSplit[l,y];
        """
        emission_activity_ratio: pd.DataFrame = self["EmissionActivityRatio"]
        yearsplit: pd.DataFrame = self["YearSplit"]
        rate_of_activity: pd.DataFrame = self["RateOfActivity"]

        data = emission_activity_ratio.mul(yearsplit)
        data = data.mul(rate_of_activity)

        if not data.empty:
            data = data.groupby(by=["REGION", "TECHNOLOGY", "EMISSION", "YEAR"]).sum()

            return data[(data != 0).all(1)]

        else:
            return pd.DataFrame()

    def annual_technology_emission_by_mode(self) -> pd.DataFrame:
        """

        Notes
        -----
        r~REGION, t~TECHNOLOGY, e~EMISSION, m~MODE_OF_OPERATION, y~YEAR,
        sum{l in TIMESLICE: EmissionActivityRatio[r,t,e,m,y] <> 0}
            EmissionActivityRatio[r,t,e,m,y] * RateOfActivity[r,l,t,m,y]
                * YearSplit[l,y]
        """
        emission_activity_ratio: pd.DataFrame = self["EmissionActivityRatio"]
        yearsplit: pd.DataFrame = self["YearSplit"]
        rate_of_activity: pd.DataFrame = self["RateOfActivity"]

        data = emission_activity_ratio.mul(yearsplit)
        data = data.mul(rate_of_activity)

        if not data.empty:
            data = data.groupby(
                by=["REGION", "TECHNOLOGY", "EMISSION", "MODE_OF_OPERATION", "YEAR"]
            ).sum()

            return data[(data != 0).all(1)]

        else:
            return pd.DataFrame()

    def annual_variable_operating_cost(self) -> pd.DataFrame:
        """

        Notes
        -----
        r~REGION, t~TECHNOLOGY, y~YEAR,
        sum{m in MODE_OF_OPERATION, l in TIMESLICE}
            RateOfActivity[r,l,t,m,y] * YearSplit[l,y] * VariableCost[r,t,m,y] ~VALUE;

        """
        rate_of_activity = self["RateOfActivity"]
        yearsplit = self["YearSplit"]
        variable_cost = self["VariableCost"]

        split_activity = rate_of_activity.mul(yearsplit, fill_value=0.0)
        operating_cost = split_activity.mul(variable_cost, fill_value=0.0)
        if operating_cost.empty:
            return operating_cost
        else:
            data = operating_cost.groupby(by=["REGION", "TECHNOLOGY", "YEAR"]).sum()
            return data[(data != 0).all(1)]

    def capital_investment(self) -> pd.DataFrame:
        """

        Notes
        -----
        r~REGION, t~TECHNOLOGY, y~YEAR,
        CapitalCost[r,t,y] * NewCapacity[r,t,y] ~VALUE;
        """
        capital_cost = self["CapitalCost"]
        new_capacity = self["NewCapacity"]

        data = capital_cost.mul(new_capacity, fill_value=0.0)
        return data[(data != 0).all(1)]

    def demand(self) -> pd.DataFrame:
        """

        Notes
        -----
        r~REGION, l~TIMESLICE, f~FUEL, y~YEAR,
        SpecifiedAnnualDemand[r,f,y] * SpecifiedDemandProfile[r,f,l,y] ~VALUE;
        """
        specified_annual_demand = self["SpecifiedAnnualDemand"]
        specified_demand_profile = self["SpecifiedDemandProfile"]

        data = specified_annual_demand.mul(specified_demand_profile, fill_value=0.0)
        if not data.empty:
            data = data.reset_index().set_index(["REGION", "TIMESLICE", "FUEL", "YEAR"])
        return data[(data != 0).all(1)]

    def production_by_technology(self) -> pd.DataFrame:
        """Compute production by technology

        Notes
        -----
        r~REGION, l~TIMESLICE, t~TECHNOLOGY, f~FUEL, y~YEAR,
        sum{m in MODE_OF_OPERATION: OutputActivityRatio[r,t,f,m,y] <> 0}
            RateOfActivity[r,l,t,m,y] * OutputActivityRatio[r,t,f,m,y]
            * YearSplit[l,y] ~VALUE;
        """
        rate_of_activity = self["RateOfActivity"]
        output_activity_ratio = self["OutputActivityRatio"]
        year_split = self["YearSplit"]

        split_activity = rate_of_activity.mul(year_split, fill_value=0.0)
        data = split_activity.mul(output_activity_ratio, fill_value=0.0)
        if not data.empty:
            data = data.groupby(
                by=["REGION", "TIMESLICE", "TECHNOLOGY", "FUEL", "YEAR"]
            ).sum()
        return data[(data != 0).all(1)]

    def production_by_technology_annual(self) -> pd.DataFrame:
        """Aggregates production by technology to the annual level
        """
        production_by_technology = self["ProductionByTechnology"]
        data = production_by_technology
        if not data.empty:
            data = data.groupby(by=["REGION", "TECHNOLOGY", "FUEL", "YEAR"]).sum()
        return data[(data != 0).all(1)]

    def rate_of_production_tech_mode(self) -> pd.DataFrame:
        """

        Arguments
        ---------
        rate_of_activity: pd.DataFrame
        output_activity_ratio: pd.DataFrame

        Notes
        -----
        r~REGION, l~TIMESLICE, t~TECHNOLOGY, m~MODE_OF_OPERATION, f~FUEL, y~YEAR,
        RateOfActivity[r,l,t,m,y] * OutputActivityRatio[r,t,f,m,y]~VALUE;
        """
        rate_of_activity = self["RateOfActivity"]
        output_activity_ratio = self["OutputActivityRatio"]

        data = rate_of_activity.mul(output_activity_ratio, fill_value=0.0)
        if not data.empty:
            data = data.reset_index().set_index(
                [
                    "REGION",
                    "TIMESLICE",
                    "TECHNOLOGY",
                    "MODE_OF_OPERATION",
                    "FUEL",
                    "YEAR",
                ]
            )
        return data[(data != 0).all(1)].sort_index()

    def rate_of_product_technology(self) -> pd.DataFrame:
        """Sums up mode of operation for rate of production

        Notes
        -----
        r~REGION, l~TIMESLICE, t~TECHNOLOGY, f~FUEL, y~YEAR,
        sum{m in MODE_OF_OPERATION: OutputActivityRatio[r,t,f,m,y] <> 0}
            RateOfActivity[r,l,t,m,y] * OutputActivityRatio[r,t,f,m,y]~VALUE;

        """
        rate_of_production = self["RateOfProductionByTechnologyByMode"]

        data = rate_of_production
        if not data.empty:
            data = data.groupby(
                by=["REGION", "TIMESLICE", "TECHNOLOGY", "FUEL", "YEAR"]
            ).sum()
        return data[(data != 0).all(1)].sort_index()

    def total_capacity_annual(self) -> pd.DataFrame:
        """Compute TotalCapacityAnnual result

        Notes
        -----
        r~REGION, t~TECHNOLOGY, y~YEAR,
        ResidualCapacity[r,t,y] +
        (sum{yy in YEAR: y-yy < OperationalLife[r,t] && y-yy>=0}
            NewCapacity[r,t,yy])~VALUE;
        """
        residual_capacity = self["ResidualCapacity"]
        acc_new_capacity = self["AccumulatedNewCapacity"]
        total_capacity = residual_capacity.add(acc_new_capacity, fill_value=0.0)
        return total_capacity[(total_capacity != 0).all(1)]
