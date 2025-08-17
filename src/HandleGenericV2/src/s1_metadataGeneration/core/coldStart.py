import json
import re
import logging
from typing import Dict, Any

from adapters.local.read.readFilesNames import directory_to_json
from adapters.local.write.writeJson import save_json_to_file
from aiBrain.ai import AzureOpenAIClient
from config import Config


logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

config = Config()


def _extract_json_from_text(text: str) -> Dict[str, Any]:
    """
    Extract the first JSON object from a text block.
    Handles code fences and extra prose.
    """
    if not isinstance(text, str):
        raise ValueError("AI answer is not a string")

    cleaned = text.strip()

    # Strip code fences if present
    cleaned = re.sub(r"^```json\s*|\s*```$", "", cleaned, flags=re.DOTALL).strip()
    cleaned = re.sub(r"^```|\s*```$", "", cleaned, flags=re.DOTALL).strip()

    # If it's already valid JSON, return it
    try:
        return json.loads(cleaned)
    except Exception:
        pass

    # Otherwise, find the first {...} JSON object in the text
    match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in AI answer")

    return json.loads(match.group(0))


def _normalize_result(d: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ensure required keys exist and are UPPERCASE strings.
    """
    lang = d.get("programming_language", "UNKNOWN")
    arch = d.get("architecture", "CLEAN ARCHITECTURE")
    return {
        "programming_language": str(lang).upper(),
        "architecture": str(arch).upper(),
    }


def analyze_codebase_with_ai(path: str) -> Dict[str, Any]:
    """
    Analyze a codebase directory with AzureOpenAIClient and return
    programming language and architecture (UPPERCASE), saving to disk.
    """
    # Get workspace from config
    workspace = getattr(config, "WORKSPACE", "LOCAL")
    logger.info(f"Using workspace: {workspace}")

    # 1) Build structure JSON (as string) with workspace parameter
    codebase_json = directory_to_json(path, workspace=workspace)
    logger.info("Directory structure generated")

    # 2) AI client
    ai_client = AzureOpenAIClient()

    # 3) Prompt (strict JSON, uppercase requirement)
    prompt = f"""
You are given a JSON structure of a codebase:

{codebase_json}

Return STRICTLY and ONLY a JSON object (no explanations, no markdown, no extra text) with EXACT keys:
{{
  "programming_language": "<LANGUAGE IN UPPERCASE>",
  "architecture": "<ARCHITECTURE IN UPPERCASE>"
}}

If no architecture is clear, set "architecture" to "CLEAN ARCHITECTURE".
"""

    result = ai_client.ask_question(prompt, max_tokens=200, temperature=0.0)

    # Resolve config targets with safe defaults
    output_dir = getattr(config, "OUTPUT_DIR", None) or "./output"
    filename = (
        getattr(config, "LANGUAGE_ARCHITECTURE", None) or "language_architecture.json"
    )

    try:
        raw_answer = result.get("answer", "")
        parsed = _extract_json_from_text(raw_answer)
        analysis = _normalize_result(parsed)
        saved_path = save_json_to_file(
            filename, analysis, output_dir, workspace=workspace
        )
        logger.info(f"Analysis saved to: {saved_path}")
        return analysis

    except Exception as e:
        logger.error(f"Failed to parse AI response, using fallback. Reason: {e}")
        fallback = {
            "programming_language": "UNKNOWN",
            "architecture": "CLEAN ARCHITECTURE",
            "raw_answer": result.get("answer", None),
        }
        saved_path = save_json_to_file(
            filename, fallback, output_dir, workspace=workspace
        )
        logger.info(f"Fallback analysis saved to: {saved_path}")
        return fallback


if __name__ == "__main__":
    analysis = analyze_codebase_with_ai(getattr(config, "CODEBASE_ROOT", "."))
    print(json.dumps(analysis, indent=4))
