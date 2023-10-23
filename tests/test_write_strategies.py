import io
import os
from tempfile import NamedTemporaryFile

import pandas as pd

from otoole.write_strategies import WriteDatafile, WriteExcel


class TestWriteExcel:
    def test_form_empty_parameter_with_defaults(self, user_config):

        convert = WriteExcel(user_config)  # typing: WriteExcel

        data = []

        df = pd.DataFrame(data=data, columns=["REGION", "FUEL", "VALUE"]).set_index(
            ["REGION", "FUEL"]
        )
        actual = convert._form_parameter(df, "test_parameter", 0)
        expected = pd.DataFrame(
            data=data, columns=["REGION", "FUEL", "VALUE"]
        ).set_index(["REGION", "FUEL"])
        pd.testing.assert_frame_equal(actual, expected)

    def test_form_empty_two_index_param_with_defaults(self, user_config):

        convert = WriteExcel(user_config)  # typing: WriteExcel

        df = pd.DataFrame(data=[], columns=["REGION", "VALUE"]).set_index("REGION")
        actual = convert._form_parameter(df, "test_parameter", 0)
        expected = pd.DataFrame(data=[], columns=["REGION", "VALUE"]).set_index(
            "REGION"
        )
        pd.testing.assert_frame_equal(actual, expected)

    def test_form_two_index_param(self, user_config):

        convert = WriteExcel(user_config)  # typing: WriteExcel

        df = pd.DataFrame(
            data=[["SIMPLICITY", 0.10], ["UTOPIA", 0.20]], columns=["REGION", "VALUE"]
        ).set_index(["REGION"])
        actual = convert._form_parameter(df, "test_parameter", 0)
        index = pd.Index(data=["SIMPLICITY", "UTOPIA"], name="REGION")
        expected = pd.DataFrame(data=[[0.10], [0.20]], columns=["VALUE"], index=index)
        # print(actual, expected)
        pd.testing.assert_frame_equal(actual, expected)

    def test_form_one_columns(self, user_config):

        convert = WriteExcel(user_config)  # typing: WriteExcel

        data = ["A", "B", "C"]

        df = pd.DataFrame(data=data, columns=["FUEL"])
        actual = convert._form_parameter(df, "test_set", 0)
        expected = pd.DataFrame(data=["A", "B", "C"], columns=["FUEL"])
        # print(actual, expected)
        pd.testing.assert_frame_equal(actual, expected)

    def test_form_template_paramter(self, user_config):
        input_data = {
            "YEAR": pd.DataFrame(data=[[2015], [2016], [2017]], columns=["VALUE"])
        }
        convert = WriteExcel(user_config)
        actual = convert._form_parameter_template(
            "AccumulatedAnnualDemand", input_data=input_data
        )
        expected = pd.DataFrame(columns=["REGION", "FUEL", 2015, 2016, 2017])

        pd.testing.assert_frame_equal(actual, expected)

    def test_form_three_columns(self, user_config):

        convert = WriteExcel(user_config)  # typing: WriteExcel

        data = [["SIMPLICITY", "COAL", 2015, 41], ["SIMPLICITY", "COAL", 2016, 42]]

        df = pd.DataFrame(
            data=data, columns=["REGION", "FUEL", "YEAR", "VALUE"]
        ).set_index(["REGION", "FUEL", "YEAR"])
        actual = convert._form_parameter(df, "test_parameter", 0)

        expected_data = [[41, 42]]
        expected = pd.DataFrame(
            data=expected_data,
            columns=pd.Index([2015, 2016], dtype="int64", name="YEAR"),
            index=pd.MultiIndex.from_tuples(
                [("SIMPLICITY", "COAL")], names=["REGION", "FUEL"]
            ),
        )

        pd.testing.assert_frame_equal(actual, expected)

    def test_form_no_pivot(self, user_config):

        convert = WriteExcel(user_config)  # typing: WriteExcel

        # Technology to/from storage data
        data = [
            ["SIMPLICITY", "HYD2", "DAM", 1, 0],
            ["SIMPLICITY", "HYD2", "DAM", 2, 1],
        ]

        df = pd.DataFrame(
            data=data,
            columns=["REGION", "TECHNOLOGY", "STORAGE", "MODE_OF_OPERATION", "VALUE"],
        ).set_index(["REGION", "TECHNOLOGY", "STORAGE", "MODE_OF_OPERATION"])

        actual = convert._form_parameter(df, "test_parameter", 0)
        expected = df.copy()

        pd.testing.assert_frame_equal(actual, expected)

    def test_write_out_empty_dataframe(self, user_config):

        temp_excel = NamedTemporaryFile(suffix=".xlsx", delete=False, mode="w")
        try:
            handle = pd.ExcelWriter(temp_excel.name)
            convert = WriteExcel(user_config)

            df = pd.DataFrame(
                data=None, columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"]
            ).set_index(["REGION", "TECHNOLOGY", "YEAR"])

            convert._write_parameter(df, "AvailabilityFactor", handle, default=0)
        finally:
            handle.close()
            temp_excel.close()
            os.unlink(temp_excel.name)


class TestWriteDatafile:
    def test_write_empty_parameter_with_defaults(self, user_config):

        convert = WriteDatafile(user_config)  # typing: WriteDatafile

        data = []

        df = pd.DataFrame(data=data, columns=["REGION", "FUEL", "VALUE"])

        stream = io.StringIO()
        convert._write_parameter(df, "test_parameter", stream, 0)

        stream.seek(0)
        expected = ["param default 0 : test_parameter :=\n", ";\n"]
        actual = stream.readlines()

        for actual_line, expected_line in zip(actual, expected):
            assert actual_line == expected_line

    def test_write_parameter_as_tabbing_format(self, user_config):

        data = [["SIMPLICITY", "BIOMASS", 0.95969], ["SIMPLICITY", "ETH1", 4.69969]]

        df = pd.DataFrame(data=data, columns=["REGION", "FUEL", "VALUE"]).set_index(
            ["REGION", "FUEL"]
        )

        stream = io.StringIO()
        convert = WriteDatafile(user_config)
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

    def test_write_parameter_skip_defaults(self, user_config):

        data = [
            ["SIMPLICITY", "BIOMASS", 0.95969],
            ["SIMPLICITY", "ETH1", 4.69969],
            ["SIMPLICITY", "ETH2", -1],
            ["SIMPLICITY", "ETH3", -1],
        ]

        df = pd.DataFrame(data=data, columns=["REGION", "FUEL", "VALUE"]).set_index(
            ["REGION", "FUEL"]
        )

        stream = io.StringIO()
        convert = WriteDatafile(user_config)
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

    def test_write_set(self, user_config):

        data = [["BIOMASS"], ["ETH1"]]

        df = pd.DataFrame(data=data, columns=["VALUE"])

        stream = io.StringIO()
        convert = WriteDatafile(user_config)
        convert._write_set(df, "TECHNOLOGY", stream)

        stream.seek(0)
        expected = ["set TECHNOLOGY :=\n", "BIOMASS\n", "ETH1\n", ";\n"]
        actual = stream.readlines()

        for actual_line, expected_line in zip(actual, expected):
            assert actual_line == expected_line
