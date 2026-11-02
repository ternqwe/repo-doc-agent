import tempfile
import os
import urllib.parse
from git.exc import GitCommandError
from dotenv import load_dotenv
from google import genai
from pathlib import Path
from git import Repo

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY is not configured")

# Filtering constants
EXCLUDED_DIRS = {".git", ".vscode", "venv", ".venv", "node_modules", "tests", "__pycache__"}
EXCLUDED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".tar", ".gz", ".mp4", ".ico", ".lock"}
EXCLUDED_FILES = {".env", "secrets.json", "credentials.yml"}
MAX_FILE_SIZE_BYTES = 100 * 1024  # 100 KB limit per file


def read_file_content(file_path: Path) -> str | None:
    """Safely reads text content, ignoring binary files."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        return None

def extract_repo_content(repo_url: str) -> dict[str, str]:
    """Clones a repository and extracts the content of all text files."""
    
    # 1. Validate GitHub URL
    parsed_url = urllib.parse.urlparse(repo_url)
    if parsed_url.netloc not in ("github.com", "www.github.com") or not parsed_url.path:
        print("Error: Invalid GitHub URL. Please provide a valid link (e.g., https://github.com/user/repo).")
        return {}

    repo_data = {}
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Cloning {repo_url} into temporary directory...")
        
        # 2. Clone with error handling
        try:
            Repo.clone_from(repo_url, temp_dir)
        except GitCommandError as e:
            print("Error: Failed to clone the repository.")
            print("Check if the repository exists, is public, and your internet connection is stable.")
            return {}

        # 3. Walk through the repository and filter files
        for root, dirs, files in os.walk(temp_dir):
            # Exclude unnecessary directories in-place
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
            
            for file in files:
                # Exclude specific files and extensions
                if file in EXCLUDED_FILES or any(file.endswith(ext) for ext in EXCLUDED_EXTENSIONS):
                    continue
                    
                file_path = os.path.join(root, file)
                
                # Restrict maximum file size
                if os.path.getsize(file_path) > MAX_FILE_SIZE_BYTES:
                    continue
                
                # Read content and store with relative path
                content = read_file_content(file_path)
                if content:
                    rel_path = os.path.relpath(file_path, temp_dir)
                    repo_data[rel_path] = content
                    
    return repo_data

def format_repo_for_llm(repo_data: dict[str, str]) -> str:
    """Formats the repository data into a single string for LLM input."""
    formatted_parts = []

    for file_path, content in repo_data.items():
        formatted_string = f"""File: {file_path}
        ```
        {content}
        ```"""

        formatted_parts.append(formatted_string)

    return "\n\n".join(formatted_parts)

def generate_documentation(repo_content: str) -> str:
    """Generates a README.md file using the Gemini API based on the extracted code."""
    client = genai.Client(api_key=API_KEY)
    
    prompt = f"""
    You are a Senior Software Architect. Your task is to analyze the provided source code of a repository and generate a comprehensive "Technical Architecture Overview" in Markdown format.

    Please include the following sections:
    1. **Project Overview**: A concise summary of what this project does and its main purpose.
    2. **Tech Stack**: Key languages, libraries, and frameworks used.
    3. **Architecture & Structure**: How the code is organized, core modules, and how they interact.
    4. **Getting Started**: Brief instructions on how a new developer can set up and run this project based on the code.

    Do not include any generic conversational filler. Output only the requested Markdown documentation.

    Repository content:
    {repo_content}
    """

    
    print("Generating documentation with Gemini...")
    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt
    )
    
    return response.text

if __name__ == "__main__":
    print("Welcome to Repo Doc Agent!")
    target_repo = input("Enter the GitHub repository URL to analyze: ").strip()

    if not target_repo:
        print("Error: No URL provided. Exiting.")
    else:
        # 1. Extract repository content
        data = extract_repo_content(target_repo)
        
        if not data:
            print("No text files found or repository is empty.")
        else:
            # 2. Format data for the LLM
            llm_context = format_repo_for_llm(data)
            approx_tokens = len(llm_context) // 4
            
            print(f"Extracted and formatted {len(data)} files.")
            print(f"Approximate token count: {approx_tokens:,}")
            
            # 3. Context size control
            TOKEN_LIMIT = 500_000  # Safe limit for API free tier
            if approx_tokens > TOKEN_LIMIT:
                print(f"\nWarning: The repository is too large ({approx_tokens:,} tokens).")
                print("This may exceed your API quota or result in a timeout.")
                proceed = input("Do you want to proceed anyway? (y/n): ").strip().lower()
                if proceed != 'y':
                    print("Operation cancelled. Consider adding more folders to EXCLUDED_DIRS.")
                    exit(0)
                    
            print("Sending to Gemini...")
            
            # 4. Generate documentation
            result_doc = generate_documentation(llm_context)
            
            if result_doc:
                output_file = "ARCHITECTURE.md"
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(result_doc)
                print(f"\nSuccess! The documentation has been saved to {output_file}.")
            else:
                print("\nFailed to generate documentation due to an API error.")

