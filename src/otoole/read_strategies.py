import logging
import os
from typing import Any, Dict, List, Tuple

import pandas as pd
from amply import Amply
from flatten_dict import flatten
from pandas_datapackage_reader import read_datapackage

from otoole.input import ReadStrategy
from otoole.preprocess.longify_data import check_datatypes, check_set_datatype

logger = logging.getLogger(__name__)


EXCEL_TO_CSV = {
    "TotalAnnualMaxCapacityInvestmen": "TotalAnnualMaxCapacityInvestment",
    "TotalAnnualMinCapacityInvestmen": "TotalAnnualMinCapacityInvestment",
    "TotalTechnologyAnnualActivityLo": "TotalTechnologyAnnualActivityLowerLimit",
    "TotalTechnologyAnnualActivityUp": "TotalTechnologyAnnualActivityUpperLimit",
    "TotalTechnologyModelPeriodActLo": "TotalTechnologyModelPeriodActivityLowerLimit",
    "TotalTechnologyModelPeriodActUp": "TotalTechnologyModelPeriodActivityUpperLimit",
}

CSV_TO_EXCEL = {v: k for k, v in EXCEL_TO_CSV.items()}


class ReadTabular(ReadStrategy):
    def _check_set(self, df, config_details, name):

        logger.info("Checking set %s", name)
        narrow = df

        return narrow

    def _check_parameter(self, df, config_details, name):
        actual_headers = df.columns
        expected_headers = config_details["indices"]
        logger.debug("Expected headers for %s: %s", name, expected_headers)

        if "REGION" in expected_headers and "REGION" not in actual_headers:
            logger.info("Added 'REGION' column to %s", name)
            df["REGION"] = "SIMPLICITY"

        if "MODEOFOPERATION" in actual_headers:
            df = df.rename(columns={"MODEOFOPERATION": "MODE_OF_OPERATION"})

        if actual_headers[-1] == "VALUE":
            logger.info(
                "%s is already in narrow form with headers %s", name, df.columns
            )
            narrow = df
        else:
            try:
                narrow = pd.melt(
                    df,
                    id_vars=expected_headers[:-1],
                    var_name=expected_headers[-1],
                    value_name="VALUE",
                )
            except IndexError as ex:
                logger.debug(df.columns)
                raise ex

        expected_headers.append("VALUE")
        for column in expected_headers:
            if column not in narrow.columns:
                logger.warning("%s not in header of %s", column, name)

        logger.debug("Final expected headers for %s: %s", name, expected_headers)

        return narrow[expected_headers]


class ReadExcel(ReadTabular):
    """Read in an Excel spreadsheet in wide format to a dict of Pandas DataFrames
    """

    def read(self, filepath) -> Tuple[Dict[str, pd.DataFrame], Dict[str, Any]]:

        config = self.config
        default_values = self._read_default_values(config)

        xl = pd.ExcelFile(filepath)

        input_data = {}

        for name in xl.sheet_names:

            try:
                mod_name = EXCEL_TO_CSV[name]
            except KeyError:
                mod_name = name

            config_details = config[mod_name]

            df = xl.parse(name)

            entity_type = config[mod_name]["type"]

            if entity_type == "param":
                narrow = self._check_parameter(df, config_details, mod_name)
                if not narrow.empty:
                    narrow_checked = check_datatypes(narrow, config, mod_name)
                else:
                    narrow_checked = narrow
            elif entity_type == "set":
                narrow = self._check_set(df, config_details, mod_name)
                if not narrow.empty:
                    narrow_checked = check_set_datatype(narrow, config, mod_name)
                else:
                    narrow_checked = narrow

            input_data[mod_name] = narrow_checked

        return input_data, default_values


