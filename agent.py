import json
import requests

from google.adk.agents.parallel_agent import ParallelAgent
from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.agents import LoopAgent
from google.adk.tools.tool_context import ToolContext
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService


GEMINI_MODEL = "gemini-2.5-flash"
CLAUDE_MODEL = "claude-3-haiku-20240307"


with open("prompts.txt", "r") as f:
    PROMPT = f.read()

with open("soure_tables_with_mapping.json", "r") as f:
    source_data = json.load(f)

with open("target_description_with_fk_id.json", "r") as f:
    target_data = json.load(f)


def exit_loop(tool_context: ToolContext):
    tool_context.actions.escalate = True
    tool_context.actions.skip_summarization = True
    return {}


def ollama_tool(prompt: str) -> str:
    r = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "llama3", "prompt": prompt, "stream": False},
        timeout=120
    )
    try:
        return r.json().get("response", "")
    except:
        return r.text


agent_gemini = LlmAgent(
    name="GeminiAgent",
    model=GEMINI_MODEL,
    instruction=f"""{PROMPT}

INPUT:
{{user_input}}

Return ONLY valid JSON.""",
    output_key="gemini_output"
)

agent_claude = LlmAgent(
    name="ClaudeAgent",
    model=CLAUDE_MODEL,
    instruction=f"""{PROMPT}

INPUT:
{{user_input}}

Return ONLY valid JSON.""",
    output_key="claude_output"
)

agent_ollama = LlmAgent(
    name="OllamaAgent",
    model=GEMINI_MODEL,
    instruction="""
You MUST call ollama_tool.

INPUT:
{user_input}

Return ONLY valid JSON.
""",
    tools=[ollama_tool],
    output_key="ollama_output"
)


parallel_agent = ParallelAgent(
    name="ParallelMappingAgent",
    sub_agents=[agent_gemini, agent_claude, agent_ollama]
)


merge_agent = LlmAgent(
    name="MergeAgent",
    model=GEMINI_MODEL,
    instruction="""
Combine outputs into ONE valid JSON.

Gemini:
{gemini_output}

Claude:
{claude_output}

Ollama:
{ollama_output}

Return ONLY valid JSON.
""",
    output_key="merged_output"
)


validator_agent = LlmAgent(
    name="ValidatorAgent",
    model=GEMINI_MODEL,
    instruction="""
Validate JSON:

{merged_output}

If valid return VALID
Else explain issue
""",
    output_key="validation_feedback"
)


refiner_agent = LlmAgent(
    name="RefinerAgent",
    model=GEMINI_MODEL,
    instruction="""
JSON:
{merged_output}

Feedback:
{validation_feedback}

If VALID call exit_loop
Else fix JSON and return JSON only
""",
    tools=[exit_loop],
    output_key="merged_output"
)


loop_agent = LoopAgent(
    name="ValidationLoop",
    sub_agents=[validator_agent, refiner_agent],
    max_iterations=3
)


root_agent = SequentialAgent(
    name="FullPipeline",
    sub_agents=[parallel_agent, merge_agent, loop_agent]
)


def normalize_key(name, dictionary):
    for k in dictionary.keys():
        if k.lower() == name.lower():
            return k
    return None


def build_input(source_table, target_table):
    s_key = normalize_key(source_table, source_data["tables"])
    t_key = normalize_key(target_table, target_data["tables"])

    return {
        "source": {s_key: source_data["tables"][s_key]},
        "target": {t_key: target_data["tables"][t_key]}
    }


def run_pipeline():
    results = {}

    session_service = InMemorySessionService()
    runner = Runner(agent=root_agent, session_service=session_service)

    for source_table, s_info in source_data["tables"].items():
        for m in s_info.get("mapped", []):
            target_table = m["name"]

            payload = build_input(source_table, target_table)

            state = {
                "user_input": json.dumps(payload, indent=2)
            }

            result = runner.run(state)

            results[f"{source_table}_TO_{target_table}"] = result

    return results


def save_results(results):
    with open("final_mappings.json", "w") as f:
        json.dump(results, f, indent=4)


if __name__ == "__main__":
    output = run_pipeline()
    save_results(output)
    print("DONE")