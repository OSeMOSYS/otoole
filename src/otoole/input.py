from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, TextIO, Tuple

import pandas as pd

from otoole import read_packaged_file

logger = logging.getLogger(__name__)


class Inputs(object):
    """Represents the set of inputs associated with an OSeMOSYS model

    Arguments
    ---------
    config : str, default=None
    """

    def __init__(self, config: str = None):
        self.config = read_packaged_file("config.yaml", "otoole.preprocess")
        self._default_values = self._read_default_values()

    def _read_default_values(self):
        default_values = {}
        for name, contents in self.config.items():
            if contents["type"] == "param":
                default_values[name] = contents["default"]
        return default_values

    def default_values(self):
        return self._default_values


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

    def _read(self, filepath: str) -> Tuple[Dict[str, pd.DataFrame], Dict[str, Any]]:
        """Delegate reading to the strategy, depending upon the format
        """
        return self._read_strategy.read(filepath)

    def _write(self, inputs: Dict, filepath: str, default_values: Dict) -> None:
        """
        Delegate writing to the strategy, depending upon the format
        """
        self._write_strategy.write(inputs, filepath, default_values)

    def convert(self, input_filepath: str, output_filepath: str):
        """Converts from file ``input_filepath`` to file ``output_filepath``

        Arguments
        ---------
        input_filepath: str
        output_filepath: str
        """
        inputs, default_values = self._read(input_filepath)
        self._write(inputs, output_filepath, default_values)


class WriteStrategy(ABC):
    """
    The WriteStrategy interface declares operations common to all writing formats

    The Context uses this interface to call the algorithm defined by Concrete
    Strategies.
    """

    @abstractmethod
    def _header(self) -> TextIO:
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
        handle = self._header()
        logger.debug(default_values)

        for name, df in inputs.items():
            logger.debug(name)

            df = df.reset_index()
            if "index" in df.columns:
                df = df.drop(columns="index")

            logger.debug("Number of columns: %s, %s", len(df.columns), df.columns)
            if len(df.columns) > 1:
                default_value = default_values[name]
                self._write_parameter(df, name, handle, default=default_value)
            else:
                self._write_set(df, name, handle)

        self._footer(handle)

        handle.close()


class ReadStrategy(ABC):
    """
    The Strategy interface declares operations common to all reading formats.

    The Context uses this interface to call the algorithm defined by Concrete
    Strategies.
    """

    @abstractmethod
    def read(self, filepath: str) -> Tuple[Dict[str, pd.DataFrame], Dict[str, Any]]:
        pass
