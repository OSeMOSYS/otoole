import logging
from abc import abstractmethod
from typing import Any, Dict, List, Optional, Set, TextIO, Tuple, Union

import pandas as pd

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

        cbc = self._convert_to_dataframe(filepath)
        results = self._convert_dataframe_to_csv(cbc, input_data)
        default_values = self._read_default_values(self.results_config)
        return results, default_values

    @abstractmethod
    def _convert_to_dataframe(self, file_path: Union[str, TextIO]) -> pd.DataFrame:
        raise NotImplementedError()

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

        for name, details in sorted(results_config.items()):
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

        LOGGER.debug("Unable to find result variables for: %s", ", ".join(not_found))

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


class ReadCplex(ReadStrategy):
    """
    """

    def read(
        self, filepath: Union[str, TextIO], **kwargs
    ) -> Tuple[Dict[str, pd.DataFrame], Dict[str, Any]]:
        data = {}  # type: Dict

        if "input_data" in kwargs:
            input_data = kwargs["input_data"]
            years = input_data["YEAR"].values  # type: List
            start_year = int(years[0])
            end_year = int(years[-1])
        else:
            raise RuntimeError("To process CPLEX results please provide the input file")

        for linenum, line in enumerate(filepath):
            try:
                row_as_list = line.split("\t")
                name, df = self.convert_df(row_as_list, start_year, end_year,)

                if name in data:
                    data[name] = data[name].append(df)
                else:
                    data[name] = [df]

            except ValueError as ex:
                msg = "Error caused at line {}: {}. {}"
                raise ValueError(msg.format(linenum, line, ex))

        results = {}

        for name, contents in data.items():
            results[name] = pd.concat(contents)

        return results, self._read_default_values(self.results_config)

    def extract_variable_dimensions_values(self, data: List) -> Tuple[str, Tuple, List]:
        """Extracts useful information from a line of a results file
        """
        variable = data[0]
        number = len(self.results_config[variable]["indices"])
        dimensions = tuple(data[1:(number)])
        values = data[(number):]
        return (variable, dimensions, values)

    def convert_df(
        self, row_as_list: List, start_year: int, end_year: int
    ) -> Tuple[str, pd.DataFrame]:
        """Read the cplex line into a pandas DataFrame

        """
        variable, dimensions, values = self.extract_variable_dimensions_values(
            row_as_list
        )
        index = self.results_config[variable]["indices"]
        columns = index[:-1] + list(range(start_year, end_year + 1, 1))
        df = pd.DataFrame(data=[list(dimensions) + values], columns=columns).set_index(
            index[:-1]
        )
        df = df.melt(var_name="YEAR", value_name="VALUE", ignore_index=False)
        df = df.reset_index()
        df = check_datatypes(df, {**self.input_config, **self.results_config}, variable)
        df = df.set_index(index)
        df = df[(df != 0).any(axis=1)]
        return (variable, df)


class ReadGurobi(ReadResults):
    """Read a Gurobi solution file into memory
    """

    def _convert_to_dataframe(self, file_path: Union[str, TextIO]) -> pd.DataFrame:
        """Reads a Gurobi solution file into a pandas DataFrame

        Arguments
        ---------
        file_path : str
        """
        df = pd.read_csv(
            file_path, header=None, sep=" ", names=["Variable", "Value"], skiprows=2,
        )  # type: pd.DataFrame
        df[["Variable", "Index"]] = df["Variable"].str.split("(", expand=True)
        df["Index"] = df["Index"].str.replace(")", "")
        LOGGER.debug(df)
        df = df[(df["Value"] != 0)].reset_index()
        return df[["Variable", "Index", "Value"]].astype({"Value": float})


class ReadCbc(ReadResults):
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
