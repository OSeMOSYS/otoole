"""The ``input`` module allows you to access the conversion routines programmatically

To use the routines, you need to instantiate a ``ReadStrategy`` and a ``WriteStrategy``
relevant for the format of the input and output data.  You then pass these to a
``Context``.

Example
-------
Convert an in-memory dictionary of pandas DataFrames containing OSeMOSYS parameters
to an Excel spreadsheet::

>>> from otoole import ReadMemory
>>> from otoole import WriteExcel
>>> from otoole import Context
>>> reader = ReadMemory(parameters)
>>> writer = WriteExcel()
>>> converter = Context(read_strategy=reader, write_strategy=writer)
>>> converter.convert('.', 'osemosys_to_excel.xlsx')

Convert a GNUMathProg datafile to a folder of CSV files::

>>> from otoole import ReadDataFile
>>> from otoole import WriteCsv
>>> from otoole import Context
>>> reader = ReadDataFile()
>>> writer = WriteCsv()
>>> converter = Context(read_strategy=reader, write_strategy=writer)
>>> converter.convert('my_datafile.txt', 'folder_of_csv_files')

"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TextIO, Tuple, Union

import pandas as pd

from otoole.exceptions import OtooleIndexError, OtooleNameMismatchError

logger = logging.getLogger(__name__)


class Context:
    """
    The Context defines the interface of interest to clients.
    """

    def __init__(
        self, read_strategy: ReadStrategy, write_strategy: WriteStrategy
    ) -> None:
        """
        Usually, the Context accepts a strategy through the constructor, but
        also provides a setter to change it at runtime.
        """
        self._read_strategy = read_strategy
        self._write_strategy = write_strategy

    @property
    def write_strategy(self) -> WriteStrategy:
        """
        The Context maintains a reference to one of the Strategy objects. The
        Context does not know the concrete class of a strategy. It should work
        with all strategies via the Strategy interface.
        """
        return self._write_strategy

    @write_strategy.setter
    def write_strategy(self, strategy: WriteStrategy) -> None:
        """
        Usually, the Context allows replacing a Strategy object at runtime.
        """
        self._write_strategy = strategy

    @property
    def read_strategy(self) -> ReadStrategy:
        """
        The Context maintains a reference to one of the Strategy objects. The
        Context does not know the concrete class of a strategy. It should work
        with all strategies via the Strategy interface.
        """
        return self._read_strategy

    @read_strategy.setter
    def read_strategy(self, strategy: ReadStrategy) -> None:
        """
        Usually, the Context allows replacing a Strategy object at runtime.
        """
        self._read_strategy = strategy

    def _read(
        self, filepath: str, **kwargs
    ) -> Tuple[Dict[str, pd.DataFrame], Dict[str, Any]]:
        """Delegate reading to the strategy, depending upon the format"""
        return self._read_strategy.read(filepath, **kwargs)

    def _write(
        self, inputs: Dict, filepath: str, default_values: Dict, **kwargs
    ) -> None:
        """
        Delegate writing to the strategy, depending upon the format
        """
        self._write_strategy.write(inputs, filepath, default_values, **kwargs)

    def convert(self, input_filepath: str, output_filepath: str, **kwargs: Dict):
        """Converts from file ``input_filepath`` to file ``output_filepath``

        Arguments
        ---------
        input_filepath: str
        output_filepath: str
        """

        inputs, default_values = self._read(input_filepath, **kwargs)
        self._write(inputs, output_filepath, default_values, **kwargs)


class Strategy(ABC):
    """
    Arguments
    ---------
    user_config : dict, default=None
        A user configuration for the input parameters and sets
    """

    def __init__(self, user_config: Dict[str, Dict]):

        self.user_config = user_config
        self.input_config = {
            x: y for x, y in self.user_config.items() if y["type"] in ["param", "set"]
        }
        self.results_config = {
            x: y for x, y in self.user_config.items() if y["type"] == "result"
        }

    def _add_dtypes(self, config: Dict):
        for name, details in config.items():
            if details["type"] == "param":
                dtypes = {}
                for column in details["indices"] + ["VALUE"]:
                    if column == "VALUE":
                        dtypes["VALUE"] = (
                            details["dtype"] if details["dtype"] != "int" else "int64"
                        )
                    else:
                        dtypes[column] = (
                            config[column]["dtype"]
                            if config[column]["dtype"] != "int"
                            else "int64"
                        )
                details["index_dtypes"] = dtypes
            elif details["type"] == "set":
                details["dtype"] = (
                    details["dtype"] if details["dtype"] != "int" else "int64"
                )
        return config

    @property
    def user_config(self) -> Dict:
        return self._user_config

    @user_config.setter
    def user_config(self, value: Dict):
        if value:
            self._user_config = self._add_dtypes(value)
        elif value is None:
            raise ValueError("A user configuration must be passed into the reader")

    @staticmethod
    def _read_default_values(config):
        default_values = {}
        for name, contents in config.items():
            if contents["type"] != "set":
                default_values[name] = contents["default"]
        return default_values


class WriteStrategy(Strategy):
    """
    The WriteStrategy interface declares operations common to all writing formats

    The Context uses this interface to call the algorithm defined by Concrete
    Strategies.

    Arguments
    ---------
    user_config: dict, default=None
    filepath: str, default=None
    default_values: dict, default=None
    input_data: dict, default=None

    """

    def __init__(
        self,
        user_config: Dict,
        filepath: Optional[str] = None,
        default_values: Optional[Dict] = None,
        input_data: Optional[Dict[str, pd.DataFrame]] = None,
    ):
        super().__init__(user_config=user_config)
        if filepath:
            self.filepath = filepath
        else:
            self.filepath = ""

        if default_values:
            self.default_values = default_values
        else:
            self.default_values = {}

        if input_data:
            self.input_data = input_data
        else:
            self.input_data = {}

    @abstractmethod
    def _header(self) -> Union[TextIO, Any]:
        raise NotImplementedError()

    @abstractmethod
    def _write_parameter(
        self,
        df: pd.DataFrame,
        parameter_name: str,
        handle: TextIO,
        default: float,
        **kwargs,
    ) -> pd.DataFrame:
        """Write parameter data"""
        raise NotImplementedError()

    @abstractmethod
    def _write_set(self, df: pd.DataFrame, set_name, handle: TextIO) -> pd.DataFrame:
        """Write set data"""
        raise NotImplementedError()

    @abstractmethod
    def _footer(self, handle: TextIO):
        raise NotImplementedError()

    def write(
        self,
        inputs: Dict[str, pd.DataFrame],
        filepath: str,
        default_values: Dict[str, float],
        **kwargs,
    ):
        """Perform the conversion from dict of dataframes to destination format"""
        self.filepath = filepath
        self.default_values = default_values

        handle = self._header()
        logger.debug(default_values)

        self.inputs = inputs  # parameter/set data OR result data
        self.input_params = kwargs.get("input_data", None)  # parameter/set data

        for name, df in sorted(self.inputs.items()):
            logger.debug("%s has %s columns: %s", name, len(df.index.names), df.columns)

            try:
                entity_type = self.user_config[name]["type"]
            except KeyError:
                try:
                    entity_type = self.results_config[name]["type"]
                except KeyError:
                    raise KeyError("Cannot find %s in input or results config", name)

            if entity_type != "set":
                self._write_parameter(
                    df,
                    name,
                    handle,
                    default=default_values[name],
                    input_data=self.inputs,
                )
            else:
                self._write_set(df, name, handle)

        self._footer(handle)

        if isinstance(handle, TextIO):
            handle.close()


class ReadStrategy(Strategy):
    """
    The Strategy interface declares operations common to all reading formats.

    The Context uses this interface to call the algorithm defined by Concrete
    Strategies.
    """

    def __init__(
        self,
        user_config: Dict,
        write_defaults: bool = False,
    ):
        super().__init__(user_config=user_config)

        self.write_defaults = write_defaults

    def _check_index(
        self, input_data: Dict[str, pd.DataFrame]
    ) -> Dict[str, pd.DataFrame]:
        """Checks index and datatypes are applied to the parameter DataFrame

        Also removes empty lines

        Arguments
        ---------
        input_data : dict
            Dictionary and pandas DataFrames containing the OSeMOSYS parameters

        Returns
        -------
        dict
            Dictionary and pandas DataFrames containing the OSeMOSYS parameters
        """
        for name, df in input_data.items():

            details = self.user_config[name]

            if details["type"] == "param":
                self._check_param_index_names(name=name, config=details, df=df)
            elif details["type"] == "set":
                self._check_set_index_names(name=name, df=df)

            try:
                df = self._check_index_dtypes(name=name, config=details, df=df)
            except ValueError as ex:
                raise ValueError(f"{name}: {ex}")

            input_data[name] = df

        return input_data

    @staticmethod
    def _check_param_index_names(
        name: str, config: Dict[str, Any], df: pd.DataFrame
    ) -> None:
        """Checks parameter index names input data against config file

        Arguments
        ---------
        name: str
            Name of parameter
        config: Dict[str,Any]
            Configuration file data for the parameter
        df: pd.DataFrame
            Data read in for the parameter

        Raises
        ------
        OtooleIndexError
            If actual indices do not match expected indices
        """

        actual_indices = df.index.names
        if actual_indices[0] is None:  # for ReadMemory
            logger.debug(f"No multi-index identified for {name}")
            actual_indices = list(df)[:-1]  # Drop "VALUE"

        logger.debug(f"Actual indices for {name} are {actual_indices}")
        try:
            expected_indices = config["indices"]
            logger.debug(f"Expected indices for {name} are {expected_indices}")
        except KeyError:
            logger.debug(f"No expected indices identified for {name}")
            return

        if actual_indices == expected_indices:
            return
        else:
            raise OtooleIndexError(
                resource=name,
                config_indices=expected_indices,
                data_indices=actual_indices,
            )

    @staticmethod
    def _check_set_index_names(name: str, df: pd.DataFrame) -> None:
        """Checks for proper set index name

        Arguments
        ---------
        name: str
            Name of set
        df: pd.DataFrame
            Data read in for the parameter

        Raises
        ------
        OtooleIndexError
            If actual indices do not match expected indices
        """
        if not list(df.columns) == ["VALUE"]:
            raise OtooleIndexError(
                resource=name,
                config_indices=["VALUE"],
                data_indices=df.columns,
            )

    @staticmethod
    def _check_index_dtypes(
        name: str, config: Dict[str, Any], df: pd.DataFrame
    ) -> pd.DataFrame:
        """Checks datatypes of input data against config file

        Arguments
        ---------
        name: str
            Name of parameter
        config: Dict[str,Any]
            Configuration file data for the parameter
        df: pd.DataFrame
            Data read in for the parameter

        Returns
        -------
        pd.DataFrame
            input_data with corrected datatypes
        """

        if config["type"] == "param":
            logger.debug("Identified {} as a parameter".format(name))
            try:
                df.set_index(config["indices"], inplace=True)
            except KeyError:
                logger.debug("Unable to set index on {}".format(name))
                pass

            logger.debug("Column dtypes identified: {}".format(config["index_dtypes"]))
            logger.debug(df.head())
            # Drop empty rows
            try:
                df = (
                    df.dropna(axis=0, how="all")
                    .reset_index()
                    .astype(config["index_dtypes"])
                    .set_index(config["indices"])
                )
            except ValueError:  # ValueError: invalid literal for int() with base 10:
                df = df.dropna(axis=0, how="all").reset_index()
                for index, dtype in config["index_dtypes"].items():
                    if dtype == "int64":
                        df[index] = df[index].astype(float).astype("int64")
                    else:
                        df[index] = df[index].astype(dtype)
                df = df.set_index(config["indices"])

        else:
            logger.debug("Identified {} as a set".format(name))
            df = df.astype(config["dtype"])

        return df

    def _get_missing_input_dataframes(
        self, input_data: Dict[str, pd.DataFrame], config_type: str
    ) -> Dict[str, pd.DataFrame]:
        """Creates empty dataframes if user config data does not exist

        Arguments:
        ----------
        input_data: Dict[str, pd.DataFrame]
            Internal datastore
        config_type: str
            Type of value. Must be "set", "param", or "result"

        Returns:
        --------
        all_params: Dict[str, pd.DataFrame]
            Input data plus empty dataframes
        """

        if config_type not in ["set", "param", "result"]:
            raise ValueError(f"{config_type} not of type 'set', 'param', or 'result'")

        all_values = [
            value
            for value, data in self.user_config.items()
            if data["type"] == config_type
        ]
        missing_values = [x for x in all_values if x not in input_data]

        for value in missing_values:
            try:  # param and result condition
                indices = self.user_config[value]["indices"]
                df = pd.DataFrame(columns=indices)
                df = df.set_index(indices)
            except KeyError:  # set condition
                df = pd.DataFrame()
            df["VALUE"] = ""
            input_data[value] = df

        return input_data

    def _compare_read_to_expected(
        self, names: List[str], short_names: bool = False
    ) -> None:
        """Compares input data definitions to config file definitions

        Arguments:
        ---------
        names: List[str]
            Parameter and set names read in
        map_names: bool = False
            If should be checking short_names from config file

        Raises:
        -------
        OtooleNameMismatchError
            If the info in the data and config file do not match
        """
        user_config = self.input_config
        if short_names:
            expected = []
            for name in user_config:
                try:
                    expected.append(user_config[name]["short_name"])
                except KeyError:
                    expected.append(name)
        else:
            expected = [x for x in user_config]

        errors = list(set(expected).symmetric_difference(set(names)))
        if errors:
            logger.debug(f"data and config name errors are: {errors}")
            raise OtooleNameMismatchError(name=errors)

    def _expand_dataframe(
        self,
        name: str,
        input_data: Dict[str, pd.DataFrame],
        default_values: Dict[str, pd.DataFrame],
    ) -> pd.DataFrame:
        """Populates default value entry rows in dataframes

        Parameters
        ----------
        name: str
            Name of parameter/result to expand
        input_data: Dict[str, pd.DataFrame],
            internal datastore
        default_values: Dict[str, pd.DataFrame],

        Returns
        -------
        pd.DataFrame,
            Input data with expanded default values replacing missing entries
        """

        df = input_data[name]

        # TODO: Issue with how otoole handles trade route right now.
        # The double definition of REGION throws an error.
        if name == "TradeRoute":
            return df

        default_df = self._get_default_dataframe(name, input_data, default_values)

        # future warning of concating empty dataframe
        if not df.empty:
            df = pd.concat([df, default_df])
        else:
            df = default_df.copy()

        df = df[~df.index.duplicated(keep="first")]

        df = self._check_index_dtypes(name, self.user_config[name], df)

        return df.sort_index()

    def _get_default_dataframe(
        self,
        name: str,
        input_data: Dict[str, pd.DataFrame],
        default_values: Dict[str, pd.DataFrame],
    ) -> pd.DataFrame:
        """Creates default dataframe"""

        index_data = {}
        indices = self.user_config[name]["indices"]
        for index in indices:
            index_data[index] = input_data[index]["VALUE"].to_list()

        if len(index_data) > 1:
            new_index = pd.MultiIndex.from_product(
                list(index_data.values()), names=list(index_data.keys())
            )
        else:
            new_index = pd.Index(
                list(index_data.values())[0], name=list(index_data.keys())[0]
            )

        df = pd.DataFrame(index=new_index).sort_index()
        df["VALUE"] = default_values[name]

        return df

    def write_default_params(
        self,
        input_data: Dict[str, pd.DataFrame],
        default_values: Dict[str, Union[str, int, float]],
    ) -> Dict[str, pd.DataFrame]:
        """Returns paramter dataframes with default values expanded"""
        names = [x for x in self.user_config if self.user_config[x]["type"] == "param"]
        for name in names:
            try:
                logger.debug(f"Serching for {name} data to expand")
                input_data[name] = self._expand_dataframe(
                    name, input_data, default_values
                )
            except KeyError:
                logger.warning(f"Can not expand {name} data")
        return input_data

    def write_default_results(
        self,
        result_data: Dict[str, pd.DataFrame],
        input_data: Dict[str, pd.DataFrame],
        default_values: Dict[str, Union[str, int, float]],
    ) -> Dict[str, pd.DataFrame]:
        """Returns result dataframes with default values expanded"""

        all_data = {**result_data, **input_data}
        names = [x for x in self.user_config if self.user_config[x]["type"] == "result"]
        for name in names:
            try:
                logger.debug(f"Serching for {name} data to expand")
                result_data[name] = self._expand_dataframe(
                    name, all_data, default_values
                )
            except KeyError:
                logger.debug(f"Can not expand {name} data")
        return result_data

    @abstractmethod
    def read(
        self, filepath: Union[str, TextIO], **kwargs
    ) -> Tuple[Dict[str, pd.DataFrame], Dict[str, Any]]:
        """Reads in data from file

        Arguments
        ---------
        filepath: Union[str, TextIO]

        Returns
        -------
        Tuple[Dict[str, pd.DataFrame], Dict[str, Any]]
            tuple of input_data as a dictionary of pandas DataFrames and
            dictionary of default values
        """
        raise NotImplementedError()
