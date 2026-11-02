import os
import logging
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY is not configured")

# Filtering constants
EXCLUDED_DIRS = {".git", ".vscode", "venv", ".venv", "node_modules", "tests", "__pycache__"}
EXCLUDED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".tar", ".gz", ".mp4", ".ico", ".lock"}
EXCLUDED_FILES = {".env", "secrets.json", "credentials.yml"}
MAX_FILE_SIZE_BYTES = 100 * 1024  # 100 KB limit per file
TOKEN_LIMIT = 500_000

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)