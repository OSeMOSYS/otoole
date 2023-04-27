from pytest import mark, raises
from yaml import SafeLoader, load

from otoole.exceptions import OtooleConfigFileError
from otoole.utils import UniqueKeyLoader, validate_config


class TestValidConfigs:
    valid_set = """
        SET_NAME:
          dtype: str
          type: set
          short_name: SET
    """

    valid_parameter_1 = """
        Parameter_Name:
          indices: [SET]
          type: param
          dtype: float
          default: 0
        SET:
          dtype: str
          type: set
    """

    valid_parameter_2 = """
        Parameter_Name:
          indices: [SET]
          type: param
          dtype: float
          default: 0
          short_name: Parameter
        SET:
          dtype: str
          type: set
    """

    valid_result_1 = """
        Result_Name:
          indices: [SET]
          type: result
          dtype: float
          default: 0
        SET:
          dtype: str
          type: set
    """

    valid_result_2 = """
        Result_Name:
          indices: [SET]
          type: result
          dtype: float
          default: 0
          calculated: True
          short_name: Result
        SET:
          dtype: str
          type: set
    """

    config_data = [
        valid_set,
        valid_parameter_1,
        valid_parameter_2,
        valid_result_1,
        valid_result_2,
    ]

    config_data_ids = [
        "valid_set",
        "valid_parameter_1",
        "valid_parameter_2",
        "valid_result_1",
        "valid_result_2",
    ]

    @mark.parametrize("config_data", config_data, ids=config_data_ids)
    def test_valid_configs(self, config_data):
        config = load(config_data, Loader=SafeLoader)
        validate_config(config)


class TestInvalidConfigs:
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
        Result:
          indices: [SET]
          type: result
          dtype: float
          default: 0
        SET:
          dtype: str
          type: set
    """

    invalid_duplicate_names_diff_types_1 = """
        Parameter:
          indices: [SET]
          type: param
          dtype: float
          default: 0
        Parameter:
          dtype: str
          type: set
    """

    invalid_duplicate_names_diff_types_2 = """
        Parameter:
          indices: [SET]
          type: param
          dtype: float
          default: 0
        PARAMETER:
          dtype: str
          type: set
    """

    config_data_duplicates = [
        invalid_duplicate_set_names,
        invalid_duplicate_param_names,
        invalid_duplicate_result_names,
        invalid_duplicate_names_diff_types_1,
        invalid_duplicate_names_diff_types_2,
    ]

    config_data_duplicates_ids = [
        "invalid_duplicate_set_names",
        "invalid_duplicate_param_names",
        "invalid_duplicate_result_names",
        "invalid_duplicate_names_diff_types_1",
        "invalid_duplicate_names_diff_types_2",
    ]

    @mark.parametrize(
        "config_data", config_data_duplicates, ids=config_data_duplicates_ids
    )
    def test_invalid_config_multi_defs(self, config_data):
        with raises(ValueError):
            load(config_data, Loader=UniqueKeyLoader)


class TestUserDefinedValue:
    invalid_set_type = """
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
        SET:
          dtype: str
          type: set
    """

    invalid_name_spaces = """
        Parameter With Spaces:
          indices: [SET]
          type: param
          dtype: float
          default: 0
        SET:
          dtype: str
          type: set
    """

    invalid_name_numbers = """
        Parameter12345:
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
        Parameter!@?%[):
          indices: [SET]
          type: param
          dtype: float
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

    invalid_short_name_spaces = """
        Parameter:
          short_name: Parameter Short Name
          indices: [SET]
          type: param
          dtype: float
          default: 0
        SET:
          dtype: str
          type: set
    """

    invalid_short_name_numbers = """
        Parameter:
          short_name: ParameterShortName12345
          indices: [SET]
          type: param
          dtype: float
          default: 0
        SET:
          dtype: str
          type: set
    """

    # does not inlcude underscores
    invalid_short_name_special_chars = """
        Parameter:
          short_name: ParameterShortName!@?%[)
          indices: [SET]
          type: param
          dtype: float
          default: 0
        SET:
          dtype: str
          type: set
    """

    invalid_short_name_length_1 = """
        Parameter:
          short_name: ParameterShortNameLongerThanThirtyOneChars
          indices: [SET]
          type: param
          dtype: float
          default: 0
        SET:
          dtype: str
          type: set
    """

    invalid_short_name_length_2 = """
        ParameterNameLongerThanThirtyOneChars:
          short_name: ParameterShortNameLongerThanThirtyOneChars
          indices: [SET]
          type: param
          dtype: float
          default: 0
        SET:
          dtype: str
          type: set
    """

    config_data_invalid = [
        invalid_set_type,
        invalid_parameter_type,
        invalid_result_type,
        invalid_name_spaces,
        invalid_name_numbers,
        invalid_name_special_chars,
        invalid_name_length,
        invalid_short_name_spaces,
        invalid_short_name_numbers,
        invalid_short_name_special_chars,
        invalid_short_name_length_1,
        invalid_short_name_length_2,
    ]

    config_data_invalid_ids = [
        "invalid_set_type",
        "invalid_parameter_type",
        "invalid_result_type",
        "invalid_name_spaces",
        "invalid_name_numbers",
        "invalid_name_special_chars",
        "invalid_name_length",
        "invalid_short_name_spaces",
        "invalid_short_name_numbers",
        "invalid_short_name_special_chars",
        "invalid_short_name_length_1",
        "invalid_short_name_length_2",
    ]

    @mark.parametrize("config_data", config_data_invalid, ids=config_data_invalid_ids)
    def test_invalid_configs(self, config_data):
        config = load(config_data, Loader=UniqueKeyLoader)
        with raises(OtooleConfigFileError):
            validate_config(config)


class TestUserDefinedSet:
    invalid_dtype = """
        SET:
          dtype: float
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
        invalid_unexpected_field,
        invalid_missing_field,
    ]

    config_data_ids = [
        "invalid_dtype",
        "invalid_unexpected_field",
        "invalid_missing_field",
    ]

    @mark.parametrize("config_data", config_data, ids=config_data_ids)
    def test_invalid_config_sets(self, config_data):
        config = load(config_data, Loader=UniqueKeyLoader)
        with raises(OtooleConfigFileError):
            validate_config(config)


class TestUserDefinedParameter:
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
        invalid_unexpected_field,
        invalid_missing_field,
        invalid_missing_index,
        invalid_default,
    ]
    config_data_ids = [
        "invalid_dtype",
        "invalid_unexpected_field",
        "invalid_missing_field",
        "invalid_missing_index",
        "invalid_default",
    ]

    @mark.parametrize("config_data", config_data, ids=config_data_ids)
    def test_invalid_config_params(self, config_data):
        config = load(config_data, Loader=UniqueKeyLoader)
        with raises(OtooleConfigFileError):
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

    invalid_unexpected_field = """
        Result:
          indices: [SET]
          type: result
          dtype: float
          default: 0
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
        SET:
          dtype: str
          type: set
    """

    config_data = [
        invalid_dtype,
        invalid_unexpected_field,
        invalid_missing_field,
        invalid_missing_index,
        invalid_default,
    ]
    config_data_ids = [
        "invalid_dtype",
        "invalid_unexpected_field",
        "invalid_missing_field",
        "invalid_missing_index",
        "invalid_default",
    ]

    @mark.parametrize("config_data", config_data, ids=config_data_ids)
    def test_invalid_config_results(self, config_data):
        config = load(config_data, Loader=UniqueKeyLoader)
        with raises(OtooleConfigFileError):
            validate_config(config)
