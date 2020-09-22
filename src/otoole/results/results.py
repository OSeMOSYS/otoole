import logging
from typing import Any, Dict, List, Optional, TextIO, Tuple, Union

import pandas as pd

from otoole.input import ReadStrategy
from otoole.results.result_package import ResultsPackage
from otoole.utils import read_packaged_file

# from tempfile import TemporaryFile
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
        self.results_config = read_packaged_file("config.yaml", "otoole.results")
        self.number = len(self.results_config[self.data[0]]["indices"])

    def _do_it(self) -> Tuple:
        variable = self.data[0]
        dimensions = tuple(self.data[1 : (self.number)])
        values = self.data[(self.number) :]
        return (variable, dimensions, values)

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


# class ReadCplex(ReadStrategy):
#     """
#     """

#     def read(self, filepath: str) -> Tuple[Dict[str, pd.DataFrame], Dict[str, Any]]:

#         with TemporaryFile("w") as output_file:
#             self._convert_cplex_file(filepath, output_file.name)

#     def _convert_cplex_file(
#         self,
#         cplex_filename: str,
#         output_filename: str,
#         start_year=2015,
#         end_year=2070,
#         output_format="cbc",
#     ):
#         """Converts a CPLEX solution file into that of the CBC solution file

#         Arguments
#         ---------
#         cplex_filename : str
#             Path to the transformed CPLEX solution file
#         output_filename : str
#             Path for the processed data to be written to
#         """
#         with open(output_filename, "w") as cbc_file:
#             with open(cplex_filename, "r") as cplex_file:
#                 for linenum, line in enumerate(cplex_file):
#                     try:
#                         row_as_list = line.split("\t")
#                         convertor = ConvertLine(
#                             row_as_list, start_year, end_year, output_format
#                         )
#                         if convertor:
#                             cbc_file.writelines(convertor.convert())
#                     except ValueError:
#                         msg = "Error caused at line {}: {}"
#                         raise ValueError(msg.format(linenum, line))


class ReadCbc(ReadStrategy):
    """Read a CBC solution file into memory

    Arguments
    ---------
    user_config
    results_config
    """

    def read(
        self, filepath: Union[str, TextIO], **kwargs
    ) -> Tuple[Dict[str, pd.DataFrame], Dict[str, Any]]:
        """Read a solution file from ``filepath`` and process using ``input_data``

        Arguments
        ---------
        filepath : str, TextIO
            A path name or file buffer pointing to the CBC solution file
        input_data : dict, default=None
            dict of dataframes

        Returns
        -------
        tuple
            A tuple containing dict of pandas.DataFrames and a dict of default_values

        """
        if "input_data" in kwargs:
            input_data = kwargs["input_data"]
        else:
            input_data = None

        cbc = self._convert_cbc_to_dataframe(filepath)
        results = self._convert_dataframe_to_csv(cbc, input_data)
        default_values = self._read_default_values(self.results_config)
        return results, default_values

    def _convert_cbc_to_dataframe(self, file_path: Union[str, TextIO]) -> pd.DataFrame:
        """Reads a CBC solution file into a pandas DataFrame

        Arguments
        ---------
        file_path : str
        """
        df = pd.read_csv(
            file_path,
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

    def _convert_dataframe_to_csv(
        self, data: pd.DataFrame, input_data: Optional[Dict[str, pd.DataFrame]] = None
    ) -> Dict[str, pd.DataFrame]:
        """Convert from dataframe to long format

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
        input_config = self.input_config
        results_config = self.results_config

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

                columns = indices + ["VALUE"]

                df = df[columns]

                index = details["indices"].copy()
                # catches pandas error when there are duplicate column indices
                if check_duplicate_index(index):
                    index = rename_duplicate_column(index)
                    LOGGER.debug("Original column names: %s", columns)
                    renamed_columns = rename_duplicate_column(columns)
                    LOGGER.debug("New column names: %s", renamed_columns)
                    df.columns = renamed_columns
                results[name] = df.set_index(index)
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


def check_duplicate_index(index: List) -> bool:
    return len(set(index)) != len(index)


def identify_duplicate(index: List) -> Union[int, bool]:
    elements = set()  # type: Set
    for counter, elem in enumerate(index):
        if elem in elements:
            return counter
        else:
            elements.add(elem)
    return False


def rename_duplicate_column(index: List) -> List:
    column = index.copy()
    location = identify_duplicate(column)
    if location:
        column[location] = "_" + column[location]
    return column