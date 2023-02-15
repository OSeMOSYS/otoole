"""Module to create template data"""
from typing import Any, Dict, Tuple

import pandas as pd

from otoole.read_strategies import ReadCsv
from otoole.utils import read_packaged_file


def get_csv_setup_data(
    config: Dict[str, Any]
) -> Tuple[Dict[str, pd.DataFrame], Dict[str, Any]]:
    """Gets template dataframe data to write as csvs

    Arguments
    ---------
    config: Dict[str,Any]
        Configuration data to get CSV data to match against

    Returns
    -------
    Dict[str: pd.DataFrame]
        Parameters with empty template dataframes
    Dict[str: Any]
        Default values extracted from config file
    """

    input_data: Dict[str, pd.DataFrame] = {}

    reader = ReadCsv(user_config=config)

    for config_type in ["param", "set"]:
        input_data = reader._get_missing_input_dataframes(
            input_data, config_type=config_type
        )
    input_data = reader._check_index(input_data)
    default_values = reader._read_default_values(config)

    return input_data, default_values


def get_config_setup_data() -> Dict[str, Any]:
    """Reads in template config data"""
    return read_packaged_file("config.yaml", "otoole.preprocess")
