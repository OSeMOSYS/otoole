from otoole.preprocess.excel_to_osemosys import (
    _build_result_string,
    _insert_no_variables,
    _insert_parameter_table,
    _insert_table,
    read_config
)


class TestConfig:

    def test_read_config(self):

        actual = read_config()
        expected = {
                        'indices': ['REGION', 'FUEL', 'YEAR'],
                        'type': 'param',
                        'default': 0
                    }
        assert actual['AccumulatedAnnualDemand'] == expected


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

        actual = _insert_parameter_table(data, 2)

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

        actual = _insert_parameter_table(data, 2)

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

        expected = "\nBACKSTOP1 BACKSTOP2 BIOMASSPRO CHP:=\nSIMPLICITY 1.0 1.0 1.0 1.0\n;\n"

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

    def test_model_period_exo_emiss_empty(self):

        data = {'ModelPeriodExogenousEmission': []}
        actual = _build_result_string(data)
        expected = "param ModelPeriodExogenousEmission default 0 :=\n;\n"

        assert actual == expected

    def test_operational_life(self):

        data = {'OperationalLife': [["TECHNOLOGY", "VALUE"],
                                    ["BACKSTOP1", 1.0],
                                    ["BACKSTOP2", 1.0]]}

        expected = "param OperationalLife default 1 :\n" + \
                   "BACKSTOP1 BACKSTOP2:=\n" + \
                   "SIMPLICITY 1.0 1.0\n" + \
                   ";\n"
        actual = _build_result_string(data)
        assert actual == expected

    def test_operational_life_headers_only(self):

        data = {'OperationalLife': [["TECHNOLOGY", "VALUE"]]}

        expected = "param OperationalLife default 1 :=\n" + \
                   ";\n"
        actual = _build_result_string(data)
        assert actual == expected

    def test_year_split(self):

        data = {'YearSplit':
                [["TIMESLICE", 2014.0, 2015.0],
                 ["ID", 0.1667, 0.1667],
                 ["IN", 0.0833, 0.0833],
                 ["SD", 0.1667, 0.1667],
                 ["SN", 0.0833, 0.0833],
                 ["WD", 0.3333, 0.3333],
                 ["WN", 0.1667, 0.1667]]}
        expected = "param YearSplit default 0 :\n" + \
                   "2014.0 2015.0:=\n" + \
                   "ID 0.1667 0.1667\n" + \
                   "IN 0.0833 0.0833\n" + \
                   "SD 0.1667 0.1667\n" + \
                   "SN 0.0833 0.0833\n" + \
                   "WD 0.3333 0.3333\n" + \
                   "WN 0.1667 0.1667\n"
        actual = _build_result_string(data)
        assert actual == expected
