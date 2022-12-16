from tempfile import NamedTemporaryFile
from unittest.mock import MagicMock

import pandas as pd
import pytest
import yaml

from otoole.exceptions import OtooleExcelNameLengthError, OtooleExcelNameMismatchError
from otoole.read_strategies import ReadExcel
from otoole.utils import (
    UniqueKeyLoader,
    create_name_mappings,
    extract_config,
    read_packaged_file,
)
from otoole.write_strategies import WriteExcel


@pytest.fixture()
def user_config_long_param_name():
    config = {}
    config["REGION"] = {"dtype": "str", "type": "set"}
    config["ParameterNameLongerThanThirtyOneChars"] = {
        "indices": ["REGION"],
        "type": "param",
        "dtype": "float",
        "default": 0.05,
    }
    return config


@pytest.fixture()
def user_config_long_short_name():
    config = {}
    config["REGION"] = {"dtype": "str", "type": "set"}
    config["ParameterNameLongerThanThirtyOneChars"] = {
        "short_name": "ShortNameAlsoLongerThanThirtyOneChars",
        "indices": ["REGION"],
        "type": "param",
        "dtype": "float",
        "default": 0.05,
    }
    return config


class TestDataPackageSchema:
    @pytest.mark.xfail
    def test_read_datapackage_schema_into_config(self):

        schema = read_packaged_file("datapackage.json", "otoole.preprocess")
        mock = MagicMock()
        mock.__getitem__.return_value = 0

        actual = extract_config(schema, mock)

        expected = read_packaged_file("config.yaml", "otoole.preprocess")
        assert actual == expected


class TestCreateNameMappings:
    def test_create_name_mappings(self, user_config):
        expected = {
            "TotalAnnualMaxCapacityInvestment": "TotalAnnualMaxCapacityInvestmen",
            "TotalAnnualMinCapacityInvestment": "TotalAnnualMinCapacityInvestmen",
            "TotalTechnologyAnnualActivityLowerLimit": "TotalTechnologyAnnualActivityLo",
            "TotalTechnologyAnnualActivityUpperLimit": "TotalTechnologyAnnualActivityUp",
            "TotalTechnologyModelPeriodActivityLowerLimit": "TotalTechnologyModelPeriodActLo",
            "TotalTechnologyModelPeriodActivityUpperLimit": "TotalTechnologyModelPeriodActUp",
        }
        actual = create_name_mappings(user_config)
        assert actual == expected

    def test_create_name_mappings_reversed(self, user_config):
        expected = {
            "TotalAnnualMaxCapacityInvestmen": "TotalAnnualMaxCapacityInvestment",
            "TotalAnnualMinCapacityInvestmen": "TotalAnnualMinCapacityInvestment",
            "TotalTechnologyAnnualActivityLo": "TotalTechnologyAnnualActivityLowerLimit",
            "TotalTechnologyAnnualActivityUp": "TotalTechnologyAnnualActivityUpperLimit",
            "TotalTechnologyModelPeriodActLo": "TotalTechnologyModelPeriodActivityLowerLimit",
            "TotalTechnologyModelPeriodActUp": "TotalTechnologyModelPeriodActivityUpperLimit",
        }
        actual = create_name_mappings(user_config, map_full_to_short=False)
        assert actual == expected


def test_excel_name_mismatch_error(user_config):
    read_excel = ReadExcel(user_config=user_config)
    sheet_names = ["AccumulatedAnnualDemand", "MismatchSheet"]
    with pytest.raises(OtooleExcelNameMismatchError):
        read_excel._check_input_sheet_names(sheet_names=sheet_names)


user_config_name_errors = ["user_config_long_param_name", "user_config_long_short_name"]


@pytest.mark.parametrize(
    "user_config_simple",
    user_config_name_errors,
    ids=["full_name_error", "short_name_error"],
)
def test_excel_name_length_error(user_config_simple, request):
    user_config = request.getfixturevalue(user_config_simple)
    write_excel = WriteExcel(user_config=user_config)
    temp_excel = NamedTemporaryFile(suffix=".xlsx")
    handle = pd.ExcelWriter(temp_excel.name)

    with pytest.raises(OtooleExcelNameLengthError):
        write_excel._write_parameter(
            df=pd.DataFrame(),
            parameter_name="ParameterNameLongerThanThirtyOneChars",
            handle=pd.ExcelWriter(handle),
            default=0,
        )


class TestYamlUniqueKeyReader:
    @pytest.fixture()
    def valid_yaml(self):
        data = """
            Key1:
              data1: valid data
              data2: 123
            Key2:
              data1: valid data
              data2: 123
            """
        return data

    @pytest.fixture()
    def invalid_yaml(self):
        data = """
            Key1:
              data1: valid data
              data2: 123
            Key1:
              data1: valid data
              data2: 123
            """
        return data

    def test_valid_yaml(self, valid_yaml):
        actual = yaml.load(valid_yaml, Loader=UniqueKeyLoader)
        expected = {
            "Key1": {"data1": "valid data", "data2": 123},
            "Key2": {"data1": "valid data", "data2": 123},
        }
        assert actual == expected

    def test_invalid_yaml(self, invalid_yaml):
        with pytest.raises(ValueError):
            yaml.load(invalid_yaml, Loader=UniqueKeyLoader)
