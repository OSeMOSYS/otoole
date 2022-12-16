from unittest.mock import MagicMock

import pytest
import yaml

from otoole.utils import UniqueKeyLoader, extract_config, read_packaged_file


class TestDataPackageSchema:
    @pytest.mark.xfail
    def test_read_datapackage_schema_into_config(self):

        schema = read_packaged_file("datapackage.json", "otoole.preprocess")
        mock = MagicMock()
        mock.__getitem__.return_value = 0

        actual = extract_config(schema, mock)

        expected = read_packaged_file("config.yaml", "otoole.preprocess")
        assert actual == expected


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
