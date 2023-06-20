"""This module tests the public API of the otoole package

"""
import os
from tempfile import NamedTemporaryFile, TemporaryDirectory

from pytest import raises

from otoole import convert, convert_results


class TestConvert:
    """Test the convert function"""

    def test_convert_excel_to_datafile(self):
        """Test converting from Excel to datafile"""

        user_config = os.path.join("tests", "fixtures", "config.yaml")
        tmpfile = NamedTemporaryFile()
        from_path = os.path.join("tests", "fixtures", "combined_inputs.xlsx")

        convert(user_config, "excel", "datafile", from_path, tmpfile.name)

        tmpfile.seek(0)
        actual = tmpfile.readlines()
        tmpfile.close()

        assert actual[-1] == b"end;\n"
        assert actual[0] == b"# Model file written by *otoole*\n"
        assert actual[2] == b"09_ROK d_bld_2_coal_products 2017 20.8921\n"
        assert actual[8996] == b"param default 1 : DepreciationMethod :=\n"

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
            config, from_format, to_format, from_path, to_path, input_csvs=input_csvs
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
            input_datafile=input_datafile,
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
                input_csvs="not_a_path",
            )
