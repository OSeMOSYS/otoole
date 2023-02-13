from typing import Any, Dict, TextIO, Tuple, Union

import pandas as pd
from pandas.testing import assert_frame_equal
from pytest import fixture, mark, raises

from otoole.input import ReadStrategy, WriteStrategy


@fixture
def year():
    return pd.DataFrame(data=[2014, 2015, 2016], columns=["VALUE"])


@fixture
def region():
    return pd.DataFrame(data=["SIMPLICITY"], columns=["VALUE"])


@fixture
def technology():
    return pd.DataFrame(data=["NGCC", "HYD1"], columns=["VALUE"])


@fixture()
def simple_default_values():
    default_values = {}
    default_values["CapitalCost"] = -1.0
    default_values["DiscountRate"] = 0.25
    default_values["NewCapacity"] = 20
    return default_values


@fixture
def simple_input_data(region, year, technology):
    return {
        "REGION": region,
        "TECHNOLOGY": technology,
        "YEAR": year,
    }


# To instantiate abstract class WriteStrategy
class DummyWriteStrategy(WriteStrategy):
    def _header(self) -> Union[TextIO, Any]:
        raise NotImplementedError()

    def _write_parameter(
        self,
        df: pd.DataFrame,
        parameter_name: str,
        handle: TextIO,
        default: float,
        **kwargs
    ) -> pd.DataFrame:
        raise NotImplementedError()

    def _write_set(self, df: pd.DataFrame, set_name, handle: TextIO) -> pd.DataFrame:
        raise NotImplementedError()

    def _footer(self, handle: TextIO):
        raise NotImplementedError()


# To instantiate abstract class ReadStrategy
class DummyReadStrategy(ReadStrategy):
    def read(
        self, filepath: Union[str, TextIO], **kwargs
    ) -> Tuple[Dict[str, pd.DataFrame], Dict[str, Any]]:
        raise NotImplementedError()


