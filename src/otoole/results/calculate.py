"""

"""
import logging
from typing import Dict

import pandas as pd
from pandas_datapackage_reader import read_datapackage

LOGGER = logging.getLogger(__name__)


def compute_annual_emissions(
    emission_activity_ratio: pd.DataFrame,
    yearsplit: pd.DataFrame,
    rate_of_activity: pd.DataFrame,
) -> pd.DataFrame:
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
    data = emission_activity_ratio.mul(yearsplit, fill_value=0.0)
    data = data.mul(rate_of_activity, fill_value=0.0)

    if not data.empty:
        data = data.groupby(by=["REGION", "EMISSION", "YEAR"]).sum()

        return data.reset_index()

    else:
        return pd.DataFrame()


def compute_accumulated_new_capacity(
    operational_life: pd.DataFrame, new_capacity: pd.DataFrame, year: pd.Index
):
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
    new_capacity["OperationalLife"] = operational_life

    regions = new_capacity.reset_index()["REGION"].unique()
    technologies = new_capacity.reset_index()["TECHNOLOGY"].unique()

    index = pd.MultiIndex.from_product(
        [regions, technologies, year.to_list()], names=["REGION", "TECHNOLOGY", "YEAR"]
    )

    acc_capacity = new_capacity.reindex(index, copy=True)

    for index, data in new_capacity.reset_index().groupby(by=["REGION", "TECHNOLOGY"]):
        region, technology = index
        for yr in year:
            mask = (yr - data["YEAR"] < data["OperationalLife"]) & (
                yr - data["YEAR"] >= 0
            )
            acc_capacity.loc[region, technology, yr] = data[mask].sum()

    acc_capacity = acc_capacity.drop(columns="OperationalLife")
    return acc_capacity[(acc_capacity != 0).all(1)].reset_index()


def compute_annual_technology_emissions(
    emission_activity_ratio: pd.DataFrame,
    yearsplit: pd.DataFrame,
    rate_of_activity: pd.DataFrame,
) -> pd.DataFrame:
    """
    Notes
    -----
    REGION, TECHNOLOGY, EMISSION, YEAR,
    sum{l in TIMESLICE, m in MODE_OF_OPERATION:
        EmissionActivityRatio[r,t,e,m,y]<>0}
    EmissionActivityRatio[r,t,e,m,y] * RateOfActivity[r,l,t,m,y]
        * YearSplit[l,y];
    """
    data = emission_activity_ratio.mul(yearsplit)
    data = data.mul(rate_of_activity)

    if not data.empty:
        data = data.groupby(by=["REGION", "TECHNOLOGY", "EMISSION", "YEAR"]).sum()

        return data[(data != 0).all(1)].reset_index()

    else:
        return pd.DataFrame()


def compute_annual_technology_emission_by_mode(
    emission_activity_ratio: pd.DataFrame,
    yearsplit: pd.DataFrame,
    rate_of_activity: pd.DataFrame,
) -> pd.DataFrame:
    """
    r~REGION, t~TECHNOLOGY, e~EMISSION, m~MODE_OF_OPERATION, y~YEAR,
    sum{l in TIMESLICE: EmissionActivityRatio[r,t,e,m,y] <> 0}
        EmissionActivityRatio[r,t,e,m,y] * RateOfActivity[r,l,t,m,y]
            * YearSplit[l,y]
    """
    data = emission_activity_ratio.mul(yearsplit)
    data = data.mul(rate_of_activity)

    if not data.empty:
        data = data.groupby(
            by=["REGION", "TECHNOLOGY", "EMISSION", "MODE_OF_OPERATION", "YEAR"]
        ).sum()

        return data[(data != 0).all(1)].reset_index()

    else:
        return pd.DataFrame()


def calculate_result(
    parameter_name: str, input_data: str, results_data: Dict[str, pd.DataFrame]
):
    package = read_datapackage(input_data)  # typing: Dict[str, pd.DataFrame]

    if parameter_name == "AccumulatedNewCapacity":
        operational_life = package["OperationalLife"].copy()
        new_capacity = results_data["NewCapacity"].copy()
        year = pd.Index(package["YEAR"]["VALUE"].to_list())
        return compute_accumulated_new_capacity(operational_life, new_capacity, year)
    elif parameter_name == "AnnualEmissions":
        emission_activity_ratio = package["EmissionActivityRatio"]
        yearsplit = package["YearSplit"]
        rate_of_activity = results_data["RateOfActivity"].copy()
        return compute_annual_emissions(
            emission_activity_ratio, yearsplit, rate_of_activity
        )
    elif parameter_name == "AnnualTechnologyEmission":
        emission_activity_ratio = package["EmissionActivityRatio"]
        yearsplit = package["YearSplit"]
        rate_of_activity = results_data["RateOfActivity"].copy()
        return compute_annual_technology_emissions(
            emission_activity_ratio, yearsplit, rate_of_activity
        )
    elif parameter_name == "AnnualTechnologyEmissionByMode":
        emission_activity_ratio = package["EmissionActivityRatio"]
        yearsplit = package["YearSplit"]
        rate_of_activity = results_data["RateOfActivity"].copy()
        return compute_annual_technology_emission_by_mode(
            emission_activity_ratio, yearsplit, rate_of_activity
        )
    else:
        return pd.DataFrame()
