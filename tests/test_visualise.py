import tempfile

import pytest

from otoole.visualise import create_res

url = "tests/fixtures/simplicity-v0.2.1.zip"


@pytest.mark.skip(
    "pydot deprecated, requires replacement with pygraphviz "
    + "(https://github.com/OSeMOSYS/otoole/issues/121)"
)
def test_create_res():

    _, path_to_resfile = tempfile.mkstemp(suffix=".pdf")
    create_res(url, path_to_resfile)
