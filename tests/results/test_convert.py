from pytest import mark

from otoole.results.convert import process_line


class TestCplexToCsv:

    test_data = [
            (
                "AnnualFixedOperatingCost	REGION	AOBACKSTOP	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0		",
                []),
            (
                "AnnualFixedOperatingCost	REGION	CDBACKSTOP	0.0	0.0	137958.8400384134	305945.38410619126	626159.9611543404	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0",
                [
                'AnnualFixedOperatingCost,"REGION,CDBACKSTOP,2017",137958.8400384134\n',
                'AnnualFixedOperatingCost,"REGION,CDBACKSTOP,2018",305945.3841061913\n',
                'AnnualFixedOperatingCost,"REGION,CDBACKSTOP,2019",626159.9611543404\n']),
            (
                """RateOfActivity	REGION	S1D1	CGLFRCFURX	1	0.0	0.0	0.0	0.0	0.0	0.3284446367303371	0.3451714779880536	0.3366163200621617	0.3394945166233896	0.3137488154250392	0.28605725055560716	0.2572505015401749	0.06757558148965725	0.0558936625751148	0.04330608461292407	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0""",
                ['RateOfActivity,"REGION,S1D1,CGLFRCFURX,1,2020",0.3284446367303371\n',
                 'RateOfActivity,"REGION,S1D1,CGLFRCFURX,1,2021",0.3451714779880536\n',
                 'RateOfActivity,"REGION,S1D1,CGLFRCFURX,1,2022",0.3366163200621617\n',
                 'RateOfActivity,"REGION,S1D1,CGLFRCFURX,1,2023",0.3394945166233896\n',
                 'RateOfActivity,"REGION,S1D1,CGLFRCFURX,1,2024",0.3137488154250392\n',
                 'RateOfActivity,"REGION,S1D1,CGLFRCFURX,1,2025",0.28605725055560716\n',
                 'RateOfActivity,"REGION,S1D1,CGLFRCFURX,1,2026",0.2572505015401749\n',
                 'RateOfActivity,"REGION,S1D1,CGLFRCFURX,1,2027",0.06757558148965725\n',
                 'RateOfActivity,"REGION,S1D1,CGLFRCFURX,1,2028",0.0558936625751148\n',
                 'RateOfActivity,"REGION,S1D1,CGLFRCFURX,1,2029",0.04330608461292407\n']
            )
        ]

    @mark.parametrize("cplex_input,expected", test_data)
    def test_convert_from_cplex_to_cbc(self, cplex_input, expected):

        actual = process_line(cplex_input, 2015, 2070, 'csv')
        assert actual == expected

class TestCplexToCbc:

    test_data = [
            (
                "AnnualFixedOperatingCost	REGION	AOBACKSTOP	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0		",
                []),
            (
                "AnnualFixedOperatingCost	REGION	CDBACKSTOP	0.0	0.0	137958.8400384134	305945.38410619126	626159.9611543404	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0",
                [
                "0 AnnualFixedOperatingCost(REGION,CDBACKSTOP,2017) 137958.8400384134 0\n",
                "0 AnnualFixedOperatingCost(REGION,CDBACKSTOP,2018) 305945.3841061913 0\n",
                "0 AnnualFixedOperatingCost(REGION,CDBACKSTOP,2019) 626159.9611543404 0\n"]),
            (
                """RateOfActivity	REGION	S1D1	CGLFRCFURX	1	0.0	0.0	0.0	0.0	0.0	0.3284446367303371	0.3451714779880536	0.3366163200621617	0.3394945166233896	0.3137488154250392	0.28605725055560716	0.2572505015401749	0.06757558148965725	0.0558936625751148	0.04330608461292407	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0""",
                ["0 RateOfActivity(REGION,S1D1,CGLFRCFURX,1,2020) 0.3284446367303371 0\n",
                 "0 RateOfActivity(REGION,S1D1,CGLFRCFURX,1,2021) 0.3451714779880536 0\n",
                 "0 RateOfActivity(REGION,S1D1,CGLFRCFURX,1,2022) 0.3366163200621617 0\n",
                 "0 RateOfActivity(REGION,S1D1,CGLFRCFURX,1,2023) 0.3394945166233896 0\n",
                 "0 RateOfActivity(REGION,S1D1,CGLFRCFURX,1,2024) 0.3137488154250392 0\n",
                 "0 RateOfActivity(REGION,S1D1,CGLFRCFURX,1,2025) 0.28605725055560716 0\n",
                 "0 RateOfActivity(REGION,S1D1,CGLFRCFURX,1,2026) 0.2572505015401749 0\n",
                 "0 RateOfActivity(REGION,S1D1,CGLFRCFURX,1,2027) 0.06757558148965725 0\n",
                 "0 RateOfActivity(REGION,S1D1,CGLFRCFURX,1,2028) 0.0558936625751148 0\n",
                 "0 RateOfActivity(REGION,S1D1,CGLFRCFURX,1,2029) 0.04330608461292407 0\n"]
            )
        ]

    @mark.parametrize("cplex_input,expected", test_data)
    def test_convert_from_cplex_to_cbc(self, cplex_input, expected):

        actual = process_line(cplex_input, 2015, 2070, 'cbc')
        assert actual == expected
