# API Keys Configuration

This workflow requires API keys for external services. After importing the workflow into n8n, you need to update the following nodes with your API keys:

## Required API Keys

### 1. SerpAPI (Google Scholar)
- **Node**: `SerpAPI - Google Scholar`
- **Location**: Query parameter `api_key`
- **Get your key**: https://serpapi.com/
- **Current placeholder**: `YOUR_SERPAPI_KEY`

### 2. Tavily API
- **Node**: `Tavily - search`
- **Location**: Authorization header `Bearer YOUR_TAVILY_API_KEY`
- **Get your key**: https://tavily.com/
- **Current placeholder**: `YOUR_TAVILY_API_KEY`

### 3. Semantic Scholar API
- **Node**: `Semantic Scholar – search`
- **Location**: Header `x-api-key`
- **Get your key**: https://www.semanticscholar.org/product/api
- **Current placeholder**: `YOUR_SEMANTIC_SCHOLAR_API_KEY`
- **Note**: This API has a free tier with rate limits

## How to Update API Keys

1. Open the workflow in n8n
2. Click on each node mentioned above
3. Replace the placeholder values with your actual API keys
4. Save the workflow

## Security Note

**Never commit your actual API keys to version control!** The workflow file in this repository contains placeholder values. Always keep your real API keys secure and never share them publicly.
