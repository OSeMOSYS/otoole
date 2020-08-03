from typing import Any, Dict, Tuple

import pandas as pd
from pandas_datapackage_reader import read_datapackage

from otoole.input import ReadStrategy


class ReadDatapackage(ReadStrategy):
    def read(self, filepath) -> Tuple[Dict[str, pd.DataFrame], Dict[str, Any]]:
        inputs = read_datapackage(filepath)
        default_resource = inputs.pop("default_values").set_index("name").to_dict()
        default_values = default_resource["default_value"]
        return inputs, default_values
