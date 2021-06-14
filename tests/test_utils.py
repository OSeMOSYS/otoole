import pytest

from unittest.mock import MagicMock

from otoole.utils import extract_config, read_packaged_file


class TestDataPackageSchema:
    @pytest.mark.xfail
    def test_read_datapackage_schema_into_config(self):

        schema = read_packaged_file("datapackage.json", "otoole.preprocess")
        mock = MagicMock()
        mock.__getitem__.return_value = 0

        actual = extract_config(schema, mock)

        expected = read_packaged_file("config.yaml", "otoole.preprocess")
        assert actual == expected
