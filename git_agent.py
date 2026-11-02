import tempfile
import urllib.parse
import logging
from pathlib import Path
from git import Repo
from git.exc import GitCommandError
from config import EXCLUDED_DIRS, EXCLUDED_EXTENSIONS, EXCLUDED_FILES, MAX_FILE_SIZE_BYTES

logger = logging.getLogger(__name__)

def read_file_content(file_path: Path) -> str | None:
    """Reads file content safely, skipping binary files."""
    try:
        return file_path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        return None

def extract_repo_content(repo_url: str) -> dict[str, str]:
    """Clones a repository and extracts the content of all text files."""
    parsed_url = urllib.parse.urlparse(repo_url)
    if parsed_url.netloc not in ("github.com", "www.github.com") or not parsed_url.path:
        logger.error("Invalid GitHub URL. Please provide a valid link.")
        return {}

    repo_data = {}
    with tempfile.TemporaryDirectory() as temp_dir:
        logger.info(f"Cloning {repo_url} into temporary directory...")
        try:
            Repo.clone_from(repo_url, temp_dir)
        except GitCommandError:
            logger.error("Failed to clone the repository.")
            return {}

        temp_path = Path(temp_dir)
        
        # Traverse the directory tree using pathlib
        for file_path in temp_path.rglob('*'):
            if not file_path.is_file():
                continue
            
            # Exclude specific directories
            if any(part in EXCLUDED_DIRS for part in file_path.parts):
                continue
                
            # Exclude specific files and extensions
            if file_path.name in EXCLUDED_FILES or file_path.suffix in EXCLUDED_EXTENSIONS:
                continue
                
            # Restrict maximum file size
            if file_path.stat().st_size > MAX_FILE_SIZE_BYTES:
                continue
                
            content = read_file_content(file_path)
            if content:
                # Use as_posix() to ensure consistent forward slashes in paths
                rel_path = file_path.relative_to(temp_path).as_posix()
                repo_data[rel_path] = content
                
    return repo_data

def format_repo_for_llm(repo_data: dict[str, str]) -> str:
    """Formats the extracted repository data into a single string for the LLM."""
    formatted_text = ""
    for file_path, content in repo_data.items():
        formatted_text += f"\n\n--- File: {file_path} ---\n\n"
        formatted_text += f"```\n{content}\n```"
    return formatted_text