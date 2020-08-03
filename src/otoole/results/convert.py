"""Converts an OSeMOSYS solution file from CPLEX, CBC or GLPK into CBC or CSV format

"""
import argparse
import logging
import os
from typing import Dict, List, Optional, Tuple

import pandas as pd

from otoole import read_packaged_file
from otoole.read_strategies import ReadDatafile, ReadDatapackage
from otoole.results.result_package import ResultsPackage

LOGGER = logging.getLogger(__name__)


class ConvertLine(object):
    """Abstract class which defines the interface to the family of convertors

    Inherit this class and implement the ``_do_it()`` method to produce the
    data to be written out into a new format

    Example
    -------
    >>> cplex_line = "AnnualCost	REGION	CDBACKSTOP	1.0	0.0	137958.8400384134"
    >>> convertor = RegionTechnology()
    >>> convertor.convert()
    VariableName(REGION,TECHCODE01,2015)       42.69         0\\n
    VariableName(REGION,TECHCODE01,2017)       137958.84         0\\n
    """

    def __init__(self, data: List, start_year: int, end_year: int, output_format="cbc"):
        self.data = data
        self.start_year = start_year
        self.end_year = end_year
        self.output_format = output_format

    def _do_it(self) -> Tuple:
        raise NotImplementedError()

    def convert(self) -> List[str]:
        if self.output_format == "cbc":
            convert = self.convert_cbc()
        elif self.output_format == "csv":
            convert = self.convert_csv()
        return convert

    def convert_csv(self) -> List[str]:
        """Format the data for writing to a csv file
        """
        data = []
        variable, dimensions, values = self._do_it()

        for index, value in enumerate(values):

            year = self.start_year + index
            if (value not in ["0.0", "0", ""]) and (year <= self.end_year):

                try:
                    value = float(value)
                except ValueError:
                    value = 0

                full_dims = ",".join(dimensions + (str(year),))

                formatted_data = '{0},"{1}",{2}\n'.format(variable, full_dims, value)

                data.append(formatted_data)

        return data

    def convert_cbc(self) -> List[str]:
        """Format the data for writing to a CBC file
        """
        cbc_data = []
        variable, dimensions, values = self._do_it()

        for index, value in enumerate(values):

            year = self.start_year + index
            if (value not in ["0.0", "0", ""]) and (year <= self.end_year):

                try:
                    value = float(value)
                except ValueError:
                    value = 0

                full_dims = ",".join(dimensions + (str(year),))

                formatted_data = "0 {0}({1}) {2} 0\n".format(variable, full_dims, value)

                cbc_data.append(formatted_data)

        return cbc_data


class RegionTimeSliceTechnologyMode(ConvertLine):
    def _do_it(self) -> Tuple:
        """Produces output indexed by Region, Timeslice, Tech and Mode

        ``0 VariableName(REGION,SD1D,TECHCODE01,2,2015) 42.69 0\n``

        """
        variable = self.data[0]
        region = self.data[1]
        timeslice = self.data[2]
        technology = self.data[3]
        mode = self.data[4]
        values = self.data[5:]

        dimensions = (region, timeslice, technology, mode)

        return (variable, dimensions, values)


class RegionTechnology(ConvertLine):
    def _do_it(self) -> Tuple:
        """Produces output indexed by dimensions Region and Technology

        ``0 VariableName(REGION,TECHCODE01,2015) 42.69 0\n``

        """
        variable = self.data[0]
        region = self.data[1]
        technology = self.data[2]

        dimensions = (region, technology)

        values = self.data[3:]

        return (variable, dimensions, values)


def process_line(
    line: str, start_year: int, end_year: int, output_format: str
) -> List[str]:
    """Processes an individual line in a CPLEX file

    A different ConvertLine implementation is chosen depending upon the
    variable name

    Arguments
    ---------
    line: str
    start_year: int
    end_year: int
    output_format: str
        The file format required - either ``csv`` or ``cbc``
    """
    row_as_list = line.split("\t")
    variable = row_as_list[0]
    if variable in [
        "NewCapacity",
        "TotalCapacityAnnual",
        "CapitalInvestment",
        "AnnualFixedOperatingCost",
        "AnnualVariableOperatingCost",
    ]:
        convertor = RegionTechnology(
            row_as_list, start_year, end_year, output_format
        ).convert()
    elif variable in ["RateOfActivity"]:
        convertor = RegionTimeSliceTechnologyMode(
            row_as_list, start_year, end_year, output_format
        ).convert()
    else:
        convertor = []

    return convertor


