ARCHITECTURE_PROMPT = """
You are a Senior Software Architect. Your task is to analyze the provided source code of a repository and generate a comprehensive "Technical Architecture Overview" in Markdown format.

Please include the following sections:
1. **Project Overview**: A concise summary of what this project does and its main purpose.
2. **Tech Stack**: Key languages, libraries, and frameworks used.
3. **Architecture & Structure**: How the code is organized, core modules, and how they interact.
4. **System Diagram**: Generate a Mermaid.js flowchart (using ```mermaid ... ``` syntax) that visualizes the core components, their relationships, and data flow.
5. **Getting Started**: Brief instructions on how a new developer can set up and run this project based on the code.

Do not include any generic conversational filler. Output only the requested Markdown documentation.

Repository content:
{repo_content}
"""