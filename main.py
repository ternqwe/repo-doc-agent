import tempfile
from pathlib import Path
from git import Repo

def read_file_content(file_path: Path) -> str | None:
    """Safely reads text content, ignoring binary files."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        return None

def extract_repo_content(repo_url: str) -> dict[str, str]:
    """Clones a repo and extracts the text content of all tracked files."""
    repo_data = {}
    
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Cloning {repo_url} into {temp_dir}...")
        repo = Repo.clone_from(repo_url, temp_dir)
        raw_files = repo.git.ls_files().split("\n")
        
        for file_str in raw_files:
            if not file_str:
                continue
                
            file_path = Path(temp_dir) / file_str
            content = read_file_content(file_path)
            
            if content is not None:
                repo_data[file_str] = content
                
    return repo_data

def format_repo_for_llm(repo_data: dict[str, str]) -> str:
    """Formats the repository data into a single string for LLM input."""
    formatted_parts = []
    for file_path, content in repo_data.items():
        formatted_string = f"""File: {file_path}\n```{content}```"""

        formatted_parts.append(formatted_string)

    return "\n\n".join(formatted_parts)


