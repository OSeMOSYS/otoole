"""Provides a command line interface to the ``otoole`` package

Example
-------
>>> otoole --help
usage: otoole [-h] [-v] {prep,cplex} ...

otoole: Python toolkit of OSeMOSYS users

positional arguments:
  {prep,cplex}
    prep        Prepare an OSeMOSYS datafile
    cplex       Process a CPLEX solution file

optional arguments:
  -h, --help    show this help message and exit
  -v            Enable debug mode

"""
import argparse
import logging
import sys

from otoole.preprocess import create_datafile, create_datapackage, generate_csv_from_excel
from otoole.results.convert import convert_cplex_file


def excel2csv(args):
    generate_csv_from_excel(args.workbook, args.output_folder)


def csv2datapackage(args):
    create_datapackage(args.csv_folder, args.datapackage)


def cplex2cbc(args):
    convert_cplex_file(args.cplex_file, args.output_file, args.start_year,
                       args.end_year, args.output_format)


def datapackage2datafile(args):
    create_datafile(args.datapackage, args.datafile)


def get_parser():
    parser = argparse.ArgumentParser(description="otoole: Python toolkit of OSeMOSYS users")

    parser.add_argument('-v', help='Enable debug mode', action='store_true')

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
    return parser


def main():

    logging.basicConfig(filename='myapp.log', level=logging.DEBUG, filemode='w')
    logging.info('Started')
    parser = get_parser()
    args = parser.parse_args(sys.argv[1:])

    if args.v:
        logging.basicConfig(filename='myapp.log', level=logging.DEBUG, filemode='a')

    if 'func' in args:
        args.func(args)
    else:
        parser.print_help()
    logging.info('Finished')
