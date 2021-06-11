import io
import pandas as pd

from otoole.write_strategies import WriteDatafile, WriteExcel


class TestWriteExcel:
    def test_form_empty_parameter_with_defaults(self):

        convert = WriteExcel()  # typing: WriteExcel

        data = []

        df = pd.DataFrame(data=data, columns=["REGION", "FUEL", "VALUE"]).set_index(
            ["REGION", "FUEL"]
        )
        actual = convert._form_parameter(df, "test_parameter", 0)
        expected = pd.DataFrame(
            data=data, columns=["REGION", "FUEL", "VALUE"]
        ).set_index(["REGION", "FUEL"])
        pd.testing.assert_frame_equal(actual, expected)

    def test_form_empty_two_index_param_with_defaults(self):

        convert = WriteExcel()  # typing: WriteExcel

        df = pd.DataFrame(data=[], columns=["REGION", "VALUE"]).set_index("REGION")
        actual = convert._form_parameter(df, "test_parameter", 0)
        expected = pd.DataFrame(data=[], columns=["REGION", "VALUE"]).set_index(
            "REGION"
        )
        pd.testing.assert_frame_equal(actual, expected)

    def test_form_two_index_param(self):

        convert = WriteExcel()  # typing: WriteExcel

        df = pd.DataFrame(
            data=[["SIMPLICITY", 0.10], ["UTOPIA", 0.20]], columns=["REGION", "VALUE"]
        ).set_index(["REGION"])
        actual = convert._form_parameter(df, "test_parameter", 0)
        index = pd.Index(data=["SIMPLICITY", "UTOPIA"], name="REGION")
        expected = pd.DataFrame(data=[[0.10], [0.20]], columns=["VALUE"], index=index)
        print(actual, expected)
        pd.testing.assert_frame_equal(actual, expected)

    def test_form_one_columns(self):

        convert = WriteExcel()  # typing: WriteExcel

        data = ["A", "B", "C"]

        df = pd.DataFrame(data=data, columns=["FUEL"])
        actual = convert._form_parameter(df, "test_set", 0)
        expected = pd.DataFrame(data=["A", "B", "C"], columns=["FUEL"])
        print(actual, expected)
        pd.testing.assert_frame_equal(actual, expected)

    def test_form_three_columns(self):

        convert = WriteExcel()  # typing: WriteExcel

        data = [["SIMPLICITY", "COAL", 2015, 41], ["SIMPLICITY", "COAL", 2016, 42]]

        df = pd.DataFrame(
            data=data, columns=["REGION", "FUEL", "YEAR", "VALUE"]
        ).set_index(["REGION", "FUEL", "YEAR"])
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


class TestWriteDatafile:
    def test_write_empty_parameter_with_defaults(self):

        convert = WriteDatafile()  # typing: WriteDatafile

        data = []

        df = pd.DataFrame(data=data, columns=["REGION", "FUEL", "VALUE"])

        stream = io.StringIO()
        convert._write_parameter(df, "test_parameter", stream, 0)

        stream.seek(0)
        expected = ["param default 0 : test_parameter :=\n", ";\n"]
        actual = stream.readlines()

        for actual_line, expected_line in zip(actual, expected):
            assert actual_line == expected_line

    def test_write_parameter_as_tabbing_format(self):

        data = [["SIMPLICITY", "BIOMASS", 0.95969], ["SIMPLICITY", "ETH1", 4.69969]]

        df = pd.DataFrame(data=data, columns=["REGION", "FUEL", "VALUE"]).set_index(
            ["REGION", "FUEL"]
        )

        stream = io.StringIO()
        convert = WriteDatafile()
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

    def test_write_parameter_skip_defaults(self):

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
        convert = WriteDatafile()
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

    def test_write_set(self):

        data = [["BIOMASS"], ["ETH1"]]

        df = pd.DataFrame(data=data, columns=["VALUE"])

        stream = io.StringIO()
        convert = WriteDatafile()
        convert._write_set(df, "TECHNOLOGY", stream)

        stream.seek(0)
        expected = ["set TECHNOLOGY :=\n", "BIOMASS\n", "ETH1\n", ";\n"]
        actual = stream.readlines()

        for actual_line, expected_line in zip(actual, expected):
            assert actual_line == expected_line
