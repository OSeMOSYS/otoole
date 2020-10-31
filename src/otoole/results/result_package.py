import logging
from collections.abc import Mapping
from datetime import datetime
from typing import Dict, Iterable, List, Optional, Tuple

import pandas as pd

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
    input_data: dict, default=None
        Dictionary of input data

    """

    def __init__(
        self,
        data: Dict[str, pd.DataFrame],
        input_data: Optional[Dict[str, pd.DataFrame]] = None,
    ):
        super().__init__()
        self._data = data
        if input_data:
            self._package = input_data
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
            "DiscountedTechnologyEmissionsPenalty": self.discounted_tech_emis_pen,
            "ProductionByTechnology": self.production_by_technology,
            "ProductionByTechnologyAnnual": self.production_by_technology_annual,
            "RateOfProductionByTechnology": self.rate_of_product_technology,
            "RateOfProductionByTechnologyByMode": self.rate_of_production_tech_mode,
            "RateOfUseByTechnology": self.rate_of_use_by_technology,
            "RateOfUseByTechnologyByMode": self.rate_of_use_by_technology_by_mode,
            "TotalAnnualTechnologyActivityByMode": self.total_annual_tech_activity_mode,
            "TotalCapacityAnnual": self.total_capacity_annual,
            "TotalDiscountedCost": self.total_discounted_cost,
            "TotalTechnologyAnnualActivity": self.total_technology_annual_activity,
            "TotalTechnologyModelPeriodActivity": self.total_tech_model_period_activity,
            "UseByTechnology": self.use_by_technology,
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
        LOGGER.debug("Returning '%s' from ... ", name)
        if name in self.data.keys():
            LOGGER.debug("    ... ResultsPackage.data")
            return self.data[name]
        elif name in self._package.keys():
            LOGGER.debug("    ... ResultsPackage.input_data")
            return self._package[name]
        elif name in self.result_cache.keys():
            LOGGER.debug("    ... ResultsPackage.result_cache")
            return self.result_cache[name]
        elif name in self.result_mapper.keys():
            # Implements a crude form of caching, where calculated results are
            # first stored in the internal dict, and then returned
            LOGGER.debug("  ... ResultsPackage.calculating ...")
            start = datetime.now()
            results = self.result_mapper[name]()
            stop = datetime.now()
            diff = stop - start
            total = diff.total_seconds()
            LOGGER.debug("Calculation took %s secs", total)
            LOGGER.debug("Caching results for %s", name)
            self.result_cache[name] = results
            return self.result_cache[name]
        else:
            LOGGER.debug("  ... Not found in cache or calculation methods")
            raise KeyError("{} is not accessible or available".format(name))
        return self.data[name]

    def __iter__(self):
        raise NotImplementedError()

    def __len__(self):
        raise NotImplementedError()

    def _msg(self, name: str, error: str):
        return "Cannot calculate {} due to missing data: {}".format(name, error)

    def accumulated_new_capacity(self) -> pd.DataFrame:
        """AccumulatedNewCapacity

        Arguments
        ---------
        operational_life: pandas.DataFrame

        new_capacity: pandas.DataFrame

        year: pandas.Index

        Notes
        -----
        From the formulation::

            r~REGION, t~TECHNOLOGY, y~YEAR,
            sum{yy in YEAR: y-yy < OperationalLife[r,t] && y-yy>=0}
                NewCapacity[r,t,yy] ~VALUE;

        """
        try:
            new_capacity = self["NewCapacity"].copy()
            year = pd.Index(self["YEAR"]["VALUE"].to_list())
        except KeyError as ex:
            raise KeyError(self._msg("AccumulatedNewCapacity", str(ex)))

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
        From the formulation::

            sum{t in TECHNOLOGY, l in TIMESLICE, m in MODE_OF_OPERATION:
                    EmissionActivityRatio[r,t,e,m,y]<>0}
                RateOfActivity[r,l,t,m,y] * EmissionActivityRatio[r,t,e,m,y]
                    * YearSplit[l,y]~VALUE;
        """
        try:
            emission_activity_ratio = self["EmissionActivityRatio"]
            yearsplit = self["YearSplit"]
            rate_of_activity = self["RateOfActivity"]
        except KeyError as ex:
            raise KeyError(self._msg("AnnualEmissions", str(ex)))

        mid = emission_activity_ratio.mul(yearsplit)
        data = mid.mul(rate_of_activity, fill_value=0.0)

        if not data.empty:
            data = data.groupby(by=["REGION", "EMISSION", "YEAR"]).sum()
        return data

    def annual_fixed_operating_cost(self) -> pd.DataFrame:
        """Compute AnnualFixedOperatingCost result

        Notes
        -----
        From the formulation::

            r~REGION, t~TECHNOLOGY, y~YEAR,
            FixedCost[r,t,y] *
            ((sum{yy in YEAR: y-yy < OperationalLife[r,t] && y-yy>=0}
                NewCapacity[r,t,yy]) + ResidualCapacity[r,t,y]) ~VALUE;

        """
        try:
            total_capacity = self["TotalCapacityAnnual"]
            fixed_cost = self["FixedCost"]
        except KeyError as ex:
            raise KeyError(self._msg("AnnualFixedOperatingCost", str(ex)))

        total_fixed_costs = total_capacity.mul(fixed_cost, fill_value=0.0)

        return total_fixed_costs[(total_fixed_costs != 0).all(1)].dropna()

    def annual_technology_emissions(self) -> pd.DataFrame:
        """Calculates results ``AnnualTechnologyEmission``

        Notes
        -----
        From the formulation::

            REGION, TECHNOLOGY, EMISSION, YEAR,
            sum{l in TIMESLICE, m in MODE_OF_OPERATION:
                EmissionActivityRatio[r,t,e,m,y]<>0}
            EmissionActivityRatio[r,t,e,m,y] * RateOfActivity[r,l,t,m,y]
                * YearSplit[l,y];

        """
        try:
            data = self["AnnualTechnologyEmissionByMode"].copy(deep=True)
        except KeyError as ex:
            raise KeyError(self._msg("AnnualTechnologyEmission", str(ex)))

        if not data.empty:
            data = data.groupby(by=["REGION", "TECHNOLOGY", "EMISSION", "YEAR"]).sum()

        return data[(data != 0).all(1)]

    def annual_technology_emission_by_mode(self) -> pd.DataFrame:
        """

        Notes
        -----
        From the formulation::

            r~REGION, t~TECHNOLOGY, e~EMISSION, m~MODE_OF_OPERATION, y~YEAR,
            sum{l in TIMESLICE: EmissionActivityRatio[r,t,e,m,y] <> 0}
                EmissionActivityRatio[r,t,e,m,y] * RateOfActivity[r,l,t,m,y]
                    * YearSplit[l,y]
        """
        try:
            emission_activity_ratio: pd.DataFrame = self["EmissionActivityRatio"]
            yearsplit: pd.DataFrame = self["YearSplit"]
            rate_of_activity: pd.DataFrame = self["RateOfActivity"]
        except KeyError as ex:
            raise KeyError(self._msg("AnnualTechnologyEmissionByMode", str(ex)))

        mid = emission_activity_ratio.mul(yearsplit)
        data = mid.mul(rate_of_activity)

        if not data.empty:
            data = data.groupby(
                by=["REGION", "TECHNOLOGY", "EMISSION", "MODE_OF_OPERATION", "YEAR"]
            ).sum()

        return data[(data != 0).all(1)]

    def annual_variable_operating_cost(self) -> pd.DataFrame:
        """AnnualVariableOperatingCost

        Notes
        -----
        From the formulation::

            r~REGION, t~TECHNOLOGY, y~YEAR,
            sum{m in MODE_OF_OPERATION, l in TIMESLICE}
                RateOfActivity[r,l,t,m,y]
                * YearSplit[l,y]
                * VariableCost[r,t,m,y] ~VALUE;

        """
        try:
            rate_of_activity = self["RateOfActivity"]
            yearsplit = self["YearSplit"]
            variable_cost = self["VariableCost"]
        except KeyError as ex:
            raise KeyError(self._msg("AnnualVariableOperatingCost", str(ex)))

        split_activity = rate_of_activity.mul(yearsplit, fill_value=0.0)
        data = split_activity.mul(variable_cost, fill_value=0.0)
        if not data.empty:
            data = data.groupby(by=["REGION", "TECHNOLOGY", "YEAR"]).sum()
        return data[(data != 0).all(1)]

    def capital_investment(self) -> pd.DataFrame:
        """CapitalInvestment

        Notes
        -----
        From the formulation::

            r~REGION, t~TECHNOLOGY, y~YEAR,
            CapitalCost[r,t,y] * NewCapacity[r,t,y] ~VALUE;
        """
        try:
            capital_cost = self["CapitalCost"]
            new_capacity = self["NewCapacity"]
        except KeyError as ex:
            raise KeyError(self._msg("CapitalInvestment", str(ex)))

        data = capital_cost.mul(new_capacity, fill_value=0.0)
        return data[(data != 0).all(1)]

    def demand(self) -> pd.DataFrame:
        """Demand

        Notes
        -----
        From the formulation::

            r~REGION, l~TIMESLICE, f~FUEL, y~YEAR,
            SpecifiedAnnualDemand[r,f,y] * SpecifiedDemandProfile[r,f,l,y] ~VALUE;
        """
        try:
            specified_annual_demand = self["SpecifiedAnnualDemand"]
            specified_demand_profile = self["SpecifiedDemandProfile"]
        except KeyError as ex:
            raise KeyError(self._msg("Demand", str(ex)))

        data = specified_annual_demand.mul(specified_demand_profile, fill_value=0.0)
        if not data.empty:
            data = data.reset_index().set_index(["REGION", "TIMESLICE", "FUEL", "YEAR"])
        return data[(data != 0).all(1)]

    def discounted_tech_emis_pen(self) -> pd.DataFrame:
        """
        Notes
        -----
        From the formulation::

            DiscountedTechnologyEmissionsPenalty[r,t,y] :=

            EmissionActivityRatio[r,t,e,m,y] * RateOfActivity[r,l,t,m,y] *
            YearSplit[l,y] * EmissionsPenalty[r,e,y] /
            ((1+DiscountRate[r, t]) ^ (y - min{yy in YEAR} min(yy) + 0.5))

        """
        try:
            annual_technology_emission_by_mode = self["AnnualTechnologyEmissionByMode"]
            emission_penalty = self["EmissionsPenalty"]
            regions = self["REGION"]["VALUE"].to_list()
            technologies = list(
                annual_technology_emission_by_mode.reset_index()["TECHNOLOGY"].unique()
            )
            years = self["YEAR"]["VALUE"].to_list()
            discount_rate = self["DiscountRate"]

            crf = capital_recovery_factor(
                regions, technologies, years, discount_rate, adj=0.5
            )
        except KeyError as ex:
            raise KeyError(self._msg("DiscountedTechnologyEmissionsPenalty", str(ex)))

        emissions_penalty = annual_technology_emission_by_mode.mul(
            emission_penalty, fill_value=0.0
        )
        data = emissions_penalty.div(crf, fill_value=0.0)

        if not data.empty:
            data = data.groupby(by=["REGION", "TECHNOLOGY", "YEAR"]).sum()

        return data[(data != 0).all(1)]

    def production_by_technology(self) -> pd.DataFrame:
        """Compute production by technology

        ProductionByTechnology

        Notes
        -----
        From the formulation::

            r~REGION, l~TIMESLICE, t~TECHNOLOGY, f~FUEL, y~YEAR,
            sum{m in MODE_OF_OPERATION: OutputActivityRatio[r,t,f,m,y] <> 0}
                RateOfActivity[r,l,t,m,y] * OutputActivityRatio[r,t,f,m,y]
                * YearSplit[l,y] ~VALUE;
        """
        try:
            rate_of_activity = self["RateOfActivity"]
            output_activity_ratio = self["OutputActivityRatio"]
            year_split = self["YearSplit"]
        except KeyError as ex:
            raise KeyError(self._msg("ProductionByTechnology", str(ex)))

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
        try:
            production_by_technology = self["ProductionByTechnology"].copy(deep=True)
        except KeyError as ex:
            raise KeyError(self._msg("ProductionByTechnologyAnnual", str(ex)))

        data = production_by_technology
        if not data.empty:
            data = data.groupby(by=["REGION", "TECHNOLOGY", "FUEL", "YEAR"]).sum()
        return data[(data != 0).all(1)]

    def rate_of_production_tech_mode(self) -> pd.DataFrame:
        """RateOfProductionByTechnologyByMode

        Notes
        -----
        From the formulation::

            r~REGION, l~TIMESLICE, t~TECHNOLOGY, m~MODE_OF_OPERATION, f~FUEL, y~YEAR,
            RateOfActivity[r,l,t,m,y] * OutputActivityRatio[r,t,f,m,y]~VALUE;
        """
        try:
            rate_of_activity = self["RateOfActivity"]
            output_activity_ratio = self["OutputActivityRatio"]
        except KeyError as ex:
            raise KeyError(self._msg("RateOfProductionByTechnologyByMode", str(ex)))

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
        From the formulation::

            r~REGION, l~TIMESLICE, t~TECHNOLOGY, f~FUEL, y~YEAR,
            sum{m in MODE_OF_OPERATION: OutputActivityRatio[r,t,f,m,y] <> 0}
                RateOfActivity[r,l,t,m,y] * OutputActivityRatio[r,t,f,m,y]~VALUE;

        """
        try:
            rate_of_production = self["RateOfProductionByTechnologyByMode"].copy(
                deep=True
            )
        except KeyError as ex:
            raise KeyError(self._msg("RateOfProductionByTechnology", str(ex)))

        data = rate_of_production
        if not data.empty:
            data = data.groupby(
                by=["REGION", "TIMESLICE", "TECHNOLOGY", "FUEL", "YEAR"]
            ).sum()
        return data[(data != 0).all(1)].sort_index()

    def rate_of_use_by_technology(self) -> pd.DataFrame:
        """RateOfUseByTechnology

        Notes
        -----
        From the formulation::

            r~REGION, l~TIMESLICE, t~TECHNOLOGY, f~FUEL, y~YEAR,
            sum{m in MODE_OF_OPERATION: InputActivityRatio[r,t,f,m,y]<>0}
                RateOfActivity[r,l,t,m,y] * InputActivityRatio[r,t,f,m,y]~VALUE;
        """
        try:
            rate_of_use_by_technology_by_mode = self[
                "RateOfUseByTechnologyByMode"
            ].copy(deep=True)
        except KeyError as ex:
            raise KeyError(self._msg("RateOfUseByTechnology", str(ex)))

        data = rate_of_use_by_technology_by_mode
        if not data.empty:
            data = data.groupby(
                by=["REGION", "TIMESLICE", "TECHNOLOGY", "FUEL", "YEAR"]
            ).sum()
        return data[(data != 0).all(1)]

    def rate_of_use_by_technology_by_mode(self) -> pd.DataFrame:
        """RateOfUseByTechnologyByMode

        Notes
        -----
        From the formulation::

            r~REGION, l~TIMESLICE, t~TECHNOLOGY, m~MODE_OF_OPERATION, f~FUEL, y~YEAR,
            RateOfActivity[r,l,t,m,y] * InputActivityRatio[r,t,f,m,y]~VALUE;
        """
        try:
            input_activity_ratio = self["InputActivityRatio"]
            rate_of_activity = self["RateOfActivity"]
        except KeyError as ex:
            raise KeyError(self._msg("RateOfUseByTechnology", str(ex)))

        data = input_activity_ratio.mul(rate_of_activity, fill_value=0.0)

        return data[(data != 0).all(1)]

    def total_annual_tech_activity_mode(self) -> pd.DataFrame:
        """TotalAnnualTechnologyActivityByMode

        Notes
        -----
        From the formulation::

            r~REGION, t~TECHNOLOGY, m~MODE_OF_OPERATION, y~YEAR,
            sum{l in TIMESLICE}
                RateOfActivity[r,l,t,m,y] * YearSplit[l,y]~VALUE;
        """
        try:
            rate_of_activity = self["RateOfActivity"]
            year_split = self["YearSplit"]
        except KeyError as ex:
            raise KeyError(self._msg("TotalAnnualTechnologyActivityByMode", str(ex)))

        data = rate_of_activity.mul(year_split, fill_value=0.0)
        return data[(data != 0).all(1)]

    def total_capacity_annual(self) -> pd.DataFrame:
        """Compute TotalCapacityAnnual result

        Notes
        -----
        From the formulation::

            r~REGION, t~TECHNOLOGY, y~YEAR,
            ResidualCapacity[r,t,y] +
            (sum{yy in YEAR: y-yy < OperationalLife[r,t] && y-yy>=0}
                NewCapacity[r,t,yy])~VALUE;
        """
        try:
            residual_capacity = self["ResidualCapacity"]
            acc_new_capacity = self["AccumulatedNewCapacity"]
        except KeyError as ex:
            raise KeyError(self._msg("TotalCapacityAnnual", str(ex)))

        data = residual_capacity.add(acc_new_capacity, fill_value=0.0)
        return data[(data != 0).all(1)]

    def total_discounted_cost(self) -> pd.DataFrame:
        """TotalDiscountedCost

        Notes
        -----
        From the formulation::

            r~REGION, y~YEAR,
            sum{t in TECHNOLOGY}
            ((((    (sum{yy in YEAR: y-yy
                         < OperationalLife[r,t]
                         && y-yy>=0}
                        NewCapacity[r,t,yy])
                        + ResidualCapacity[r,t,y])
                    * FixedCost[r,t,y]
                    + sum{m in MODE_OF_OPERATION, l in TIMESLICE}
                        RateOfActivity[r,l,t,m,y] * YearSplit[l,y]
                        * VariableCost[r,t,m,y])
                / ((1+DiscountRate[r,t])^(y-min{yy in YEAR} min(yy)+0.5))
                + CapitalCost[r,t,y] * NewCapacity[r,t,y]
                / ((1+DiscountRate[r,t])^(y-min{yy in YEAR} min(yy)))
                + DiscountedTechnologyEmissionsPenalty[r,t,y]
                - DiscountedSalvageValue[r,t,y]
            )    )
            + sum{r in REGION, s in STORAGE, y in YEAR}
                (CapitalCostStorage[r,s,y] * NewStorageCapacity[r,s,y]
                / ((1+DiscountRate[r,t])^(y-min{yy in YEAR} min(yy)))
                    - SalvageValueStorage[r,s,y]
                    / ((1+DiscountRate[r,t])^(max{yy in YEAR}
                        max(yy)-min{yy in YEAR} min(yy)+1))
                )~VALUE;
        """
        try:
            discount_rate = self["DiscountRate"]
            year_df = self["YEAR"].copy(deep=True)
            region_df = self["REGION"].copy(deep=True)

            years = year_df["VALUE"].tolist()
            regions = region_df["VALUE"].tolist()

            annual_fixed_operating_cost = self["AnnualFixedOperatingCost"]
            annual_variable_operating_cost = self["AnnualVariableOperatingCost"]
            capital_investment = self["CapitalInvestment"]

            technologies = self.get_unique_values_from_index(
                [
                    annual_fixed_operating_cost,
                    annual_variable_operating_cost,
                    capital_investment,
                ],
                "TECHNOLOGY",
            )

            discounted_emissions_penalty = self["DiscountedTechnologyEmissionsPenalty"]
            discounted_salvage_value = self["DiscountedSalvageValue"]

            # capital_cost_storage = self["CapitalCostStorage"]
        except KeyError as ex:
            raise KeyError(self._msg("TotalDiscountedCost", str(ex)))

        crf_op = capital_recovery_factor(
            regions, technologies, years, discount_rate, 0.5
        )
        crf_cap = capital_recovery_factor(
            regions, technologies, years, discount_rate, 0.0
        )

        undiscounted_operational_costs = annual_fixed_operating_cost.add(
            annual_variable_operating_cost, fill_value=0.0
        )
        discounted_operational_costs = undiscounted_operational_costs.div(
            crf_op, fill_value=0.0
        )
        discounted_capital_costs = capital_investment.div(crf_cap, fill_value=0.0)
        discounted_total_costs = discounted_operational_costs.add(
            discounted_capital_costs, fill_value=0.0
        )
        discounted_total_costs = discounted_total_costs.add(
            discounted_emissions_penalty, fill_value=0.0
        )
        discounted_total_costs = discounted_total_costs.sub(
            discounted_salvage_value, fill_value=0.0
        )

        # try:
        # new_storage_capacity = self["NewStorageCapacity"]
        # storage_investment = capital_investment.mul(
        #     new_storage_capacity, fill_value=0.0
        # )
        # except KeyError:
        #     LOGGER.info("Cannot find NewStorageCapacity, assuming empty")
        # storage_investment = pd.DataFrame()

        # try:
        # salvage_value_storage = self["SalvageValueStorage"]
        # except KeyError:
        #     LOGGER.info("Cannot find SalvageValueStorage, assuming empty")
        # salvage_value_storage = pd.DataFrame()

        data = discounted_total_costs

        if not data.empty:
            data = data.groupby(by=["REGION", "YEAR"]).sum()

        return data[(data != 0).all(1)].dropna()

    def get_unique_values_from_index(self, dataframes: List, name: str) -> List:
        """Utility function to extract list of unique values

        Extract unique values from the same index of the passed dataframes
        """
        elements = []  # type: List
        for df in dataframes:
            df = df.reset_index()
            if name in df.columns:
                elements += list(df[name].unique())
        return list(set(elements))

    def total_technology_annual_activity(self) -> pd.DataFrame:
        """TotalTechnologyAnnualActivity

        Notes
        -----
        From the formulation::

            ResultsPath & "/TotalTechnologyAnnualActivity.csv":
            r~REGION, t~TECHNOLOGY, y~YEAR,
            sum{l in TIMESLICE, m in MODE_OF_OPERATION}
                RateOfActivity[r,l,t,m,y] * YearSplit[l,y]~VALUE;
        """
        try:
            data = self["TotalAnnualTechnologyActivityByMode"].copy(deep=True)
        except KeyError as ex:
            raise KeyError(self._msg("TotalTechnologyAnnualActivity", str(ex)))

        if not data.empty:
            data = data.groupby(["REGION", "TECHNOLOGY", "YEAR"]).sum()

        return data[(data != 0).all(1)]

    def total_tech_model_period_activity(self) -> pd.DataFrame:
        """TotalTechnologyModelPeriodActivity

        Notes
        -----
        From the formulation::

            ResultsPath & "/TotalTechnologyModelPeriodActivity.csv":
            r~REGION, t~TECHNOLOGY,
            sum{l in TIMESLICE, m in MODE_OF_OPERATION, y in YEAR}
                RateOfActivity[r,l,t,m,y]*YearSplit[l,y]~VALUE;
        """
        try:
            data = self["TotalTechnologyAnnualActivity"].copy(deep=True)
        except KeyError as ex:
            raise KeyError(self._msg("TotalTechnologyModelPeriodActivity", str(ex)))

        if not data.empty:
            data = data.groupby(["REGION", "TECHNOLOGY"]).sum()

        return data[(data != 0).all(1)]

    def use_by_technology(self) -> pd.DataFrame:
        """UseByTechnology

        Notes
        -----
        From the formulation::

            r~REGION, l~TIMESLICE, t~TECHNOLOGY, f~FUEL, y~YEAR,
            sum{m in MODE_OF_OPERATION}
                RateOfActivity[r,l,t,m,y]
                * InputActivityRatio[r,t,f,m,y]
                * YearSplit[l,y]~VALUE;

        """
        try:
            rate_of_use = self["RateOfUseByTechnologyByMode"]
            year_split = self["YearSplit"]
        except KeyError as ex:
            raise KeyError(self._msg("UseByTechnology", str(ex)))

        data = rate_of_use.mul(year_split, fill_value=0.0)

        if not data.empty:
            data = data.groupby(
                ["REGION", "TIMESLICE", "TECHNOLOGY", "FUEL", "YEAR"]
            ).sum()

        return data[(data != 0).all(1)]


def capital_recovery_factor(
    regions: List,
    technologies: List,
    years: List,
    discount_rate: pd.DataFrame,
    adj: float = 0.0,
) -> pd.DataFrame:
    """Calculates the capital recovery factor

    Arguments
    ---------
    regions: list
    years: list
    discount_rate: pd.DataFrame
    adj: float, default=0.0
        Adjust to beginning of the year (default), mid year (0.5) or end year (1.0)
    """
    if regions and technologies and years:
        index = pd.MultiIndex.from_product(
            [regions, technologies, years], names=["REGION", "TECHNOLOGY", "YEAR"]
        )
        crf = discount_rate.reindex(index)
        crf = crf.reset_index(level="YEAR")
        crf["NUM"] = crf["YEAR"] - crf["YEAR"].min()
        crf["Rate"] = 1 + discount_rate
        crf["VALUE"] = crf["Rate"].pow(crf["NUM"] + adj)
        return crf.reset_index()[["REGION", "TECHNOLOGY", "YEAR", "VALUE"]].set_index(
            ["REGION", "TECHNOLOGY", "YEAR"]
        )
    else:
        return pd.DataFrame(
            [], columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"]
        ).set_index(["REGION", "TECHNOLOGY", "YEAR"])
