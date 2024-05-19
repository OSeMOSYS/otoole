import logging
import os
from typing import Any, TextIO

import pandas as pd

from otoole.exceptions import OtooleExcelNameLengthError
from otoole.input import WriteStrategy

logger = logging.getLogger(__name__)


class WriteExcel(WriteStrategy):
    def _header(self):
        return pd.ExcelWriter(self.filepath, mode="w")

    def _form_parameter(
        self, df: pd.DataFrame, parameter_name: str, default: float
    ) -> pd.DataFrame:
        """Converts data into wide format

        Arguments
        ---------
        df: pd.DataFrame
        parameter_name: str
        default: float

        Returns
        -------
        pandas.DataFrame
        """

        index_names = df.index.names
        column_names = df.columns.to_list()
        if index_names[0]:
            names = index_names + column_names
        else:
            names = column_names
        logger.debug(f"Identified {len(names)} names: {names}")

        total_columns = len(names)

        if "YEAR" not in names:
            pivot = df.copy()
        elif total_columns > 3:
            logger.debug("More than 3 columns for {}: {}".format(parameter_name, names))
            rows = names[0:-2]
            columns = names[-2]
            values = names[-1]
            logger.debug(f"Rows: {rows}; columns: {columns}; values: {values}")
            logger.debug("dtypes: {}".format(df.dtypes))
            pivot = df.reset_index().pivot(index=rows, columns=columns, values=values)
        else:
            logger.debug(f"One column for {parameter_name}: {names}")
            pivot = df.copy()

        return pivot

    def _form_parameter_template(self, parameter_name: str, **kwargs) -> pd.DataFrame:
        """Creates wide format excel template

        Pivots the data to wide format using the data from the YEAR set as the columns.
        This requires input data to be passed into this function.

        Arguments
        ---------
        parameter_name: str
        input_data: dict[str, pd.DataFrame])

        Returns
        -------
        pd.DataFrame
        """

        indices = self.user_config[parameter_name]["indices"]

        if "input_data" not in kwargs:
            logger.debug(f"Can not pivot excel template for {parameter_name}")
            return pd.DataFrame(columns=indices)
        else:
            input_data = kwargs["input_data"]

        if "YEAR" in indices:
            years = input_data["YEAR"]["VALUE"].to_list()
            indices.remove("YEAR")
            indices.extend(years)
        else:
            indices.extend(["VALUE"])

        return pd.DataFrame(columns=indices)

    def _write_parameter(
        self,
        df: pd.DataFrame,
        parameter_name: str,
        handle: pd.ExcelWriter,
        default: float,
        **kwargs,
    ):
        try:
            name = self.user_config[parameter_name]["short_name"]
        except KeyError:
            name = parameter_name

        if len(name) > 31:
            raise OtooleExcelNameLengthError(name=name)

        if not df.empty:
            df = self._form_parameter(df, parameter_name, default)
            df.to_excel(handle, sheet_name=name, merge_cells=False, index=True)
        else:
            logger.debug(f"Dataframe {parameter_name} is empty")
            df = self._form_parameter_template(parameter_name, **kwargs)
            df.to_excel(handle, sheet_name=name, merge_cells=False, index=False)

    def _write_set(self, df: pd.DataFrame, set_name, handle: pd.ExcelWriter):
        df.to_excel(handle, sheet_name=set_name, merge_cells=False, index=False)

    def _footer(self, handle=pd.ExcelWriter):
        handle.close()


class WriteDatafile(WriteStrategy):
    def _header(self):
        filepath = open(self.filepath, "w", newline="")
        msg = "# Model file written by *otoole*\n"
        filepath.write(msg)
        return filepath

    def _form_parameter(self, df: pd.DataFrame, default: float):

        # Don't write out values equal to the default value
        df = df[df.VALUE != default]
        return df

    def _write_parameter(
        self,
        df: pd.DataFrame,
        parameter_name: str,
        handle: TextIO,
        default: float,
        **kwargs,
    ):
        """Write parameter data to a GMPL datafile, omitting data with default value

        Arguments
        ---------
        filepath : StreamIO
        df : pandas.DataFrame
        parameter_name : str
        handle: TextIO
        default : int
        """

        df = self._form_parameter(df, default)
        handle.write("param default {} : {} :=\n".format(default, parameter_name))
        df.to_csv(
            path_or_buf=handle,
            sep=" ",
            header=False,
            index=True,
            float_format="%g",
            lineterminator="\n",
        )
        handle.write(";\n")

    def _write_set(self, df: pd.DataFrame, set_name, handle: TextIO):
        """Write set data to a GMPL datafile

        Arguments
        ---------
        df : pandas.DataFrame
        set_name : str
        handle: TextIO
        """
        handle.write("set {} :=\n".format(set_name))
        df.to_csv(
            path_or_buf=handle,
            sep=" ",
            header=False,
            index=False,
            float_format="%g",
            lineterminator="\n",
        )
        handle.write(";\n")

    def _footer(self, handle: TextIO):
        handle.write("end;\n")
        handle.close()


class WriteCsv(WriteStrategy):
    """Write parameters to comma-separated value files

    Arguments
    ---------
    filepath: str, default=None
        The path to write a folder of csv files
    default_values: dict, default=None
    user_config: dict, default=None
    """

    @staticmethod
    def _write_out_dataframe(folder, parameter, df, index=False):
        """Writes out a dataframe as a csv into a data subfolder

        Arguments
        ---------
        folder : str
        parameter : str
        df : pandas.DataFrame
        index : bool, default=False
            Write the index to CSV
        """
        filepath = os.path.join(folder, parameter + ".csv")
        with open(filepath, "w", newline="") as csvfile:
            logger.info(
                "Writing %s rows into narrow file for %s", df.shape[0], parameter
            )
            df.to_csv(csvfile, index=index)

    def _header(self) -> Any:
        os.makedirs(os.path.join(self.filepath), exist_ok=True)
        return None

    def _write_parameter(
        self,
        df: pd.DataFrame,
        parameter_name: str,
        handle: TextIO,
        default: float,
        **kwargs,
    ) -> pd.DataFrame:
        """Write parameter data"""
        self._write_out_dataframe(self.filepath, parameter_name, df, index=True)

    def _write_set(self, df: pd.DataFrame, set_name, handle: TextIO) -> pd.DataFrame:
        """Write set data"""
        self._write_out_dataframe(self.filepath, set_name, df, index=False)

    def _footer(self, handle: TextIO):
        pass
