import tempfile

from otoole.visualise import create_res


def test_create_res():

    url = 'https://raw.githubusercontent.com/OSeMOSYS/simplicity/master/datapackage.json'
    _, path_to_resfile = tempfile.mkstemp(suffix='.pdf')
    create_res(url, path_to_resfile)
