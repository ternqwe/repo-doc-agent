from git_agent import extract_repo_content, format_repo_for_llm
from ai_agent import generate_documentation
from config import TOKEN_LIMIT

if __name__ == "__main__":
    print("Welcome to Repo Doc Agent!")
    target_repo = input("Enter the GitHub repository URL to analyze: ").strip()

    if not target_repo:
        print("Error: No URL provided. Exiting.")
    else:
        data = extract_repo_content(target_repo)
        
        if not data:
            print("No text files found or repository is empty.")
        else:
            llm_context = format_repo_for_llm(data)
            approx_tokens = len(llm_context) // 4
            
            print(f"Extracted and formatted {len(data)} files.")
            print(f"Approximate token count: {approx_tokens:,}")
            
            if approx_tokens > TOKEN_LIMIT:
                print(f"\nWarning: The repository is too large ({approx_tokens:,} tokens).")
                proceed = input("Do you want to proceed anyway? (y/n): ").strip().lower()
                if proceed != 'y':
                    print("Operation cancelled.")
                    exit(0)
                    
            print("Sending to Gemini...")
            result_doc = generate_documentation(llm_context)
            
            if result_doc:
                output_file = "ARCHITECTURE.md"
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(result_doc)
                print(f"\nSuccess! The documentation has been saved to {output_file}.")
            else:
                print("\nFailed to generate documentation due to an API error.")
