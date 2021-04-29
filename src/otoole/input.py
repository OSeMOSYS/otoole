"""The ``input`` module allows you to access the conversion routines programmatically

To use the routines, you need to instanciate a ``ReadStrategy`` and a ``WriteStrategy``
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

Convert a GNUMathProg datafile to a folder of Tabular DataPackage::

>>> from otoole import ReadDataFile
>>> from otoole import WriteDatapackage
>>> from otoole import Context
>>> reader = ReadDataFile()
>>> writer = WriteDatapackage()
>>> converter = Context(read_strategy=reader, write_strategy=writer)
>>> converter.convert('my_datafile.txt', 'my_datapackage')

"""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TextIO, Tuple, Union

import pandas as pd

from otoole.utils import read_packaged_file

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
        """Delegate reading to the strategy, depending upon the format
        """
        return self._read_strategy.read(filepath, **kwargs)

    def _write(self, inputs: Dict, filepath: str, default_values: Dict) -> None:
        """
        Delegate writing to the strategy, depending upon the format
        """
        self._write_strategy.write(inputs, filepath, default_values)

    def convert(self, input_filepath: str, output_filepath: str, **kwargs: Dict):
        """Converts from file ``input_filepath`` to file ``output_filepath``

        Arguments
        ---------
        input_filepath: str
        output_filepath: str
        """
        inputs, default_values = self._read(input_filepath, **kwargs)
        self._write(inputs, output_filepath, default_values)


class Strategy(ABC):
    """

    Arguments
    ---------
    input_config : dict, default=None
        A user configuration for the input parameters and sets
    results_config : dict, default=None
        A user configuration for the results parameters

    """

    def __init__(
        self, user_config: Optional[Dict] = None, results_config: Optional[Dict] = None
    ):
        self._input_config = {}  # type: Dict[str, Dict[str, Union[str, List[str]]]]
        self._results_config = {}

        if user_config:
            self.input_config = user_config
        else:
            self.input_config = self._read_config()
        if results_config:
            self._results_config = results_config
        else:
            self._results_config = self._read_results_config()

    def _add_dtypes(self, config: Dict):
        for name, details in config.items():
            if details["type"] == "param":
                dtypes = {}
                for column in details["indices"] + ["VALUE"]:
                    if column == "VALUE":
                        dtypes["VALUE"] = details["dtype"]
                    else:
                        dtypes[column] = config[column]["dtype"]
                details["index_dtypes"] = dtypes
        return config

    def _read_config(self) -> Dict[str, Dict]:
        return read_packaged_file("config.yaml", "otoole.preprocess")

    def _read_results_config(self) -> Dict[str, Dict]:
        return read_packaged_file("config.yaml", "otoole.results")

    @property
    def input_config(self) -> Dict:
        return self._input_config

    @input_config.setter
    def input_config(self, value: Dict):
        self._input_config = self._add_dtypes(value)

    @property
    def results_config(self):
        return self._results_config

    @staticmethod
    def _read_default_values(config):
        default_values = {}
        for name, contents in config.items():
            if contents["type"] == "param":
                default_values[name] = contents["default"]
        return default_values


class WriteStrategy(Strategy):
    """
    The WriteStrategy interface declares operations common to all writing formats

    The Context uses this interface to call the algorithm defined by Concrete
    Strategies.

    Arguments
    ---------
    filepath: str, default=None
    default_values: dict, default=None
    user_config: dict, default=None

    """

    def __init__(
        self,
        filepath: Optional[str] = None,
        default_values: Optional[Dict] = None,
        user_config: Optional[Dict] = None,
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

    @abstractmethod
    def _header(self) -> Union[TextIO, Any]:
        raise NotImplementedError()

    @abstractmethod
    def _write_parameter(
        self, df: pd.DataFrame, parameter_name: str, handle: TextIO, default: float
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

    def write(self, inputs: Dict, filepath: str, default_values: Dict):
        """Perform the conversion from dict of dataframes to destination format
        """
        self.filepath = filepath
        self.default_values = default_values

        handle = self._header()
        logger.debug(default_values)

        for name, df in sorted(inputs.items()):
            logger.debug("%s has %s columns: %s", name, len(df.index.names), df.columns)

            try:
                entity_type = self.input_config[name]["type"]
            except KeyError:
                try:
                    entity_type = self.results_config[name]["type"]
                except KeyError:
                    raise KeyError("Cannot find %s in input or results config", name)

            if entity_type == "param":
                default_value = default_values[name]
                self._write_parameter(df, name, handle, default=default_value)
            else:
                self._write_set(df, name, handle)

        self._footer(handle)

        if handle:
            handle.close()


class ReadStrategy(Strategy):
    """
    The Strategy interface declares operations common to all reading formats.

    The Context uses this interface to call the algorithm defined by Concrete
    Strategies.
    """

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

            details = self.input_config[name]

            if details["type"] == "param":
                logger.debug("Identified {} as a parameter".format(name))
                try:
                    df.set_index(details["indices"], inplace=True)
                except KeyError:
                    logger.debug("Unable to set index on {}".format(name))
                    pass

                logger.debug(
                    "Column dtypes identified: {}".format(details["index_dtypes"])
                )
                logger.debug(df.head())
                # Drop empty rows
                df = (
                    df.dropna(axis=0, how="all")
                    .reset_index()
                    .astype(details["index_dtypes"])
                    .set_index(details["indices"])
                )
            else:
                logger.debug("Identified {} as a set".format(name))
                df = df.astype(details["dtype"])

            input_data[name] = df

        return input_data

    @abstractmethod
    def read(
        self, filepath: Union[str, TextIO], **kwargs
    ) -> Tuple[Dict[str, pd.DataFrame], Dict[str, Any]]:
        raise NotImplementedError()
