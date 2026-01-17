# 🔬 Paper Search Agent

A powerful, high-performance research paper search agent that connects **ArXiv**, **Google Scholar**, **Semantic Scholar**, and **Tavily** into a single neural pipeline. Built with **n8n**, **FastAPI**, **Streamlit**, and **Ollama**.

![Neural Pipeline](pipeline.png)

## 🌟 Key Features

-   🔍 **Multi-Source Intelligence**: Simultaneously queries ArXiv, Google Scholar (via SerpAPI), Semantic Scholar, and Tavily.
-   🧠 **Local LLM Keywords**: Uses Ollama (`qwen3:4b`) to translate natural language queries into precise search keywords.
-   ⚖️ **Smart Relevance Scoring**: Papers are ranked using a hybrid score of content similarity, citation impact, and year matches.
-   🔄 **Auto-Deduplication**: Never see the same paper twice, even if found across multiple sources.
-   📜 **Research History**: Every search is logged locally in a SQLite database via a FastAPI backend.
-   🎨 **Premium UI**: A sleek, modern Streamlit interface with high-resolution card views and persistence.

---

## 🛠️ Components of the n8n Workflow

The heart of the system is the **n8n orchestrator**, which manages the data flow through several specialized stages:

1.  **n8n link (Webhook)**: The entry point that receives queries from the Streamlit app.
2.  **Detect time intent**: A logic node that identifies if you asked for a specific year (e.g., "in 2025") or relative time ("latest").
3.  **Build prompt & Ollama**: Prepares the neural instruction and calls your local Ollama model to generate clean search keywords.
4.  **Parallel Search Cluster**:
    *   **ArXiv**: Direct XML query for physics, computer science, and math.
    *   **SerpAPI**: Leverages Google Scholar for wide academic coverage.
    *   **Tavily**: Scours the web for the absolute latest journal pre-prints.
    *   **Semantic Scholar**: Fetches deep citation counts and abstracts.
5.  **Merge & Score**: Aggregates all papers into a single pool and calculates their "Final Score."
6.  **SQL_link**: Sends the final ranked results to your local FastAPI service for database storage.

---

## 🚀 Getting Started

### 1. Prerequisites
*   **n8n Desktop/Self-hosted**: [Install here](https://n8n.io/)
*   **Ollama**: [Install here](https://ollama.ai/) and run `ollama pull qwen3:4b`.
*   **Python 3.10+**: For the UI and Backend.

### 2. Setup the Neural Backend (n8n)
1.  Import `Paper Search Agent.json` into n8n.
2.  Set the workflow to **Active**.
3.  Ensure your API keys are configured in the `SerpAPI` and `Tavily` nodes.

### 3. Launching the Local Services

Open two terminals in the project folder:

**Terminal A: The Memory API**
```powershell
pip install -r requirements.txt  # If not already installed
uvicorn memory_api:app --reload --port 8000
```

**Terminal B: The Streamlit UI**
```powershell
streamlit run app.py
```

---

## 📖 Project Structure

*   `app.py`: The Premium Streamlit discovery interface.
*   `memory_api.py`: FastAPI backend managing the SQLite database.
*   `Paper Search Agent.json`: The full n8n workflow logic.
*   `memory.db`: SQLite database storing your research history.
*   `pipeline.png`: Visual architecture of the agent logic.

---

## 📜 License
MIT License. Created by Ali Baghizadeh.
