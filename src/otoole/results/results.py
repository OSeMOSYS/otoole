import logging
from abc import abstractmethod
from io import StringIO
from typing import Any, Dict, TextIO, Tuple, Union

import pandas as pd

from otoole.input import ReadStrategy
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
            A path name or file buffer pointing to the solution file
        input_data : dict, default=None
            dict of dataframes

        Returns
        -------
        tuple
            A tuple containing dict of pandas.DataFrames and a dict of default_values

        """
        if "input_data" in kwargs:
            input_data = kwargs["input_data"]
            param_default_values = self._read_default_values(self.input_config)
        else:
            input_data = {}
            param_default_values = {}

        available_results = self.get_results_from_file(
            filepath, input_data
        )  # type: Dict[str, pd.DataFrame]

        default_values = self._read_default_values(self.results_config)  # type: Dict

        input_data = self._expand_required_params(input_data, param_default_values)

        results = self.calculate_results(
            available_results, input_data
        )  # type: Dict[str, pd.DataFrame]

        if self.write_defaults:
            results = self.write_default_results(results, input_data, default_values)

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

    def _expand_required_params(
        self,
        input_data: dict[str, pd.DataFrame],
        param_defaults: dict[str, Any],
    ) -> dict[str, pd.DataFrame]:
        """Expands required default values for results processing"""

        if "DiscountRate" in input_data:
            input_data["DiscountRate"] = self._expand_dataframe(
                "DiscountRate", input_data, param_defaults
            )
        if "DiscountRateIdv" in input_data:
            input_data["DiscountRateIdv"] = self._expand_dataframe(
                "DiscountRateIdv", input_data, param_defaults
            )

        return input_data


class ReadWideResults(ReadResults):
    def get_results_from_file(self, filepath, input_data):
        cbc = self._convert_to_dataframe(filepath)
        available_results = self._convert_wide_to_long(cbc)
        return available_results

    @abstractmethod
    def _convert_to_dataframe(self, file_path: Union[str, TextIO]) -> pd.DataFrame:
        raise NotImplementedError()

    def _convert_wide_to_long(self, data: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Convert from wide to long format

        Converts a pandas DataFrame containing all wide format results to reformatted
        dictionary of pandas DataFrames in long format ready to write out

        Arguments
        ---------
        data : pandas.DataFrame
            results stored in a dataframe

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

        sets = {x: y for x, y in self.user_config.items() if y["type"] == "set"}

        results = {}  # type: Dict[str, pd.DataFrame]
        not_found = []

        for name, details in sorted(self.results_config.items()):
            df_cbc = data[data["Variable"] == name]

            if not df_cbc.empty:

                df = df_cbc.copy()  # setting with copy warning
                LOGGER.debug("Extracting results for %s", name)
                indices = details["indices"]  # typing: List

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


def check_duplicate_index(df: pd.DataFrame, columns: list, index: list) -> pd.DataFrame:
    """Catches pandas error when there are duplicate column indices"""
    if check_for_duplicates(index):
        index = rename_duplicate_column(index)
        LOGGER.debug("Original column names: %s", columns)
        renamed_columns = rename_duplicate_column(columns)
        LOGGER.debug("New column names: %s", renamed_columns)
        df.columns = renamed_columns
    return df, index


def check_for_duplicates(index: list) -> bool:
    return len(set(index)) != len(index)


def identify_duplicate(index: list) -> Union[int, bool]:
    elements = set()  # type: set
    for counter, elem in enumerate(index):
        if elem in elements:
            return counter
        else:
            elements.add(elem)
    return False


def rename_duplicate_column(index: list) -> list:
    column = index.copy()
    location = identify_duplicate(column)
    if location:
        column[location] = "_" + column[location]
    return column


class ReadCplex(ReadWideResults):
    """Read a CPLEX solution file into memeory"""

    def _convert_to_dataframe(self, file_path: Union[str, TextIO]) -> pd.DataFrame:
        """Reads a Cplex solution file into a pandas DataFrame

        Arguments
        ---------
        user_config : Dict[str, Dict]
        file_path : Union[str, TextIO]
        """
        df = pd.read_xml(file_path, xpath=".//variable", parser="etree")
        df[["Variable", "Index"]] = df["name"].str.split("(", expand=True)
        df["Index"] = df["Index"].str.replace(")", "", regex=False)
        LOGGER.debug(df)
        df = df[(df["value"] != 0)].reset_index().rename(columns={"value": "Value"})
        return df[["Variable", "Index", "Value"]].astype({"Value": float})


class ReadGurobi(ReadWideResults):
    """Read a Gurobi solution file into memory"""

    def _convert_to_dataframe(self, file_path: Union[str, TextIO]) -> pd.DataFrame:
        """Reads a Gurobi solution file into a pandas DataFrame

        Arguments
        ---------
        user_config : Dict[str, Dict]
        file_path : Union[str, TextIO]
        """
        df = pd.read_csv(
            file_path,
            header=None,
            sep=" ",
            names=["Variable", "Value"],
            skiprows=2,
        )  # type: pd.DataFrame
        df[["Variable", "Index"]] = df["Variable"].str.split("(", expand=True)
        df["Index"] = df["Index"].str.replace(")", "", regex=False)
        LOGGER.debug(df)
        df = df[(df["Value"] != 0)].reset_index()
        return df[["Variable", "Index", "Value"]].astype({"Value": float})


class ReadCbc(ReadWideResults):
    """Read a CBC solution file into memory"""

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
            .str.replace(r"^\*\*", "", regex=True)
            .str.split(expand=True)[1]
        )
        df[["Index", "Value"]] = df["indexvalue"].str.split(expand=True).loc[:, 0:1]
        df["Index"] = df["Index"].str.replace(")", "", regex=False)
        df = df.drop(columns=["indexvalue"])
        return df[["Variable", "Index", "Value"]].astype({"Value": float})


class ReadHighs(ReadWideResults):
    """Read a HiGHS solution file into memory"""

    def _convert_to_dataframe(self, file_path: Union[str, TextIO]) -> pd.DataFrame:
        """Reads a HiGHS solution file into a pandas DataFrame

        Arguments
        ---------
        file_path : str
        """
        df = pd.read_csv(
            file_path,
            sep=r"\s+",
            skiprows=1,
            index_col=0,
            dtype=str,
        )

        # Type column is not garunteed in the the model output
        # retain conditional as filtering on type is more explicit
        if "Type" in df.columns:
            var_types = ["Continuous", "Integer", "SemiContinuous", "SemiInteger"]
            df = df[df.Type.isin(var_types)].copy()
        else:
            df = df.reset_index()
            row = df[df.Index == "Rows"].index[0]
            df = df.iloc[:row].set_index("Index")

        df.index.name = ""  # remove the name Index, as otoole uses that

        df[["Variable", "Index"]] = df["Name"].str.split("(", expand=True).loc[:, 0:1]
        df["Index"] = df["Index"].str.replace(")", "", regex=False)
        df = df[~(df.Primal.astype(float).abs() < 1e-6)]
        return (
            df[["Variable", "Index", "Primal"]]
            .rename(columns={"Primal": "Value"})
            .reset_index(drop=True)
            .astype({"Variable": str, "Index": str, "Value": float})
        )


class ReadGlpk(ReadWideResults):
    """Reads a GLPK Solution file into memory

    Arguments
    ---------
    user_config : Dict[str, Dict]
    glpk_model: Union[str, TextIO]
        Path to GLPK model file. Can be created using the `--wglp` flag.
    """

    def __init__(
        self,
        user_config: Dict[str, Dict],
        glpk_model: Union[str, TextIO],
        write_defaults: bool = False,
    ):
        super().__init__(user_config=user_config, write_defaults=write_defaults)

        if isinstance(glpk_model, str):
            with open(glpk_model, "r") as model_file:
                self.model = self.read_model(model_file)
        elif isinstance(glpk_model, StringIO):
            self.model = self.read_model(glpk_model)
        else:
            raise TypeError("Argument filepath type must be a string or an open file")

    def _convert_to_dataframe(self, glpk_sol: Union[str, TextIO]) -> pd.DataFrame:
        """Creates a wide formatted dataframe from GLPK solution

        Arguments
        ---------
        glpk_sol: Union[str, TextIO]
            Path to GLPK solution file. Can be created using the `--write` flag

        Returns
        -------
        pd.DataFrame
        """

        if isinstance(glpk_sol, str):
            with open(glpk_sol, "r"):
                _, sol = self.read_solution(glpk_sol)
        elif isinstance(glpk_sol, StringIO):
            _, sol = self.read_solution(glpk_sol)
        else:
            raise TypeError("Argument filepath type must be a string or an open file")

        return self._merge_model_sol(sol)

    def read_model(self, file_path: Union[str, TextIO]) -> pd.DataFrame:
        """Reads in a GLPK Model File

        Arguments
        ---------
        file_path: Union[str, TextIO]
            Path to GLPK model file. Can be created using the `--wglp` flag.

        Returns
        -------
        pd.DataFrame

           ID  NUM  NAME                      INDEX
        0  i   1    CAa4_Constraint_Capacity  "SIMPLICITY,ID,BACKSTOP1,2015"
        1  j   2    NewCapacity               "SIMPLICITY,WINDPOWER,2039"

        Notes
        -----

        -> GENERAL LAYOUT OF SOLUTION FILE

        n p NAME # p = problem instance
        n z NAME # z = objective function
        n i ROW NAME # i = constraint name, ROW is the row ordinal number
        n j COL NAME # j = variable name, COL is the column ordinal number
        """

        df = pd.read_csv(
            file_path,
            header=None,
            sep=r"\s+",
            index_col=0,
            names=["ID", "NUM", "value", 4, 5],
        ).drop(columns=[4, 5])

        df = df[(df["ID"].isin(["i", "j"])) & (df["value"] != "cost")]

        df[["NAME", "INDEX"]] = df["value"].str.split("[", expand=True)
        df["INDEX"] = df["INDEX"].map(lambda x: x.split("]")[0])
        df = (
            df[["ID", "NUM", "NAME", "INDEX"]]
            .astype({"ID": str, "NUM": "int64", "NAME": str, "INDEX": str})
            .reset_index(drop=True)
        )

        return df

    def read_solution(
        self, file_path: Union[str, TextIO]
    ) -> Tuple[Dict[str, Union[str, float]], pd.DataFrame]:
        """Reads a GLPK solution file

        Arguments
        ---------
        file_path: Union[str, TextIO]
            Path to GLPK solution file. Can be created using the `--write` flag

        Returns
        -------
        Tuple[Dict[str,Union[str, float]], pd.DataFrame]
            Dict[str,Union[str, float]] -> Problem name, status, and objective value
            pd.DataFrame -> Variables and constraints

        {"name":"osemosys", "status":"OPTIMAL", "objective":4497.31976}

           ID  NUM  STATUS PRIM DUAL
        0  i   1    b      5    0
        1  j   2    l      0    2

        Notes
        -----

        -> ROWS IN SOLUTION FILE

        i ROW ST PRIM DUAL

        ROW is the ordinal number of the row
        ST is one of:
        - b = inactive constraint;
        - l = inequality constraint active on its lower bound;
        - u = inequality constraint active on its upper bound;
        - f = active free (unounded) row;
        - s = active equality constraint.
        PRIM specifies the row primal value (float)
        DUAL specifies the row dual value (float)

        -> COLUMNS IN SOLUTION FILE

        j COL ST PRIM DUAL

        COL specifies the column ordinal number
        ST contains one of the following lower-case letters that specifies the column status in the basic solution:
        - b = basic variable
        - l = non-basic variable having its lower bound active
        - u = non-basic variable having its upper bound active
        - f = non-basic free (unbounded) variable
        - s = non-basic fixed variable.
        PRIM field contains column primal value (float)
        DUAL field contains the column dual value (float)
        """

        df = pd.read_csv(file_path, header=None, sep=":")

        # get status information
        status = {}
        df_status = df.loc[:8].set_index(0)
        status["name"] = df_status.loc["c Problem", 1].strip()
        status["status"] = df_status.loc["c Status", 1].strip()
        status["objective"] = float(df_status.loc["c Objective", 1].split()[2])

        # get solution infromation
        data = df.iloc[8:-1].copy()
        data[["ID", "NUM", "STATUS", "PRIM", "DUAL"]] = data[0].str.split(
            " ", expand=True
        )

        data = (
            data[["ID", "NUM", "STATUS", "PRIM", "DUAL"]]
            .astype(
                {"ID": str, "NUM": "int64", "STATUS": str, "PRIM": float, "DUAL": float}
            )
            .reset_index(drop=True)
        )

        return status, data

    def _merge_model_sol(self, sol: pd.DataFrame) -> pd.DataFrame:
        """Merges GLPK model and solution file into one dataframe

        Arguments
        ---------
        sol: pd.DataFrame
            see output from ReadGlpk.read_solution(...)

        Returns
        -------
        pd.DataFrame

        >>> pd.DataFrame(data=[
                ['TotalDiscountedCost', "SIMPLICITY,2015", 187.01576],
                ['TotalDiscountedCost', "SIMPLICITY,2016", 183.30788]],
                columns=['Variable', 'Index', 'Value'])
        """

        model = self.model.copy()
        model.index = model["ID"].str.cat(model["NUM"].astype(str))
        model = model.drop(columns=["ID", "NUM"])

        sol.index = sol["ID"].str.cat(sol["NUM"].astype(str))
        sol = sol.drop(columns=["ID", "NUM", "STATUS", "DUAL"])

        df = model.join(sol)
        df = (
            df[df.index.str.startswith("j")]
            .reset_index(drop=True)
            .rename(columns={"NAME": "Variable", "INDEX": "Index", "PRIM": "Value"})
        )

        return df
