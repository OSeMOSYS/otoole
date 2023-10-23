"""This module tests the public API of the otoole package

"""
import os
from tempfile import NamedTemporaryFile, TemporaryDirectory

import pandas as pd
from pytest import raises

from otoole import convert, convert_results, read, read_results, write
from otoole.exceptions import OtooleError


class TestRead:
    """Tests the public api for reading data"""

    def test_read_datafile(self):
        """Test reading data from a file"""
        data, defaults = read(
            os.path.join("tests", "fixtures", "config.yaml"),
            "datafile",
            os.path.join("tests", "fixtures", "simplicity.txt"),
        )

        assert isinstance(data, dict)
        assert isinstance(defaults, dict)

    def test_read_excel(self):
        """Test reading data from an Excel file"""
        data, defaults = read(
            os.path.join("tests", "fixtures", "config.yaml"),
            "excel",
            os.path.join("tests", "fixtures", "combined_inputs.xlsx"),
        )

        assert isinstance(data, dict)
        assert isinstance(defaults, dict)

    def test_read_csv(self):
        """Test reading data from a CSV file"""
        data, defaults = read(
            os.path.join("tests", "fixtures", "super_simple", "super_simple.yaml"),
            "csv",
            os.path.join("tests", "fixtures", "super_simple", "csv"),
        )

        assert isinstance(data, dict)
        assert "REGION" in data
        pd.testing.assert_frame_equal(data["REGION"], pd.DataFrame({"VALUE": ["BB"]}))
        assert "TECHNOLOGY" in data
        assert "MODE_OF_OPERATION" in data
        assert "YEAR" in data
        assert isinstance(defaults, dict)


class TestWrite:
    """Tests the public api for writing data"""

    def test_write_datafile(self):
        """Test writing data to a file"""
        data = {"REGION": pd.DataFrame({"VALUE": ["BB"]})}
        temp = NamedTemporaryFile(delete=False, mode="w")
        try:
            assert write(
                os.path.join("tests", "fixtures", "config.yaml"),
                "datafile",
                temp.name,
                data,
            )
        finally:
            temp.close()
            os.unlink(temp.name)

    def test_write_excel(self):
        """Test writing data to an Excel file"""
        data = {"REGION": pd.DataFrame({"VALUE": ["BB"]})}
        temp = NamedTemporaryFile(suffix=".xlsx", delete=False, mode="w")
        try:
            assert write(
                os.path.join("tests", "fixtures", "config.yaml"),
                "excel",
                temp.name,
                data,
            )
        finally:
            temp.close()
            os.unlink(temp.name)

    def test_write_csv(self):
        """Test writing data to a CSV file"""
        data = {"REGION": pd.DataFrame({"VALUE": ["BB"]})}
        temp = TemporaryDirectory()
        assert write(
            os.path.join("tests", "fixtures", "super_simple", "super_simple.yaml"),
            "csv",
            temp.name,
            data,
        )


class TestConvert:
    """Test the convert function"""

    def test_convert_excel_to_datafile(self):
        """Test converting from Excel to datafile"""
        user_config = os.path.join("tests", "fixtures", "config.yaml")
        from_path = os.path.join("tests", "fixtures", "combined_inputs.xlsx")
        tmpfile = NamedTemporaryFile(delete=False, mode="w+b")

        try:
            convert(user_config, "excel", "datafile", from_path, tmpfile.name)
            tmpfile.seek(0)
            actual = tmpfile.readlines()

            assert actual[-1] == b"end;\n"
            assert actual[0] == b"# Model file written by *otoole*\n"
            assert actual[2] == b"09_ROK d_bld_2_coal_products 2017 20.8921\n"
            assert actual[8996] == b"param default 1 : DepreciationMethod :=\n"
        finally:
            tmpfile.close()
            os.unlink(tmpfile.name)

    def test_convert_excel_to_csv(self):
        """Test converting from Excel to CSV"""

        tmpfile = TemporaryDirectory()
        user_config = os.path.join("tests", "fixtures", "config.yaml")
        from_path = os.path.join("tests", "fixtures", "combined_inputs.xlsx")

        convert(user_config, "excel", "csv", from_path, tmpfile.name)

        with open(os.path.join(tmpfile.name, "EMISSION.csv")) as csv_file:
            csv_file.seek(0)
            actual = csv_file.readlines()

        assert actual[-1] == "NOX\n"
        assert actual[0] == "VALUE\n"
        assert actual[1] == "CO2\n"


