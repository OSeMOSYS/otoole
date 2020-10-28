import tempfile

from otoole.visualise import create_res

url = "tests/fixtures/simplicity-v0.2.1.zip"


def test_create_res():

    _, path_to_resfile = tempfile.mkstemp(suffix=".pdf")
    create_res(url, path_to_resfile)
