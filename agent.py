from google.adk.agents.parallel_agent import ParallelAgent
from google.adk.agents.llm_agent import LlmAgent
import requests

GEMINI_MODEL = "gemini-2.5-flash"

# --- TOOL: Ollama ---
def ollama_tool(prompt: str) -> str:
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        }
    )
    return response.json()["response"]


# --- Agent 1 (Gemini) ---
agent1 = LlmAgent(
    name="Agent1",
    model=GEMINI_MODEL,
    instruction="""
    Answer: Why is the sky blue?
    Keep it short.
    """
)

# --- Agent 2 (Gemini) ---
agent2 = LlmAgent(
    name="Agent2",
    model=GEMINI_MODEL,
    instruction="""
    Explain simply why the sky is blue.
    """
)

# --- Agent 3 (Ollama via tool) ---
agent3 = LlmAgent(
    name="OllamaAgent",
    model=GEMINI_MODEL,
    instruction="""
    Use the tool to answer: Why is the sky blue?
    """,
    tools=[ollama_tool]
)

# --- Parallel Agent ---
parallel_agent = ParallelAgent(
    name="SimpleParallelAgent",
    sub_agents=[agent1, agent2, agent3]
)

root_agent = parallel_agent

if __name__ == "__main__":
    print("Ask: Why is the sky blue?")