class TestReadResults:
    """Test the read_results function"""

    def test_read_results(self):
        config = os.path.join("tests", "fixtures", "super_simple", "super_simple.yaml")

        input_path = os.path.join("tests", "fixtures", "super_simple", "csv")
        input_format = "csv"
        from_format = "cbc"
        from_path = os.path.join(
            "tests", "fixtures", "super_simple", "super_simple_gnu.sol"
        )

        actual, _ = read_results(
            config, from_format, from_path, input_format, input_path
        )

        expected_data = [["BB", "gas_import", 2016, 2.342422]]
        expected_columns = ["REGION", "TECHNOLOGY", "YEAR", "VALUE"]
        index = ["REGION", "TECHNOLOGY", "YEAR"]
        expected_data_frame = pd.DataFrame(
            expected_data, columns=expected_columns
        ).set_index(index)

        pd.testing.assert_frame_equal(
            actual["AccumulatedNewCapacity"], expected_data_frame
        )


class TestConvertResults:
    """Test the convert_results function"""

    def test_convert_results_cbc_csv(self):
        """Test converting CBC solution file to folder of CSVs"""
        config = os.path.join("tests", "fixtures", "super_simple", "super_simple.yaml")
        from_format = "cbc"
        to_format = "csv"
        from_path = os.path.join(
            "tests", "fixtures", "super_simple", "super_simple_gnu.sol"
        )
        tmpfile = TemporaryDirectory()
        to_path = tmpfile.name
        input_csvs = os.path.join("tests", "fixtures", "super_simple", "csv")

        result = convert_results(
            config, from_format, to_format, from_path, to_path, "csv", input_csvs
        )
        assert result is True

        with open(os.path.join(tmpfile.name, "NewCapacity.csv")) as csv_file:
            csv_file.seek(0)
            actual = csv_file.readlines()

        assert actual[0] == "REGION,TECHNOLOGY,YEAR,VALUE\n"
        assert actual[-1] == "BB,gas_import,2016,2.342422\n"

    def test_convert_results_cbc_csv_datafile(self):
        """Test converting CBC solution file to folder of CSVs"""
        config = os.path.join("tests", "fixtures", "super_simple", "super_simple.yaml")
        from_format = "cbc"
        to_format = "csv"
        from_path = os.path.join(
            "tests", "fixtures", "super_simple", "super_simple_gnu.sol"
        )
        tmpfile = TemporaryDirectory()
        to_path = tmpfile.name
        input_datafile = os.path.join(
            "tests", "fixtures", "super_simple", "super_simple.txt"
        )

        result = convert_results(
            config,
            from_format,
            to_format,
            from_path,
            to_path,
            "datafile",
            input_datafile,
        )
        assert result is True

        with open(os.path.join(tmpfile.name, "NewCapacity.csv")) as csv_file:
            csv_file.seek(0)
            actual = csv_file.readlines()

        assert actual[0] == "REGION,TECHNOLOGY,YEAR,VALUE\n"
        assert actual[-1] == "BB,gas_import,2016,2.342422\n"

    def test_convert_results_cbc_csv_raises(self):
        """Test converting CBC solution file to folder of CSVs"""
        config = os.path.join("tests", "fixtures", "super_simple", "super_simple.yaml")
        from_format = "cbc"
        to_format = "csv"
        from_path = os.path.join(
            "tests", "fixtures", "super_simple", "super_simple_gnu.sol"
        )
        tmpfile = TemporaryDirectory()
        to_path = tmpfile.name

        with raises(FileNotFoundError):
            convert_results(
                config,
                from_format,
                to_format,
                from_path,
                to_path,
                "csv",
                "not_a_path",
            )


class TestGetReadResultsStrategy:
    def test_read_results_glpk_raises(self):
        """Checks for .glp model file"""
        config = os.path.join("tests", "fixtures", "super_simple", "super_simple.yaml")
        input_path = ""
        input_format = "csv"
        from_format = "glpk"
        from_path = ""

        with raises(OtooleError):
            read_results(config, from_format, from_path, input_format, input_path)
