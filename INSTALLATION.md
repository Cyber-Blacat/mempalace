# MemPalace - Complete Installation Guide

## 📋 System Requirements

### Operating System
- **Windows**: Windows 10/11 (64-bit)
- **macOS**: macOS 10.15+ (Catalina and later)
- **Linux**: Ubuntu 18.04+, CentOS 7+, Debian 10+, and most modern distributions

### Python Version
- **Required**: Python 3.9+ 
- **Supported**: Python 3.9, 3.10, 3.11, 3.12, 3.13
- **Package Manager**: pip (latest version recommended)

### Hardware Requirements
- **RAM**: Minimum 4GB, Recommended 8GB+
- **Disk Space**: 
  - ~500MB for dependencies
  - Additional space for your palace (ChromaDB data storage)
- **CPU**: Any modern processor (multi-core recommended for better performance)

---

## 🚀 Quick Start (5 Minutes)

### Option A: Install from PyPI (Recommended for Users)

```bash
# Install MemPalace
pip install mempalace

# Verify installation
mempalace --version

# Should output: MemPalace v3.0.14+
```

### Option B: Install from Source (Recommended for Developers)

```bash
# Clone the repository
git clone https://github.com/milla-jovovich/mempalace.git
cd mempalace

# Install with development dependencies
pip install -e ".[dev]"

# Verify installation
mempalace --version
```

---

## 📦 Detailed Installation

### 1. Install MemPalace

### 1. Install MemPalace

#### Standard Installation
```bash
# Install MemPalace with core dependencies
pip install mempalace
```

#### Development Installation
```bash
# Install with development tools (pytest, ruff, etc.)
pip install -e ".[dev]"
```

#### Manual Dependency Installation
If you prefer to install dependencies manually:
```bash
# Core dependencies
pip install chromadb>=0.5.0,<0.7
pip install pyyaml>=6.0
pip install rank-bm25>=0.2.2

# Optional development dependencies
pip install pytest>=7.0
pip install pytest-cov>=4.0
pip install ruff>=0.4.0
pip install psutil>=5.9
```

### 2. Verify Installation

```bash
# Check Python version
python --version  # Should be 3.9+

# Check MemPalace installation
mempalace --version

# Test imports
python -c "import chromadb, yaml, rank_bm25; print('✓ All imports successful')"
```

---

## ✅ Verification & Testing

### Quick Verification
```bash
# Run basic verification
mempalace --help  # Should show available commands

# Test the demo system (if installed from source)
python demo_hybrid/verify_demo.py
```

### Run Test Suite
```bash
# Run all tests (excluding benchmarks and slow tests)
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=mempalace --cov-report=term-missing

# Run specific test categories
pytest tests/ -m "not slow and not stress"  # Skip slow/stress tests
pytest tests/benchmarks/ -m benchmark       # Run benchmark tests only
```

### Demo System (Source Installation Only)
```bash
# Run interactive demo
python demo_hybrid/main.py

# Options:
# 1. Run all test queries automatically
# 2. Single query demo with details
# 3. Compare aggregation methods
# 4. Interactive mode (enter your own queries)
```

---

## 🔧 Configuration

### Initial Setup
```bash
# Initialize your palace (one-time setup)
mempalace init ~/projects/myapp

# This creates:
# - ~/.mempalace/config.json (configuration)
# - ~/.mempalace/palace/ (ChromaDB database)
# - ~/.mempalace/people_map.json (entity mapping)
```

### Configuration Files

#### Main Configuration (~/.mempalace/config.json)
```json
{
  "palace_path": "~/.mempalace/palace",
  "collection_name": "mempalace_drawers",
  "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
  "hybrid_search": {
    "enabled": true,
    "alpha": 0.7,
    "beta": 0.3,
    "doc_top_k": 20,
    "room_top_k": 5,
    "aggregation_method": "average"
  }
}
```

#### Environment Variables
```bash
# Override configuration via environment variables
export MEMPALACE_PALACE_PATH="/custom/path"
export MEMPALACE_COLLECTION_NAME="my_collection"
```

---

## 🐍 Python Environment Details

### Check Your Environment
```bash
# Check Python version
python --version

# Check installed packages
pip list | grep -E "mempalace|chromadb|rank-bm25"

# Verify ChromaDB installation
python -c "import chromadb; print(f'ChromaDB version: {chromadb.__version__}')"
```

### Common Python Issues

#### Multiple Python Versions
If you have multiple Python versions installed:
```bash
# Use specific Python version
python3.11 -m pip install mempalace
python3.11 -m mempalace --version
```

#### Permission Issues
```bash
# Install for current user only
pip install --user mempalace
```

---

## 🔍 Troubleshooting

### Issue 1: `ModuleNotFoundError: No module named 'rank_bm25'`
```bash
# Install the missing dependency
pip install rank-bm25
```

