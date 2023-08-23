"""This module implements the public API of the otoole package

Use the otoole ``convert`` function to convert between different file formats.
Import the convert function from the otoole package::

>>> from otoole import convert
>>> convert('config.yaml', 'excel', 'datafile', 'input.xlsx', 'output.dat')

"""
import logging
import os
from typing import Dict, Optional, Tuple, Union

import pandas as pd

from otoole.exceptions import OtooleError
from otoole.input import Context, ReadStrategy, WriteStrategy
from otoole.read_strategies import ReadCsv, ReadDatafile, ReadExcel
from otoole.results.results import ReadCbc, ReadCplex, ReadGlpk, ReadGurobi, ReadResults
from otoole.utils import _read_file, read_deprecated_datapackage, validate_config
from otoole.write_strategies import WriteCsv, WriteDatafile, WriteExcel

logger = logging.getLogger(__name__)


def read_results(
    config: str,
    from_format: str,
    from_path: str,
    input_format: str,
    input_path: str,
    glpk_model: str = None,
) -> Tuple[Dict[str, pd.DataFrame], Dict[str, float]]:
    """Read OSeMOSYS results from CBC, GLPK, Gurobi, or CPLEX results files

    Arguments
    ---------
    config : str
        Path to config file
    from_format : str
        Available options are 'cbc', 'gurobi', 'cplex', and 'glpk'
    from_path : str
        Path to source file (if datafile or excel) or folder (csv)
    input_format: str
        Format of input data. Available options are 'datafile', 'csv' and 'excel'
    input_path: str
        Path to input data
    glpk_model : str
        Path to ``*.glp`` model file

    Returns
    -------
    Tuple[dict[str, pd.DataFrame], dict[str, float]]
        Dictionary of parameter and set data and dictionary of default values
    """
    user_config = _get_user_config(config)
    input_strategy = _get_read_strategy(user_config, input_format)
    result_strategy = _get_read_result_strategy(user_config, from_format, glpk_model)

    if input_strategy:
        input_data, _ = input_strategy.read(input_path)
    else:
        input_data = {}

    if result_strategy:
        results, default_values = result_strategy.read(from_path, input_data=input_data)
        return results, default_values
    else:
        msg = "Conversion from {} is not yet implemented".format(from_format)
        raise NotImplementedError(msg)


def convert_results(
    config: str,
    from_format: str,
    to_format: str,
    from_path: str,
    to_path: str,
    input_format: str,
    input_path: str,
    write_defaults: bool = False,
    glpk_model: str = None,
) -> bool:
    """Post-process results from a CBC, CPLEX, Gurobi, or GLPK solution file into CSV format

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
    input_format: str
        Format of input data. Available options are 'datafile', 'csv' and 'excel'
    input_path: str
        Path to input data
    write_defaults : bool
        Write default values to CSVs
    glpk_model : str
        Path to ``*.glp`` model file

    Returns
    -------
    bool
        True if conversion was successful, False otherwise

    """
    msg = "Conversion from {} to {} is not yet implemented".format(
        from_format, to_format
    )

    user_config = _get_user_config(config)

    # set read strategy

    read_strategy = _get_read_result_strategy(user_config, from_format, glpk_model)

    # set write strategy

    write_defaults = True if write_defaults else False

    if to_format == "csv":
        write_strategy = WriteCsv(
            user_config=user_config, write_defaults=write_defaults
        )
    else:
        raise NotImplementedError(msg)

    # read in input file
    input_data, _ = read(config, input_format, input_path)

    if read_strategy and write_strategy:
        context = Context(read_strategy, write_strategy)
        context.convert(from_path, to_path, input_data=input_data)
    else:
        raise NotImplementedError(msg)

    return True


def _get_read_result_strategy(
    user_config, from_format, glpk_model=None
) -> Union[ReadResults, None]:
    """Get ``ReadResults`` for gurobi, cbc, cplex, and glpk formats

    Arguments
    ---------
    config : dict
        User configuration describing parameters and sets
    from_format : str
        Available options are 'cbc', 'gurobi', 'cplex', and 'glpk'
    glpk_model : str
        Path to ``*.glp`` model file

    Returns
    -------
    ReadStrategy or None
        A ReadStrategy object. Returns None if from_format is not recognised

    """

    if from_format == "cbc":
        read_strategy: ReadResults = ReadCbc(user_config)
    elif from_format == "gurobi":
        read_strategy = ReadGurobi(user_config=user_config)
    elif from_format == "cplex":
        read_strategy = ReadCplex(user_config=user_config)
    elif from_format == "glpk":
        if not glpk_model:
            raise OtooleError(resource="Read GLPK", message="Provide glpk model file")
        read_strategy = ReadGlpk(user_config=user_config, glpk_model=glpk_model)
    else:
        return None

    return read_strategy


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


