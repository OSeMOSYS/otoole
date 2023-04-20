from typing import Any, Dict, TextIO, Tuple, Union

import pandas as pd
from pandas.testing import assert_frame_equal
from pytest import fixture, mark, raises

from otoole.exceptions import OtooleIndexError, OtooleNameMismatchError
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


@fixture
def capital_cost():
    df = pd.DataFrame(
        data=[
            ["SIMPLICITY", "NGCC", 2014, 1.23],
            ["SIMPLICITY", "NGCC", 2015, 2.34],
            ["SIMPLICITY", "NGCC", 2016, 3.45],
            ["SIMPLICITY", "HYD1", 2014, 3.45],
            ["SIMPLICITY", "HYD1", 2015, 2.34],
            ["SIMPLICITY", "HYD1", 2016, 1.23],
        ],
        columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"],
    ).set_index(["REGION", "TECHNOLOGY", "YEAR"])
    return df


@fixture()
def simple_default_values():
    default_values = {}
    default_values["CapitalCost"] = -1.0
    default_values["DiscountRate"] = 0.25
    default_values["NewCapacity"] = 20
    return default_values


@fixture
def simple_input_data(region, year, technology, capital_cost):
    return {
        "REGION": region,
        "TECHNOLOGY": technology,
        "YEAR": year,
        "CapitalCost": capital_cost,
    }


