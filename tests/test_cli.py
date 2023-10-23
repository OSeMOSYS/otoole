import os
from subprocess import run
from tempfile import NamedTemporaryFile, mkdtemp

from pytest import mark

from otoole import __version__


class TestResults:
    """Test the conversion of results via the command line interface"""

    def test_convert_results(self):
        """Test converting CBC solution file to folder of CSVs"""
        config = os.path.join("tests", "fixtures", "super_simple", "super_simple.yaml")
        super_simple_csvs = os.path.join("tests", "fixtures", "super_simple", "csv")
        from_format = "cbc"
        to_format = "csv"
        from_path = os.path.join(
            "tests", "fixtures", "super_simple", "super_simple_gnu.sol"
        )
        to_path = mkdtemp()
        commands = [
            "otoole",
            "results",
            from_format,
            to_format,
            from_path,
            to_path,
            "csv",
            super_simple_csvs,
            config,
        ]
        actual = run(commands, capture_output=True)
        assert actual.returncode == 0, print(actual.stdout)
        assert os.path.exists(os.path.join(to_path, "NewCapacity.csv"))


class TestConvert:
    def test_version(self):
        result = run(["otoole", "--version"], capture_output=True)
        assert result.stdout.strip().decode() == str(__version__)

    def test_help(self):
        commands = ["otoole", "-v", "convert", "--help"]
        expected = "usage: otoole convert [-h]"
        actual = run(commands, capture_output=True)
        assert expected in str(actual.stdout)
        assert actual.returncode == 0, print(actual.stdout)

    temp = mkdtemp()
    simplicity = os.path.join("tests", "fixtures", "simplicity.txt")
    config_path = os.path.join("tests", "fixtures", "config.yaml")

    test_data = [
        (
            "excel",
            [
                "otoole",
                "-v",
                "convert",
                "datafile",
                "excel",
                simplicity,
                "convert_to_file_path",  # replaced with NamedTemporaryFile
                config_path,
            ],
            "",
        ),
        (
            "datafile",
            [
                "otoole",
                "-v",
                "convert",
                "datafile",
                "datafile",
                simplicity,
                "convert_to_file_path",  # replaced with NamedTemporaryFile
                config_path,
            ],
            "",
        ),
    ]

    @mark.parametrize(
        "convert_to,commands,expected", test_data, ids=["excel", "datafile"]
    )
    def test_convert_commands(self, convert_to, commands, expected):
        if convert_to == "datafile":
            temp = NamedTemporaryFile(suffix=".dat", delete=False, mode="w")
        elif convert_to == "excel":
            temp = NamedTemporaryFile(suffix=".xlsx", delete=False, mode="w")
        else:
            raise NotImplementedError
        try:
            commands_adjusted = [
                x if x != "convert_to_file_path" else temp.name for x in commands
            ]
            actual = run(commands_adjusted, capture_output=True)
            assert expected in str(actual.stdout)
            print(" ".join(commands_adjusted))
            assert actual.returncode == 0, print(actual.stdout)
        finally:
            temp.close()
            os.unlink(temp.name)

    test_errors = [
        (
            ["otoole", "convert", "datafile", "cplex", "x", "y", config_path],
            "error: argument to_format: invalid choice: 'cplex'",
        )
    ]

    @mark.parametrize("commands,expected", test_errors, ids=["invalid"])
    def test_convert_error(self, commands, expected):
        actual = run(commands, capture_output=True)
        assert expected in str(actual.stderr)

    def test_convert_datafile_datafile_no_user_config(self):
        simplicity = os.path.join("tests", "fixtures", "simplicity.txt")
        temp_datafile = NamedTemporaryFile(suffix=".dat", delete=False, mode="w")
        try:
            commands = [
                "otoole",
                "convert",
                "datafile",
                "datafile",
                simplicity,
                temp_datafile.name,
            ]
            actual = run(commands, capture_output=True)
            assert actual.returncode == 2
        finally:
            temp_datafile.close()
            os.unlink(temp_datafile.name)

    def test_convert_datafile_datafile_with_user_config(self):
        simplicity = os.path.join("tests", "fixtures", "simplicity.txt")
        user_config = os.path.join("tests", "fixtures", "config.yaml")
        temp_datafile = NamedTemporaryFile(suffix=".dat", delete=False, mode="w")
        try:
            commands = [
                "otoole",
                "-vvv",
                "convert",
                "datafile",
                "datafile",
                simplicity,
                temp_datafile.name,
                user_config,
            ]
            actual = run(commands, capture_output=True)
            assert actual.returncode == 0
        finally:
            temp_datafile.close()
            os.unlink(temp_datafile.name)

    def test_convert_datafile_datafile_with_default_flag(self):
        simplicity = os.path.join("tests", "fixtures", "simplicity.txt")
        user_config = os.path.join("tests", "fixtures", "config.yaml")
        temp_datafile = NamedTemporaryFile(suffix=".dat", delete=False, mode="w")
        try:
            commands = [
                "otoole",
                "-vvv",
                "convert",
                "datafile",
                "datafile",
                simplicity,
                temp_datafile.name,
                user_config,
                "--write_defaults",
            ]
            actual = run(commands, capture_output=True)
            assert actual.returncode == 0
        finally:
            temp_datafile.close()
            os.unlink(temp_datafile.name)


class TestSetup:

    test_data = [
        (
            [
                "otoole",
                "-v",
                "setup",
                "config",
                NamedTemporaryFile(
                    suffix=".yaml"
                ).name,  # representes a new config file
            ],
            "",
        ),
        (["otoole", "-v", "setup", "config", "temp_file", "--overwrite"], ""),
    ]

    @mark.parametrize(
        "commands,expected", test_data, ids=["setup", "setup_with_overwrite"]
    )
    def test_setup_commands(self, commands, expected):
        temp_yaml = NamedTemporaryFile(suffix=".yaml", delete=False, mode="w+b")
        try:
            commands_adjusted = [
                x if x != "temp_file" else temp_yaml.name for x in commands
            ]
            actual = run(commands_adjusted, capture_output=True)
            assert expected in str(actual.stdout)
            print(" ".join(commands_adjusted))
            assert actual.returncode == 0, print(actual.stdout)
        finally:
            temp_yaml.close()
            os.unlink(temp_yaml.name)

    test_errors = [
        (["otoole", "-v", "setup", "config", "temp_file"], "OtooleSetupError"),
    ]

    @mark.parametrize("commands,expected", test_errors, ids=["setup_fails"])
    def test_setup_error(self, commands, expected):
        temp_yaml = NamedTemporaryFile(suffix=".yaml", delete=False, mode="w")
        try:
            commands_adjusted = [
                x if x != "temp_file" else temp_yaml.name for x in commands
            ]
            actual = run(commands_adjusted, capture_output=True)
            assert expected in str(actual.stderr)
        finally:
            temp_yaml.close()
            os.unlink(temp_yaml.name)