class TestExpandDefaults:

    year = pd.DataFrame(data=[2014, 2015, 2016], columns=["VALUE"])
    region = pd.DataFrame(data=["SIMPLICITY"], columns=["VALUE"])
    technology = pd.DataFrame(data=["NGCC", "HYD1"], columns=["VALUE"])

    def input_data_multi_index_no_defaults(region, technology, year):
        capex_in = pd.DataFrame(
            [
                ["SIMPLICITY", "HYD1", 2014, 2000],
                ["SIMPLICITY", "HYD1", 2015, 1500],
                ["SIMPLICITY", "HYD1", 2016, 1000],
                ["SIMPLICITY", "NGCC", 2014, 1000],
                ["SIMPLICITY", "NGCC", 2015, 900],
                ["SIMPLICITY", "NGCC", 2016, 800],
            ],
            columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"],
        ).set_index(["REGION", "TECHNOLOGY", "YEAR"])
        capex_out = capex_in.copy()
        capex_out["VALUE"] = capex_out["VALUE"].astype(float)

        data = {
            "CapitalCost": capex_in,
            "TECHNOLOGY": technology,
            "YEAR": year,
            "REGION": region,
        }
        return data, "CapitalCost", capex_out

    def input_data_multi_index(region, technology, year):
        capex_in = pd.DataFrame(
            [
                ["SIMPLICITY", "NGCC", 2014, 1000],
                ["SIMPLICITY", "NGCC", 2015, 900],
                ["SIMPLICITY", "HYD1", 2015, 1500],
                ["SIMPLICITY", "HYD1", 2016, 1000],
            ],
            columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"],
        ).set_index(["REGION", "TECHNOLOGY", "YEAR"])
        capex_out = pd.DataFrame(
            [
                ["SIMPLICITY", "HYD1", 2014, -1],
                ["SIMPLICITY", "HYD1", 2015, 1500],
                ["SIMPLICITY", "HYD1", 2016, 1000],
                ["SIMPLICITY", "NGCC", 2014, 1000],
                ["SIMPLICITY", "NGCC", 2015, 900],
                ["SIMPLICITY", "NGCC", 2016, -1],
            ],
            columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"],
        ).set_index(["REGION", "TECHNOLOGY", "YEAR"])
        capex_out["VALUE"] = capex_out["VALUE"].astype(float)

        data = {
            "CapitalCost": capex_in,
            "TECHNOLOGY": technology,
            "YEAR": year,
            "REGION": region,
        }
        return data, "CapitalCost", capex_out

    def input_data_multi_index_empty(region, technology, year):
        capex_in = pd.DataFrame(
            [],
            columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"],
        ).set_index(["REGION", "TECHNOLOGY", "YEAR"])
        capex_out = pd.DataFrame(
            [
                ["SIMPLICITY", "HYD1", 2014, -1],
                ["SIMPLICITY", "HYD1", 2015, -1],
                ["SIMPLICITY", "HYD1", 2016, -1],
                ["SIMPLICITY", "NGCC", 2014, -1],
                ["SIMPLICITY", "NGCC", 2015, -1],
                ["SIMPLICITY", "NGCC", 2016, -1],
            ],
            columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"],
        ).set_index(["REGION", "TECHNOLOGY", "YEAR"])
        capex_out["VALUE"] = capex_out["VALUE"].astype(float)

        data = {
            "CapitalCost": capex_in,
            "TECHNOLOGY": technology,
            "YEAR": year,
            "REGION": region,
        }
        return data, "CapitalCost", capex_out

    def input_data_single_index(region):
        discount_rate_in = pd.DataFrame(
            [["SIMPLICITY", 0.05]], columns=["REGION", "VALUE"]
        ).set_index(["REGION"])
        discount_rate_out = discount_rate_in.copy()
        discount_rate_out["VALUE"] = discount_rate_out["VALUE"].astype(float)

        data = {
            "DiscountRate": discount_rate_in,
            "REGION": region,
        }
        return data, "DiscountRate", discount_rate_out

    def input_data_single_index_empty(region):
        discount_rate_in = pd.DataFrame([], columns=["REGION", "VALUE"]).set_index(
            ["REGION"]
        )
        discount_rate_out = pd.DataFrame(
            [["SIMPLICITY", 0.25]], columns=["REGION", "VALUE"]
        ).set_index(["REGION"])
        discount_rate_out["VALUE"] = discount_rate_out["VALUE"].astype(float)

        data = {
            "DiscountRate": discount_rate_in,
            "TECHNOLOGY": technology,
            "YEAR": year,
            "REGION": region,
        }
        return data, "DiscountRate", discount_rate_out

    @fixture
    def result_data(region):
        new_capacity_in = pd.DataFrame(
            [
                ["SIMPLICITY", "HYD1", 2015, 100],
                ["SIMPLICITY", "HYD1", 2016, 0.1],
                ["SIMPLICITY", "NGCC", 2014, 0.5],
                ["SIMPLICITY", "NGCC", 2015, 100],
            ],
            columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"],
        ).set_index(["REGION", "TECHNOLOGY", "YEAR"])
        new_capacity_out = pd.DataFrame(
            [
                ["SIMPLICITY", "HYD1", 2014, 20],
                ["SIMPLICITY", "HYD1", 2015, 100],
                ["SIMPLICITY", "HYD1", 2016, 0.1],
                ["SIMPLICITY", "NGCC", 2014, 0.5],
                ["SIMPLICITY", "NGCC", 2015, 100],
                ["SIMPLICITY", "NGCC", 2016, 20],
            ],
            columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"],
        ).set_index(["REGION", "TECHNOLOGY", "YEAR"])

        data = {
            "NewCapacity": new_capacity_in,
        }
        return data, "NewCapacity", new_capacity_out

    parameter_test_data = [
        input_data_multi_index_no_defaults(region, technology, year),
        input_data_multi_index(region, technology, year),
        input_data_multi_index_empty(region, technology, year),
        input_data_single_index(region),
        input_data_single_index_empty(region),
    ]
    parameter_test_data_ids = [
        "multi_index_no_defaluts",
        "multi_index",
        "multi_index_empty",
        "single_index",
        "single_index_empty",
    ]

    @mark.parametrize(
        "input_data,parameter,expected",
        parameter_test_data,
        ids=parameter_test_data_ids,
    )
    def test_expand_parmaters_defaults(
        self, user_config, simple_default_values, input_data, parameter, expected
    ):
        write_strategy = DummyWriteStrategy(
            user_config=user_config, default_values=simple_default_values
        )
        actual = write_strategy._expand_defaults(
            input_data, write_strategy.default_values
        )
        assert_frame_equal(actual[parameter], expected)

    def test_expand_result_defaults(
        self, user_config, simple_default_values, simple_input_data, result_data
    ):
        write_strategy = DummyWriteStrategy(
            user_config=user_config, default_values=simple_default_values
        )
        actual = write_strategy._expand_defaults(
            result_data[0], write_strategy.default_values, input_data=simple_input_data
        )
        assert_frame_equal(actual[result_data[1]], result_data[2])

    def test_expand_defaults_exception(
        self, user_config, simple_default_values, result_data
    ):
        write_strategy = DummyWriteStrategy(
            user_config=user_config, default_values=simple_default_values
        )
        with raises(KeyError):
            write_strategy._expand_defaults(
                result_data[0], write_strategy.default_values
            )


class TestReadStrategy:
    missing_input_test_data = (
        (
            "param",
            "AccumulatedAnnualDemand",
            pd.DataFrame(columns=["REGION", "FUEL", "YEAR", "VALUE"]).set_index(
                ["REGION", "FUEL", "YEAR"]
            ),
        ),
        ("set", "REGION", pd.DataFrame(columns=["VALUE"])),
    )

    @mark.parametrize(
        "config_type, test_value, expected",
        missing_input_test_data,
        ids=["param", "set"],
    )
    def test_get_missing_input_dataframes(
        self, user_config, config_type, test_value, expected
    ):
        input_data = {}
        reader = DummyReadStrategy(user_config)
        input_data = reader._get_missing_input_dataframes(input_data, config_type)
        actual = input_data[test_value]
        pd.testing.assert_frame_equal(actual, expected)

    def test_get_missing_input_dataframes_excpetion(self, user_config):
        input_data = {}
        reader = DummyReadStrategy(user_config)
        with raises(ValueError):
            reader._get_missing_input_dataframes(input_data, config_type="not_valid")
