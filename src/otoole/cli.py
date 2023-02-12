"""Provides a command line interface to the ``otoole`` package

The key functions are **convert**, **cplex** and **viz**.

The ``convert`` command allows convertion of multiple different OSeMOSYS input formats
including from/to csv, an AMPL format datafile, a Tabular Data Package, a folder of
CSVs, an Excel workbook with one tab per parameter, an SQLite database

The ``cplex`` command provides access to scripts which transform and process a CPLEX
solution file into a format which is more readily processed - either to CBC or CSV
format.

The ``validate`` command checks the technology and fuel names of a tabular data package
against a standard or user defined configuration file.

The **viz** command allows you to produce a Reference Energy System diagram from a
Tabular Data Package.

Example
-------

Ask for help on the command line::

    >>> $ otoole --help
    usage: otoole [-h] [--verbose] [--version] {convert,cplex,validate,viz} ...

    otoole: Python toolkit of OSeMOSYS users

    positional arguments:
    {convert,cplex,validate,viz}
        convert             Convert from one input format to another
        cplex               Process a CPLEX solution file
        validate            Validate an OSeMOSYS model
        viz                 Visualise the model

    optional arguments:
    -h, --help            show this help message and exit
    --verbose, -v         Enable debug mode
    --version, -V         The version of otoole

"""
import argparse
import logging
import os
import sys

from otoole import (
    ReadCbc,
    ReadCplex,
    ReadCsv,
    ReadDatafile,
    ReadExcel,
    ReadGurobi,
    WriteCsv,
    WriteDatafile,
    WriteExcel,
    __version__,
)
from otoole.input import Context
from otoole.utils import (
    _read_file,
    read_deprecated_datapackage,
    read_packaged_file,
    validate_config,
)
from otoole.validate import main as validate
from otoole.visualise import create_res

logger = logging.getLogger(__name__)


def validate_model(args):
    file_format = args.format

    if args.config:
        config = read_packaged_file(args.config)
        validate(file_format, args.filepath, config)
    else:
        validate(file_format, args.filepath)


def cplex2cbc(args):
    ReadCplex()._convert_cplex_file(
        args.cplex_file,
        args.output_file,
        args.start_year,
        args.end_year,
        args.output_format,
    )


def result_matrix(args):
    """Post-process results from CBC solution file into CSV format"""
    msg = "Conversion from {} to {} is not yet implemented".format(
        args.from_format, args.to_format
    )

    read_strategy = None
    write_strategy = None

    config = None
    if args.config:
        _, ending = os.path.splitext(args.config)
        with open(args.config, "r") as config_file:
            config = _read_file(config_file, ending)
        logger.info("Reading config from {}".format(args.config))
        logger.info("Validating config from {}".format(args.config))
        validate_config(config)

    # set read strategy

    if args.from_format == "cbc":
        read_strategy = ReadCbc(user_config=config)
    elif args.from_format == "cplex":
        read_strategy = ReadCplex(user_config=config)
    elif args.from_format == "gurobi":
        read_strategy = ReadGurobi(user_config=config)

    # set write strategy

    write_defaults = True if args.write_defaults else False

    if args.to_format == "csv":
        write_strategy = WriteCsv(user_config=config, write_defaults=write_defaults)

    if args.input_datapackage:
        logger.warning(
            "Reading from datapackage is deprecated, trying to read from CSVs"
        )
        input_csvs = read_deprecated_datapackage(args.input_datapackage)
        input_data, _ = ReadCsv(user_config=config).read(input_csvs)
    elif args.input_datafile:
        input_data, _ = ReadDatafile(user_config=config).read(args.input_datafile)
    else:
        input_data = {}

    if read_strategy and write_strategy:
        context = Context(read_strategy, write_strategy)
        context.convert(args.from_path, args.to_path, input_data=input_data)
    else:
        raise NotImplementedError(msg)


def conversion_matrix(args):
    """Convert from one format to another

    Implemented conversion functions::

        from\to     ex cs dp df
        -----------------------
        excel       -- yy -- --
        csv         nn -- yy nn
        datafile    nn -- yy --

    """

    msg = "Conversion from {} to {} is not yet implemented".format(
        args.from_format, args.to_format
    )

    read_strategy = None
    write_strategy = None

    from_path = args.from_path
    to_path = args.to_path

    config = None
    if args.config:
        _, ending = os.path.splitext(args.config)
        with open(args.config, "r") as config_file:
            config = _read_file(config_file, ending)
        logger.info("Reading config from {}".format(args.config))
        logger.info("Validating config from {}".format(args.config))
        validate_config(config)

    # set read strategy

    if args.from_format == "datafile":
        read_strategy = ReadDatafile(user_config=config)
    elif args.from_format == "datapackage":
        logger.warning(
            "Reading from datapackage is deprecated, trying to read from CSVs"
        )
        from_path = read_deprecated_datapackage(from_path)
        read_strategy = ReadCsv(user_config=config)
    elif args.from_format == "csv":
        read_strategy = ReadCsv(user_config=config)
    elif args.from_format == "excel":
        read_strategy = ReadExcel(user_config=config)

    input_data, _ = read_strategy.read(args.from_path)

    # set write strategy

    write_defaults = True if args.write_defaults else False

    if args.to_format == "datapackage":
        logger.warning("Writing to datapackage is deprecated, writing to CSVs")
        to_path = os.path.join(os.path.dirname(to_path), "data")
        write_strategy = WriteCsv(user_config=config, write_defaults=write_defaults)
    elif args.to_format == "excel":
        write_strategy = WriteExcel(user_config=config, write_defaults=write_defaults)
    elif args.to_format == "datafile":
        write_strategy = WriteDatafile(
            user_config=config, write_defaults=write_defaults
        )
    elif args.to_format == "csv":
        write_strategy = WriteCsv(user_config=config, write_defaults=write_defaults)

    if read_strategy and write_strategy:
        context = Context(read_strategy, write_strategy)
        context.convert(from_path, to_path)
    else:
        raise NotImplementedError(msg)


