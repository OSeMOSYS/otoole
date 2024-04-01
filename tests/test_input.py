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
            ["SIMPLICITY", "HYD1", 2015, 3.45],
            ["SIMPLICITY", "HYD1", 2016, 4.56],
        ],
        columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"],
    ).set_index(["REGION", "TECHNOLOGY", "YEAR"])
    return df


@fixture
def new_capacity():
    df = pd.DataFrame(
        data=[
            ["SIMPLICITY", "NGCC", 2016, 1.23],
            ["SIMPLICITY", "HYD1", 2014, 2.34],
            ["SIMPLICITY", "HYD1", 2015, 3.45],
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
def simple_input_data(region, year, technology, capital_cost, discount_rate):
    return {
        "REGION": region,
        "TECHNOLOGY": technology,
        "YEAR": year,
        "CapitalCost": capital_cost,
        "DiscountRate": discount_rate,
    }


@fixture
def simple_available_results(new_capacity):
    return {"NewCapacity": new_capacity}


@fixture
def simple_user_config():
    return {
        "CapitalCost": {
            "indices": ["REGION", "TECHNOLOGY", "YEAR"],
            "type": "param",
            "dtype": "float",
            "default": -1,
            "short_name": "CAPEX",
        },
        "DiscountRate": {
            "indices": ["REGION"],
            "type": "param",
            "dtype": "float",
            "default": 0.25,
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
        "NewCapacity": {
            "indices": ["REGION", "TECHNOLOGY", "YEAR"],
            "type": "result",
            "dtype": "float",
            "default": 20,
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

    # capital costs fixtures

    input_data_multi_index_full = pd.DataFrame(
        [
            ["SIMPLICITY", "HYD1", 2014, 2000.0],
            ["SIMPLICITY", "HYD1", 2015, 1500.0],
            ["SIMPLICITY", "HYD1", 2016, 1000.0],
            ["SIMPLICITY", "NGCC", 2014, 1000.0],
            ["SIMPLICITY", "NGCC", 2015, 900.0],
            ["SIMPLICITY", "NGCC", 2016, 800.0],
        ],
        columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"],
    ).set_index(["REGION", "TECHNOLOGY", "YEAR"])

    output_data_multi_index_full = input_data_multi_index_full.copy()

    input_data_multi_index_partial = pd.DataFrame(
        [
            ["SIMPLICITY", "NGCC", 2014, 1000.0],
            ["SIMPLICITY", "NGCC", 2015, 900.0],
            ["SIMPLICITY", "HYD1", 2015, 1500.0],
            ["SIMPLICITY", "HYD1", 2016, 1000.0],
        ],
        columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"],
    ).set_index(["REGION", "TECHNOLOGY", "YEAR"])

    output_data_multi_index_partial = pd.DataFrame(
        [
            ["SIMPLICITY", "HYD1", 2014, -1.0],
            ["SIMPLICITY", "HYD1", 2015, 1500.0],
            ["SIMPLICITY", "HYD1", 2016, 1000.0],
            ["SIMPLICITY", "NGCC", 2014, 1000.0],
            ["SIMPLICITY", "NGCC", 2015, 900.0],
            ["SIMPLICITY", "NGCC", 2016, -1.0],
        ],
        columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"],
    ).set_index(["REGION", "TECHNOLOGY", "YEAR"])

    # discount rate fixtures

    input_data_multi_index_empty = pd.DataFrame(
        [],
        columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"],
    ).set_index(["REGION", "TECHNOLOGY", "YEAR"])

    output_data_multi_index_empty = pd.DataFrame(
        [
            ["SIMPLICITY", "HYD1", 2014, -1.0],
            ["SIMPLICITY", "HYD1", 2015, -1.0],
            ["SIMPLICITY", "HYD1", 2016, -1.0],
            ["SIMPLICITY", "NGCC", 2014, -1.0],
            ["SIMPLICITY", "NGCC", 2015, -1.0],
            ["SIMPLICITY", "NGCC", 2016, -1.0],
        ],
        columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"],
    ).set_index(["REGION", "TECHNOLOGY", "YEAR"])

    input_data_single_index_full = pd.DataFrame(
        [["SIMPLICITY", 0.05]], columns=["REGION", "VALUE"]
    ).set_index(["REGION"])

    output_data_single_index_full = input_data_single_index_full.copy()

    input_data_single_index_empty = pd.DataFrame(
        [], columns=["REGION", "VALUE"]
    ).set_index(["REGION"])

    output_data_single_index_empty = pd.DataFrame(
        [["SIMPLICITY", 0.25]], columns=["REGION", "VALUE"]
    ).set_index(["REGION"])

    # test expansion of dataframe

    test_data = [
        ("CapitalCost", input_data_multi_index_full, output_data_multi_index_full),
        (
            "CapitalCost",
            input_data_multi_index_partial,
            output_data_multi_index_partial,
        ),
        ("CapitalCost", input_data_multi_index_empty, output_data_multi_index_empty),
        ("DiscountRate", input_data_single_index_full, output_data_single_index_full),
        (
            "DiscountRate",
            input_data_single_index_empty,
            output_data_single_index_empty,
        ),
    ]
    test_data_ids = [
        "multi_index_full",
        "multi_index_partial",
        "multi_index_empty",
        "single_index_full",
        "single_index_empty",
    ]

    @mark.parametrize(
        "name,input,expected",
        test_data,
        ids=test_data_ids,
    )
    def test_expand_parameters_defaults(
        self,
        simple_user_config,
        simple_default_values,
        simple_input_data,
        name,
        input,
        expected,
    ):
        input_data = simple_input_data.copy()
        input_data[name] = input

        read_strategy = DummyReadStrategy(user_config=simple_user_config)
        actual = read_strategy._expand_dataframe(
            name, input_data, simple_default_values
        )
        assert_frame_equal(actual, expected)

    def test_expand_results_key_error(
        self, simple_user_config, simple_input_data, simple_default_values
    ):
        read_strategy = DummyReadStrategy(
            user_config=simple_user_config, write_defaults=True
        )

        with raises(KeyError, match="SpecifiedAnnualDemand"):
            read_strategy._expand_dataframe(
                "SpecifiedAnnualDemand", simple_input_data, simple_default_values
            )

    # test get default dataframe

    test_data_defaults = [
        ("CapitalCost", output_data_multi_index_empty),
        ("DiscountRate", output_data_single_index_empty),
    ]
    test_data_defaults_ids = [
        "multi_index",
        "single_index",
    ]

    @mark.parametrize(
        "name,expected",
        test_data_defaults,
        ids=test_data_defaults_ids,
    )
    def test_get_default_dataframe(
        self,
        simple_user_config,
        simple_default_values,
        simple_input_data,
        name,
        expected,
    ):

        read_strategy = DummyReadStrategy(user_config=simple_user_config)
        actual = read_strategy._get_default_dataframe(
            name, simple_input_data, simple_default_values
        )
        assert_frame_equal(actual, expected)

    # test expand all input data

    def test_write_default_params(
        self, simple_user_config, simple_input_data, simple_default_values
    ):
        read_strategy = DummyReadStrategy(user_config=simple_user_config)
        actual_expanded = read_strategy.write_default_params(
            simple_input_data, simple_default_values
        )
        actual = actual_expanded["CapitalCost"]

        expected = pd.DataFrame(
            data=[
                ["SIMPLICITY", "HYD1", 2014, -1],
                ["SIMPLICITY", "HYD1", 2015, 3.45],
                ["SIMPLICITY", "HYD1", 2016, 4.56],
                ["SIMPLICITY", "NGCC", 2014, 1.23],
                ["SIMPLICITY", "NGCC", 2015, 2.34],
                ["SIMPLICITY", "NGCC", 2016, -1],
            ],
            columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"],
        ).set_index(["REGION", "TECHNOLOGY", "YEAR"])

        assert_frame_equal(actual, expected)

    def test_write_default_results(
        self,
        simple_user_config,
        simple_input_data,
        simple_available_results,
        simple_default_values,
    ):

        read_strategy = DummyReadStrategy(user_config=simple_user_config)
        actual_expanded = read_strategy.write_default_results(
            simple_available_results, simple_input_data, simple_default_values
        )

        actual = actual_expanded["NewCapacity"]

        expected = pd.DataFrame(
            data=[
                ["SIMPLICITY", "HYD1", 2014, 2.34],
                ["SIMPLICITY", "HYD1", 2015, 3.45],
                ["SIMPLICITY", "HYD1", 2016, 20],
                ["SIMPLICITY", "NGCC", 2014, 20],
                ["SIMPLICITY", "NGCC", 2015, 20],
                ["SIMPLICITY", "NGCC", 2016, 1.23],
            ],
            columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"],
        ).set_index(["REGION", "TECHNOLOGY", "YEAR"])

        assert_frame_equal(actual, expected)


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
        [["CapitalCost", "DiscountRate", "REGION", "TECHNOLOGY", "YEAR"], False],
        [["CAPEX", "DiscountRate", "REGION", "TECHNOLOGY", "YEAR"], True],
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
            ["SIMPLICITY", "NGCC", "2014", "1.23"],
            ["SIMPLICITY", "NGCC", 2015.0, 2.34],
            ["SIMPLICITY", "NGCC", "2016.0", 3.45],
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

    year_incorrect_header = pd.DataFrame(
        data=["2014", 2015.0, "2016.0"], columns=["YEAR"]
    )

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
