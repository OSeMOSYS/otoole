"""Read in a folder of irregular wide-format csv files and write them out as narrow csvs
"""
import logging
from typing import Dict

import pandas as pd

logger = logging.getLogger()


def check_set_datatype(
    narrow: pd.DataFrame, config_details: Dict, set_name: str
) -> pd.DataFrame:
    """Checks the datatypes of a set_name dataframe

    Arguments
    ---------
    narrow : pandas.DataFrame
        The set data
    config_details : dict
        The configuration dictionary
    set_name : str
        The name of the set
    """
    datatype = config_details[set_name]["dtype"]
    logger.debug("Columns for set %s are: %s", set_name, narrow.columns)
    if narrow.iloc[:, 0].dtype != datatype:
        logger.warning("dtype does not match %s for set %s", datatype, set_name)
    return narrow


def check_datatypes(
    narrow: pd.DataFrame, config_details: Dict, parameter: str
) -> pd.DataFrame:
    """Checks a parameters datatypes

    Arguments
    ---------
    narrow : pandas.DataFrame
        The parameter data
    config_details : dict
        The configuration dictionary
    parameter : str
        The name of the parameter
    """
    logger.info("Checking datatypes for %s", parameter)
    dtypes = {}

    for column in narrow.columns:
        if column == "VALUE":
            datatype = config_details[parameter]["dtype"]
            dtypes["VALUE"] = datatype
        else:
            datatype = config_details[column]["dtype"]
            dtypes[column] = datatype
        if narrow[column].dtype != datatype:
            logger.warning(
                "dtype of column %s does not match %s for parameter %s",
                column,
                datatype,
                parameter,
            )
            if datatype == "int":
                try:
                    narrow[column] = narrow[column].apply(_cast_to_int)
                except ValueError as ex:
                    msg = "Unable to apply datatype for column {}: {}".format(
                        column, str(ex)
                    )
                    raise ValueError(msg)
    return narrow.astype(dtypes)


def _cast_to_int(value):
    return int(float(value))
