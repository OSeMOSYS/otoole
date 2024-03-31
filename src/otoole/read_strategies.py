import logging
import os
from typing import Any, Dict, List, Optional, TextIO, Tuple, Union

import pandas as pd
from amply import Amply
from flatten_dict import flatten

from otoole.exceptions import OtooleDeprecationError, OtooleError
from otoole.input import ReadStrategy
from otoole.preprocess.longify_data import check_datatypes, check_set_datatype
from otoole.utils import create_name_mappings

logger = logging.getLogger(__name__)


class ReadMemory(ReadStrategy):
    """Read a dict of OSeMOSYS parameters from memory

    Arguments
    ---------
    parameters : Dict[str, pd.DataFrame]
        Dictionary of OSeMOSYS parameters
    user_config : Dict[str, Dict]
        User configuration

    """

    def __init__(
        self, parameters: Dict[str, pd.DataFrame], user_config: Dict[str, Dict]
    ):
        super().__init__(user_config)
        self._parameters = parameters

    def read(
        self, filepath: Union[str, TextIO, None] = None, **kwargs
    ) -> Tuple[Dict[str, pd.DataFrame], Dict[str, Any]]:

        config = self.user_config
        default_values = self._read_default_values(config)
        self._parameters = self._check_index(self._parameters)
        return self._parameters, default_values


class _ReadTabular(ReadStrategy):
    def __init__(
        self,
        user_config: Dict[str, Dict],
        write_defaults: bool = False,
        keep_whitespace: bool = False,
    ):
        super().__init__(user_config=user_config, write_defaults=write_defaults)
        self.keep_whitespace = keep_whitespace

    def _check_set(self, df: pd.DataFrame, config_details: Dict, name: str):

        logger.info("Checking set %s", name)
        narrow = df

        return narrow

    def _convert_wide_2_narrow(self, df: pd.DataFrame, name: str):
        """Converts a dataframe from wide to narrow format

        Arguments
        ---------
        df: pd.DataFrame
        expected_headers: List
        name: str
        """
        actual_headers = list(df.columns)

        if "MODEOFOPERATION" in actual_headers:
            df = df.rename(columns={"MODEOFOPERATION": "MODE_OF_OPERATION"})
            actual_headers = list(df.columns)

        if actual_headers[-1] == "VALUE":
            logger.info(
                f"{name} is already in narrow form with headers {actual_headers}"
            )
            narrow = df
            converted_headers = actual_headers[:-1]  # remove "VALUE"
        else:
            try:
                converted_headers = [
                    x for x in actual_headers if not isinstance(x, int)
                ]
                converted_headers += ["YEAR"]
                if "VALUE" in converted_headers:
                    raise OtooleError(
                        resource=name,
                        message="'VALUE' can not be a header in wide format data",
                    )
                narrow = pd.melt(
                    df,
                    id_vars=converted_headers[:-1],
                    var_name=converted_headers[-1],  # Normally 'YEAR'
                    value_name="new_VALUE",
                )
                narrow = narrow.rename(columns={"new_VALUE": "VALUE"})
                logger.info(f"{name} reshaped from wide to narrow format")
            except IndexError as ex:
                logger.debug(f"Could not reshape {name}")
                raise ex
            except KeyError as ex:
                logger.debug(
                    f"Actual headers: {actual_headers}\nConverted headers: {converted_headers}"
                )
                raise ex

        all_headers = converted_headers + ["VALUE"]
        return narrow[all_headers].set_index(converted_headers)

    def _whitespace_converter(self, indices: List[str]) -> Dict[str, Any]:
        """Creates converter for striping whitespace in dataframe

        Arguments
        ---------
        indicies: List[str]
            Column headers of dataframe

        Returns
        -------
        Dict[str,Any]
            Converter dictionary
        """
        if self.keep_whitespace:
            return {}
        else:
            return {x: str.strip for x in indices}


class ReadExcel(_ReadTabular):
    """Read in an Excel spreadsheet in wide format to a dict of Pandas DataFrames

    Arguments
    ---------
    user_config : Dict[str, Dict]
        User configuration
    keep_whitespace : bool
        Whether to keep whitespace in the dataframes
    """

    def read(
        self, filepath: Union[str, TextIO], **kwargs
    ) -> Tuple[Dict[str, pd.DataFrame], Dict[str, Any]]:

        config = self.user_config
        default_values = self._read_default_values(config)
        excel_to_csv = create_name_mappings(config, map_full_to_short=False)

        xl = pd.ExcelFile(filepath, engine="openpyxl")
        self._compare_read_to_expected(names=xl.sheet_names, short_names=True)

        input_data = {}

        for name in xl.sheet_names:

            try:
                mod_name = excel_to_csv[name]
            except KeyError:
                mod_name = name

            config_details = config[mod_name]

            df = xl.parse(name)

            entity_type = config[mod_name]["type"]

            if entity_type == "param":
                narrow = self._convert_wide_2_narrow(df, mod_name)
            elif entity_type == "set":
                narrow = self._check_set(df, config_details, mod_name)

            input_data[mod_name] = narrow

        for config_type in ["param", "set"]:
            input_data = self._get_missing_input_dataframes(
                input_data, config_type=config_type
            )

        if self.write_defaults:
            input_data = self.write_default_params(input_data, default_values)

        input_data = self._check_index(input_data)

        return input_data, default_values


