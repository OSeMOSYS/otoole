"""Converts an OSeMOSYS datafile to a Tabular Data Package

"""
import logging
import os
import sys
from typing import Dict, List

import pandas as pd
from flatten_dict import flatten
from pulp import Amply

from otoole import read_packaged_file
from otoole.preprocess.longify_data import check_datatypes, check_set_datatype, write_out_dataframe

logger = logging.getLogger(__name__)


def convert_file_to_package(path_to_datafile: str, path_to_datapackage: str):
    """Converts an OSeMOSYS datafile to a Tabular Data Package

    Arguments
    ---------
    path_to_datafile: str
    path_to_datapackage: str
        Path to the folder in which to write the new Tabular Data Package

    """
    config = read_packaged_file('config.yaml', 'otoole.preprocess')
    amply_datafile = read_in_datafile(path_to_datafile, config)
    dict_of_dataframes = convert_amply_to_dataframe(amply_datafile, config)
    if not os.path.exists(path_to_datapackage):
        os.mkdir(path_to_datapackage)
    for name, df in dict_of_dataframes.items():
        write_out_dataframe(path_to_datapackage, name, df)
    datapackage = read_packaged_file('datapackage.json', 'otoole.preprocess')
    filepath = os.path.join(path_to_datapackage, 'datapackage.json')
    with open(filepath, 'w') as destination:
        destination.writelines(datapackage)


def read_in_datafile(path_to_datafile: str, config: Dict) -> Amply:
    """Read in a datafile using the Amply parsing class

    Arguments
    ---------
    path_to_datafile: str
    config: Dict
    """
    parameter_definitions = load_parameter_definitions(config)
    datafile_parser = Amply(parameter_definitions)
    logger.debug(datafile_parser)

    with open(path_to_datafile, 'r') as datafile:
        datafile_parser.load_file(datafile)

    return datafile_parser


def convert_amply_to_dataframe(datafile_parser, config) -> Dict[str, pd.DataFrame]:
    """Converts an amply parser to a dict of pandas dataframes

    Arguments
    ---------
    datafile_parser : Amply
    config : Dict

    Returns
    -------
    dict of pandas.DataFrame
    """

    dict_of_dataframes = {}

    for name in datafile_parser.symbols.keys():
        logger.debug("Extracting data for %s", name)
        if config[name]['type'] == 'param':
            indices = config[name]['indices']
            indices_dtypes = [config[index]['dtype'] for index in indices]
            indices.append('VALUE')
            indices_dtypes.append('float')

            raw_data = datafile_parser[name].data
            data = convert_amply_data_to_list(raw_data)
            df = pd.DataFrame(data=data, columns=indices)
            try:
                dict_of_dataframes[name] = check_datatypes(df, config, name)
            except ValueError as ex:
                msg = "Validation error when checking datatype of {}: {}".format(name, str(ex))
                raise ValueError(msg)
        elif config[name]['type'] == 'set':
            data = datafile_parser[name].data
            logger.debug(data)

            indices = ['VALUE']
            df = pd.DataFrame(data=data, columns=indices, dtype=config[name]['dtype'])
            dict_of_dataframes[name] = check_set_datatype(df, config, name)
        logger.debug("\n%s\n", dict_of_dataframes[name])

    return dict_of_dataframes


def convert_amply_data_to_list(amply_data: Dict) -> List[List]:
    """Flattens a dictionary into a list of lists

    Arguments
    ---------
    amply_data: dict
    """

    data = []

    raw_data = flatten(amply_data)
    for key, value in raw_data.items():
        data.append(list(key) + [value])

    return data


def load_parameter_definitions(config: dict) -> str:
    """Load the set and parameter dimensions into datafile parser

    Returns
    -------
    str
    """
    elements = ""

    for name, attributes in config.items():
        if attributes['type'] == 'param':
            elements += 'param {} {};\n'.format(name, "{" + ",".join(attributes['indices']) + "}")
        elif attributes['type'] == 'set':
            elements += 'set {};\n'.format(name)

    logger.debug(elements)
    return elements


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    path_to_datafile = sys.argv[1]
    path_to_datapackage = sys.argv[2]

    convert_file_to_package(path_to_datafile, path_to_datapackage)
