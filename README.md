# Paper Search Agent

A local, privacy-focused research paper search agent built with n8n, Ollama, and SQLite. This agent searches across multiple academic sources (ArXiv, Google Scholar, Semantic Scholar, Tavily) and ranks results by relevance.

## Features

- 🔍 **Multi-source search**: Searches ArXiv, Google Scholar (via SerpAPI), Semantic Scholar, and Tavily simultaneously
- 🤖 **Local LLM**: Uses Ollama with qwen3:4b model for query extraction
- 📊 **Smart ranking**: Combines content similarity and citation counts for relevance scoring
- 🔄 **Deduplication**: Automatically removes duplicate papers across sources
- 📅 **Time-aware**: Detects and handles year constraints in queries
- 💾 **Local-first**: All processing happens locally - no cloud dependencies

## Prerequisites

Before setting up, ensure you have:

1. **n8n** installed and running locally
   - Download from [n8n.io](https://n8n.io/)
   - Or install via npm: `npm install n8n -g`
   - Run: `n8n start`

2. **Ollama** installed and running locally
   - Download from [ollama.ai](https://ollama.ai/)
   - Pull the model: `ollama pull qwen3:4b`
   - Ensure Ollama is running on `http://127.0.0.1:11434`

3. **API Keys** (for external services):
   - SerpAPI key (for Google Scholar search)
   - Tavily API key (for web search)
   - Semantic Scholar API key (optional but recommended)

## Setup

### 1. Import the Workflow

1. Open your local n8n instance (usually `http://localhost:5678`)
2. Click "Import from File"
3. Select `workflow/paper-search-agent.json`
4. The workflow will be imported with placeholder API keys

### 2. Configure API Keys

See [API_KEYS.md](API_KEYS.md) for detailed instructions on obtaining and configuring API keys.

In the imported workflow, update these nodes with your API keys:

- **SerpAPI - Google Scholar**: Replace `YOUR_SERPAPI_KEY` in the query parameters
- **Tavily - search**: Replace `YOUR_TAVILY_API_KEY` in the Authorization header
- **Semantic Scholar – search**: Replace `YOUR_SEMANTIC_SCHOLAR_API_KEY` in the x-api-key header

### 3. Verify Ollama Connection

Ensure Ollama is running and the model is available:
```bash
ollama list
# Should show qwen3:4b

# Test the API
curl http://127.0.0.1:11434/api/tags
```

### 4. Activate the Workflow

1. In n8n, open the "Paper Search Agent" workflow
2. Click "Active" toggle to activate it
3. The chat trigger will be available at the webhook URL shown

## Usage

### Via n8n Chat Interface

1. In n8n, click on the "When chat message received" node
2. Click "Test workflow" or use the chat interface
3. Enter your query, e.g., "Find papers about machine learning in 2024"

### Example Queries

- "Find recent papers on transformer architectures"
- "Show me papers about quantum computing from 2023"
- "Search for research on climate change mitigation"

## Workflow Architecture

```
User Query
    ↓
Detect Time Intent
    ↓
Build Prompt → Ollama (Extract Keywords)
    ↓
Parallel Search:
    ├─ ArXiv
    ├─ Google Scholar (SerpAPI)
    ├─ Tavily
    └─ Semantic Scholar
    ↓
Parse & Normalize Results
    ↓
Merge → Score → Deduplicate → Sort
    ↓
Format Output
```

## Project Structure

```
.
├── workflow/
│   └── paper-search-agent.json    # n8n workflow file (with placeholder API keys)
├── .gitignore                      # Git ignore rules
├── API_KEYS.md                     # API keys configuration guide
└── README.md                       # This file
```

## Local Development

This project is designed to run entirely locally:

- **n8n**: Workflow automation (local instance)
- **Ollama**: Local LLM inference
- **SQLite**: Local database (to be added for memory feature)

## Future Enhancements

- [ ] Add SQLite-based memory for search history
- [ ] Create Streamlit web interface
- [ ] Add paper bookmarking/favorites
- [ ] Implement user preferences storage

## License

MIT License - feel free to use and modify for your needs.

## Contributing

Contributions welcome! Please open an issue or submit a pull request.