@fixture
def simple_user_config():
    return {
        "CapitalCost": {
            "indices": ["REGION", "TECHNOLOGY", "YEAR"],
            "type": "param",
            "dtype": "float",
            "default": 0,
            "short_name": "CAPEX",
        },
        "REGION": {
            "dtype": "str",
            "type": "set",
        },
        "TECHNOLOGY": {
            "dtype": "str",
            "type": "set",
        },
        "YEAR": {
            "dtype": "int",
            "type": "set",
        },
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
            "CapitalCost",
            pd.DataFrame(columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"]).set_index(
                ["REGION", "TECHNOLOGY", "YEAR"]
            ),
        ),
        ("set", "REGION", pd.DataFrame(columns=["VALUE"])),
    )
    compare_read_to_expected_data = [
        [["CapitalCost", "REGION", "TECHNOLOGY", "YEAR"], False],
        [["CAPEX", "REGION", "TECHNOLOGY", "YEAR"], True],
    ]
    compare_read_to_expected_data_exception = [
        ["CapitalCost", "REGION", "TECHNOLOGY"],
        ["CapitalCost", "REGION", "TECHNOLOGY", "YEAR", "Extra"],
    ]

    capex_correct = pd.DataFrame(
        data=[
            ["SIMPLICITY", "NGCC", 2014, 1.23],
            ["SIMPLICITY", "NGCC", 2015, 2.34],
            ["SIMPLICITY", "NGCC", 2016, 3.45],
        ],
        columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"],
    ).set_index(["REGION", "TECHNOLOGY", "YEAR"])

    capex_incorrect_dtype = pd.DataFrame(
        data=[
            ["SIMPLICITY", "NGCC", "2014", 1.23],
            ["SIMPLICITY", "NGCC", "2015", 2.34],
            ["SIMPLICITY", "NGCC", "2016", 3.45],
        ],
        columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"],
    ).set_index(["REGION", "TECHNOLOGY", "YEAR"])

    capex_incorrect_header = pd.DataFrame(
        data=[
            ["SIMPLICITY", "NGCC", 2014, 1.23],
            ["SIMPLICITY", "NGCC", 2015, 2.34],
            ["SIMPLICITY", "NGCC", 2016, 3.45],
        ],
        columns=["REGION", "FUEL", "YEAR", "VALUE"],
    ).set_index(["REGION", "FUEL", "YEAR"])

    year_correct = pd.DataFrame(data=[2014, 2015, 2016], columns=["VALUE"])

    year_incorrect_dtype = pd.DataFrame(
        data=["2014", "2015", "2016"], columns=["VALUE"]
    )

    year_incorrect_header = pd.DataFrame(data=[2014, 2015, 2016], columns=["YEAR"])

    input_data_correct = (
        ({"CapitalCost": capex_correct}, capex_correct),
        ({"YEAR": year_correct}, year_correct),
    )

    input_data_incorrect_dtype = (
        ({"CapitalCost": capex_incorrect_dtype}, capex_correct),
        ({"YEAR": year_incorrect_dtype}, year_correct),
    )

    input_data_incorrect_header = (
        {"CapitalCost": capex_incorrect_header},
        {"YEAR": year_incorrect_header},
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

    @mark.parametrize(
        "input_data, expected",
        input_data_correct,
        ids=["param", "set"],
    )
    def test_check_index(self, user_config, input_data, expected):
        reader = DummyReadStrategy(user_config)
        actual = reader._check_index(input_data)
        for _, df in actual.items():
            pd.testing.assert_frame_equal(df, expected)

    @mark.parametrize(
        "input_data, expected",
        input_data_incorrect_dtype,
        ids=["param", "set"],
    )
    def test_check_index_dtype(self, user_config, input_data, expected):
        reader = DummyReadStrategy(user_config)
        actual = reader._check_index(input_data)
        for _, df in actual.items():
            pd.testing.assert_frame_equal(df, expected)

    @mark.parametrize(
        "input_data",
        input_data_incorrect_header,
        ids=["param", "set"],
    )
    def test_check_index_header(self, user_config, input_data):
        reader = DummyReadStrategy(user_config)
        with raises(OtooleIndexError):
            reader._check_index(input_data)

    def test_check_index_config(self):
        incorrect_user_config = {
            "CapitalCost": {
                "indices": ["REGION"],
                "type": "param",
                "dtype": "float",
                "default": 0,
            },
            "REGION": {
                "dtype": "str",
                "type": "set",
            },
        }
        data = pd.DataFrame(
            data=[
                ["SIMPLICITY", "NGCC", 2014, 1.23],
            ],
            columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"],
        ).set_index(["REGION", "TECHNOLOGY", "YEAR"])
        input_data = {"CapitalCost": data}
        reader = DummyReadStrategy(incorrect_user_config)
        with raises(OtooleIndexError):
            reader._check_index(input_data)

    @mark.parametrize(
        "input_data, expected",
        input_data_correct,
        ids=["param", "set"],
    )
    def test_check_dtypes(self, user_config, input_data, expected):
        reader = DummyReadStrategy(user_config)
        for param, df in input_data.items():
            actual = reader._check_index_dtypes(
                name=param, config=user_config[param], df=df
            )
            pd.testing.assert_frame_equal(actual, expected)

    def test_check_param_index_name_passes(self, user_config):
        capex = pd.DataFrame(
            data=[
                ["SIMPLICITY", "NGCC", 2014, 1.23],
                ["SIMPLICITY", "NGCC", 2015, 2.34],
                ["SIMPLICITY", "NGCC", 2016, 3.45],
            ],
            columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"],
        ).set_index(["REGION", "TECHNOLOGY", "YEAR"])

        reader = DummyReadStrategy(user_config)
        reader._check_param_index_names(
            name="CapitalCost", config=user_config["CapitalCost"], df=capex
        )

    def test_check_param_index_name_fails(self, user_config):
        capex = pd.DataFrame(
            data=[
                ["SIMPLICITY", "NGCC", 2014, 1.23],
                ["SIMPLICITY", "NGCC", 2015, 2.34],
                ["SIMPLICITY", "NGCC", 2016, 3.45],
            ],
            columns=["REGION", "FUEL", "YEAR", "VALUE"],
        ).set_index(["REGION", "FUEL", "YEAR"])

        reader = DummyReadStrategy(user_config)
        with raises(OtooleIndexError):
            reader._check_param_index_names(
                name="CapitalCost", config=user_config["CapitalCost"], df=capex
            )

    def test_check_set_index_name_passes(self, user_config):
        year = pd.DataFrame(data=[2014, 2015, 2016], columns=["VALUE"])
        reader = DummyReadStrategy(user_config)
        reader._check_set_index_names(name="YEAR", df=year)

    def test_check_set_index_name_fails(self, user_config):
        year = pd.DataFrame(data=[2014, 2015, 2016], columns=["YEAR"])
        reader = DummyReadStrategy(user_config)
        with raises(OtooleIndexError):
            reader._check_set_index_names(name="YEAR", df=year)

    @mark.parametrize(
        "expected, short_name",
        compare_read_to_expected_data,
        ids=["full_name", "short_name"],
    )
    def test_compare_read_to_expected(self, simple_user_config, expected, short_name):
        reader = DummyReadStrategy(simple_user_config)
        reader._compare_read_to_expected(names=expected, short_names=short_name)

    @mark.parametrize(
        "expected",
        compare_read_to_expected_data_exception,
        ids=["missing_value", "extra_value"],
    )
    def test_compare_read_to_expected_exception(self, simple_user_config, expected):
        reader = DummyReadStrategy(simple_user_config)
        with raises(OtooleNameMismatchError):
            reader._compare_read_to_expected(names=expected)