class ReadCsv(_ReadTabular):
    """Read in a folder of CSV files to a dict of Pandas DataFrames

    Arguments
    ---------
    user_config : Dict[str, Dict]
        User configuration
    keep_whitespace : bool
        Whether to keep whitespace in the dataframes
    """

    def read(
        self, filepath, **kwargs
    ) -> Tuple[Dict[str, pd.DataFrame], Dict[str, Any]]:

        input_data = {}

        self._check_for_default_values_csv(filepath)
        names = [
            f.split(".csv")[0]
            for f in os.listdir(filepath)
            if f.split(".")[-1] == "csv"
        ]
        logger.debug(names)
        self._compare_read_to_expected(names=names)

        default_values = self._read_default_values(self.user_config)

        for parameter, details in self.user_config.items():
            logger.info("Looking for %s", parameter)

            entity_type = details["type"]
            try:
                converter = self._whitespace_converter(details["indices"])
            except KeyError:  # sets don't have indices def
                converter = self._whitespace_converter(["VALUE"])

            if entity_type == "param":
                df = self._get_input_data(filepath, parameter, details, converter)
                narrow = self._convert_wide_2_narrow(df, parameter)
                if not narrow.empty:
                    narrow_checked = check_datatypes(
                        narrow, self.user_config, parameter
                    )
                else:
                    narrow_checked = narrow

            elif entity_type == "set":
                df = self._get_input_data(filepath, parameter, details, converter)
                narrow = self._check_set(df, details, parameter)
                if not narrow.empty:
                    narrow_checked = check_set_datatype(
                        narrow, self.user_config, parameter
                    )
                else:
                    narrow_checked = narrow

            else:  # results
                continue

            input_data[parameter] = narrow_checked

        for config_type in ["param", "set"]:
            input_data = self._get_missing_input_dataframes(
                input_data, config_type=config_type
            )

        input_data = self._check_index(input_data)

        if self.write_defaults:
            input_data = self.write_default_params(input_data, default_values)

        return input_data, default_values

    @staticmethod
    def _get_input_data(
        filepath: str, parameter: str, details: Dict, converter: Optional[Dict] = None
    ) -> pd.DataFrame:
        """Reads in and checks CSV data format.

        Arguments
        ---------
        filepath:str
            Directory of csv files
        parameter:str
            parameter name
        config_details: dict[str,Union[str,float,int]]
            configuration data for the parameter being read in

        Returns
        -------
        pd.DataFrame
            CSV data as a dataframe
        """
        converter = {} if not converter else converter
        csv_path = os.path.join(filepath, parameter + ".csv")
        try:
            df = pd.read_csv(csv_path, converters=converter)
        except pd.errors.EmptyDataError:
            logger.error("No data found in file for %s", parameter)
            expected_columns = details["indices"]
            default_columns = expected_columns + ["VALUE"]
            df = pd.DataFrame(columns=default_columns)
        return df

    @staticmethod
    def _check_for_default_values_csv(filepath: str) -> None:
        """Checks for a default values csv, which has been deprecated.

        Arguments
        ---------
        filepath:str
            Directory of csv files

        Raises
        ------
        OtooleDeprecationError
            If a default_values.csv is found in input data
        """

        default_values_csv_path = os.path.join(
            os.path.dirname(filepath), "default_values.csv"
        )
        if os.path.exists(default_values_csv_path):
            raise OtooleDeprecationError(
                resource="data/default_values.csv",
                message="Remove default_values.csv and define all default values in the configuration file",
            )


class ReadDatafile(ReadStrategy):
    """Read in a datafile to a dict of Pandas DataFrames

    Arguments
    ---------
    user_config : Dict[str, Dict]
        User configuration
    keep_whitespace : bool
        Whether to keep whitespace in the dataframes

    """

    def read(
        self, filepath, **kwargs
    ) -> Tuple[Dict[str, pd.DataFrame], Dict[str, Any]]:

        config = self.user_config
        default_values = self._read_default_values(config)

        # Check filepath exists
        if os.path.exists(filepath):
            amply_datafile = self.read_in_datafile(filepath, config)
            input_data = self._convert_amply_to_dataframe(amply_datafile, config)
            for config_type in ["param", "set"]:
                input_data = self._get_missing_input_dataframes(
                    input_data, config_type=config_type
                )
            input_data = self._check_index(input_data)

            if self.write_defaults:
                input_data = self.write_default_params(input_data, default_values)

            return input_data, default_values
        else:
            raise FileNotFoundError(f"File not found: {filepath}")

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

        logger.debug("Amply Elements: %s", elements)
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
