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
            "CapitalInvestmentStorage": self.capital_investment_storage,
            "Demand": self.demand,
            "DiscountedCapitalInvestment": self.discounted_capital_investment,
            "DiscountedCapitalInvestmentStorage": self.discounted_capital_investment_storage,
            "DiscountedCostByStorage": self.discounted_storage_cost,
            "DiscountedCostByTechnology": self.discounted_technology_cost,
            "DiscountedOperationalCost": self.discounted_operational_cost,
            "DiscountedSalvageValueStorage": self.discounted_salvage_value_storage,
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
        """View the results dictionary"""
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
        """AnnualTechnologyEmissionByMode

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
            CapitalCost[r,t,y] * NewCapacity[r,t,y] * CapitalRecoveryFactor[r,t] *
            PvAnnuity[r,t] ~VALUE;
        """
        try:
            capital_cost = self["CapitalCost"]
            new_capacity = self["NewCapacity"]
            operational_life = self["OperationalLife"]
            discount_rate = self["DiscountRate"]

            if "DiscountRateIdv" in self.keys():
                discount_rate_idv = self["DiscountRateIdv"]
                if discount_rate_idv.empty:
                    discount_rate_idv = self["DiscountRate"]
            else:
                discount_rate_idv = self["DiscountRate"]

            regions = self["REGION"]["VALUE"].to_list()
            technologies = self.get_unique_values_from_index(
                [
                    capital_cost,
                    new_capacity,
                ],
                "TECHNOLOGY",
            )

        except KeyError as ex:
            raise KeyError(self._msg("CapitalInvestment", str(ex)))

        crf = capital_recovery_factor(
            regions, technologies, discount_rate_idv, operational_life
        )
        pva = pv_annuity(regions, technologies, discount_rate, operational_life)
        capital_investment = capital_cost.mul(new_capacity, fill_value=0.0)
        capital_investment = capital_investment.mul(crf, fill_value=0.0).mul(
            pva, fill_value=0.0
        )

        data = capital_investment

        if not data.empty:
            data = data.groupby(by=["REGION", "TECHNOLOGY", "YEAR"]).sum()

        return data[(data != 0).all(1)]

    def capital_investment_storage(self) -> pd.DataFrame:
        """CapitalInvestmentStorage

        Notes
        -----
        From the formulation::

            r~REGION, s~STORAGE, y~YEAR,
            CapitalCostStorage[r,s,y] * NewStorageCapacity[r,s,y]
            ~VALUE;
        """
        try:
            capital_cost_storage = self["CapitalCostStorage"]
            new_capacity_storage = self["NewStorageCapacity"]

        except KeyError as ex:
            raise KeyError(self._msg("CapitalInvestmentStorage", str(ex)))

        capital_investment_storage = capital_cost_storage.mul(
            new_capacity_storage, fill_value=0
        )

        data = capital_investment_storage

        if not data.empty:
            data = data.groupby(by=["REGION", "STORAGE", "YEAR"]).sum()

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
        """DiscountedTechnologyEmissionsPenalty


        Notes
        -----
        From the formulation::

            DiscountedTechnologyEmissionsPenalty[r,t,y] :=
            EmissionActivityRatio[r,t,e,m,y] * RateOfActivity[r,l,t,m,y] *
            YearSplit[l,y] * EmissionsPenalty[r,e,y] / DiscountFactorMid[r,y]
        """
        try:
            annual_technology_emission_by_mode = self["AnnualTechnologyEmissionByMode"]
            emission_penalty = self["EmissionsPenalty"]
            regions = self["REGION"]["VALUE"].to_list()
            years = self["YEAR"]["VALUE"].to_list()
            discount_rate = self["DiscountRate"]

        except KeyError as ex:
            raise KeyError(self._msg("DiscountedTechnologyEmissionsPenalty", str(ex)))

        discount_factor_mid = discount_factor(regions, years, discount_rate, 0.5)
        emissions_penalty = annual_technology_emission_by_mode.mul(
            emission_penalty, fill_value=0.0
        )
        data = emissions_penalty.div(discount_factor_mid, fill_value=0.0)

        if not data.empty:
            data = data.groupby(by=["REGION", "TECHNOLOGY", "YEAR"]).sum()

        return data[(data != 0).all(1)]

    def discounted_capital_investment(self) -> pd.DataFrame:
        """DiscountingCapitalInvestment

        Notes
        -----
        From the formulation::

            r~REGION, t~TECHNOLOGY, y~YEAR,
            DiscountingCapitalInvestment[r,t,y] :=
            CapitalCost[r,t,y] * NewCapacity[r,t,y] * CapitalRecoveryFactor[r,t] * PvAnnuity[r,t] / DiscountFactor[r,y]

        Alternatively, can be written as::

            r~REGION, t~TECHNOLOGY, y~YEAR,
            DiscountingCapitalInvestment[r,t,y] := UndiscountedCapitalInvestment[r,t,y] / DiscountFactor[r,y]

        """

        try:
            discount_rate = self["DiscountRate"]
            year_df = self["YEAR"].copy(deep=True)
            region_df = self["REGION"].copy(deep=True)

            years = year_df["VALUE"].tolist()
            regions = region_df["VALUE"].tolist()
            capital_investment = self["CapitalInvestment"]

        except KeyError as ex:
            raise KeyError(self._msg("DiscountedCapitalInvestment", str(ex)))

        df = discount_factor(regions, years, discount_rate, 0.0)

        data = capital_investment.div(df, fill_value=0.0)

        if not data.empty:
            data = data.groupby(by=["REGION", "TECHNOLOGY", "YEAR"]).sum()

        return data[(data != 0).all(1)]

    def discounted_capital_investment_storage(self) -> pd.DataFrame:
        """DiscountedCapitalInvestmentStorage

        Notes
        -----
        From the formulation::

            r~REGION, s~STORAGE, y~YEAR,
            DiscountedCapitalInvestmentStorage[r,s,y] :=
            CapitalCostStorage[r,s,y] * NewCapacity[r,t,y] / DiscountFactor[r,y]

        Alternatively, can be written as::

            r~REGION, s~STORAGE, y~YEAR,
            DiscountedCapitalInvestmentStorage[r,s,y] := UndiscountedCapitalInvestmentStorage[r,s,y] / DiscountFactor[r,y]

        """

        try:
            discount_rate_storage = self["DiscountRateStorage"]
            year_df = self["YEAR"].copy(deep=True)
            region_df = self["REGION"].copy(deep=True)

            years = year_df["VALUE"].tolist()
            regions = region_df["VALUE"].tolist()
            capital_investment_storage = self["CapitalInvestmentStorage"]

            storages = self.get_unique_values_from_index(
                [
                    capital_investment_storage,
                ],
                "STORAGE",
            )

        except KeyError as ex:
            raise KeyError(self._msg("DiscountedCapitalInvestmentStorage", str(ex)))

        dfs = discount_factor_storage(
            regions, storages, years, discount_rate_storage, 0.0
        )

        data = capital_investment_storage.div(dfs, fill_value=0.0)

        if not data.empty:
            data = data.groupby(by=["REGION", "STORAGE", "YEAR"]).sum()

        return data[(data != 0).all(1)]

    def discounted_operational_cost(self) -> pd.DataFrame:
        """DiscountedOperationalCosts

        Notes
        -----
        From the formulation::

            r~REGION, t~TECHNOLOGY, y~YEAR,
            DiscountedOperatingCost[r,t,y] :=
            (
                (
                    (
                        sum{yy in YEAR: y-yy < OperationalLife[r,t] && y-yy>=0}
                        NewCapacity[r,t,yy]
                    )
                    + ResidualCapacity[r,t,y]
                )
                * FixedCost[r,t,y]
                + sum{l in TIMESLICE, m in MODEperTECHNOLOGY[t]}
                RateOfActivity[r,l,t,m,y] * YearSplit[l,y] * VariableCost[r,t,m,y]
            )
            / (DiscountFactorMid[r,y])

        Alternatively, can be written as::

            r~REGION, t~TECHNOLOGY, y~YEAR,
            DiscountedOperatingCost[r,t,y] :=
            (
                AnnualVariableOperatingCost[r,t,y] + AnnualFixedOperatingCost[r,t,y]
            )
            / DiscountFactorMid[r, y]

            OR

            r~REGION, t~TECHNOLOGY, y~YEAR,
            DiscountedOperatingCost[r,t,y] := OperatingCost[r,t,y] / DiscountFactorMid[r, y]

        """

        try:
            discount_rate = self["DiscountRate"]
            year_df = self["YEAR"].copy(deep=True)
            region_df = self["REGION"].copy(deep=True)

            years = year_df["VALUE"].tolist()
            regions = region_df["VALUE"].tolist()

            annual_fixed_operating_cost = self["AnnualFixedOperatingCost"]
            annual_variable_operating_cost = self["AnnualVariableOperatingCost"]

        except KeyError as ex:
            raise KeyError(self._msg("DiscountedOperationalCost", str(ex)))

        df_mid = discount_factor(regions, years, discount_rate, 0.5)

        undiscounted_operational_costs = annual_fixed_operating_cost.add(
            annual_variable_operating_cost, fill_value=0.0
        )

        discounted_operational_costs = undiscounted_operational_costs.div(
            df_mid, fill_value=0.0
        )

        data = discounted_operational_costs

        if not data.empty:
            data = data.groupby(by=["REGION", "TECHNOLOGY", "YEAR"]).sum()

        return data[(data != 0).all(1)]

    def discounted_storage_cost(self) -> pd.DataFrame:
        """TotalDiscountedCostByStorage

        Notes
        -----
        From the formulation::

            r~REGION, s~STORAGE, y~YEAR,
            TotalDiscountedStorageCost[r,s,y]:=
            (
                CapitalCostStorage[r,s,y] * NewStorageCapacity[r,s,y] / DiscountFactorStorage[r,s,y] -
                SalvageValueStorage[r,s,y] /
                (
                    (1+DiscountRateStorage[r,s])^(max{yy in YEAR} max(yy)-min{yy in YEAR} min(yy)+1))
                )
            )

        Alternatively, can be written as::

            r~REGION, s~STORAGE, y~YEAR,
            TotalDiscountedStorageCost[r,s,y]:=
            DiscountedCapitalInvestmentStorage[r,s,y] - DiscountedSalvageValueStorage[r,s,y]
        """

        try:
            discounted_capital_investment_storage = self[
                "DiscountedCapitalInvestmentStorage"
            ]
            discounted_salvage_value_storage = self["DiscountedSalvageValueStorage"]

        except KeyError as ex:
            raise KeyError(self._msg("TotalDiscountedCostByStorage", str(ex)))

        discounted_storage_costs = discounted_capital_investment_storage.sub(
            discounted_salvage_value_storage, fill_value=0.0
        )

        data = discounted_storage_costs

        if not data.empty:
            data = data.groupby(by=["REGION", "STORAGE", "YEAR"]).sum()
        return data[(data != 0).all(1)]

    def discounted_salvage_value_storage(self) -> pd.DataFrame:
        """DiscountedSalvageValueStorage

        Notes
        -----
        From the formulation::

            DiscountedSalvageValueStorage[r,s,y] = SalvageValueStorage[r,s,y] / ((1+DiscountRateStorage[r,s])^(max{yy in YEAR} max(yy)-min{yy in YEAR} min(yy)+1)))
        """

        try:
            salvage_value_storage = self["SalvageValueStorage"]
            discount_rate_storage = self["DiscountRateStorage"]
            year_df = self["YEAR"].copy(deep=True)
            region_df = self["REGION"].copy(deep=True)
            storage_df = self["STORAGE"].copy(deep=True)

            years = year_df["VALUE"].tolist()
            regions = region_df["VALUE"].tolist()
            storages = storage_df["VALUE"].tolist()

        except KeyError as ex:
            raise KeyError(self._msg("DiscountedSalvageValueStorage", str(ex)))

        df_storage_salvage = discount_factor_storage_salvage(
            regions, storages, years, discount_rate_storage
        )

        discounted_salvage_value_storage = salvage_value_storage.div(
            df_storage_salvage, fill_value=0
        )

        data = discounted_salvage_value_storage

        if not data.empty:
            data = data.groupby(by=["REGION", "STORAGE", "YEAR"]).sum()

        return data[(data != 0).all(1)]

    def discounted_technology_cost(self) -> pd.DataFrame:
        """TotalDiscountedCostByTechnology

        Notes
        -----
        From the formulation::

            r~REGION, t~TECHNOLOGY, y~YEAR,
            TotalDiscountedCostByTechnology[r,t,y]:=
            (
                (
                    (
                        sum{yy in YEAR: y-yy < OperationalLife[r,t] && y-yy>=0}
                        NewCapacity[r,t,yy]
                    )
                    + ResidualCapacity[r,t,y]
                )
                * FixedCost[r,t,y]
                + sum{l in TIMESLICE, m in MODEperTECHNOLOGY[t]}
                RateOfActivity[r,l,t,m,y] * YearSplit[l,y] * VariableCost[r,t,m,y]
            )
            / (DiscountFactorMid[r,y])
            + CapitalCost[r,t,y] * NewCapacity[r,t,y] * CapitalRecoveryFactor[r,t] * PvAnnuity[r,t] / (DiscountFactor[r,y])
            + DiscountedTechnologyEmissionsPenalty[r,t,y] - DiscountedSalvageValue[r,t,y])

        Alternatively, can be written as::

            r~REGION, t~TECHNOLOGY, y~YEAR,
            TotalDiscountedCostByTechnology[r,t,y]: =
            DiscountedOperatingCost[r,t,y] + DiscountedCapitalInvestment[r,t,y] + DiscountedTechnologyEmissionsPenalty[r,t,y] - DiscountedSalvageValue[r,t,y]
        """

        try:
            discounted_capital_costs = self["DiscountedCapitalInvestment"]
            discounted_operational_costs = self["DiscountedOperationalCost"]
            discounted_emissions_penalty = self["DiscountedTechnologyEmissionsPenalty"]
            discounted_salvage_value = self["DiscountedSalvageValue"]

        except KeyError as ex:
            raise KeyError(self._msg("DiscountedCostByTechnology", str(ex)))

        discounted_total_costs = discounted_operational_costs.add(
            discounted_capital_costs, fill_value=0.0
        )

        discounted_total_costs = discounted_total_costs.add(
            discounted_emissions_penalty, fill_value=0.0
        )

        discounted_total_costs = discounted_total_costs.sub(
            discounted_salvage_value, fill_value=0.0
        )

        data = discounted_total_costs

        if not data.empty:
            data = data.groupby(by=["REGION", "TECHNOLOGY", "YEAR"]).sum()
        return data[(data != 0).all(1)]

    def production_by_technology(self) -> pd.DataFrame:
        """ProductionByTechnology

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
        """Aggregates production by technology to the annual level"""
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
        """TotalCapacityAnnual

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
            (
                (
                    (
                        (
                            sum{yy in YEAR: y-yy < OperationalLife[r,t] && y-yy>=0}
                            NewCapacity[r,t,yy]
                        )
                        + ResidualCapacity[r,t,y]
                    )
                    * FixedCost[r,t,y]
                    + sum{l in TIMESLICE, m in MODEperTECHNOLOGY[t]}
                    RateOfActivity[r,l,t,m,y] * YearSplit[l,y] * VariableCost[r,t,m,y]
                )
                / (DiscountFactorMid[r,y])
                + CapitalCost[r,t,y] * NewCapacity[r,t,y] * CapitalRecoveryFactor[r,t] * PvAnnuity[r,t] / (DiscountFactor[r,y])
                + DiscountedTechnologyEmissionsPenalty[r,t,y] - DiscountedSalvageValue[r,t,y])
                + sum{r in REGION, s in STORAGE, y in YEAR}
                (
                    CapitalCostStorage[r,s,y] * NewStorageCapacity[r,s,y] / (DiscountFactorStorage[r,s,y]
                    - SalvageValueStorage[r,s,y] / ((1+DiscountRateStorage[r,s])^(max{yy in YEAR} max(yy)-min{yy in YEAR} min(yy)+1))
                )
            ) ~VALUE;

        Alternatively, can be written as::

            r~REGION, y~YEAR,
            TotalDiscountedCost[r,y] :=
            sum{t in TECHNOLOGY} TotalDiscountedCostByTechnology[r,t,y] + sum{s in STORAGE} TotalDiscountedStorageCost[r,s,y]
        """
        try:
            discounted_cost_by_technology = self["DiscountedCostByTechnology"]
        except KeyError as ex:
            raise KeyError(self._msg("TotalDiscountedCost", str(ex)))

        discounted_tech = (
            discounted_cost_by_technology.droplevel("TECHNOLOGY")
            .reset_index()
            .groupby(["REGION", "YEAR"])
            .sum()
        )

        try:
            discounted_cost_by_storage = self["DiscountedCostByStorage"]

            discounted_storage = (
                discounted_cost_by_storage.droplevel("STORAGE")
                .reset_index()
                .groupby(["REGION", "YEAR"])
                .sum()
            )
        except KeyError as ex:  # storage not always included
            LOGGER.debug(ex)

            discounted_storage = pd.DataFrame(
                columns=["REGION", "YEAR", "VALUE"]
            ).set_index(["REGION", "YEAR"])

        total_discounted_cost = discounted_tech.add(
            discounted_storage, fill_value=0
        ).astype(float)

        data = total_discounted_cost

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
    discount_rate_idv: pd.DataFrame,
    operational_life: pd.DataFrame,
) -> pd.DataFrame:
    """Calculates the capital recovery factor

    Arguments
    ---------
    regions: list
    technologies: list
    discount_rate_idv: pd.DataFrame
    operational_life: pd.DataFrame

    Notes
    -----
    From the formulation::

        param CapitalRecoveryFactor{r in REGION, t in TECHNOLOGY} :=
                (1 - (1 + DiscountRateIdv[r,t])^(-1))/(1 - (1 + DiscountRateIdv[r,t])^(-(OperationalLife[r,t])));
    """

    def calc_crf(df: pd.DataFrame, operational_life: pd.Series) -> pd.Series:
        rate = df["VALUE"] + 1
        numerator = 1 - rate.pow(-1)
        denominator = 1 - rate.pow(-operational_life)

        return numerator / denominator

    if discount_rate_idv.empty or operational_life.empty:
        raise ValueError("Cannot calculate PV Annuity due to missing data")

    if not regions and not technologies:
        return pd.DataFrame(
            data=[],
            columns=["REGION", "TECHNOLOGY", "VALUE"],
        ).set_index(["REGION", "TECHNOLOGY"])

    index = pd.MultiIndex.from_product(
        [regions, technologies], names=["REGION", "TECHNOLOGY"]
    )
    if "TECHNOLOGY" in discount_rate_idv.index.names:
        crf = discount_rate_idv.reindex(index)
        crf["VALUE"] = calc_crf(crf, operational_life["VALUE"])

    else:
        values = discount_rate_idv["VALUE"].copy()
        crf = discount_rate_idv.reindex(index)
        # This is a hack to get around the fact that the discount rate is
        # indexed by REGION and not REGION, TECHNOLOGY
        crf[:] = values
        crf["VALUE"] = calc_crf(crf, operational_life["VALUE"])

    return crf.reset_index()[["REGION", "TECHNOLOGY", "VALUE"]].set_index(
        ["REGION", "TECHNOLOGY"]
    )


def pv_annuity(
    regions: List,
    technologies: List,
    discount_rate: pd.DataFrame,
    operational_life: pd.DataFrame,
) -> pd.DataFrame:
    """Calculates the present value of an annuity

    Arguments
    ---------
    regions: list
    technologies: list
    discount_rate: pd.DataFrame
    operational_life: pd.DataFrame

    Notes
    -----
    From the formulation::

        param PvAnnuity{r in REGION, t in TECHNOLOGY} :=
                (1 - (1 + DiscountRate[r])^(-(OperationalLife[r,t]))) * (1 + DiscountRate[r]) / DiscountRate[r];
    """

    if discount_rate.empty or operational_life.empty:
        raise ValueError("Cannot calculate PV Annuity due to missing data")

    if regions and technologies:
        index = pd.MultiIndex.from_product(
            [regions, technologies], names=["REGION", "TECHNOLOGY"]
        )

        pva = discount_rate.reindex(index).reset_index(level="TECHNOLOGY")
        pva["RATE"] = discount_rate["VALUE"] + 1
        pva = pva.set_index([pva.index, "TECHNOLOGY"])

        pva["VALUE"] = (
            (1 - pva["RATE"].pow(-operational_life["VALUE"])).mul(pva["RATE"])
            / discount_rate["VALUE"]
        ).round(6)

        return pva.reset_index()[["REGION", "TECHNOLOGY", "VALUE"]].set_index(
            ["REGION", "TECHNOLOGY"]
        )
    else:
        return pd.DataFrame([], columns=["REGION", "TECHNOLOGY", "VALUE"]).set_index(
            ["REGION", "TECHNOLOGY"]
        )


def discount_factor(
    regions: List,
    years: List,
    discount_rate: pd.DataFrame,
    adj: float = 0.0,
) -> pd.DataFrame:
    """DiscountFactor

    Arguments
    ---------
    regions: list
    years: list
    discount_rate: pd.DataFrame
    adj: float, default=0.0
        Adjust to beginning of the year (default), mid year (0.5) or end year (1.0)

    Notes
    -----
    From the formulation::

        param DiscountFactor{r in REGION, y in YEAR} :=
                (1 + DiscountRate[r]) ^ (y - min{yy in YEAR} min(yy) + 0.0);

        param DiscountFactorMid{r in REGION, y in YEAR} :=
                (1 + DiscountRate[r]) ^ (y - min{yy in YEAR} min(yy) + 0.5);
    """

    if discount_rate.empty:
        raise ValueError(
            "Cannot calculate discount factor due to missing discount rate"
        )

    if regions and years:
        discount_rate["YEAR"] = [years]
        discount_factor = discount_rate.explode("YEAR").reset_index(level="REGION")
        discount_factor["YEAR"] = discount_factor["YEAR"].astype("int64")
        discount_factor["NUM"] = discount_factor["YEAR"] - discount_factor["YEAR"].min()
        discount_factor["RATE"] = discount_factor["VALUE"] + 1
        discount_factor["VALUE"] = (
            discount_factor["RATE"].pow(discount_factor["NUM"] + adj).astype(float)
        )
        return discount_factor.reset_index()[["REGION", "YEAR", "VALUE"]].set_index(
            ["REGION", "YEAR"]
        )
    else:
        return pd.DataFrame([], columns=["REGION", "YEAR", "VALUE"]).set_index(
            ["REGION", "YEAR"]
        )


def discount_factor_storage(
    regions: List,
    storages: List,
    years: List,
    discount_rate_storage: pd.DataFrame,
    adj: float = 0.0,
) -> pd.DataFrame:
    """DiscountFactorStorage

    Arguments
    ---------
    regions: list
    storages: list
    years: list
    discount_rate_storage: pd.DataFrame
    adj: float, default=0.0
        Adjust to beginning of the year (default), mid year (0.5) or end year (1.0)

    Notes
    -----
    From the formulation::

        param DiscountFactorStorage{r in REGION, s in STORAGE, y in YEAR} :=
                (1 + DiscountRateStorage[r,s]) ^ (y - min{yy in YEAR} min(yy) + 0.0);
    """

    if discount_rate_storage.empty:
        raise ValueError(
            "Cannot calculate discount_factor_storage due to missing discount rate"
        )

    if regions and years:
        index = pd.MultiIndex.from_product(
            [regions, storages, years], names=["REGION", "STORAGE", "YEAR"]
        )
        discount_fac_storage = discount_rate_storage.reindex(index).reset_index(
            level="YEAR"
        )
        discount_fac_storage["NUM"] = (
            discount_fac_storage["YEAR"] - discount_fac_storage["YEAR"].min()
        )
        discount_fac_storage["RATE"] = 1 + discount_rate_storage
        discount_fac_storage["VALUE"] = discount_fac_storage["RATE"].pow(
            discount_fac_storage["NUM"] + adj
        )
        return discount_fac_storage.reset_index()[
            ["REGION", "STORAGE", "YEAR", "VALUE"]
        ].set_index(["REGION", "STORAGE", "YEAR"])
    else:
        return pd.DataFrame(
            [], columns=["REGION", "STORAGE", "YEAR", "VALUE"]
        ).set_index(["REGION", "STORAGE", "YEAR"])


def discount_factor_storage_salvage(
    regions: List,
    storages: List,
    years: List,
    discount_rate_storage: pd.DataFrame,
) -> pd.DataFrame:
    """Discount Factor used for salvage value claculations

    Arguments
    ---------
    regions: list
    storages: list
    years: list
    discount_rate_storage: pd.DataFrame

    Notes
    -----
    From the formulation::

        ((1+DiscountRateStorage[r,s])^(1+max{yy in YEAR} max(yy)-min{yy in YEAR} min(yy)));
    """

    if discount_rate_storage.empty:
        raise ValueError(
            "Cannot calculate discount_factor_storage_salvage due to missing discount rate"
        )

    if regions and years:
        index = pd.MultiIndex.from_product(
            [regions, storages, years], names=["REGION", "STORAGE", "YEAR"]
        )
        discount_fac_storage_salv = discount_rate_storage.reindex(index)

        max_year = max(years)
        min_year = min(years)

        discount_fac_storage_salv["VALUE"] = (1 + discount_fac_storage_salv).pow(
            1 + max_year - min_year
        )

        return discount_fac_storage_salv

    else:
        return pd.DataFrame(
            [], columns=["REGION", "STORAGE", "YEAR", "VALUE"]
        ).set_index(["REGION", "STORAGE", "YEAR"])
