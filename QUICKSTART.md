# MemPalace - Quick Start Guide

**Get started with MemPalace in 3 simple steps!**

## ⚡ 3-Step Quick Start

### Step 1: Install MemPalace
```bash
pip install mempalace
```

### Step 2: Initialize Your Palace
```bash
mempalace init ~/projects/myapp
```

### Step 3: Start Using It
```bash
# Mine your data
mempalace mine ~/projects/myapp

# Search for anything
mempalace search "your query"
```

**That's it!** 🎉

---

## 📋 Requirements

- **Python 3.9+** (Python 3.9, 3.10, 3.11, 3.12, 3.13)
- **pip** (Python package manager)

---

## 🎯 What You Can Do

### 1. Initialize and Mine (2 minutes)
```bash
# Initialize palace for a project
mempalace init ~/projects/myapp

# Mine project files
mempalace mine ~/projects/myapp

# Mine conversations (Claude, ChatGPT, Slack exports)
mempalace mine ~/chats/ --mode convos

# Mine with automatic classification
mempalace mine ~/chats/ --mode convos --extract general
```

### 2. Search Everything (Seconds)
```bash
# Semantic search across all your data
mempalace search "authentication system"
mempalace search "database migration strategy"
mempalace search "project planning decisions"

# Filter by wing (project)
mempalace search "API design" --wing myapp

# Filter by room (aspect)
mempalace search "testing framework" --room testing
```

### 3. Check Status
```bash
# See what's been filed
mempalace status

# Wake-up context for your AI
mempalace wake-up

# Wake-up for specific project
mempalace wake-up --wing myapp
```

### 4. Integrate with Your AI (5 minutes)
```bash
# For MCP-compatible tools (Claude, ChatGPT, Cursor, Gemini)
claude mcp add mempalace -- python -m mempalace.mcp_server

# For Claude Code (recommended)
claude plugin marketplace add milla-jovovich/mempalace
claude plugin install --scope user mempalace
```

---

## 🔧 Quick Test Commands

```bash
# Verify installation
mempalace --version

# Test search with example query
mempalace search "test"

# Check command-line help
mempalace --help
mempalace init --help
mempalace mine --help
mempalace search --help

# Test Python imports (development)
python -c "from mempalace.searcher import search; print('✓ Search module imported')"
```

---

## 📊 Expected Results

### Successful Installation
```
$ mempalace --version
MemPalace v3.0.14+
```

### Successful Initialization
```
$ mempalace init ~/projects/myapp
Initializing palace for: ~/projects/myapp
Configuration saved to: ~/.mempalace/config.json
Palace directory created: ~/.mempalace/palace
```

### Successful Mining
```
$ mempalace mine ~/projects/myapp
Mining project files from: ~/projects/myapp
Processing 15 files...
Added 47 drawers to palace
```

### Search Results
```
$ mempalace search "database migration"
Search results (5/47):

1. [backend/database] Score: 0.92
   Database migration strategy using Alembic with PostgreSQL 15...

2. [backend/database] Score: 0.87  
   Backup and recovery procedures for production databases...

3. [planning/infra] Score: 0.81
   Q3 migration timeline and team assignments...
```

---

## 🚀 Next Steps

### 1. Read Detailed Documentation
- **[INSTALLATION.md](INSTALLATION.md)** - Complete installation guide
- **[README.md](README.md)** - Project overview and features
- **[INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)** - API and integration guide
- **[DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)** - Full documentation index

### 2. Explore Examples
```bash
# Check examples directory
ls examples/

# Try example scripts
python examples/basic_mining.py
python examples/convo_import.py
```

### 3. Learn the CLI
```bash
# All available commands
mempalace --help

# Command-specific help
mempalace init --help
mempalace mine --help
mempalace search --help
mempalace status --help
mempalace wake-up --help
```

### 4. Integrate into Your Workflow
```python
# Python API example
from mempalace.searcher import search_memories

results = search_memories(
    query="authentication decisions",
    palace_path="~/.mempalace/palace",
    wing="myapp",
    n_results=10
)
```

---

## 🆘 Troubleshooting

### "Module not found: rank_bm25"
```bash
pip install rank-bm25
```

### "Module not found: chromadb"
```bash
pip install chromadb
```

### "Python version error"
```bash
python --version  # Must be 3.9+
python3 --version # Try python3 if python doesn't work
```

### "Command not found: mempalace"
```bash
# Check if pip install was successful
pip show mempalace

# Try reinstalling
pip install --force-reinstall mempalace

# Or install for current user
pip install --user mempalace
```

### "Permission denied"
```bash
# Install for current user only
pip install --user mempalace
```

### Still having issues?
```bash
# Clean reinstall
pip install --force-reinstall mempalace

# Check detailed installation guide
# See INSTALLATION.md for complete troubleshooting
```

---

## 📦 What Gets Installed

### Core Dependencies
- `chromadb>=0.5.0,<0.7` - Vector database for embeddings
- `pyyaml>=6.0` - YAML configuration support  
- `rank-bm25>=0.2.2` - BM25 algorithm for keyword search

### Optional Development Dependencies
- `pytest>=7.0` - Testing framework
- `pytest-cov>=4.0` - Coverage reporting
- `ruff>=0.4.0` - Linter and formatter
- `psutil>=5.9` - System monitoring

---

## 📝 Quick Reference

### Installation Options
```bash
# Standard installation
pip install mempalace

# Development installation (from source)
git clone https://github.com/milla-jovovich/mempalace.git
cd mempalace
pip install -e ".[dev]"
```

### Common Commands
```bash
# Initialize new palace
mempalace init <directory>

# Mine data
mempalace mine <directory>                    # Projects
mempalace mine <directory> --mode convos      # Conversations
mempalace mine <directory> --mode convos --extract general  # With classification

# Search
mempalace search "query"
mempalace search "query" --wing <project>
mempalace search "query" --room <aspect>

# Information
mempalace status
mempalace wake-up
mempalace wake-up --wing <project>
```

---

**Need more help?** Check [INSTALLATION.md](INSTALLATION.md) for detailed instructions and troubleshooting.

---

**Quick Start Guide Version**: 2.0  
**Last Updated**: 2026-04-10  
**For**: MemPalace v3.0.14+