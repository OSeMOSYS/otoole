import logging
import os
import sys

import pandas as pd
from excel_to_osemosys import read_config

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


def main(output_folder):
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
        elif entity_type == 'set':
            narrow = check_set(df, config_details, parameter)

        filepath = os.path.join(output_folder, 'narrow', parameter + '.csv')
        with open(filepath, 'w') as csvfile:
            logger.info("Writing %s rows into narrow file for %s", narrow.shape[0], parameter)
            narrow.to_csv(csvfile, index=False)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    output_folder = sys.argv[1]
    main(output_folder)
