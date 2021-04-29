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
    temp_excel = NamedTemporaryFile(suffix="xlsx")
    temp_datafile = NamedTemporaryFile(suffix="dat")
    simplicity = os.path.join("tests", "fixtures", "simplicity.txt")

    test_data = [
        (["otoole", "convert", "--help"], "usage: otoole convert [-h]"),
        (["otoole", "convert", "datafile", "datapackage", simplicity, temp], ""),
        (["otoole", "convert", "datafile", "excel", simplicity, temp_excel.name], ""),
        (
            [
                "otoole",
                "convert",
                "datafile",
                "datafile",
                simplicity,
                temp_datafile.name,
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
