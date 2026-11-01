import tempfile
import os
from dotenv import load_dotenv
from google import genai
from pathlib import Path
from git import Repo

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

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
            print(f"Extracted and formatted {len(data)} files. Sending to Gemini...")
            
            # 3. Generate documentation
            result_doc = generate_documentation(llm_context)
            
            # 4. Save the generated result
            output_file = "ARCHITECTURE.md"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(result_doc)
                
            print(f"\nSuccess! The documentation has been saved to {output_file}.")
