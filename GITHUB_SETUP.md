# GitHub Setup Guide

Follow these steps to push your project to GitHub.

## Step 1: Create a GitHub Repository

1. Go to https://github.com/new
2. Repository name: `paper-search-agent` (or your preferred name)
3. Description: "Local n8n workflow for multi-source academic paper search using Ollama"
4. Choose **Public** or **Private** (your choice)
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click "Create repository"

## Step 2: Connect Local Repository to GitHub

After creating the repository, GitHub will show you commands. Use these:

```bash
# Make sure you're in the project directory
cd "C:\Ali\kaggle\n8n\Paper Search Agent"

# Add the remote repository (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/paper-search-agent.git

# Or if you prefer SSH:
# git remote add origin git@github.com:YOUR_USERNAME/paper-search-agent.git
```

## Step 3: Make Your First Commit

```bash
# Commit all files
git commit -m "Initial commit: Paper Search Agent workflow"

# Push to GitHub
git branch -M main
git push -u origin main
```

## Step 4: Verify

1. Go to your GitHub repository page
2. You should see all the files:
   - `README.md`
   - `API_KEYS.md`
   - `workflow/paper-search-agent.json`
   - `.gitignore`

## Future Updates

When you make changes to the project:

```bash
# Stage changes
git add .

# Commit with a descriptive message
git commit -m "Description of your changes"

# Push to GitHub
git push
```

## Important Notes

- ✅ The workflow file in `workflow/` has placeholder API keys - safe to commit
- ✅ Your original `Paper Search Agent.json` file is also included (you can remove it later if you want)
- ✅ `.gitignore` will prevent committing sensitive files like `.env` or database files
- ⚠️ **Never commit your actual API keys!**
