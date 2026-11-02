from google import genai
from google.genai import errors
from config import API_KEY
from prompts import ARCHITECTURE_PROMPT

def generate_documentation(repo_content: str) -> str | None:
    """Generates a README.md file using the Gemini API."""
    
    client = genai.Client(api_key=API_KEY)
    prompt = ARCHITECTURE_PROMPT.format(repo_content=repo_content)
    
    print("Generating documentation with Gemini...")
    try:
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt
        )
        return response.text
    except errors.APIError as e:
        print(f"Error: Gemini API failed. Details: {e.message}")
        return None
    except Exception as e:
        print(f"Error: An unexpected error occurred: {e}")
        return None
