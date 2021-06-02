import logging
import pandas as pd
from abc import abstractmethod
from io import StringIO
from typing import Any, Dict, List, Set, TextIO, Tuple, Union

from otoole.input import ReadStrategy
from otoole.preprocess.longify_data import check_datatypes
from otoole.results.result_package import ResultsPackage

LOGGER = logging.getLogger(__name__)


class ReadResults(ReadStrategy):
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

        available_results = self.get_results_from_file(
            filepath, input_data
        )  # type: Dict[str, pd.DataFrame]
        results = self.calculate_results(
            available_results, input_data
        )  # type: Dict[str, pd.DataFrame]
        default_values = self._read_default_values(self.results_config)  # type: Dict
        return results, default_values

    @abstractmethod
    def get_results_from_file(self, filepath, input_data):
        raise NotImplementedError()

    def calculate_results(
        self,
        available_results: Dict[str, pd.DataFrame],
        input_data: Dict[str, pd.DataFrame],
    ) -> Dict[str, pd.DataFrame]:
        """Populates the results with calculated values using input data"""

        results = {}
        results_package = ResultsPackage(available_results, input_data)

        for name in sorted(self.results_config.keys()):

            LOGGER.info("Looking for %s", name)

            try:
                results[name] = results_package[name]
            except KeyError as ex:
                LOGGER.info("No calculation method available for %s", name)
                LOGGER.debug("Error calculating %s: %s", name, str(ex))

        return results


