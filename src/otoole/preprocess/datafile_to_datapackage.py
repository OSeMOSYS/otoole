"""Converts an OSeMOSYS datafile to a Tabular Data Package

"""
import logging
import sys

from pulp import Amply

from otoole.preprocess.excel_to_osemosys import read_config

logger = logging.getLogger(__name__)


def convert_file_to_package(path_to_datafile: str, path_to_datapackage: str):
    """Converts an OSeMOSYS datafile to a Tabular Data Package

    Arguments
    ---------
    path_to_datafile: str
    path_to_datapackage: str

    """
    parameter_definitions = load_parameter_definitions()
    datafile_parser = Amply(parameter_definitions)
    logger.debug(datafile_parser)

    with open(path_to_datafile, 'r') as datafile:
        datafile_parser.load_file(datafile)

    with open(path_to_datapackage, 'w') as datapackage:
        for symbol in datafile_parser.symbols:
            datapackage.write(datafile_parser[symbol])


def load_parameter_definitions():
    """Load the set and parameter dimensions into datafile parser
    """
    config = read_config()

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
