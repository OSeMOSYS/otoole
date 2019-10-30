import logging
import os
import sys
from typing import Dict

import pandas as pd

from otoole import read_packaged_file

logger = logging.getLogger()


def check_parameter(df, config_details, name):
    actual_headers = df.columns
    expected_headers = config_details['indices']
    logger.debug("Expected headers for %s: %s", name, expected_headers)

    if 'REGION' in expected_headers and 'REGION' not in actual_headers:
        logger.info("Added 'REGION' column to %s", name)
        df['REGION'] = 'SIMPLICITY'

    if 'MODEOFOPERATION' in actual_headers:
        df = df.rename(columns={'MODEOFOPERATION': 'MODE_OF_OPERATION'})

    if actual_headers[-1] == 'VALUE':
        logger.info("%s is already in narrow form with headers %s", name, df.columns)
        narrow = df
    else:
        try:
            narrow = pd.melt(df, id_vars=expected_headers[:-1], var_name=expected_headers[-1], value_name='VALUE')
        except IndexError as ex:
            logger.debug(df.columns)
            raise ex

    expected_headers.append('VALUE')
    for column in expected_headers:
        if column not in narrow.columns:
            logger.warning("%s not in header of %s", column, name)

    logger.debug("Final expected headers for %s: %s", name, expected_headers)

    return narrow[expected_headers]


def check_set(df, config_details, name):

    logger.info("Checking set %s", name)
    narrow = df

    return narrow


def check_set_datatype(narrow: pd.DataFrame, config_details: Dict, set_name: str) -> pd.DataFrame:
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
    datatype = config_details[set_name]['dtype']
    logger.debug('Columns for set %s are: %s', set_name, narrow.columns)
    if narrow.iloc[:, 0].dtype != datatype:
        logger.warning("dtype does not match %s for set %s", datatype, set_name)
    return narrow


def check_datatypes(narrow: pd.DataFrame, config_details: Dict, parameter: str) -> pd.DataFrame:
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
        if column == 'VALUE':
            datatype = config_details[parameter]['dtype']
            dtypes['VALUE'] = datatype
        else:
            datatype = config_details[column]['dtype']
            dtypes[column] = datatype
        if narrow[column].dtype != datatype:
            logger.warning("dtype of column %s does not match %s for parameter %s", column, datatype, parameter)
            if datatype == 'int':
                try:
                    narrow[column] = narrow[column].apply(_cast_to_int)
                except ValueError as ex:
                    msg = "Unable to apply datatype for column {}: {}".format(column, str(ex))
                    raise ValueError(msg)
    return narrow.astype(dtypes)


def _cast_to_int(value):
    return int(float(value))


def main(output_folder, narrow_folder):
    """Read in a folder of irregular wide-format files and write as narrow csvs
    """
    config = read_packaged_file('config.yaml', 'otoole.preprocess')

    for parameter, details in config.items():
        logger.info("Looking for %s", parameter)
        config_details = config[parameter]

        filepath = os.path.join(output_folder, parameter + '.csv')

        try:
            df = pd.read_csv(filepath)
        except pd.errors.EmptyDataError:
            logger.error("No data found in file for %s", parameter)
            expected_columns = config_details['indices']
            default_columns = expected_columns + ['VALUE']
            df = pd.DataFrame(columns=default_columns)

        entity_type = config[parameter]['type']

        if entity_type == 'param':
            narrow = check_parameter(df, config_details, parameter)
            if not narrow.empty:
                narrow_checked = check_datatypes(narrow, config, parameter)
            else:
                narrow_checked = narrow
        elif entity_type == 'set':
            narrow = check_set(df, config_details, parameter)
            if not narrow.empty:
                narrow_checked = check_set_datatype(narrow, config, parameter)
            else:
                narrow_checked = narrow

        write_out_dataframe(narrow_folder, parameter, narrow_checked)


def write_out_dataframe(folder, parameter, df):
    """Writes out a dataframe as a csv into the data subfolder of a datapackage

    Arguments
    ---------
    folder : str
    parameter : str
    df : pandas.DataFrame

    """
    os.makedirs(os.path.join(folder, 'data'), exist_ok=True)
    filepath = os.path.join(folder, 'data', parameter + '.csv')
    with open(filepath, 'w') as csvfile:
        logger.info("Writing %s rows into narrow file for %s", df.shape[0], parameter)
        df.to_csv(csvfile, index=False)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    output_folder = sys.argv[1]
    narrow_folder = sys.argv[2]
    main(output_folder, narrow_folder)
