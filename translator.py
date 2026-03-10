import pandas as pd
import json
import os
import sys

def load_file(file_path):
    # Get the file extension (.csv, .xlsx, .json)
    extension = os.path.splitext(file_path)[1].lower()

    # Load CSV
    if extension == ".csv":
        df = pd.read_csv(file_path)
    # Load Excel
    elif extension == ".xlsx":
        df = pd.read_excel(file_path)
    # Load JSON
    elif extension == ".json":
        df = pd.read_json(file_path)
    else:
        raise ValueError("Unsupported file type")

    return df

def get_table_name(file_path):
    # Get the filename only
    file_name = os.path.basename(file_path)
    # Remove the extension
    table_name = os.path.splitext(file_name)[0]

    return table_name

#Normalizes data types to a standard set (integer, float, datetime, boolean, string)
def normalize_data_type(dtype):
    dtype = str(dtype).lower()

    if "int" in dtype:
        return "integer"
    elif "float" in dtype:
        return "float"
    elif "date" in dtype or "time" in dtype:
        return "datetime"
    elif "bool" in dtype:
        return "boolean"
    else:
        return "string"

#metadata test, creates a dictionary from the metadata CSV file for easy lookup of descriptions based on table and column names
def load_metadata(metadata_file):
    metadata_df = pd.read_csv(metadata_file)
    metadata_dict = {}

    for _, row in metadata_df.iterrows():
        key = f"{row['TableNM']}.{row['ColumnNM']}"
        metadata_dict[key] = row["DescriptionTXT"]

    return metadata_dict

#Pulls column names
def extract_columns(df, table_name, metadata):
    columns = []

    for col in df.columns:
        data_type = normalize_data_type(df[col].dtype)

        sample_values = df[col].dropna().unique().tolist()[:3]

        #Looks for columns that end with "_id" to identify potential foreign keys
        is_fk = col.lower().endswith("_id")
        metadata_key = f"{table_name}.{col}"
        description = metadata.get(metadata_key, f"{col} column")

        column_info = {
            "column_name": col,
            "table_name": table_name,
            "table_description": f"Table containing data from {table_name}",
            "data_type": data_type,
            "description": description,
            "sample_data": sample_values,
            "is_foreign_key": is_fk,
            "references": None 
        }

        columns.append(column_info)

    return columns

#Formatting for the JSON structure
def build_output(columns):
    output = {
        "columns": columns
    }

    return output

#Creates the proper JSON file
def save_json(output, file_name):
    with open(file_name, "w") as f:
        json.dump(output, f, indent=4)

#Test block

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage: python translator.py <input_file>")
        sys.exit(1)

    file_path = sys.argv[1]

    metadata = load_metadata("EDWMetadata.csv")  #metadata test

    df = load_file(file_path)

    table_name = get_table_name(file_path)

    columns = extract_columns(df, table_name, metadata)

    output = build_output(columns)

    save_json(output, "output.json")

    print("Translation complete. Output saved to output.json")