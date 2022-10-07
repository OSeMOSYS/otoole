import os
from typing import Dict

import pandas as pd
from pandas.testing import assert_frame_equal
from pytest import fixture

from otoole.results.results import ReadResults
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
def input_data():
    """To test that data will not be overwritten"""

    capex = pd.DataFrame(
        [
            ["SIMPLICITY", "NGCC", 2014, 1000],
            ["SIMPLICITY", "NGCC", 2015, 900],
            ["SIMPLICITY", "NGCC", 2016, 800],
            ["SIMPLICITY", "HYD1", 2014, 2000],
            ["SIMPLICITY", "HYD1", 2015, 1500],
            ["SIMPLICITY", "HYD1", 2016, 1000],
        ],
        columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"],
    ).set_index(["REGION", "TECHNOLOGY", "YEAR"])

    discount_rate = pd.DataFrame(columns=["VALUE"])

    discount_rate_idv = pd.DataFrame(columns=["VALUE"])

    technology = pd.DataFrame(["NGCC", "HYD1"], columns=["VALUE"])
    year = pd.DataFrame([2014, 2015, 2016], columns=["VALUE"])
    region = pd.DataFrame(["SIMPLICITY"], columns=["VALUE"])

    data = {
        "CapitalCost": capex,
        "DiscountRate": discount_rate,
        "DiscountRateIdv": discount_rate_idv,
        "TECHNOLOGY": technology,
        "YEAR": year,
        "REGION": region,
    }

    return data


@fixture
def result_data():

    new_capacity = pd.DataFrame(
        [
            ["SIMPLICITY", "NGCC", 2014, 10],
            ["SIMPLICITY", "NGCC", 2015, 5],
            ["SIMPLICITY", "HYD1", 2015, 10],
            ["SIMPLICITY", "HYD1", 2016, 5],
        ],
        columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"],
    ).set_index(["REGION", "TECHNOLOGY", "YEAR"])

    discounted_cost = pd.DataFrame(
        [["SIMPLICITY", 2014, 100], ["SIMPLICITY", 2015, 90], ["SIMPLICITY", 2016, 80]],
        columns=["REGION", "YEAR", "VALUE"],
    ).set_index(["REGION", "YEAR"])

    data = {
        "NewCapacity": new_capacity,
        "TotalDiscountedCost": discounted_cost,
    }

    return data


class DummyReadResults(ReadResults):
    def get_results_from_file(self, filepath, input_data):
        raise NotImplementedError()


class TestReadResults:
    def test_expand_parameter_defaults_full(self, input_data, user_config):
        results = DummyReadResults(user_config=user_config)
        expected = input_data["CapitalCost"]
        actual = results._expand_parameter_defaults(input_data)["CapitalCost"]
        assert_frame_equal(actual, expected)

    def test_expand_parameter_defaults_single_index(self, input_data, user_config):
        index = pd.MultiIndex.from_product([["SIMPLICITY"]], names=["REGION"])
        expected = pd.DataFrame(index=index)
        expected["VALUE"] = 0.05
        results = DummyReadResults(user_config=user_config)
        actual = results._expand_parameter_defaults(input_data)["DiscountRate"]
        assert_frame_equal(actual, expected)

    def test_expand_parameter_defaults_multi_index(self, input_data, user_config):
        index = pd.MultiIndex.from_product(
            [["SIMPLICITY"], ["NGCC", "HYD1"]], names=["REGION", "TECHNOLOGY"]
        )
        expected = pd.DataFrame(index=index)
        expected["VALUE"] = 0.05
        results = DummyReadResults(user_config=user_config)
        actual = results._expand_parameter_defaults(input_data)["DiscountRateIdv"]
        assert_frame_equal(actual, expected)

    def test_expand_result_defaults_full(self, input_data, result_data, user_config):
        results = DummyReadResults(user_config=user_config)
        default_values = results._read_default_values(user_config)
        expected = result_data["TotalDiscountedCost"]
        actual = results._expand_result_defaults(
            result_data, input_data, default_values
        )["TotalDiscountedCost"]
        assert_frame_equal(actual, expected)

    def test_expand_result_defaults(self, input_data, result_data, user_config):

        expected = pd.DataFrame(
            [
                ["SIMPLICITY", "HYD1", 2014, 0],
                ["SIMPLICITY", "HYD1", 2015, 10],
                ["SIMPLICITY", "HYD1", 2016, 5],
                ["SIMPLICITY", "NGCC", 2014, 10],
                ["SIMPLICITY", "NGCC", 2015, 5],
                ["SIMPLICITY", "NGCC", 2016, 0],
            ],
            columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"],
        ).set_index(["REGION", "TECHNOLOGY", "YEAR"])

        results = DummyReadResults(user_config=user_config)
        default_values = results._read_default_values(user_config)
        actual = results._expand_result_defaults(
            result_data, input_data, default_values
        )["NewCapacity"]
        assert_frame_equal(actual, expected)
