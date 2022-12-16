# from pydantic import ValidationError
from pytest import mark, raises
from yaml import SafeLoader, load

# from otoole.exceptions import OtooleConfigFileError
from otoole.utils import UniqueKeyLoader, validate_config


class TestValidConfigs:
    valid_set = """
        SET_NAME:
          dtype: str
          type: set
    """

    valid_parameter = """
        Parameter_Name:
          indices: [SET]
          type: param
          dtype: float
          default: 0
        SET:
          dtype: str
          type: set
    """

    valid_result = """
        Result_Name:
          indices: [SET]
          type: result
          dtype: float
          default: 0
          calculated: True
        SET:
          dtype: str
          type: set
    """

    config_data = [valid_set, valid_parameter, valid_result]

    config_data_ids = ["valid_set", "valid_parameter", "valid_result"]

    @mark.parametrize("config_data", config_data, ids=config_data_ids)
    def test_valid_configs(self, config_data):
        config = load(config_data, Loader=SafeLoader)
        validate_config(config)


class TestInvalidConfig:
    invalid_type = """
        SET:
          dtype: str
          type: not_valid_type
    """

    invalid_parameter_type = """
        Parameter:
          indices: [SET]
          type: not_valid_type
          dtype: float
          default: 0
        SET:
          dtype: str
          type: set
    """

    invalid_result_type = """
        Result:
          indices: [SET]
          type: not_valid_type
          dtype: float
          default: 0
          calculated: True
        SET:
          dtype: str
          type: set
    """

    invalid_name_spaces = """
        SET WITH SPACES:
          dtype: str
          type: set
    """

    invalid_name_numbers = """
        SETWITHNUMBERS123:
          dtype: str
          type: set
    """

    # does not inlcude underscores
    invalid_name_special_chars = """
        SETWITHSPECIALCHARS!@?%:
          dtype: str
          type: set
    """

    invalid_duplicate_set_names = """
        SET:
          dtype: float
          type: set
        SET:
          dtype: str
          type: set
    """

    invalid_duplicate_param_names = """
        Parameter:
          indices: [SET]
          type: param
          dtype: float
          default: 0
        Parameter:
          indices: [SET]
          type: param
          dtype: float
          default: 0
        SET:
          dtype: str
          type: set
    """

    invalid_duplicate_result_names = """
        Result:
          indices: [SET]
          type: result
          dtype: float
          default: 0
          calculated: True
        Result:
          indices: [SET]
          type: result
          dtype: float
          default: 0
          calculated: True
        SET:
          dtype: str
          type: set
    """

    config_data_duplicates = [
        invalid_duplicate_set_names,
        invalid_duplicate_param_names,
        invalid_duplicate_result_names,
    ]

    config_data_duplicates_ids = [
        "invalid_duplicate_set_names",
        "invalid_duplicate_param_names",
        "invalid_duplicate_result_names",
    ]

    config_data_invalid = [
        invalid_type,
        invalid_parameter_type,
        invalid_result_type,
        invalid_name_spaces,
        invalid_name_numbers,
        invalid_name_special_chars,
    ]

    config_data_invalid_ids = [
        "invalid_type",
        "invalid_parameter_type",
        "invalid_result_type",
        "invalid_name_spaces",
        "invalid_name_numbers",
        "invalid_name_special_chars",
    ]

    @mark.parametrize("config_data", config_data_invalid, ids=config_data_invalid_ids)
    def test_invalid_configs(self, config_data):
        config = load(config_data, Loader=UniqueKeyLoader)
        with raises(ValueError):
            validate_config(config)

    @mark.parametrize(
        "config_data", config_data_duplicates, ids=config_data_duplicates_ids
    )
    def test_invalid_config_multi_defs(self, config_data):
        with raises(ValueError):
            load(config_data, Loader=UniqueKeyLoader)


class TestInvalidConfigSets:
    invalid_dtype = """
        SET:
          dtype: float
          type: set
    """

    invalid_name_length = """
        SETNAMEWITHMORETHANTHIRTYONECHARS:
          dtype: str
          type: set
    """

    invalid_unexpected_field = """
        SET:
          dtype: str
          type: set
          fieldnotexpected: True
    """

    invalid_missing_field = """
        SET:
          type: set
    """

    config_data = [
        invalid_dtype,
        invalid_name_length,
        invalid_missing_field,
    ]

    config_data_ids = [
        "invalid_dtype",
        "invalid_name_length",
        "invalid_missing_field",
    ]

    @mark.parametrize("config_data", config_data, ids=config_data_ids)
    def test_invalid_config_sets(self, config_data):
        config = load(config_data, Loader=UniqueKeyLoader)
        with raises(ValueError):
            validate_config(config)


