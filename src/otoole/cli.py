import argparse

from otoole.results.convert import convert_cplex_file


def main():
    parser = argparse.ArgumentParser(description="Otoole: Python toolkit of OSeMOSYS users")
    parser.add_argument("cplex_file",
                        help="The filepath of the OSeMOSYS cplex output file")
    parser.add_argument("output_file",
                        help="The filepath of the converted file that will be written")
    parser.add_argument("-s", "--start_year", type=int, default=2015,
                        help="Output only the results from this year onwards")
    parser.add_argument("-e", "--end_year", type=int, default=2070,
                        help="Output only the results upto and including this year")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--csv", action="store_true",
                       help="Output file in comma-separated-values format")
    group.add_argument("--cbc", action="store_true",
                       help="Output file in CBC format, (default option)")
    args = parser.parse_args()

    if args.csv:
        output_format = 'csv'
    else:
        output_format = 'cbc'

    convert_cplex_file(args.cplex_file, args.output_file,
                       args.start_year, args.end_year,
                       output_format)
