import os
import tempfile
import urllib.parse
from git import Repo
from git.exc import GitCommandError
from config import EXCLUDED_DIRS, EXCLUDED_EXTENSIONS, EXCLUDED_FILES, MAX_FILE_SIZE_BYTES

def read_file_content(file_path: str) -> str | None:
    """Reads file content safely, skipping binary files."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        return None

def extract_repo_content(repo_url: str) -> dict[str, str]:
    """Clones a repository and extracts the content of all text files."""
    parsed_url = urllib.parse.urlparse(repo_url)
    if parsed_url.netloc not in ("github.com", "www.github.com") or not parsed_url.path:
        print("Error: Invalid GitHub URL. Please provide a valid link.")
        return {}

    repo_data = {}
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Cloning {repo_url} into temporary directory...")
        try:
            Repo.clone_from(repo_url, temp_dir)
        except GitCommandError:
            print("Error: Failed to clone the repository.")
            return {}

        for root, dirs, files in os.walk(temp_dir):
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
            for file in files:
                if file in EXCLUDED_FILES or any(file.endswith(ext) for ext in EXCLUDED_EXTENSIONS):
                    continue
                file_path = os.path.join(root, file)
                if os.path.getsize(file_path) > MAX_FILE_SIZE_BYTES:
                    continue
                content = read_file_content(file_path)
                if content:
                    rel_path = os.path.relpath(file_path, temp_dir)
                    repo_data[rel_path] = content
    return repo_data

def format_repo_for_llm(repo_data: dict[str, str]) -> str:
    """Formats the extracted repository data into a single string for the LLM."""
    formatted_text = ""
    for file_path, content in repo_data.items():
        formatted_text += f"\n\n--- File: {file_path} ---\n\n"
        formatted_text += f"```\n{content}\n```"
    return formatted_text

