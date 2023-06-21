"""This module implements the public API of the otoole package

Use the otoole ``convert`` function to convert between different file formats.
Import the convert function from the otoole package::

>>> from otoole import convert
>>> convert('config.yaml', 'excel', 'datafile', 'input.xlsx', 'output.dat')

"""
import logging
import os
from typing import Union

from otoole.input import Context, ReadStrategy, WriteStrategy
from otoole.read_strategies import ReadCsv, ReadDatafile, ReadExcel
from otoole.results.results import ReadCbc, ReadCplex, ReadGurobi
from otoole.utils import _read_file, read_deprecated_datapackage, validate_config
from otoole.write_strategies import WriteCsv, WriteDatafile, WriteExcel

logger = logging.getLogger(__name__)


def convert_results(
    config,
    from_format,
    to_format,
    from_path,
    to_path,
    input_datapackage=None,
    input_csvs=None,
    input_datafile=None,
    write_defaults=False,
):
    """Post-process results from a CBC, CPLEX or Gurobi solution file into CSV format

    Arguments
    ---------
    config : str
        Path to config file
    from_format : str
        Available options are 'cbc', 'cplex' and 'gurobi'
    to_format : str
        Available options are 'csv'
    from_path : str
        Path to cbc, cplex or gurobi solution file
    to_path : str
        Path to destination folder
    input_datapackage : str
        Path to folder containing datapackage.json
    input_csvs : str
        Path to folder containing CSVs
    input_datafile : str
        Path to datafile
    write_defaults : str
        Write default values to CSVs

    Returns
    -------
    bool
        True if conversion was successful, False otherwise

    """
    msg = "Conversion from {} to {} is not yet implemented".format(
        from_format, to_format
    )

    read_strategy = None
    write_strategy = None

    if config:
        _, ending = os.path.splitext(config)
        with open(config, "r") as config_file:
            user_config = _read_file(config_file, ending)
        logger.info("Reading config from {}".format(config))
        logger.info("Validating config from {}".format(config))
        validate_config(user_config)

    # set read strategy

    if from_format == "cbc":
        read_strategy = ReadCbc(user_config=user_config)
    elif from_format == "cplex":
        read_strategy = ReadCplex(user_config=user_config)
    elif from_format == "gurobi":
        read_strategy = ReadGurobi(user_config=user_config)

    # set write strategy

    write_defaults = True if write_defaults else False

    if to_format == "csv":
        write_strategy = WriteCsv(
            user_config=user_config, write_defaults=write_defaults
        )

    if input_datapackage:
        logger.warning(
            "Reading from datapackage is deprecated, trying to read from CSVs"
        )
        input_csvs = read_deprecated_datapackage(input_datapackage)
        logger.info("Successfully read folder of CSVs")
        input_data, _ = ReadCsv(user_config=user_config).read(input_csvs)
    elif input_datafile:
        input_data, _ = ReadDatafile(user_config=user_config).read(input_datafile)
    elif input_csvs:
        input_data, _ = ReadCsv(user_config=user_config).read(input_csvs)
    else:
        input_data = {}

    if read_strategy and write_strategy:
        context = Context(read_strategy, write_strategy)
        context.convert(from_path, to_path, input_data=input_data)
    else:
        raise NotImplementedError(msg)
        return False

    return True


def _get_user_config(config) -> dict:
    """Read in the configuration file

    Arguments
    ---------
    config : str
        Path to config file

    Returns
    -------
    dict
        A dictionary containing the user configuration
    """
    if config:
        _, ending = os.path.splitext(config)
        with open(config, "r") as config_file:
            user_config = _read_file(config_file, ending)
        logger.info("Reading config from {}".format(config))
        logger.info("Validating config from {}".format(config))
        validate_config(user_config)
    return user_config


def _get_read_strategy(
    user_config, from_format, from_path, keep_whitespace=False
) -> Union[ReadStrategy, None]:
    """Read OSeMOSYS parameter data from csv/datafile/excel format

    Arguments
    ---------
    config : dict
        User configuration describing parameters and sets
    from_format : str
        Available options are 'datafile', 'datapackage', 'csv' and 'excel'
    from_path : str
        Path to destination file (if datafile or excel) or folder (csv or datapackage)
    keep_whitespace: bool, default: False
        Keep whitespace in CSVs

    Returns
    -------
    dict[str, pandas.DataFrame]
        Dictionary of pandas DataFrames containing the data

    """
    keep_whitespace = True if keep_whitespace else False

    if from_format == "datafile":
        read_strategy: Union[ReadStrategy, None] = ReadDatafile(user_config=user_config)
    elif from_format == "datapackage":
        logger.warning(
            "Reading from datapackage is deprecated, trying to read from CSVs"
        )
        from_path = read_deprecated_datapackage(from_path)
        logger.info("Successfully read folder of CSVs")
        read_strategy = ReadCsv(
            user_config=user_config, keep_whitespace=keep_whitespace
        )  # typing: ReadStrategy
    elif from_format == "csv":
        read_strategy = ReadCsv(
            user_config=user_config, keep_whitespace=keep_whitespace
        )  # typing: ReadStrategy
    elif from_format == "excel":
        read_strategy = ReadExcel(
            user_config=user_config, keep_whitespace=keep_whitespace
        )  # typing: ReadStrategy
    else:
        read_strategy = None

    return read_strategy


def _get_write_strategy(
    user_config, to_format, to_path, write_defaults=False
) -> Union[WriteStrategy, None]:
    """ """
    # set write strategy
    write_defaults = True if write_defaults else False

    if to_format == "datapackage":
        logger.warning("Writing to datapackage is deprecated, writing to CSVs")
        to_path = os.path.join(os.path.dirname(to_path), "data")
        write_strategy: Union[WriteStrategy, None] = WriteCsv(
            user_config=user_config, write_defaults=write_defaults
        )
    elif to_format == "excel":
        write_strategy = WriteExcel(
            user_config=user_config, write_defaults=write_defaults
        )
    elif to_format == "datafile":
        write_strategy = WriteDatafile(
            user_config=user_config, write_defaults=write_defaults
        )
    elif to_format == "csv":
        write_strategy = WriteCsv(
            user_config=user_config, write_defaults=write_defaults
        )
    else:
        write_strategy = None

    return write_strategy


def convert(
    config,
    from_format,
    to_format,
    from_path,
    to_path,
    write_defaults=False,
    keep_whitespace=False,
) -> bool:
    """Convert OSeMOSYS data from/to datafile, csv and Excel formats

    Arguments
    ---------
    config : str
        Path to config file
    from_format : str
        Available options are 'datafile', 'datapackage', 'csv' and 'excel'
    to_format : str
        Available options are 'datafile', 'datapackage', 'csv' and 'excel'
    from_path : str
        Path to destination file (if datafile or excel) or folder (csv or datapackage)
    write_defaults: bool, default: False
        Write default values to CSVs
    keep_whitespace: bool, default: False
        Keep whitespace in CSVs

    Returns
    -------
    bool
        True if conversion was successful, False otherwise
    """

    msg = "Conversion from {} to {} is not yet implemented".format(
        from_format, to_format
    )

    user_config = _get_user_config(config)
    read_strategy = _get_read_strategy(
        user_config, from_format, from_path, keep_whitespace=keep_whitespace
    )

    write_strategy = _get_write_strategy(
        user_config, to_format, to_path, write_defaults=write_defaults
    )

    if read_strategy and write_strategy:
        context = Context(read_strategy, write_strategy)
        context.convert(from_path, to_path)
    else:
        raise NotImplementedError(msg)
        return False

    return True