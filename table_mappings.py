from typing import Dict
import os
import re
import json
import numpy as np
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
from dotenv import load_dotenv
import prompts
load_dotenv()


def output_parser(response: AIMessage):
    """
    Lightweight JSON extractor like the notebook:
    - strip newlines/backticks/backslashes
    - extract the first {...} or [...] block
    - json.loads()
    """
    content = response.content
    content = re.sub(r'\n\s*|\\|`', '', content).strip()
    match = re.search(r'(\{|\[).*(\}|\])', content, re.DOTALL)
    if match:
        content = match.group(0)
    try:
        obj = json.loads(content)
    except json.JSONDecodeError:
        obj = {"description": "", "omop_mappings": []}
    return obj

def table_description_llm(table_desc_file: str,model: str = "gpt-4o-mini", 
                          temperature: float = 0.2) -> Dict[str, Dict]:
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY not set in environment.")

    with open(table_desc_file, 'r') as file:
        table_data = json.load(file)
    
    chat_prompt = ChatPromptTemplate.from_messages([
        ("system", prompts.LLM_TABLE_DESC_PROMPT),
        ("user",   prompts.LLM_TABLE_USER_PROMPT),
    ])
    llm = ChatOpenAI(model=model, temperature=temperature)
    chain = chat_prompt | llm | output_parser

    for table in table_data["tables"]:
        if table_data["tables"][table]["description"] is None or table_data["tables"][table]["description"] =="":
            cols = table_data["tables"][table]["cols"]
            cols = " /n".join([d+":"+str(cols[d]) for d in cols])
            sample_data = table_data["tables"][table]["sample_data"]
            if sample_data != []:
                sample_data = [" ".join([str(y) 
                                    for y in row if not (isinstance(y, float) 
                                        and np.isnan(y))]) for row in sample_data]
                sample_data = " /n ".join(sample_data)
            else:
                sample_data = ""
            params = {
                "table_name": table,
                "columns": cols,
                "sample_data": sample_data,
            }
            result = chain.invoke(params)
            description = result.get("description", "") if isinstance(result, dict) else ""
            table_data["tables"][table]["description"] = description
            omop_maps = result.get("omop_mappings", []) if isinstance(result, dict) else []
            table_data["tables"][table]["mapped"] = []
            for m in omop_maps:
                if not isinstance(m, dict):
                    continue
                mapping = {}
                omop = str(m.get("omop_table", "")).strip()
                mapping["name"] = omop
                try:
                    confidence = float(m.get("confidence", 0.0))
                except Exception:
                    confidence = 0.0
                if omop:
                    mapping["confidence"] = confidence
                    table_data["tables"][table]["mapped"].append(mapping)
                    mapping = {}
    with open("data/out_desc_mapping.json", "w") as file:
        json.dump(table_data, file, indent=4)

if __name__ == "__main__":
    TABLE_DESC_FILE = "data/table_description.json"
    table_description_llm(TABLE_DESC_FILE)
