from pytest import mark

import os
from subprocess import run
from tempfile import NamedTemporaryFile, mkdtemp

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
                "datapackage",
                simplicity,
                temp,
                "-c",
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
                "excel",
                simplicity,
                temp_excel.name,
                "-c",
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
                "-c",
                config_path,
            ],
            "",
        ),
    ]

    @mark.parametrize(
        "commands,expected", test_data, ids=["help", "datapackage", "excel", "datafile"]
    )
    def test_convert_commands(self, commands, expected):
        actual = run(commands, capture_output=True)
        assert expected in str(actual.stdout)
        print(" ".join(commands))
        assert actual.returncode == 0, print(actual.stdout)

    test_errors = [
        (
            ["otoole", "convert", "datafile", "cplex", "x", "y"],
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
        assert actual.returncode == 1
        assert (
            actual.stdout
            == b"ValueError: A user configuration must be passed into the reader\n"
        )

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
            "-c",
            user_config,
        ]
        actual = run(commands, capture_output=True)
        assert actual.returncode == 0
