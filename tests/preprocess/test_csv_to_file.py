from otoole.preprocess.excel_to_osemosys import (
    _build_result_string,
    _insert_no_variables,
    _insert_table,
    _insert_variables
)


class TestWritingFunctions:

    def test_insert_table(self):

        data = [["TECHNOLOGY", "2014", "2015"],
                ["BACKSTOP1", 999999.0, "999999.0"],
                ["BACKSTOP2", 999999.0, "999999.0"]
                ]

        actual = _insert_table('bla', data, default=99999, region=False)

        expected = "param bla default 99999 :=\n2014 2015 :=\n" + \
                   "BACKSTOP1 999999.0 999999.0\nBACKSTOP2 999999.0 999999.0\n;\n"

        assert actual == expected

    def test_insert_table_empty(self):

        data = []

        actual = _insert_table('bla', data, default=1, region=False)

        expected = "param bla default 1 :=\n;\n"

        assert actual == expected

    def test_insert_two_variables(self):
        """
        Read from this format::

            "TECHNOLOGY","TIMESLICE",2014.0,2015.0,
            "HYD1","ID",0.4
            "HYD1","IN",0.4

        Write into this format::

            param CapacityFactor default 1 :=
            [SIMPLICITY,HYD1,*,*]:
            2014 2015 :=
            ID 0.4 0.4
            IN 0.4 0.4
        """

        data = [["TECHNOLOGY", "TIMESLICE", "2014", "2015"],
                ["HYD1", "ID", 0.4, 0.4],
                ["HYD1", "IN", 0.4, 0.4]
                ]

        actual = _insert_variables(data, 2)

        expected = "[SIMPLICITY, HYD1, *, *]:\n2014 2015 :=\nID 0.4 0.4\nIN 0.4 0.4\n;\n"

        assert actual == expected

    def test_insert_two_variables_complex(self):
        """
        Read from this format::

            "TECHNOLOGY","TIMESLICE",2014.0,2015.0,
            "HYD1","ID",0.4,0.4
            "HYD1","IN",0.4,0.4
            "RIVER","ID",0.11,0.12
            "RIVER","IN",0.21,0.22

        Write into this format::

            param CapacityFactor default 1 :=
            [SIMPLICITY,HYD1,*,*]:
            2014 2015 :=
            ID 0.4 0.4
            IN 0.4 0.4
            [SIMPLICITY,RIVER,*,*]:
            2014 2015 :=
            ID 0.11 0.12
            IN 0.21 0.22
        """

        data = [["TECHNOLOGY", "FUEL", "2014", "2015"],
                ["HYD1", "ID", 0.4, 0.4],
                ["HYD1", "IN", 0.4, 0.4],
                ["RIVER", "ID", 0.11, 0.12],
                ["RIVER", "IN", 0.21, 0.22]
                ]

        actual = _insert_variables(data, 2)

        expected = "[SIMPLICITY, HYD1, *, *]:\n2014 2015 :=\nID 0.4 0.4\nIN 0.4 0.4\n" + \
                   "[SIMPLICITY, RIVER, *, *]:\n2014 2015 :=\nID 0.11 0.12\nIN 0.21 0.22\n;\n"

        assert actual == expected

    def test_no_variables(self):
        """
        From::

            "TECHNOLOGY","VALUE"
            "BACKSTOP1",1.0
            "BACKSTOP2",1.0
            "BIOMASSPRO",1.0
            "CHP",1.0

        To::

            param CapacityToActivityUnit default 1 :\n
            BACKSTOP1 BACKSTOP2 BIOMASSPRO CHP:=\n
            SIMPLICITY 1 1 1 1\n
            ;\n

        """
        data = [
                ["TECHNOLOGY", "VALUE"],
                ["BACKSTOP1", 1.0],
                ["BACKSTOP2", 1.0],
                ["BIOMASSPRO", 1.0],
                ["CHP", 1.0]
                ]

        actual = _insert_no_variables(data)

        expected = "BACKSTOP1 BACKSTOP2 BIOMASSPRO CHP:=\nSIMPLICITY 1.0 1.0 1.0 1.0\n;\n"

        assert actual == expected


class TestDataProcess:

    def test_annual_exogenous_emission(self):

        data = {'AnnualExogenousEmission':
                [["EMISSION", 2014.0, 2015.0], ["CO2", 0.05, 0.05]]
                }
        actual = _build_result_string(data)
        expected = "param AnnualExogenousEmission default 0 :=\n" + \
                   "[SIMPLICITY, *, *]:\n" + \
                   "2014.0 2015.0 :=\nCO2 0.05 0.05\n;\n"

        assert actual == expected
