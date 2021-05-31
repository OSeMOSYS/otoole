"""Read in a folder of irregular wide-format csv files and write them out as narrow csvs
"""
import logging
import numpy as np
import pandas as pd
from typing import Dict

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
        logger.info("dtype does not match %s for set %s", datatype, set_name)
    return narrow


def check_datatypes(
    df: pd.DataFrame, config_details: Dict, parameter: str
) -> pd.DataFrame:
    """Checks a parameters datatypes

    Arguments
    ---------
    df : pandas.DataFrame
        The parameter data
    config_details : dict
        The configuration dictionary
    parameter : str
        The name of the parameter
    """
    logger.info("Checking datatypes for %s", parameter)
    logger.debug(df.columns)
    dtypes = {}

    for column in df.columns:
        if column == "VALUE":
            datatype = config_details[parameter]["dtype"]
            dtypes["VALUE"] = datatype
        else:
            datatype = config_details[column]["dtype"]
            dtypes[column] = datatype
            logger.debug(f"Found {datatype} for column {column}")
        if df[column].dtype != datatype:
            logger.info(
                "dtype of column %s does not match %s for parameter %s",
                column,
                datatype,
                parameter,
            )
            if datatype == "int":
                dtypes[column] = "int64"
                try:
                    df[column] = df[column].apply(_cast_to_int)
                except ValueError as ex:
                    msg = "Unable to apply datatype for column {}: {}".format(
                        column, str(ex)
                    )
                    raise ValueError(msg)

    return df.astype(dtypes)


def _cast_to_int(value):
    return np.int64(float(value))
