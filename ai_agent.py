import logging
from google import genai
from google.genai import errors
from config import API_KEY
from prompts import ARCHITECTURE_PROMPT

logger = logging.getLogger(__name__)

def generate_documentation(repo_content: str) -> str | None:
    """Generates a README.md file using the Gemini API."""
    client = genai.Client(api_key=API_KEY)
    prompt = ARCHITECTURE_PROMPT.format(repo_content=repo_content)
    
    logger.info("Generating documentation with Gemini...")
    try:
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt
        )
        return response.text
    except errors.APIError as e:
        logger.error(f"Gemini API failed. Details: {e.message}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return None