def convert_cplex_file(
    cplex_filename: str,
    output_filename: str,
    start_year=2015,
    end_year=2070,
    output_format="cbc",
):
    """Converts a CPLEX solution file into that of the CBC solution file

    Arguments
    ---------
    cplex_filename : str
        Path to the transformed CPLEX solution file
    output_filename : str
        Path for the processed data to be written to
    """

    with open(output_filename, "w") as cbc_file:
        with open(cplex_filename, "r") as cplex_file:
            for linenum, line in enumerate(cplex_file):
                try:
                    convertor = process_line(line, start_year, end_year, output_format)
                    if convertor:
                        cbc_file.writelines(convertor)
                except ValueError:
                    msg = "Error caused at line {}: {}"
                    raise ValueError(msg.format(linenum, line))


def convert_cbc_to_dataframe(data_file: str) -> pd.DataFrame:
    """Reads a CBC solution file into a pandas DataFrame

    Arguments
    ---------
    data_file : str
    """
    df = pd.read_csv(
        data_file,
        header=None,
        names=["temp", "VALUE"],
        delim_whitespace=True,
        skiprows=1,
        usecols=[1, 2],
    )  # type: pd.DataFrame
    df.columns = ["temp", "Value"]
    df[["Variable", "Index"]] = df["temp"].str.split("(", expand=True)
    df = df.drop("temp", axis=1)
    df["Index"] = df["Index"].str.replace(")", "")
    return df[["Variable", "Index", "Value"]]


def convert_dataframe_to_csv(
    data: pd.DataFrame, input_data: Optional[Dict[str, pd.DataFrame]] = None
) -> Dict[str, pd.DataFrame]:
    """Convert from dataframe to csv

    Converts a pandas DataFrame containing all CBC results to reformatted
    dictionary of pandas DataFrames in long format ready to write out as
    csv files

    Arguments
    ---------
    data : pandas.DataFrame
        CBC results stored in a dataframe
    input_data_path : str, default=None
        Path to the OSeMOSYS data file containing input data

    Example
    -------
    >>> df = pd.DataFrame(data=[
            ['TotalDiscountedCost', "SIMPLICITY,2015", 187.01576],
            ['TotalDiscountedCost', "SIMPLICITY,2016", 183.30788]],
            columns=['Variable', 'Index', 'Value'])
    >>> convert_dataframe_to_csv(df)
    {'TotalDiscountedCost':        REGION  YEAR      VALUE
                                0  SIMPLICITY  2015  187.01576
                                1  SIMPLICITY  2016  183.30788}
    """
    input_config = read_packaged_file("config.yaml", "otoole.preprocess")
    results_config = read_packaged_file("config.yaml", "otoole.results")

    sets = {x: y for x, y in input_config.items() if y["type"] == "set"}

    results = {}  # type: Dict[str, pd.DataFrame]

    not_found = []

    for name, details in results_config.items():
        df = data[data["Variable"] == name]

        if not df.empty:

            LOGGER.debug("Extracting results for %s", name)
            indices = details["indices"]

            df[indices] = df["Index"].str.split(",", expand=True)

            types = {index: sets[index]["dtype"] for index in indices}
            df = df.astype(types)

            df = df.drop(columns=["Variable", "Index"])

            df = df.rename(columns={"Value": "VALUE"})

            results[name] = df[indices + ["VALUE"]].set_index(indices)

        else:
            not_found.append(name)

    LOGGER.debug("Unable to find CBC variables for: %s", ", ".join(not_found))

    results_package = ResultsPackage(results, input_data)

    for name in not_found:

        LOGGER.info("Looking for %s", name)
        details = results_config[name]

        try:
            df = results_package[name]
        except KeyError as ex:
            LOGGER.info("No calculation method available for %s", name)
            LOGGER.debug("Error calculating %s: %s", name, str(ex))
            df = pd.DataFrame()

        if not df.empty:
            results[name] = df
        else:
            LOGGER.warning(
                "Calculation returned empty dataframe for parameter '%s'", name
            )

    return results


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

    df = convert_cbc_to_dataframe(from_file)
    csv = convert_dataframe_to_csv(df, input_data)
    write_csvs(to_file, csv)


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