class ReadResultsCBC(ReadResults):
    def get_results_from_file(self, filepath, input_data):
        cbc = self._convert_to_dataframe(filepath)
        available_results = self._convert_wide_to_long(cbc)
        return available_results

    @abstractmethod
    def _convert_to_dataframe(self, file_path: Union[str, TextIO]) -> pd.DataFrame:
        raise NotImplementedError()

    def _convert_wide_to_long(self, data: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Convert from wide to long format

        Converts a pandas DataFrame containing all CBC results to reformatted
        dictionary of pandas DataFrames in long format ready to write out

        Arguments
        ---------
        data : pandas.DataFrame
            CBC results stored in a dataframe

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

        sets = {x: y for x, y in self.input_config.items() if y["type"] == "set"}

        results = {}  # type: Dict[str, pd.DataFrame]
        not_found = []

        for name, details in sorted(self.results_config.items()):
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
                df, index = check_duplicate_index(df, columns, index)
                results[name] = df.set_index(index)
            else:
                not_found.append(name)

        LOGGER.debug("Unable to find result variables for: %s", ", ".join(not_found))

        return results


def check_duplicate_index(df: pd.DataFrame, columns: List, index: List) -> pd.DataFrame:
    """Catches pandas error when there are duplicate column indices"""
    if check_for_duplicates(index):
        index = rename_duplicate_column(index)
        LOGGER.debug("Original column names: %s", columns)
        renamed_columns = rename_duplicate_column(columns)
        LOGGER.debug("New column names: %s", renamed_columns)
        df.columns = renamed_columns
    return df, index


def check_for_duplicates(index: List) -> bool:
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


class ReadCplex(ReadResults):
    """ """

    def get_results_from_file(
        self, filepath: Union[str, TextIO], input_data
    ) -> Dict[str, pd.DataFrame]:

        if input_data:
            years = input_data["YEAR"].values  # type: List
            start_year = int(years[0])
            end_year = int(years[-1])
        else:
            raise RuntimeError("To process CPLEX results please provide the input file")

        if isinstance(filepath, str):
            with open(filepath, "r") as sol_file:
                data = self.extract_rows(sol_file, start_year, end_year)
        elif isinstance(filepath, StringIO):
            data = self.extract_rows(filepath, start_year, end_year)
        else:
            raise TypeError("Argument filepath type must be a string or an open file")

        results = {}

        for name in data.keys():
            results[name] = self.convert_df(data[name], name, start_year, end_year)

        return results

    def extract_rows(
        self, sol_file: TextIO, start_year: int, end_year: int
    ) -> Dict[str, List[List[str]]]:
        """ """
        data = {}  # type: Dict[str, List[List[str]]]
        for linenum, line in enumerate(sol_file):
            line = line.replace("\n", "")
            try:
                row_as_list = line.split("\t")  # type: List[str]
                name = row_as_list[0]  # type: str

                if name in data.keys():
                    data[name].append(row_as_list)
                else:
                    data[name] = [row_as_list]
            except ValueError as ex:
                msg = "Error caused at line {}: {}. {}"
                raise ValueError(msg.format(linenum, line, ex))
        return data

    def extract_variable_dimensions_values(self, data: List) -> Tuple[str, Tuple, List]:
        """Extracts useful information from a line of a results file"""
        variable = data[0]
        try:
            number = len(self.results_config[variable]["indices"])
        except KeyError as ex:
            print(data)
            raise KeyError(ex)
        dimensions = tuple(data[1:(number)])
        values = data[(number):]
        return (variable, dimensions, values)

    def convert_df(
        self, data: List[List[str]], variable: str, start_year: int, end_year: int
    ) -> pd.DataFrame:
        """Read the cplex lines into a pandas DataFrame"""
        index = self.results_config[variable]["indices"]
        columns = ["variable"] + index[:-1] + list(range(start_year, end_year + 1, 1))
        df = pd.DataFrame(data=data, columns=columns)
        df, index = check_duplicate_index(df, columns, index)
        df = df.drop(columns="variable")

        LOGGER.debug(
            f"Attempting to set index for {variable} with columns {index[:-1]}"
        )
        try:
            df = df.set_index(index[:-1])
        except NotImplementedError as ex:
            LOGGER.error(f"Error setting index for {df.head()}")
            raise NotImplementedError(ex)
        df = df.melt(var_name="YEAR", value_name="VALUE", ignore_index=False)
        df = df.reset_index()
        df = check_datatypes(df, {**self.input_config, **self.results_config}, variable)
        df = df.set_index(index)
        df = df[(df != 0).any(axis=1)]
        return df


class ReadGurobi(ReadResultsCBC):
    """Read a Gurobi solution file into memory"""

    def _convert_to_dataframe(self, file_path: Union[str, TextIO]) -> pd.DataFrame:
        """Reads a Gurobi solution file into a pandas DataFrame

        Arguments
        ---------
        file_path : str
        """
        df = pd.read_csv(
            file_path,
            header=None,
            sep=" ",
            names=["Variable", "Value"],
            skiprows=2,
        )  # type: pd.DataFrame
        df[["Variable", "Index"]] = df["Variable"].str.split("(", expand=True)
        df["Index"] = df["Index"].str.replace(")", "")
        LOGGER.debug(df)
        df = df[(df["Value"] != 0)].reset_index()
        return df[["Variable", "Index", "Value"]].astype({"Value": float})


class ReadCbc(ReadResultsCBC):
    """Read a CBC solution file into memory

    Arguments
    ---------
    user_config
    results_config
    """

    def _convert_to_dataframe(self, file_path: Union[str, TextIO]) -> pd.DataFrame:
        """Reads a CBC solution file into a pandas DataFrame

        Arguments
        ---------
        file_path : str
        """
        df = pd.read_csv(
            file_path,
            header=None,
            sep="(",
            names=["Variable", "indexvalue"],
            skiprows=1,
        )  # type: pd.DataFrame
        if df["Variable"].astype(str).str.contains(r"^\*\*").any():
            LOGGER.warning(
                "CBC Solution File contains decision variables out of bounds. "
                + "You have an infeasible solution"
            )
        df["Variable"] = (
            df["Variable"]
            .astype(str)
            .str.replace(r"^\*\*", "")
            .str.split(expand=True)[1]
        )
        df[["Index", "Value"]] = df["indexvalue"].str.split(expand=True).loc[:, 0:1]
        df["Index"] = df["Index"].str.replace(")", "")
        df = df.drop(columns=["indexvalue"])
        return df[["Variable", "Index", "Value"]].astype({"Value": float})
