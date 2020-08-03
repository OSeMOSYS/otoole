import logging
from typing import Any, Dict, List, Tuple

import pandas as pd
from amply import Amply
from flatten_dict import flatten
from pandas_datapackage_reader import read_datapackage

from otoole import read_packaged_file
from otoole.input import ReadStrategy
from otoole.preprocess.longify_data import check_datatypes, check_set_datatype

logger = logging.getLogger(__name__)


class ReadExcel(ReadStrategy):
    def read(self, filepath) -> Tuple[Dict[str, pd.DataFrame], Dict[str, Any]]:
        raise NotImplementedError()


class ReadCsv(ReadStrategy):
    def read(self, filepath) -> Tuple[Dict[str, pd.DataFrame], Dict[str, Any]]:
        raise NotImplementedError()


class ReadDatapackage(ReadStrategy):
    def read(self, filepath) -> Tuple[Dict[str, pd.DataFrame], Dict[str, Any]]:
        inputs = read_datapackage(filepath)
        default_resource = inputs.pop("default_values").set_index("name").to_dict()
        default_values = default_resource["default_value"]
        return inputs, default_values


class ReadDatafile(ReadStrategy):
    def read(self, filepath) -> Tuple[Dict[str, pd.DataFrame], Dict[str, Any]]:

        config = read_packaged_file("config.yaml", "otoole.preprocess")  # type: Dict
        amply_datafile = self.read_in_datafile(filepath, config)
        inputs = self._convert_amply_to_dataframe(amply_datafile, config)
        default_values = self._read_default_values(config)

        return inputs, default_values

    def _read_default_values(self, config):
        default_values = {}
        for name, contents in config.items():
            if contents["type"] == "param":
                default_values[name] = contents["default"]
        return default_values

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
