# -*- coding: utf-8 -*-
"""
    Dummy conftest.py for otoole.

    If you don't know what this is for, just leave it empty.
    Read more about conftest.py under:
    https://pytest.org/latest/plugins.html
"""

from pytest import fixture

import pandas as pd


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
    )
    return df.set_index(
        ["REGION", "TECHNOLOGY", "EMISSION", "MODE_OF_OPERATION", "YEAR"]
    )


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
    )
    return df.set_index(
        ["REGION", "TECHNOLOGY", "EMISSION", "MODE_OF_OPERATION", "YEAR"]
    )


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
    )
    return df.set_index(["TIMESLICE", "YEAR"])
