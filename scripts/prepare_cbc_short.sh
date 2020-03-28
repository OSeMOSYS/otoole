# Run OSeMOSYS using CBC and compare results with run using GLPK
curl https://zenodo.org/record/3707794/files/OSeMOSYS/simplicity-v0.2.1.zip -o simplicity.zip
unzip -fo simplicity.zip
otoole convert datapackage datafile OSeMOSYS-simplicity-* simplicity.txt

sed '$d' simplicity.txt > trimmed.txt
echo "param ResultsPath := results;" >> trimmed.txt
echo "end;" >> trimmed.txt

# Omitting --check, which runs the solve using GLPK as well
glpsol --wlp simplicity.lp -m ../osemosys/OSeMOSYS_GNU_MathProg/src/osemosys_short.txt -d trimmed.txt
cbc simplicity.lp -dualpivot pesteep -psi 1.0 -pertv 52 -duals solve -solu simplicity.sol
otoole -vvv results cbc csv simplicity.sol output --input_data OSeMOSYS-simplicity-11a3a26/datapackage.json

ls output > output_files
ls results > result_file
diff -wylNs output_files result_file