class TestInvalidConfigParams:
    invalid_dtype = """
        Parameter:
          indices: [SET]
          type: param
          dtype: dict
          default: 0
        SET:
          dtype: str
          type: set
    """

    invalid_name_length = """
        ParameterNameLongerThanThirtyOneChars:
          indices: [SET]
          type: param
          dtype: float
          default: 0
        SET:
          dtype: str
          type: set
    """

    invalid_name_spaces = """
        Param Name With Spaces:
          indices: [SET]
          type: param
          dtype: float
          default: 0
        SET:
          dtype: str
          type: set
    """

    invalid_name_numbers = """
        ParamNameWithNumbers123:
          indices: [SET]
          type: param
          dtype: float
          default: 0
        SET:
          dtype: str
          type: set
    """

    # does not inlcude underscores
    invalid_name_special_chars = """
        ParamNameWithSpecialChars!@?%:
          indices: [SET]
          type: param
          dtype: float
          default: 0
        SET:
          dtype: str
          type: set
    """

    invalid_unexpected_field = """
        Parameter:
          indices: [SET]
          type: param
          dtype: float
          default: 0
          fieldnotexpected: True
        SET:
          dtype: str
          type: set
    """

    invalid_missing_field = """
        Parameter:
          type: param
          dtype: float
          default: 0
        SET:
          dtype: str
          type: set
    """

    invalid_missing_index = """
        Parameter:
          indices: [SET, MISSING_SET]
          type: param
          dtype: float
          default: 0
        SET:
          dtype: str
          type: set
    """

    invalid_default = """
        Parameter:
          indices: [SET, MISSING_SET]
          type: param
          dtype: float
          default: s
        SET:
          dtype: str
          type: set
    """

    config_data = [
        invalid_dtype,
        invalid_name_length,
        invalid_name_spaces,
        invalid_name_numbers,
        invalid_name_special_chars,
        invalid_unexpected_field,
        invalid_missing_field,
        invalid_missing_index,
        invalid_default,
    ]
    config_data_ids = [
        "invalid_dtype",
        "invalid_name_length",
        "invalid_name_spaces",
        "invalid_name_numbers",
        "invalid_name_special_chars",
        "invalid_unexpected_field",
        "invalid_missing_field",
        "invalid_missing_index",
        "invalid_default",
    ]

    @mark.parametrize("config_data", config_data, ids=config_data_ids)
    def test_invalid_config_params(self, config_data):
        config = load(config_data, Loader=UniqueKeyLoader)
        with raises(ValueError):
            validate_config(config)


class TestInvalidConfigResults:
    invalid_dtype = """
        Result:
          type: param
          dtype: dict
          default: 0
          fieldnotexpected: True
        SET:
          dtype: str
          type: set
    """

    invalid_name_length = """
        ResultNameLongerThanThirtyOneChars:
          indices: [SET]
          type: result
          dtype: float
          default: 0
          calculated: True
        SET:
          dtype: str
          type: set
    """

    invalid_name_spaces = """
        Result Name With Spaces:
          indices: [SET]
          type: result
          dtype: float
          default: 0
          calculated: True
        SET:
          dtype: str
          type: set
    """

    invalid_name_numbers = """
        ResultNameWithNumbers123:
          indices: [SET]
          type: result
          dtype: float
          default: 0
          calculated: True
        SET:
          dtype: str
          type: set
    """

    # does not inlcude underscores
    invalid_name_special_chars = """
        ResultNameWithSpecialChars!@?%:
          indices: [SET]
          type: result
          dtype: float
          default: 0
          calculated: True
        SET:
          dtype: str
          type: set
    """

    invalid_unexpected_field = """
        Result:
          indices: [SET]
          type: result
          dtype: float
          default: 0
          calculated: True
          fieldnotexpected: True
        SET:
          dtype: str
          type: set
    """

    invalid_missing_field = """
        Result:
          indices: [SET]
          type: result
          dtype: float
          default: 0
        SET:
          dtype: str
          type: set
    """

    invalid_missing_index = """
        Result:
          indices: [SET, MISSING_SET]
          type: result
          dtype: float
          default: 0
          calculated: True
        SET:
          dtype: str
          type: set
    """

    invalid_default = """
        Result:
          indices: [SET]
          type: result
          dtype: float
          default: s
          calculated: True
        SET:
          dtype: str
          type: set
    """

    config_data = [
        invalid_dtype,
        invalid_name_length,
        invalid_name_spaces,
        invalid_name_numbers,
        invalid_name_special_chars,
        invalid_unexpected_field,
        invalid_missing_field,
        invalid_missing_index,
        invalid_default,
    ]
    config_data_ids = [
        "invalid_dtype",
        "invalid_name_length",
        "invalid_name_spaces",
        "invalid_name_numbers",
        "invalid_name_special_chars",
        "invalid_unexpected_field",
        "invalid_missing_field",
        "invalid_missing_index",
        "invalid_default",
    ]

    @mark.parametrize("config_data", config_data, ids=config_data_ids)
    def test_invalid_config_results(self, config_data):
        config = load(config_data, Loader=UniqueKeyLoader)
        with raises(ValueError):
            validate_config(config)