def _get_read_strategy(user_config, from_format, keep_whitespace=False) -> ReadStrategy:
    """Get ``ReadStrategy`` for csv/datafile/excel format

    Arguments
    ---------
    config : dict
        User configuration describing parameters and sets
    from_format : str
        Available options are 'datafile', 'datapackage', 'csv' and 'excel'
    keep_whitespace: bool, default: False
        Keep whitespace in CSVs

    Returns
    -------
    ReadStrategy or None
        A ReadStrategy object. Returns None if from_format is not recognised

    """
    keep_whitespace = True if keep_whitespace else False

    if from_format == "datafile":
        read_strategy: ReadStrategy = ReadDatafile(user_config=user_config)
    elif from_format == "datapackage":
        logger.warning(
            "Reading from datapackage is deprecated, trying to read from CSVs"
        )
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
        msg = f"Conversion from {from_format} is not supported"
        raise NotImplementedError(msg)

    return read_strategy


def _get_write_strategy(user_config, to_format, write_defaults=False) -> WriteStrategy:
    """Get ``WriteStrategy`` for csv/datafile/excel format

    Arguments
    ---------
    user_config : dict
        User configuration describing parameters and sets
    to_format : str
        Available options are 'datafile', 'datapackage', 'csv' and 'excel'
    write_defaults: bool, default: False
        Write default values to output format

    Returns
    -------
    WriteStrategy or None
        A ReadStrategy object. Returns None if to_format is not recognised

    """
    # set write strategy
    write_defaults = True if write_defaults else False

    if to_format == "datapackage":
        write_strategy: WriteStrategy = WriteCsv(
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
        msg = f"Conversion to {to_format} is not supported"
        raise NotImplementedError(msg)

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

    user_config = _get_user_config(config)
    read_strategy = _get_read_strategy(
        user_config, from_format, keep_whitespace=keep_whitespace
    )

    write_strategy = _get_write_strategy(
        user_config, to_format, write_defaults=write_defaults
    )

    if from_format == "datapackage":
        logger.warning(
            "Reading from and writing to datapackage is deprecated, writing to CSVs"
        )
        from_path = read_deprecated_datapackage(from_path)
        to_path = os.path.join(os.path.dirname(to_path), "data")

    context = Context(read_strategy, write_strategy)
    context.convert(from_path, to_path)

    return True


def read(
    config: str, from_format: str, from_path: str, keep_whitespace: bool = False
) -> Tuple[Dict[str, pd.DataFrame], Dict[str, float]]:
    """Read OSeMOSYS data from datafile, csv or Excel formats

    Arguments
    ---------
    config : str
        Path to config file
    from_format : str
        Available options are 'datafile', 'csv', 'excel' and 'datapackage' [deprecated]
    from_path : str
        Path to source file (if datafile or excel) or folder (csv)
    keep_whitespace: bool, default: False
        Keep whitespace in source files

    Returns
    -------
    Tuple[dict[str, pd.DataFrame], dict[str, float]]
        Dictionary of parameter and set data and dictionary of default values
    """
    user_config = _get_user_config(config)
    read_strategy = _get_read_strategy(
        user_config, from_format, keep_whitespace=keep_whitespace
    )

    if from_format == "datapackage":
        from_path = read_deprecated_datapackage(from_path)

    return read_strategy.read(from_path)


def write(
    config: str,
    to_format: str,
    to_path: str,
    inputs,
    default_values: Optional[Dict[str, float]] = None,
) -> bool:
    """Write OSeMOSYS data to datafile, csv or Excel formats

    Arguments
    ---------
    config : str
        Path to config file
    to_format : str
        Available options are 'datafile', 'csv', 'excel' and 'datapackage' [deprecated],
    to_path : str
        Path to destination file (if datafile or excel) or folder (csv))
    inputs : dict[str, pd.DataFrame]
        Dictionary of pandas data frames to write
    default_values: dict[str, float], default: None
        Dictionary of default values to write to datafile

    """
    user_config = _get_user_config(config)
    if default_values is None:
        write_strategy = _get_write_strategy(
            user_config, to_format, write_defaults=False
        )
        write_strategy.write(inputs, to_path, {})
    else:
        write_strategy = _get_write_strategy(
            user_config, to_format, write_defaults=True
        )
        write_strategy.write(inputs, to_path, default_values)

    return True
