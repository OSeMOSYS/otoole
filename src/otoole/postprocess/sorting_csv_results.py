# a simple script to sort the OSeMOSYS css_result_tables and save the result into a new dataframe
# applied on the variable "ProductionByTechnology"

technologies = ["tech1","tech2","tech_n"]

# import data from ProductionByTechnology

csv_result = pd.read_csv("#path", sep=",", decimal=".")

# create empty dataframe
df_filtered = pd.DataFrame()
# filter for desired technology & fuel pairs in columns t - technologies, and f - fuel and create an index
index = [i for i,(s1,s2) in enumerate(zip(csv_result.t, csv_result.f)) if ((s1 in technologies) & (s2 == "fuel_electricity"))]
# loop through the csv result table "ProductionByTechnology" at the position of the filtered indexes (tech_fuel_pairs) and group the columns: t - technologies, and f - fuel
for tech_fuel_pair, df in csv_result.iloc[index].groupby(["t","f"]):
    # write the filtered pairs into a reduced dataframe, only saving the columns: t - technologies, and f - fuel, and the value; additionally set the index to the name of the respective timeslice
    df_reduced = df.loc[:,["l","ProductionByTechnology"]].set_index("l", drop=True)
    # rename the column header to the "tech_fuel_pair" - indicating the tech - fuel relation
    df_reduced.rename(columns={"ProductionByTechnology":str(tech_pair)}, inplace=True)
    # add the filtered "tech_fuel_pair" column to the filtered dataframe; add the tech_fuel_pairs column by column;
    df_filtered = pd.concat([df_filtered, df_reduced], axis=1)

# save the filtered dataframe with all filtered technology fuel paris for further post-processing
df_filtered.to_csv(path_or_buf=r'#path', index=True)