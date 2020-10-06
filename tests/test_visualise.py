import tempfile

from otoole.visualise import create_res

url = (
    "https://zenodo.org/record/3707794/files/OSeMOSYS/simplicity-v0.2.1.zip?download=1"
)


def test_create_res():

    _, path_to_resfile = tempfile.mkstemp(suffix=".pdf")
    create_res(url, path_to_resfile)
