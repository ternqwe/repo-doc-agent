import logging
from git_agent import extract_repo_content, format_repo_for_llm
from ai_agent import generate_documentation
from config import TOKEN_LIMIT

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Welcome to Repo Doc Agent!")
    target_repo = input("Enter the GitHub repository URL to analyze: ").strip()

    if not target_repo:
        logger.error("No URL provided. Exiting.")
    else:
        data = extract_repo_content(target_repo)
        
        if not data:
            logger.warning("No text files found or repository is empty.")
        else:
            llm_context = format_repo_for_llm(data)
            approx_tokens = len(llm_context) // 4
            
            logger.info(f"Extracted and formatted {len(data)} files.")
            logger.info(f"Approximate token count: {approx_tokens:,}")
            
            if approx_tokens > TOKEN_LIMIT:
                logger.warning(f"The repository is too large ({approx_tokens:,} tokens).")
                proceed = input("Do you want to proceed anyway? (y/n): ").strip().lower()
                if proceed != 'y':
                    logger.info("Operation cancelled.")
                    exit(0)
                    
            logger.info("Sending to Gemini...")
            result_doc = generate_documentation(llm_context)
            
            if result_doc:
                output_file = "ARCHITECTURE.md"
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(result_doc)
                logger.info(f"Success! The documentation has been saved to {output_file}.")
            else:
                logger.error("Failed to generate documentation due to an API error.")