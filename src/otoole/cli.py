"""Provides a command line interface to the ``otoole`` package

The key functions are **convert**, **cplex** and **viz**.

The ``convert`` command allows convertion of multiple different OSeMOSYS input formats including
from/to csv, an AMPL format datafile, a Tabular Data Package, a folder of CSVs, an Excel workbook with
one tab per parameter, an SQLite database

The ``cplex`` command provides access to scripts which transform and process a CPLEX solution file
into a format which is more readily processed - either to CBC or CSV format.

The ``validate`` command checks the technology and fuel names of a tabular data package against a standard
or user defined configuration file.

The **viz** command allows you to produce a Reference Energy System diagram from a Tabular Data Package.

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
import sys

from otoole import __version__, read_packaged_file
from otoole.preprocess import convert_file_to_package, create_datafile, create_datapackage, generate_csv_from_excel
from otoole.preprocess.create_datapackage import convert_datapackage_to_sqlite
from otoole.results.convert import convert_cplex_file
from otoole.validate import main as validate
from otoole.visualise import create_res


def validate_model(args):
    file_format = args.format

    if args.config:
        config = read_packaged_file(args.config)
        validate(file_format, args.filepath, config)
    else:
        validate(file_format, args.filepath)


def cplex2cbc(args):
    convert_cplex_file(args.cplex_file, args.output_file, args.start_year,
                       args.end_year, args.output_format)


def conversion_matrix(args):
    """Convert from one format to another

    Implemented conversion functions::

        from\to     ex cs dp sq df
        --------------------------
        excel       -- yy
        csv         nn -- yy nn nn
        datapackage nn ?? -- yy yy
        sql         nn       -- yy
        datafile    nn ?? yy    --

    """

    msg = "Conversion from {} to {} is not yet implemented".format(args.from_format, args.to_format)

    if args.from_format == 'datafile':

        if args.to_format == 'datapackage':
            convert_file_to_package(args.from_path, args.to_path)
        else:
            raise NotImplementedError(msg)

    elif (args.from_format == 'datapackage'):

        if args.to_format == 'sql':
            convert_datapackage_to_sqlite(args.from_path, args.to_path)
        elif args.to_format == 'datafile':
            create_datafile(args.from_path, args.to_path)
        else:
            raise NotImplementedError(msg)

    elif args.from_format == 'sql':

        if args.to_format == 'datafile':
            create_datafile(args.from_path, args.to_path, sql=True)
        else:
            raise NotImplementedError(msg)

    elif args.from_format == 'csv':
        if args.to_format == 'datapackage':
            create_datapackage(args.from_path, args.to_path)
        else:
            raise NotImplementedError(msg)

    elif args.from_format == 'excel':
        if args.to_format == 'csv':
            generate_csv_from_excel(args.from_path, args.to_path)
        else:
            raise NotImplementedError(msg)

    else:
        raise NotImplementedError(msg)


def datapackage2res(args):
    create_res(args.datapackage, args.resfile)


def get_parser():
    parser = argparse.ArgumentParser(description="otoole: Python toolkit of OSeMOSYS users")

    parser.add_argument('--verbose', '-v', help='Enable debug mode', action='count', default=0)
    parser.add_argument('--version', '-V', action='version', version=__version__,
                        help='The version of otoole')

    subparsers = parser.add_subparsers()

    # Parser for conversion
    convert_parser = subparsers.add_parser('convert', help='Convert from one input format to another')
    convert_parser.add_argument('from_format', help='Input data format to convert from',
                                choices=sorted(['datafile', 'datapackage', 'sql', 'excel', 'csv']))
    convert_parser.add_argument('to_format', help='Input data format to convert to',
                                choices=sorted(['datafile', 'datapackage', 'sql', 'csv']))
    convert_parser.add_argument('from_path', help="Path to file or folder to convert from")
    convert_parser.add_argument('to_path', help='Path to file or folder to convert to')
    convert_parser.set_defaults(func=conversion_matrix)

    # Parser for the CPLEX related commands
    cplex_parser = subparsers.add_parser('cplex',
                                         help='Process a CPLEX solution file')

    cplex_parser.add_argument("cplex_file",
                              help="The filepath of the OSeMOSYS cplex output file")
    cplex_parser.add_argument("output_file",
                              help="The filepath of the converted file that will be written")
    cplex_parser.add_argument("-s", "--start_year", type=int, default=2015,
                              help="Output only the results from this year onwards")
    cplex_parser.add_argument("-e", "--end_year", type=int, default=2070,
                              help="Output only the results upto and including this year")
    cplex_parser.add_argument('output_format', choices=['csv', 'cbc'], default='cbc')
    cplex_parser.set_defaults(func=cplex2cbc)

    # Parser for validation
    valid_parser = subparsers.add_parser('validate', help='Validate an OSeMOSYS model')
    valid_parser.add_argument('format', help='The format of the OSeMOSYS model to validate')
    valid_parser.add_argument('filepath', help='Path to the OSeMOSYS model to validate')
    valid_parser.add_argument('--config', help='Path to a user-defined validation-config file')
    valid_parser.set_defaults(func=validate_model)

    # Parser for visualisation
    viz_parser = subparsers.add_parser('viz', help='Visualise the model')
    viz_subparsers = viz_parser.add_subparsers()

    res_parser = viz_subparsers.add_parser('res', help='Generate a reference energy system')
    res_parser.add_argument('datapackage', help='Path to model datapackage')
    res_parser.add_argument('resfile', help='Path to reference energy system')
    res_parser.set_defaults(func=datapackage2res)

    return parser


def main():

    parser = get_parser()
    args = parser.parse_args(sys.argv[1:])

    if args.verbose >= 1 and args.verbose < 2:
        logging.basicConfig(level=logging.INFO)
    if args.verbose > 2:
        logging.basicConfig(level=logging.DEBUG)

    if 'func' in args:
        args.func(args)
    else:
        parser.print_help()
