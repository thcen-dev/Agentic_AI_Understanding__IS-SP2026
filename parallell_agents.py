from google import genai
import os
import requests

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


class Agent:
    def __init__(self, name):
        self.name = name

    def run(self, input_text):

        if self.name == "OpenAI Agent":
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=input_text
            )
            return f"[{self.name}] {response.text}"

        elif self.name == "HuggingFace Agent":
            API_URL = "https://router.huggingface.co/v1/chat/completions"

            headers = {
                "Authorization": f"Bearer {os.getenv('HF_TOKEN')}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "meta-llama/Meta-Llama-3-8B-Instruct",
                "messages": [
                    {"role": "user", "content": input_text}
                ]
            }

            response = requests.post(API_URL, headers=headers, json=payload)

            try:
                result = response.json()
                return f"[{self.name}] {result['choices'][0]['message']['content']}"
            except:
                return f"[{self.name}] Error: {response.text}"
            
        elif self.name == "Ollama Agent":
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3",
                    "prompt": input_text,
                    "stream": False
                }
            )

            try:
                result = response.json()
                return f"[{self.name}] {result['response']}"
            except:
                return f"[{self.name}] Error: {response.text}"

        # fallback
        else:
            return f"[{self.name}] processed: {input_text}"


def run_agents(input_text):
    agent1 = Agent("OpenAI Agent")
    agent2 = Agent("HuggingFace Agent")
    agent3 = Agent("Ollama Agent")

    result1 = agent1.run(input_text)
    result2 = agent2.run(input_text)
    result3 = agent3.run(input_text)

    return {
    "OpenAI": result1,
    "HuggingFace": result2,
    "Ollama": result3
}


# Run system
results = run_agents("How is the sky blue? Keep it to one sentence.")
print("\n=== FINAL COMBINED RESULT ===\n")

for agent, res in results.items():
    output = res.split("] ", 1)[1]
    print(f"{agent}:")
    print(output)
    print()