class ReadCsv(ReadTabular):
    """Read in a folder of CSV files"""

    def read(self, filepath) -> Tuple[Dict[str, pd.DataFrame], Dict[str, Any]]:

        input_data = {}

        default_values = self._read_default_values(self.config)

        for parameter, details in self.config.items():
            logger.info("Looking for %s", parameter)
            config_details = self.config[parameter]

            csv_path = os.path.join(filepath, parameter + ".csv")

            try:
                df = pd.read_csv(csv_path)
            except pd.errors.EmptyDataError:
                logger.error("No data found in file for %s", parameter)
                expected_columns = config_details["indices"]
                default_columns = expected_columns + ["VALUE"]
                df = pd.DataFrame(columns=default_columns)

            entity_type = self.config[parameter]["type"]

            if entity_type == "param":
                narrow = self._check_parameter(df, config_details, parameter)
                if not narrow.empty:
                    narrow_checked = check_datatypes(narrow, self.config, parameter)
                else:
                    narrow_checked = narrow
            elif entity_type == "set":
                narrow = self._check_set(df, config_details, parameter)
                if not narrow.empty:
                    narrow_checked = check_set_datatype(narrow, self.config, parameter)
                else:
                    narrow_checked = narrow

            input_data[parameter] = narrow_checked

        return input_data, default_values


class ReadDatapackage(ReadStrategy):
    def read(self, filepath) -> Tuple[Dict[str, pd.DataFrame], Dict[str, Any]]:
        inputs = read_datapackage(filepath)
        default_resource = inputs.pop("default_values").set_index("name").to_dict()
        default_values = default_resource["default_value"]
        return inputs, default_values


class ReadDatafile(ReadStrategy):
    def read(self, filepath) -> Tuple[Dict[str, pd.DataFrame], Dict[str, Any]]:

        config = self.config
        default_values = self._read_default_values(config)
        amply_datafile = self.read_in_datafile(filepath, config)
        inputs = self._convert_amply_to_dataframe(amply_datafile, config)

        return inputs, default_values

    def read_in_datafile(self, path_to_datafile: str, config: Dict) -> Amply:
        """Read in a datafile using the Amply parsing class

        Arguments
        ---------
        path_to_datafile: str
        config: Dict
        """
        parameter_definitions = self._load_parameter_definitions(config)
        datafile_parser = Amply(parameter_definitions)
        logger.debug(datafile_parser)

        with open(path_to_datafile, "r") as datafile:
            datafile_parser.load_file(datafile)

        return datafile_parser

    def _load_parameter_definitions(self, config: dict) -> str:
        """Load the set and parameter dimensions into datafile parser

        Returns
        -------
        str
        """
        elements = ""

        for name, attributes in config.items():
            if attributes["type"] == "param":
                elements += "param {} {};\n".format(
                    name, "{" + ",".join(attributes["indices"]) + "}"
                )
            elif attributes["type"] == "symbolic":
                elements += "param {0} symbolic := '{1}' ;\n".format(
                    name, attributes["default"]
                )
            elif attributes["type"] == "set":
                elements += "set {};\n".format(name)

        logger.debug(elements)
        return elements

    def _convert_amply_to_dataframe(
        self, datafile_parser: Amply, config: Dict
    ) -> Dict[str, pd.DataFrame]:
        """Converts an amply parser to a dict of pandas dataframes

        Arguments
        ---------
        datafile_parser : Amply
        config : Dict

        Returns
        -------
        dict of pandas.DataFrame
        """

        dict_of_dataframes = {}

        for name in datafile_parser.symbols.keys():
            logger.debug("Extracting data for %s", name)
            if config[name]["type"] == "param":
                indices = config[name]["indices"]
                indices_dtypes = [config[index]["dtype"] for index in indices]
                indices.append("VALUE")
                indices_dtypes.append("float")

                raw_data = datafile_parser[name].data
                data = self._convert_amply_data_to_list(raw_data)
                df = pd.DataFrame(data=data, columns=indices)
                try:
                    dict_of_dataframes[name] = check_datatypes(df, config, name)
                except ValueError as ex:
                    msg = "Validation error when checking datatype of {}: {}".format(
                        name, str(ex)
                    )
                    raise ValueError(msg)
            elif config[name]["type"] == "set":
                data = datafile_parser[name].data
                logger.debug(data)

                indices = ["VALUE"]
                df = pd.DataFrame(
                    data=data, columns=indices, dtype=config[name]["dtype"]
                )
                dict_of_dataframes[name] = check_set_datatype(df, config, name)
            logger.debug("\n%s\n", dict_of_dataframes[name])

        return dict_of_dataframes

    def _convert_amply_data_to_list(self, amply_data: Dict) -> List[List]:
        """Flattens a dictionary into a list of lists

        Arguments
        ---------
        amply_data: dict
        """

        data = []

        raw_data = flatten(amply_data)
        for key, value in raw_data.items():
            data.append(list(key) + [value])

        return data
