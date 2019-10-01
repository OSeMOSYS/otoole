from otoole.preprocess.excel_to_osemosys import _insert_table


def test_insert_table():

    data = [["TECHNOLOGY", "2014", "2015"],
            ["BACKSTOP1", 999999.0, "999999.0"],
            ["BACKSTOP2", 999999.0, "999999.0"]
            ]

    actual = _insert_table('bla', data)

    expected = "2014 2015 :=\nBACKSTOP1 999999.0 999999.0\nBACKSTOP2 999999.0 999999.0\n;\n"

    assert actual == expected
