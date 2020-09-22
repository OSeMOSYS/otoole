"""Converts an OSeMOSYS solution file from CPLEX, CBC or GLPK into CBC or CSV format

"""
import argparse
import logging
import os
from typing import Dict, Union

import pandas as pd

from otoole import Context, ReadCbc, WriteCsv
from otoole.read_strategies import ReadDatafile, ReadDatapackage
from otoole.results.results import ConvertLine

LOGGER = logging.getLogger(__name__)


def write_csvs(results_path: str, results: Dict[str, pd.DataFrame]):
    """Write out CSV files from CBC file

    Arguments
    ---------
    results_path : str
    results : dict
    """
    for name, df in results.items():
        filename = os.path.join(results_path, name + ".csv")

        if not os.path.exists(results_path):
            LOGGER.info("Creating new results folder at '%s'", results_path)
            os.makedirs(results_path, exist_ok=True)

        if not df.empty:
            df.to_csv(filename, index=True)
        else:
            LOGGER.warning("Result parameter %s is empty", name)


def convert_cbc_to_csv(
    from_file: str,
    to_file: str,
    input_data_path: str = None,
    input_data_format="datapackage",
):
    """

    Arguments
    ---------
    from_file: str
        CBC solution file
    to_file: str
        Path to directory in which CSV files will be written
    input_data_path: str
        Optional path to input data (required if using short or fast versions
        of OSeMOSYS)
    input_data_format : str, default='datapackage

    """
    if input_data_format == "datapackage" and input_data_path:
        input_data, _ = ReadDatapackage().read(input_data_path)
    elif input_data_format == "datafile" and input_data_path:
        input_data, _ = ReadDatafile().read(input_data_path)
    else:
        input_data = {}

    context = Context(ReadCbc(), WriteCsv())
    context.convert(from_file, to_file, kwargs={"input_data": input_data})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert OSeMOSYS CPLEX files into different formats"
    )
    parser.add_argument(
        "cplex_file", help="The filepath of the OSeMOSYS cplex output file"
    )
    parser.add_argument(
        "output_file", help="The filepath of the converted file that will be written"
    )
    parser.add_argument(
        "-s",
        "--start_year",
        type=int,
        default=2015,
        help="Output only the results from this year onwards",
    )
    parser.add_argument(
        "-e",
        "--end_year",
        type=int,
        default=2070,
        help="Output only the results upto and including this year",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--csv",
        action="store_true",
        help="Output file in comma-separated-values format",
    )
    group.add_argument(
        "--cbc", action="store_true", help="Output file in CBC format, (default option)"
    )

    args = parser.parse_args()

    if args.csv:
        output_format = "csv"
    else:
        output_format = "cbc"

    convert_cplex_file(
        args.cplex_file, args.output_file, args.start_year, args.end_year, output_format
    )
