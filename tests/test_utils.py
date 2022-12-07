from unittest.mock import MagicMock

import pytest

from otoole.utils import create_name_mappings, extract_config, read_packaged_file


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