def data2res(args):
    """Get input data and call res creation."""

    data_format = args.data_format
    data_path = args.data_path

    _, ending = os.path.splitext(args.config)
    with open(args.config, "r") as config_file:
        config = _read_file(config_file, ending)
    logger.info("Reading config from {}".format(args.config))
    logger.info("Validating config from {}".format(args.config))
    validate_config(config)

    if data_format == "datafile":
        read_strategy = ReadDatafile(user_config=config)
    elif data_format == "datapackage":
        logger.warning(
            "Reading from datapackage is deprecated, trying to read from CSVs"
        )
        data_path = read_deprecated_datapackage(data_path)
        read_strategy = ReadCsv(user_config=config)
    elif data_format == "csv":
        read_strategy = ReadCsv(user_config=config)
    elif data_format == "excel":
        read_strategy = ReadExcel(user_config=config)

    input_data, _ = read_strategy.read(data_path)

    create_res(input_data, args.resfile)


def get_parser():
    parser = argparse.ArgumentParser(
        description="otoole: Python toolkit of OSeMOSYS users"
    )

    parser.add_argument(
        "--verbose", "-v", help="Enable debug mode", action="count", default=0
    )
    parser.add_argument(
        "--version",
        "-V",
        action="version",
        version=__version__,
        help="The version of otoole",
    )

    subparsers = parser.add_subparsers()

    # Parser for results
    result_parser = subparsers.add_parser("results", help="Post-process solution files")
    result_parser.add_argument(
        "from_format",
        help="Result data format to convert from",
        choices=sorted(["cbc", "cplex", "gurobi"]),
    )
    result_parser.add_argument(
        "to_format",
        help="Result data format to convert to",
        choices=sorted(["csv"]),
    )
    result_parser.add_argument(
        "from_path", help="Path to file or folder to convert from"
    )
    result_parser.add_argument("to_path", help="Path to file or folder to convert to")
    result_parser.add_argument(
        "--input_datapackage",
        help="Input data package required for OSeMOSYS short or fast results",
        default=None,
    )
    result_parser.add_argument(
        "--input_datafile",
        help="Input GNUMathProg datafile required for OSeMOSYS short or fast results",
        default=None,
    )
    result_parser.add_argument("config", help="Path to config YAML file")
    result_parser.add_argument(
        "--write_defaults",
        help="Writes default values",
        default=False,
        action="store_true",
    )
    result_parser.set_defaults(func=result_matrix)

    # Parser for conversion
    convert_parser = subparsers.add_parser(
        "convert", help="Convert from one input format to another"
    )
    convert_parser.add_argument(
        "from_format",
        help="Input data format to convert from",
        choices=sorted(["datafile", "datapackage", "excel", "csv"]),
    )
    convert_parser.add_argument(
        "to_format",
        help="Input data format to convert to",
        choices=sorted(["datafile", "datapackage", "csv", "excel"]),
    )
    convert_parser.add_argument(
        "from_path", help="Path to file or folder to convert from"
    )
    convert_parser.add_argument("to_path", help="Path to file or folder to convert to")
    convert_parser.add_argument("config", help="Path to config YAML file")
    convert_parser.add_argument(
        "--write_defaults",
        help="Writes default values",
        default=False,
        action="store_true",
    )
    convert_parser.set_defaults(func=conversion_matrix)

    # Parser for validation
    valid_parser = subparsers.add_parser("validate", help="Validate an OSeMOSYS model")
    valid_parser.add_argument(
        "format",
        help="The format of the OSeMOSYS model to validate",
        choices=["datapackage", "sql"],
    )
    valid_parser.add_argument(
        "filepath", help="Path to the OSeMOSYS datapackage.json file to validate"
    )
    valid_parser.add_argument(
        "--config", help="Path to a user-defined validation-config file"
    )
    valid_parser.set_defaults(func=validate_model)

    # Parser for visualisation
    viz_parser = subparsers.add_parser("viz", help="Visualise the model")
    viz_subparsers = viz_parser.add_subparsers()

    res_parser = viz_subparsers.add_parser(
        "res", help="Generate a reference energy system"
    )
    res_parser.add_argument(
        "data_format",
        help="Input data format",
        choices=sorted(["datafile", "excel", "csv"]),
    )
    res_parser.add_argument("data_path", help="Input data path")
    res_parser.add_argument("resfile", help="Path to reference energy system")
    res_parser.add_argument("config", help="Path to config YAML file")
    res_parser.set_defaults(func=data2res)

    return parser


def main():

    parser = get_parser()
    args = parser.parse_args(sys.argv[1:])

    if args.verbose >= 1 and args.verbose < 2:
        logging.basicConfig(level=logging.INFO)
    if args.verbose > 2:
        logging.basicConfig(level=logging.DEBUG)

    def exception_handler(
        exception_type, exception, traceback, debug_hook=sys.excepthook
    ):
        if args.verbose:
            debug_hook(exception_type, exception, traceback)
        else:
            print("{}: {}".format(exception_type.__name__, str(exception)))

    sys.excepthook = exception_handler

    if "func" in args:
        args.func(args)
    else:
        parser.print_help()
