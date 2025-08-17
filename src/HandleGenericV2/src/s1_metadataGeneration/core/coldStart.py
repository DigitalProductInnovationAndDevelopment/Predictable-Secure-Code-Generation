import json
import re
from adapters.read.local.readFilesNames import directory_to_json
from aiBrain.ai import AzureOpenAIClient
from config import Config

config = Config()


def analyze_codebase_with_ai(path: str) -> dict:
    """
    Analyze a codebase directory with AzureOpenAIClient and return
    programming language and architecture in clean JSON format.
    """
    # Step 1: Get codebase structure JSON
    codebase_json = directory_to_json(path)
    print(codebase_json)

    # Step 2: Initialize AI client
    ai_client = AzureOpenAIClient()

    # Step 3: Prompt that enforces JSON output
    prompt = f"""
    You are given a JSON structure of a codebase:

    {codebase_json}

    Return strictly and only a JSON object (no explanations, no markdown, no text) with:
    {{
        "programming_language": "<language>",
        "architecture": "<architecture>"
    }}

    If no architecture is found, set "architecture" to "Clean Architecture".
    """

    result = ai_client.ask_question(prompt, max_tokens=200, temperature=0.0)

    # Step 4: Parse AI response safely
    try:
        answer = result["answer"].strip()

        # Remove possible code fences or extra text
        answer = re.sub(r"^```json\s*|\s*```$", "", answer, flags=re.DOTALL).strip()
        answer = re.sub(r"^```|\s*```$", "", answer, flags=re.DOTALL).strip()

        # Load as JSON
        return json.loads(answer)
    except Exception:
        # fallback in case model still misbehaves
        return {
            "programming_language": "Unknown",
            "architecture": "Clean Architecture",
            "raw_answer": result.get("answer", None),
        }


if __name__ == "__main__":
    analysis = analyze_codebase_with_ai(config.CODEBASE_ROOT)
    print(json.dumps(analysis, indent=4))
