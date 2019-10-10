import logging
import os
import sys
from typing import Dict

import pandas as pd

from otoole.preprocess.excel_to_osemosys import read_config

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


def check_set_datatype(narrow: pd.DataFrame, config_details: Dict, parameter: str) -> pd.DataFrame:
    datatype = config_details[parameter]['dtype']
    logger.debug('Columns for set %s are: %s', parameter, narrow.columns)
    if narrow.iloc[:, 0].dtype != datatype:
        logger.warning("dtype does not match %s for set %s", datatype, parameter)
    return narrow


def check_datatypes(narrow: pd.DataFrame, config_details: Dict, parameter: str) -> pd.DataFrame:
    """
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
                narrow[column] = narrow[column].apply(cast_to_int)
    return narrow.astype(dtypes)


def cast_to_int(value):
    return int(float(value))


def main(output_folder, narrow_folder):
    """Read in a folder of irregular wide-format files and write as narrow csvs
    """
    config = read_config()

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

        filepath = os.path.join(narrow_folder, 'data', parameter + '.csv')
        with open(filepath, 'w') as csvfile:
            logger.info("Writing %s rows into narrow file for %s", narrow_checked.shape[0], parameter)
            narrow_checked.to_csv(csvfile, index=False)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    output_folder = sys.argv[1]
    narrow_folder = sys.argv[2]
    main(output_folder, narrow_folder)
