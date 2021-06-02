"""

read_strategy = None
write_strategy = None

if args.from_format == "datafile":
    read_strategy = ReadDatafile()
elif args.from_format == "datapackage":
    read_strategy = ReadDatapackage()
elif args.from_format == "csv":
    read_strategy = ReadCsv()
elif args.from_format == "excel":
    read_strategy = ReadExcel()

if args.to_format == "datapackage":
    write_strategy = WriteDatapackage()
elif args.to_format == "excel":
    write_strategy = WriteExcel()
elif args.to_format == "datafile":
    write_strategy = WriteDatafile()
elif args.to_format == "csv":
    write_strategy = WriteCsv()

if read_strategy and write_strategy:
    context = Context(read_strategy, write_strategy)
    context.convert(args.from_path, args.to_path)
else:
    raise NotImplementedError(msg)

"""
import os
from tempfile import NamedTemporaryFile, TemporaryDirectory

from otoole import Context, ReadExcel, WriteCsv, WriteDatafile


class TestConvert:
    def test_convert_excel_to_datafile(self):

        read_strategy = ReadExcel()
        write_strategy = WriteDatafile()
        context = Context(read_strategy, write_strategy)

        tmpfile = NamedTemporaryFile()
        from_path = os.path.join("tests", "fixtures", "combined_inputs.xlsx")

        context.convert(from_path, tmpfile.name)

        tmpfile.seek(0)
        actual = tmpfile.readlines()
        tmpfile.close()

        assert actual[-1] == b"end;\n"
        assert actual[0] == b"# Model file written by *otoole*\n"
        assert actual[2] == b"09_ROK d_bld_2_coal_products 2017 20.8921\n"
        assert actual[8996] == b"param default 1 : DepreciationMethod :=\n"

    def test_convert_excel_to_csv(self):

        read_strategy = ReadExcel()
        write_strategy = WriteCsv()
        context = Context(read_strategy, write_strategy)

        tmpfile = TemporaryDirectory()
        from_path = os.path.join("tests", "fixtures", "combined_inputs.xlsx")

        context.convert(from_path, tmpfile.name)

        with open(os.path.join(tmpfile.name, "EMISSION.csv")) as csv_file:
            csv_file.seek(0)
            actual = csv_file.readlines()

        assert actual[-1] == "NOX\n"
        assert actual[0] == "VALUE\n"
        assert actual[1] == "CO2\n"
