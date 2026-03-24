import pandas as pd
import json

# Read Sample data from CSV file
def read_sample_data(file, table_info_dict):
    df = pd.read_excel(file, header=None, dtype=str)
    df.dropna(how='all')
    table_name = ""
    found_coulmn = False
    for row in df.itertuples(index=False):                
        if pd.isna(row[1]) and type(row[0]).__name__ == 'str': 
            if "." in row[0]:
                table_name = row[0].split(".")[1]
            found_coulmn = False
        elif len(row) > 2 and not found_coulmn:
            found_coulmn = True
        elif len(row) > 2 and found_coulmn:
            if table_name in table_info_dict["tables"]:
                table_info_dict["tables"][table_name]["sample_data"].append(list(row))
# Extract columns from the CSV file and create a dictionary with column information
def extract_columns(file):
    table_info_dict = {}
    table_info_dict["tables"] = {}
    table_info_dict["columns"] = {}
    table_cols = {}
    df = pd.read_csv(file, skiprows=0)
    table_name = None    
    for _, row in df.iterrows():
        if len(row) == 4:
            if table_name == row[1]:
                table_cols[row[2]] = row[3]
            else:
                if len(table_cols)>0 and table_name!=row[1]:
                    table_info_dict["tables"][table_name]= {}
                    table_info_dict["tables"][table_name]["cols"]= table_cols
                    table_info_dict["tables"][table_name]["description"]= ""
                    table_info_dict["tables"][table_name]["sample_data"]= []
                    table_cols = {}
                table_cols[row[2]] = row[3]
                table_name = row[1]
    return table_info_dict

#Creates the proper JSON file
def save_json(output, file_name):
    with open(file_name, "w") as f:
        json.dump(output, f, indent=4)

if __name__ == "__main__":

    table_info_dict = extract_columns("data/omop/EDWMetadata.csv")
    data = read_sample_data("data/omop/EDW_Sample_Data.xlsx", table_info_dict)   
    save_json(table_info_dict, "data/table_description.json")
    print("Translation complete. Output saved to output.json")