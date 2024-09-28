# -*- coding: utf-8 -*-
"""
    Dummy conftest.py for otoole.

    If you don't know what this is for, just leave it empty.
    Read more about conftest.py under:
    https://pytest.org/latest/plugins.html
"""

import os
from typing import Dict

import pandas as pd
from pytest import fixture

from otoole.utils import _read_file


@fixture
def user_config() -> Dict:
    """Reads in an example user config

    Read in an example user config file which can be passed into all
    Read and Write strategies for testing

    Returns
    -------
    Dict
    """
    file_path = os.path.join("tests", "fixtures", "config.yaml")
    with open(file_path, "r") as config_file:
        config = _read_file(config_file, ".yaml")  # typing: Dict

    file_path = os.path.join("tests", "fixtures", "config_r.yaml")
    with open(file_path, "r") as config_file:
        results = _read_file(config_file, ".yaml")  # typing: Dict

    config.update(results)

    return config


@fixture
def annual_technology_emissions_by_mode():
    df = pd.DataFrame(
        data=[["SIMPLICITY", "GAS_EXTRACTION", "CO2", 1, 2014, 1.0]],
        columns=[
            "REGION",
            "TECHNOLOGY",
            "EMISSION",
            "MODE_OF_OPERATION",
            "YEAR",
            "VALUE",
        ],
    ).set_index(["REGION", "TECHNOLOGY", "EMISSION", "MODE_OF_OPERATION", "YEAR"])
    return df


@fixture
def discount_rate():
    df = pd.DataFrame(
        data=[["SIMPLICITY", 0.05]],
        columns=["REGION", "VALUE"],
    ).set_index(["REGION"])
    return df


@fixture
def discount_rate_idv():
    df = pd.DataFrame(
        data=[["SIMPLICITY", "GAS_EXTRACTION", 0.05], ["SIMPLICITY", "DUMMY", 0.05]],
        columns=["REGION", "TECHNOLOGY", "VALUE"],
    ).set_index(["REGION", "TECHNOLOGY"])
    return df


@fixture
def discount_rate_storage():
    df = pd.DataFrame(
        data=[["SIMPLICITY", "DAM", 0.05]],
        columns=["REGION", "STORAGE", "VALUE"],
    ).set_index(["REGION", "STORAGE"])
    return df


@fixture
def discount_rate_empty():
    df = pd.DataFrame(
        data=[],
        columns=["REGION", "VALUE"],
    ).set_index(["REGION"])
    return df


@fixture
def discount_rate_idv_empty():
    df = pd.DataFrame(
        data=[],
        columns=["REGION", "TECHNOLOGY", "VALUE"],
    ).set_index(["REGION", "TECHNOLOGY"])
    return df


@fixture
def discount_rate_storage_empty():
    df = pd.DataFrame(
        data=[],
        columns=["REGION", "STORAGE", "VALUE"],
    ).set_index(["REGION", "STORAGE"])
    return df


@fixture
def emission_activity_ratio():
    df = pd.DataFrame(
        data=[["SIMPLICITY", "GAS_EXTRACTION", "CO2", 1, 2014, 1.0]],
        columns=[
            "REGION",
            "TECHNOLOGY",
            "EMISSION",
            "MODE_OF_OPERATION",
            "YEAR",
            "VALUE",
        ],
    ).set_index(["REGION", "TECHNOLOGY", "EMISSION", "MODE_OF_OPERATION", "YEAR"])
    return df


@fixture
def emission_activity_ratio_two_techs():
    df = pd.DataFrame(
        data=[
            ["SIMPLICITY", "GAS_EXTRACTION", "CO2", 1, 2014, 1.0],
            ["SIMPLICITY", "DUMMY", "CO2", 1, 2014, 0.0],
        ],
        columns=[
            "REGION",
            "TECHNOLOGY",
            "EMISSION",
            "MODE_OF_OPERATION",
            "YEAR",
            "VALUE",
        ],
    ).set_index(["REGION", "TECHNOLOGY", "EMISSION", "MODE_OF_OPERATION", "YEAR"])

    return df


@fixture
def emissions_penalty():
    df = pd.DataFrame(
        data=[
            ["SIMPLICITY", "CO2", 2014, 1.23],
            ["SIMPLICITY", "CO2", 2015, 1.23],
            ["SIMPLICITY", "CO2", 2016, 1.23],
        ],
        columns=["REGION", "EMISSION", "YEAR", "VALUE"],
    ).set_index(["REGION", "EMISSION", "YEAR"])
    return df


@fixture
def yearsplit():
    df = pd.DataFrame(
        data=[
            ["ID", 2014, 0.1667],
            ["IN", 2014, 0.0833],
            ["SD", 2014, 0.1667],
            ["SN", 2014, 0.0833],
            ["WD", 2014, 0.3333],
            ["WN", 2014, 0.1667],
        ],
        columns=["TIMESLICE", "YEAR", "VALUE"],
    ).set_index(["TIMESLICE", "YEAR"])
    return df
