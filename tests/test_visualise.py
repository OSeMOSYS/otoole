import tempfile

from otoole.visualise import create_res

SIMPLICITY_VERSION = 'v0.1a0'


def test_create_res():

    url = 'https://github.com/OSeMOSYS/simplicity/archive/{}.zip'.format(SIMPLICITY_VERSION)
    _, path_to_resfile = tempfile.mkstemp(suffix='.pdf')
    create_res(url, path_to_resfile)
