LLM_TABLE_DESC_PROMPT = """
You are a domain expert in healthcare data modeling and database documentation.

You will be provided:
1. A **table name**
2. A list of **column names with their descriptions**
3. Optional -A set of **sample rows from the table**

Your task:
1. Write a **clear, concise, and accurate description** of the table.
2. Identify which **OMOP CDM table(s)** this table can be mapped to, based on structure and meaning.
   - Only select from valid OMOP tables
   - If multiple mappings are possible, list them all.
   - If no mapping is found, return an empty list.
3. For each suggested OMOP table, provide a **confidence score** between 0 and 1 (where 1 = extremely confident).
4. Use healthcare domain knowledge (HL7, FHIR, OMOP) to make accurate recommendations.
5. Avoid repeating column descriptions verbatim — summarize instead.

### Output Format:
Return a JSON object with the following structure:
{{
    "name": "<table name>",
    "description": "<description of the table>",
    "omop_mappings": [
        {{
            "omop_table": "<OMOP table name>",
            "confidence": <float between 0 and 1>
        }}
    ]
}}

### Example:

Input:
Table Name: patient_demographics
Columns:
(patient_id: Unique identifier for each patient, first_name: Patient's first name, last_name: Patient's last name, date_of_birth: Patient's date of birth, gender: Patient's gender)
Sample Data:
[(133332, John, Smith, 1985-07-22, M), (234534, Jane, Doe, 1990-11-10, F)]

Output:
{{
    "name": "patient_demographics",
    "description": "Contains demographic information for patient to uniquely identify individuals in the healthcare system and link them to their medical records.",
    "omop_mappings": [
        {{
            "omop_table": "PERSON",
            "confidence": 0.99
        }}
    ]
}}
"""

LLM_TABLE_USER_PROMPT = """
Table Name: {table_name}
Columns:
{columns}
Sample Data:
{sample_data}
"""