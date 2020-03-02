import io
from unittest.mock import Mock

from pytest import fixture

import pandas as pd

from otoole.preprocess.excel_to_osemosys import read_config
from otoole.preprocess.narrow_to_datafile import DataPackageToCsv, DataPackageToExcel


class TestDataFrameWritingExcel:
    @fixture
    def setup(self, monkeypatch) -> DataPackageToExcel:

        dp = DataPackageToExcel
        monkeypatch.setattr(dp, "_get_package", Mock())  # type: ignore
        monkeypatch.setattr(dp, "_get_default_values", Mock())  # type: ignore

        return dp("", "")

    def test_form_empty_parameter_with_defaults(self, setup):

        convert = setup  # typing: DataPackageToExcel

        data = []

        df = pd.DataFrame(data=data, columns=["REGION", "FUEL", "VALUE"])
        actual = convert._form_parameter(df, "test_parameter", 0)
        expected = pd.DataFrame(data=data, columns=["REGION", "FUEL", "VALUE"])
        pd.testing.assert_frame_equal(actual, expected)

    def test_form_one_columns(self, setup):

        convert = setup  # typing: DataPackageToExcel

        data = ["A", "B", "C"]

        df = pd.DataFrame(data=data, columns=["FUEL"])
        actual = convert._form_parameter(df, "test_set", 0)
        expected = pd.DataFrame(data=["A", "B", "C"], columns=["FUEL"])
        pd.testing.assert_frame_equal(actual, expected)

    def test_form_three_columns(self, setup):

        convert = setup  # typing: DataPackageToExcel

        data = [["SIMPLICITY", "COAL", 2015, 41], ["SIMPLICITY", "COAL", 2016, 42]]

        df = pd.DataFrame(data=data, columns=["REGION", "FUEL", "YEAR", "VALUE"])
        actual = convert._form_parameter(df, "test_parameter", 0)

        expected_data = [[41, 42]]
        expected = pd.DataFrame(
            data=expected_data,
            columns=pd.Int64Index([2015, 2016], dtype="int64", name="YEAR"),
            index=pd.MultiIndex.from_tuples(
                [("SIMPLICITY", "COAL")], names=["REGION", "FUEL"]
            ),
        )

        pd.testing.assert_frame_equal(actual, expected)


class TestDataFrameWritingCSV:
    @fixture
    def setup(self, monkeypatch) -> DataPackageToCsv:

        dp = DataPackageToCsv
        monkeypatch.setattr(dp, "_get_package", Mock())  # type: ignore
        monkeypatch.setattr(dp, "_get_default_values", Mock())  # type: ignore
        return dp("", "")

    def test_write_empty_parameter_with_defaults(self, setup):

        convert = setup  # typing: DataPackageToCsv

        data = []

        df = pd.DataFrame(data=data, columns=["REGION", "FUEL", "VALUE"])

        stream = io.StringIO()
        convert._write_parameter(df, "test_parameter", stream, 0)

        stream.seek(0)
        expected = ["param default 0 : test_parameter :=\n", ";\n"]
        actual = stream.readlines()

        for actual_line, expected_line in zip(actual, expected):
            assert actual_line == expected_line

    def test_write_parameter_as_tabbing_format(self, setup):

        data = [["SIMPLICITY", "BIOMASS", 0.95969], ["SIMPLICITY", "ETH1", 4.69969]]

        df = pd.DataFrame(data=data, columns=["REGION", "FUEL", "VALUE"])

        stream = io.StringIO()
        convert = setup
        convert._write_parameter(df, "test_parameter", stream, 0)

        stream.seek(0)
        expected = [
            "param default 0 : test_parameter :=\n",
            "SIMPLICITY BIOMASS 0.95969\n",
            "SIMPLICITY ETH1 4.69969\n",
            ";\n",
        ]
        actual = stream.readlines()

        for actual_line, expected_line in zip(actual, expected):
            assert actual_line == expected_line

    def test_write_parameter_skip_defaults(self, setup):

        data = [
            ["SIMPLICITY", "BIOMASS", 0.95969],
            ["SIMPLICITY", "ETH1", 4.69969],
            ["SIMPLICITY", "ETH2", -1],
            ["SIMPLICITY", "ETH3", -1],
        ]

        df = pd.DataFrame(data=data, columns=["REGION", "FUEL", "VALUE"])

        stream = io.StringIO()
        convert = setup
        convert._write_parameter(df, "test_parameter", stream, -1)

        stream.seek(0)
        expected = [
            "param default -1 : test_parameter :=\n",
            "SIMPLICITY BIOMASS 0.95969\n",
            "SIMPLICITY ETH1 4.69969\n",
            ";\n",
        ]
        actual = stream.readlines()

        for actual_line, expected_line in zip(actual, expected):
            assert actual_line == expected_line

    def test_write_set(self, setup):

        data = [["BIOMASS"], ["ETH1"]]

        df = pd.DataFrame(data=data, columns=["VALUE"])

        stream = io.StringIO()
        convert = setup
        convert._write_set(df, "TECHNOLOGY", stream)

        stream.seek(0)
        expected = ["set TECHNOLOGY :=\n", "BIOMASS\n", "ETH1\n", ";\n"]
        actual = stream.readlines()

        for actual_line, expected_line in zip(actual, expected):
            assert actual_line == expected_line


class TestConfig:
    def test_read_config(self):

        actual = read_config()
        expected = {
            "default": 0,
            "dtype": "float",
            "indices": ["REGION", "FUEL", "YEAR"],
            "type": "param",
        }
        assert actual["AccumulatedAnnualDemand"] == expected
