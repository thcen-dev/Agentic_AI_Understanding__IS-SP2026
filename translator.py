import pandas as pd
import json

# Read Sample data from CSV file
def read_sample_data(file, columns_dict):
    sample_data = []
    df = pd.read_excel(file, header=None)
    df.dropna(how='all')
    table_name = ""
    columns = []
    found_coulmn = False
    for row in df.itertuples(index=False):                
        if pd.isna(row[1]):
            table_name = row[0]
            found_coulmn = False
        elif len(row) > 2 and not found_coulmn:
            found_coulmn = True
            columns = [str(col) for col in row if not pd.isna(col)]
        elif len(row) > 2 and found_coulmn:            
                for index, data in enumerate(row):
                    if index == len(columns):
                        break
                    if f"{table_name}.{columns[index]}" in columns_dict and not pd.isna(data):
                            columns_dict[f"{table_name}.{columns[index]}"]['data_type'] = type(data).__name__
                            columns_dict[f"{table_name}.{columns[index]}"]['sample_data'].append(str(data))  

#Pulls column names
def extract_columns(file):
    columns_dict = {}
    columns = []
    df = pd.read_csv(file, skiprows=0)    
    for _, row in df.iterrows():
        if len(row) == 4:
            column_info = {
                "column_name": f"{row[2]}",
                "table_name": f"{row[1]}",
                "table_description": "",
                "data_type": "",
                "column_description": f"{row[3]}",
                "sample_data": [],
                "is_foreign_key": "",
                "references": None 
            }
            columns_dict[f"{row[0]}.{row[1]}.{row[2]}"] = column_info
            columns.append(column_info)
   
    return columns, columns_dict

#Creates the proper JSON file
def save_json(output, file_name):
    with open(file_name, "w") as f:
        json.dump(output, f, indent=4)

#Test block

if __name__ == "__main__":

    columns, columns_dict = extract_columns("data/omop/EDWMetadata.csv")
    data = read_sample_data("data/omop/EDW_Sample_Data.xlsx", columns_dict)
    

    save_json(columns_dict, "output.json")

    print("Translation complete. Output saved to output.json")