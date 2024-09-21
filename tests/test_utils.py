import os
from tempfile import NamedTemporaryFile

import pandas as pd
import pytest
import yaml

from otoole.exceptions import OtooleDeprecationError, OtooleExcelNameLengthError
from otoole.utils import (
    UniqueKeyLoader,
    create_name_mappings,
    read_deprecated_datapackage,
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


user_config_name_errors = ["user_config_long_param_name", "user_config_long_short_name"]


@pytest.mark.parametrize(
    "user_config_simple",
    user_config_name_errors,
    ids=["full_name_error", "short_name_error"],
)
def test_excel_name_length_error(user_config_simple, request):
    user_config = request.getfixturevalue(user_config_simple)
    write_excel = WriteExcel(user_config=user_config)
    temp_excel = NamedTemporaryFile(suffix=".xlsx", delete=False, mode="r")
    try:
        with pytest.raises(OtooleExcelNameLengthError):
            write_excel._write_parameter(
                df=pd.DataFrame(),
                parameter_name="ParameterNameLongerThanThirtyOneChars",
                handle=pd.ExcelWriter(temp_excel.name),
                default=0,
            )
    finally:
        temp_excel.close()
        os.unlink(temp_excel.name)


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

    invalid_yaml_1 = """
            Key1:
              data1: valid data
              data2: 123
            Key1:
              data1: valid data
              data2: 123
            """

    invalid_yaml_2 = """
            Key1:
              data1: valid data
              data2: 123
            KEY1:
              data1: valid data
              data2: 123
            """

    def test_valid_yaml(self, valid_yaml):
        actual = yaml.load(valid_yaml, Loader=UniqueKeyLoader)
        expected = {
            "Key1": {"data1": "valid data", "data2": 123},
            "Key2": {"data1": "valid data", "data2": 123},
        }
        assert actual == expected

    invalid_yamls = [invalid_yaml_1, invalid_yaml_2]
    invalid_yaml_ids = ["invalid_yaml_1", "invalid_yaml_2"]

    @pytest.mark.parametrize("invalid_yaml", invalid_yamls, ids=invalid_yaml_ids)
    def test_invalid_yaml(self, invalid_yaml):
        with pytest.raises(ValueError):
            yaml.load(invalid_yaml, Loader=UniqueKeyLoader)


def test_successful_read_deprecated_datapackage(tmp_path):
    f = tmp_path / "input/datapackage.json"
    f.parent.mkdir()
    f.touch()
    csvs = tmp_path / "input/data"
    csvs.mkdir()
    actual = read_deprecated_datapackage(f)
    assert actual == str(csvs)


def test_unsuccessful_read_deprecated_datapackage(tmp_path):
    f = tmp_path / "input/datapackage.json"
    f.parent.mkdir()
    f.touch()
    with pytest.raises(OtooleDeprecationError):
        read_deprecated_datapackage(f)
