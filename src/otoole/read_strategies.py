import logging
import os
from typing import Any, Dict, List, Optional, TextIO, Tuple, Union

import pandas as pd
from amply import Amply
from flatten_dict import flatten
from pandas_datapackage_reader import read_datapackage

from otoole.input import ReadStrategy
from otoole.preprocess.longify_data import check_datatypes, check_set_datatype
from otoole.utils import read_datapackage_schema_into_config

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


class ReadMemory(ReadStrategy):
    """Read a dict of OSeMOSYS parameters from memory
    """

    def __init__(
        self, parameters: Dict[str, pd.DataFrame], user_config: Optional[Dict] = None
    ):
        super().__init__(user_config)
        self._parameters = parameters

    def read(
        self, filepath: Union[str, TextIO] = None, **kwargs
    ) -> Tuple[Dict[str, pd.DataFrame], Dict[str, Any]]:

        config = self.input_config
        default_values = self._read_default_values(config)
        self._parameters = self._check_index(self._parameters)
        return self._parameters, default_values


class _ReadTabular(ReadStrategy):
    def _check_set(self, df: pd.DataFrame, config_details: Dict, name: str):

        logger.info("Checking set %s", name)
        narrow = df

        return narrow

    def _check_parameter(self, df: pd.DataFrame, expected_headers: List, name: str):
        """Converts a dataframe from wide to narrow format

        Arguments
        ---------
        df: pd.DataFrame
        expected_headers: List
        name: str
        """
        actual_headers = df.columns
        logger.debug("Expected headers for %s: %s", name, expected_headers)

        if "REGION" in expected_headers and "REGION" not in actual_headers:
            raise ValueError("No REGION column provided for %s", name)

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
                    var_name=expected_headers[-1],  # Normally 'YEAR'
                    value_name="new_VALUE",
                )
                narrow = narrow.rename(columns={"new_VALUE": "VALUE"})
            except IndexError as ex:
                logger.debug("Could not reshape %s", df.columns)
                raise ex

        all_headers = expected_headers + ["VALUE"]
        for column in all_headers:
            if column not in narrow.columns:
                logger.warning("%s not in header of %s", column, name)

        logger.debug("Final all headers for %s: %s", name, all_headers)

        return narrow[all_headers].set_index(expected_headers)


class ReadExcel(_ReadTabular):
    """Read in an Excel spreadsheet in wide format to a dict of Pandas DataFrames
    """

    def read(
        self, filepath: Union[str, TextIO], **kwargs
    ) -> Tuple[Dict[str, pd.DataFrame], Dict[str, Any]]:

        config = self.input_config
        default_values = self._read_default_values(config)

        xl = pd.ExcelFile(filepath, engine="openpyxl")

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
                narrow = self._check_parameter(df, config_details["indices"], mod_name)
            elif entity_type == "set":
                narrow = self._check_set(df, config_details, mod_name)

            input_data[mod_name] = narrow

        input_data = self._check_index(input_data)

        return input_data, default_values


class ReadCsv(_ReadTabular):
    """Read in a folder of CSV files"""

    def read(
        self, filepath, **kwargs
    ) -> Tuple[Dict[str, pd.DataFrame], Dict[str, Any]]:

        input_data = {}

        default_values = self._read_default_values(self.input_config)

        for parameter, details in self.input_config.items():
            logger.info("Looking for %s", parameter)
            config_details = self.input_config[parameter]

            csv_path = os.path.join(filepath, parameter + ".csv")

            try:
                df = pd.read_csv(csv_path)
            except pd.errors.EmptyDataError:
                logger.error("No data found in file for %s", parameter)
                expected_columns = config_details["indices"]
                default_columns = expected_columns + ["VALUE"]
                df = pd.DataFrame(columns=default_columns)

            entity_type = self.input_config[parameter]["type"]

            if entity_type == "param":
                narrow = self._check_parameter(df, config_details["indices"], parameter)
                if not narrow.empty:
                    narrow_checked = check_datatypes(
                        narrow, self.input_config, parameter
                    )
                else:
                    narrow_checked = narrow
            elif entity_type == "set":
                narrow = self._check_set(df, config_details, parameter)
                if not narrow.empty:
                    narrow_checked = check_set_datatype(
                        narrow, self.input_config, parameter
                    )
                else:
                    narrow_checked = narrow

            input_data[parameter] = narrow_checked

        input_data = self._check_index(input_data)

        return input_data, default_values


class ReadDatapackage(ReadStrategy):
    def read(
        self, filepath, **kwargs
    ) -> Tuple[Dict[str, pd.DataFrame], Dict[str, Any]]:
        inputs = read_datapackage(filepath)
        default_resource = inputs.pop("default_values").set_index("name").to_dict()
        default_values = default_resource["default_value"]
        self.input_config = read_datapackage_schema_into_config(
            filepath, default_values
        )
        inputs = self._check_index(inputs)
        return inputs, default_values


class ReadDatafile(ReadStrategy):
    def read(
        self, filepath, **kwargs
    ) -> Tuple[Dict[str, pd.DataFrame], Dict[str, Any]]:

        config = self.input_config
        default_values = self._read_default_values(config)
        amply_datafile = self.read_in_datafile(filepath, config)
        inputs = self._convert_amply_to_dataframe(amply_datafile, config)
        inputs = self._check_index(inputs)
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

        dict_of_dataframes = {}  # type: Dict[str, pd.DataFrame]

        for name in datafile_parser.symbols.keys():
            logger.debug("Extracting data for %s", name)
            if name in config and config[name]["type"] == "param":
                dict_of_dataframes[name] = self.extract_param(
                    config, name, datafile_parser, dict_of_dataframes
                )
            elif name in config and config[name]["type"] == "set":
                dict_of_dataframes[name] = self.extract_set(
                    datafile_parser, name, config, dict_of_dataframes
                )
            else:
                logger.warning(
                    "Parameter {} could not be found in the configuration.".format(name)
                )

        return dict_of_dataframes

    def extract_set(
        self, datafile_parser, name, config, dict_of_dataframes
    ) -> pd.DataFrame:
        data = datafile_parser[name].data

        indices = ["VALUE"]
        df = pd.DataFrame(data=data, columns=indices, dtype=config[name]["dtype"])

        return check_set_datatype(df, config, name)

    def extract_param(
        self, config, name, datafile_parser, dict_of_dataframes
    ) -> pd.DataFrame:
        indices = config[name]["indices"].copy()
        indices_dtypes = [config[index]["dtype"] for index in indices]
        indices.append("VALUE")
        indices_dtypes.append("float")

        raw_data = datafile_parser[name].data
        data = self._convert_amply_data_to_list(raw_data)
        df = pd.DataFrame(data=data, columns=indices)
        try:
            return check_datatypes(df, config, name)
        except ValueError as ex:
            msg = "Validation error when checking datatype of {}: {}".format(
                name, str(ex)
            )
            raise ValueError(msg)

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
