import os
from subprocess import run
from tempfile import NamedTemporaryFile, mkdtemp

from pytest import mark

from otoole import __version__


class TestConvert:
    def test_version(self):
        result = run(["otoole", "--version"], capture_output=True)
        assert result.stdout.strip().decode() == str(__version__)

    temp = mkdtemp()
    temp_excel = NamedTemporaryFile(suffix=".xlsx")
    temp_datafile = NamedTemporaryFile(suffix=".dat")
    simplicity = os.path.join("tests", "fixtures", "simplicity.txt")
    config_path = os.path.join("tests", "fixtures", "config.yaml")

    test_data = [
        (["otoole", "-v", "convert", "--help"], "usage: otoole convert [-h]"),
        (
            [
                "otoole",
                "-v",
                "convert",
                "datafile",
                "excel",
                simplicity,
                temp_excel.name,
                config_path,
            ],
            "",
        ),
        (
            [
                "otoole",
                "-v",
                "convert",
                "datafile",
                "datafile",
                simplicity,
                temp_datafile.name,
                config_path,
            ],
            "",
        ),
    ]

    @mark.parametrize("commands,expected", test_data, ids=["help", "excel", "datafile"])
    def test_convert_commands(self, commands, expected):
        actual = run(commands, capture_output=True)
        assert expected in str(actual.stdout)
        print(" ".join(commands))
        assert actual.returncode == 0, print(actual.stdout)

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
        temp_datafile = NamedTemporaryFile(suffix=".dat")
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

    def test_convert_datafile_datafile_with_user_config(self):
        simplicity = os.path.join("tests", "fixtures", "simplicity.txt")
        user_config = os.path.join("tests", "fixtures", "config.yaml")
        temp_datafile = NamedTemporaryFile(suffix=".dat")
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

    def test_convert_datafile_datafile_with_default_flag(self):
        simplicity = os.path.join("tests", "fixtures", "simplicity.txt")
        user_config = os.path.join("tests", "fixtures", "config.yaml")
        temp_datafile = NamedTemporaryFile(suffix=".dat")
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


class TestSetup:

    temp = mkdtemp()
    temp_config = NamedTemporaryFile(suffix=".yaml")

    test_data = [
        (
            [
                "otoole",
                "-v",
                "setup",
                "config",
                NamedTemporaryFile(suffix=".yaml").name,
            ],
            "",
        ),
        (["otoole", "-v", "setup", "config", temp_config.name, "--overwrite"], ""),
    ]

    @mark.parametrize(
        "commands,expected", test_data, ids=["setup", "setup_with_overwrite"]
    )
    def test_setup_commands(self, commands, expected):
        actual = run(commands, capture_output=True)
        assert expected in str(actual.stdout)
        print(" ".join(commands))
        assert actual.returncode == 0, print(actual.stdout)

    test_errors = [
        (["otoole", "-v", "setup", "config", temp_config.name], "OtooleSetupError"),
    ]

    @mark.parametrize("commands,expected", test_errors, ids=["setup_fails"])
    def test_setup_error(self, commands, expected):
        actual = run(commands, capture_output=True)
        assert expected in str(actual.stderr)
