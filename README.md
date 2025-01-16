# Discussion Retrieval Augmented Generation (dRAG)

**dRAG** is a local, privacy-focused tool designed to help educators answer discussion questions efficiently using their course materials, such as syllabi and lecture notes. By leveraging Retrieval-Augmented Generation (RAG) techniques, dRAG ensures accurate and context-aware responses, all while keeping sensitive data secure by running offline. The project uses UV for dependency management and Ollama for both LLM and embedding models.

## Features

- **PDF Indexing**: Converts and indexes course materials for efficient retrieval.
- **Customizable Prompt**: Allows users to specify LLM prompt for tailored results.
- **Ollama Integration**: Uses `qwen2.5:latest` for generation and `snowflake-arctic-embed2` for embeddings.
- **Offline Privacy**: Ensures data security by running entirely offline.

## Requirements

- Python 3.12 or higher
- [UV](https://astral.sh/uv)
- [Ollama](https://ollama.com/download) installed and running

## Installation

### Install UV

On macOS and Linux:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

On Windows:
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Clone the Repository

```bash
git clone https://github.com/Teaching-and-Learning-in-Computing/dRAG
cd dRAG
```

### Set Up the Environment

UV will handle dependencies defined in the `pyproject.toml`:
```bash
uv sync
```

## Usage

### Step 1: Place the PDF File to Index

Place the PDF file you want to index in the `/documents/source_documents/` folder. For example:

```
documents/source_documents/your_file_name.pdf
```

### Step 2: Download and Start Ollama Models

Ensure Ollama is installed and running. Pull the required models by running the following commands:

```bash
ollama pull qwen2.5:latest
ollama pull snowflake-arctic-embed2
```

Start the Ollama server to enable model usage.

### Step 3: Prepare Input Questions

Update the `documents/input/input.json` file with the questions and answers you want to use. The JSON file should follow this structure:

```json
[
    {
        "questions": "What are the course prerequisites?",
        "answer": "Prerequisites include introductory programming and basic statistics."
    }
]
```

The `answer` field should contain a "ground truth" response provided by a professor or TA for evaluation purposes.

### Step 4: Run the Project

Run the `main.py` script to process documents, generate answers, and evaluate results:

```bash
python main.py
```

The script executes the following steps in order:
1. Indexes the specified PDF files using `index.py`.
2. Processes input questions and generates answers using `generate.py`.
3. Evaluates generated answers against the provided ground truth using `evaluate.py`.

## Notes for Subsequent Runs

- **Adding Documents**: If you add new documents, place them in the `/documents/source_documents/` folder and rerun `main.py`.
- **Modifying Inputs**: To change questions or prompts, update the `input.json` file and rerun `main.py`.
- **Model Updates**: If you want to switch models, ensure they are pulled into Ollama and update each file.

## Example Workflow

1. Place a syllabus PDF in `documents/source_documents/`.
2. Add your questions and ground truth answers to `input.json`.
3. Run `main.py` to index, generate, and evaluate results.

