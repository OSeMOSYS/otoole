"""Provides a command line interface to the ``otoole`` package

Example
-------
>>> otoole --help
usage: otoole [-h] [--verbose] [--version] {prep,convert,cplex,viz} ...

otoole: Python toolkit of OSeMOSYS users

positional arguments:
  {prep,convert,cplex,viz}
    prep                Prepare an OSeMOSYS datafile
    convert             Convert from one input format to another
    cplex               Process a CPLEX solution file
    viz                 Visualise the model

optional arguments:
  -h, --help            show this help message and exit
  --verbose, -v         Enable debug mode
  --version, -V         The version of otoole

"""
import argparse
import logging
import sys

from otoole import __version__
from otoole.preprocess import convert_file_to_package, create_datafile, create_datapackage, generate_csv_from_excel
from otoole.results.convert import convert_cplex_file
from otoole.visualise import create_res


def excel2csv(args):
    generate_csv_from_excel(args.workbook, args.output_folder)


def csv2datapackage(args):
    create_datapackage(args.csv_folder, args.datapackage)


def cplex2cbc(args):
    convert_cplex_file(args.cplex_file, args.output_file, args.start_year,
                       args.end_year, args.output_format)


def datapackage2datafile(args):
    create_datafile(args.datapackage, args.datafile)


def conversion_matrix(args):
    if (args.convert_from == 'datafile') and (args.convert_to == 'datapackage'):
        convert_file_to_package(args.from_file, args.to_file)
    else:
        msg = "Conversion from {} to {} is not yet implemented".format(args.convert_from, args.convert_to)
        raise NotImplementedError(msg)


def datapackage2res(args):
    create_res(args.datapackage, args.resfile)


def get_parser():
    parser = argparse.ArgumentParser(description="otoole: Python toolkit of OSeMOSYS users")

    parser.add_argument('--verbose', '-v', help='Enable debug mode', action='count', default=0)
    parser.add_argument('--version', '-V', action='version', version=__version__,
                        help='The version of otoole')

    subparsers = parser.add_subparsers()

    # Parser for pre-processing related commands
    prep_parser = subparsers.add_parser('prep', help='Prepare an OSeMOSYS datafile')
    prep_subparsers = prep_parser.add_subparsers()

    excel_parser = prep_subparsers.add_parser('excel', help='Convert from an Excel workbook')
    excel_parser.add_argument('workbook', help='Path to the Excel workbook')
    excel_parser.add_argument('output_folder', help='Folder to which to write csv files')
    excel_parser.set_defaults(func=excel2csv)

    datapackage_parser = prep_subparsers.add_parser('datapackage',
                                                    help='Convert a folder of csv file to a datapackage')
    datapackage_parser.add_argument('csv_folder', help='Path to folder containing csv files')
    datapackage_parser.add_argument('datapackage', help='Path to destination for datapackage')
    datapackage_parser.set_defaults(func=csv2datapackage)

    datafile_parser = prep_subparsers.add_parser('datafile',
                                                 help='Convert an OSeMOSYS datapackage to a datafile')
    datafile_parser.add_argument('datapackage', help='Path to destination for datapackage')
    datafile_parser.add_argument('datafile', help='Path to datafile')
    datafile_parser.set_defaults(func=datapackage2datafile)

    # Parser for conversion
    convert_parser = subparsers.add_parser('convert', help='Convert from one input format to another')
    convert_parser.add_argument('--convert_from', '-f', help='Input data format to convert from')
    convert_parser.add_argument('--convert_to', '-t', help='Input data format to convert to')
    convert_parser.add_argument('--from_file', help="Path to file to convert from")
    convert_parser.add_argument('--to_file', help='Path to file to convert to')
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