### Issue 2: `ModuleNotFoundError: No module named 'chromadb'`
```bash
# Install ChromaDB
pip install chromadb>=0.5.0,<0.7
```

### Issue 3: ChromaDB SQLite Error (Windows)
```bash
# Install pysqlite3 for better SQLite support
pip install pysqlite3-binary
```

### Issue 4: Permission Denied
```bash
# Use --user flag
pip install --user mempalace

```

### Issue 5: Python Version Mismatch
```bash
# Check Python version
python --version

# If wrong version, specify correct one
python3.11 -m pip install mempalace
```



---

## 📁 Project Structure After Installation

```
mempalace/
├── ~/.mempalace/               # User configuration directory
│   ├── config.json             # Configuration file
│   ├── people_map.json         # Entity mapping
│   └── palace/                 # ChromaDB data storage
├── mempalace/                  # Core package (installed)
│   ├── cli.py                  # Command-line interface
│   ├── config.py               # Configuration management
│   ├── searcher.py             # Search functionality
│   ├── miner.py                # Data ingestion
│   ├── knowledge_graph.py      # Temporal knowledge graph
│   └── ...                     # Other modules
└── ...                         # Other directories
```

---

## 🚦 First-Time Setup

### 1. Initialize Your Palace
```bash
mempalace init ~/projects/myapp
```

### 2. Mine Your First Data
```bash
# Mine project files (code, docs, notes)
mempalace mine ~/projects/myapp

# Mine conversation exports (Claude, ChatGPT, Slack)
mempalace mine ~/chats/ --mode convos

# Mine with automatic classification
mempalace mine ~/chats/ --mode convos --extract general
```

### 3. Test Search
```bash
# Search for anything you've mined
mempalace search "authentication system"
mempalace search "database migration"
mempalace search "project planning decisions"
```

### 4. Check Status
```bash
# See what's been filed
mempalace status
```

---

## 🔄 Updating & Maintenance

### Update MemPalace
```bash
# Update to latest version
pip install --upgrade mempalace

# Update specific dependency
pip install --upgrade chromadb
```

### Clean Reinstallation
```bash
# Clean reinstall MemPalace
pip install --force-reinstall mempalace
```

### Clear Cache
```bash
# Clear pip cache
pip cache purge

# Clear ChromaDB cache (if experiencing issues)
rm -rf ~/.cache/chromadb/
```

---

## 📊 Performance Expectations

### Query Performance
- **Initial setup**: ~1-2 minutes (first-time indexing)
- **Subsequent searches**: < 100ms for typical queries
- **Hybrid search pipeline**: ~150-200ms end-to-end
- **Memory indexing**: ~1 second per 1,000 documents

### Memory Usage
- **ChromaDB storage**: ~2x original document size
- **BM25 index**: ~1.5x document size
- **Typical usage**: 100MB for 10,000 documents

---

## 🆘 Getting Help

### Diagnostic Commands
```bash
# Check installation
mempalace --version
python --version

# Check dependencies
pip list | grep -E "mempalace|chromadb|rank-bm25|pyyaml"

# Run verification
python demo_hybrid/verify_demo.py  # If installed from source
```

### Common Solutions
1. **Reinstall dependencies**: `pip install --force-reinstall mempalace`
2. **Clear cache**: `pip cache purge`
3. **Check Python version**: Must be 3.9+

### Resources
1. **[QUICKSTART.md](QUICKSTART.md)** - Quick start guide
2. **[README.md](README.md)** - Project overview
3. **[INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)** - API and integration guide
4. **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guidelines
5. **[docs_zh/](docs_zh/)** - Chinese documentation

---

## 📝 Installation Checklist

- [ ] Python 3.9+ installed
- [ ] pip package manager available
- [ ] MemPalace installed (`pip install mempalace`)
- [ ] Installation verified (`mempalace --version`)
- [ ] Dependencies confirmed (`pip list | grep chromadb`)
- [ ] Palace initialized (`mempalace init ~/projects/myapp`)
- [ ] Test search working (`mempalace search "test"`)

---

## 🎉 Installation Complete!

If you've completed the verification steps, MemPalace is ready to use!

**Next Steps**:
1. **Initialize your palace**: `mempalace init ~/your/project`
2. **Mine some data**: `mempalace mine ~/your/project`
3. **Try search**: `mempalace search "your query"`
4. **Integrate with your AI**: See [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)
5. **Explore examples**: Check the `examples/` directory

**Need Help?**
- Check the documentation: `DOCUMENTATION_INDEX.md`
- Run diagnostics: `python demo_hybrid/verify_demo.py` (source installation)
- Check logs for errors

---

**Installation Guide Version**: 2.0  
**Last Updated**: 2026-04-10  
**Compatibility**: MemPalace v3.0.14+