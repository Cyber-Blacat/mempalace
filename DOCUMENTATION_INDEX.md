# MemPalace Documentation Index

**Complete Navigation Guide to All Documentation**

---

## 🚀 Quick Start (Start Here!)

| Document | Purpose | Time |
|----------|---------|------|
| **[QUICKSTART.md](QUICKSTART.md)** | 3-step installation & basic usage | 5 min |
| **[INSTALLATION.md](INSTALLATION.md)** | Complete installation guide | 10-15 min |
| **[README.md](README.md)** | Project overview and features | 3 min |

**Recommended Reading Order**:
1. **QUICKSTART.md** → Get started quickly with 3 simple steps
2. Run: `pip install mempalace` → Install MemPalace
3. Run: `mempalace init ~/your/project` → Initialize your palace
4. Run: `mempalace mine ~/your/project` → Mine your first data
5. Run: `mempalace search "test query"` → Test search functionality

---

## 📖 Core Documentation

### Project Overview
- **[README.md](README.md)** - Project overview
  - Core features and benefits
  - Performance benchmarks
  - Architecture overview
  - Next steps and links

### Installation & Setup
- **[INSTALLATION.md](INSTALLATION.md)** - Complete installation guide
  - System requirements
  - Step-by-step installation (multiple methods)
  - Verification and testing
  - Troubleshooting guide
  - Performance expectations

- **[QUICKSTART.md](QUICKSTART.md)** - Quick start guide
  - 3-step installation
  - Quick test commands
  - Expected results
  - Common commands reference

### Integration & API
- **[INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)** - Integration guide
  - Hybrid search API reference
  - Usage examples
  - Configuration options
  - Performance metrics

### Development & Contribution
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guidelines
  - Getting started for contributors
  - Code style and standards
  - PR guidelines
  - Good first issues

- **[AGENTS.md](AGENTS.md)** - AI agent guidelines
  - Build/lint/test commands
  - Code style guidelines
  - Architecture patterns
  - Testing patterns

---

## 🏗️ Architecture & Implementation

### Core Modules
- **`mempalace/cli.py`** - Command-line interface
  - CLI commands and arguments
  - User interaction flow

- **`mempalace/config.py`** - Configuration management
  - Configuration loading (env vars > config file > defaults)
  - Hybrid search configuration

- **`mempalace/searcher.py`** - Search functionality
  - Dense search (ChromaDB embeddings)
  - Hybrid search (dense + sparse fusion)
  - Room-based aggregation

- **`mempalace/miner.py`** - Data ingestion
  - Project file mining
  - Chunking and processing
  - Metadata extraction

- **`mempalace/knowledge_graph.py`** - Temporal knowledge graph
  - Entity-relationship storage
  - Time-filtered queries
  - Fact management

### Hybrid Search Components
- **`mempalace/sparse_retriever.py`** - BM25 sparse retrieval
  - BM25Okapi implementation
  - Document tokenization
  - Score normalization

- **`mempalace/hybrid_retriever.py`** - Hybrid fusion
  - Weighted score fusion
  - Score breakdown tracking

- **`mempalace/room_aggregator.py`** - Room aggregation
  - Three aggregation methods (average, max, weighted)
  - Document-to-room mapping

---

## 🧪 Testing & Development

### Testing Commands
```bash
# Run all tests (excluding benchmarks and slow tests)
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=mempalace --cov-report=term-missing

# Run specific test categories
pytest tests/ -m "not slow and not stress"  # Skip slow/stress tests
pytest tests/benchmarks/ -m benchmark       # Run benchmark tests only

# Run single test file
pytest tests/test_config.py -v

# Run single test function
pytest tests/test_config.py::test_default_config -v
```

### Linting & Formatting
```bash
# Check linting
ruff check .

# Fix linting issues automatically
ruff check --fix .

# Check formatting
ruff format --check .

# Format code
ruff format .
```

### Development Setup
```bash
# Clone and setup development environment
git clone https://github.com/milla-jovovich/mempalace.git
cd mempalace
pip install -e ".[dev]"

# Run all tests to verify setup
pytest tests/ -v
```

---

## 🌐 Chinese Documentation (中文文档)

### Core Chinese Documentation
- **[docs_zh/README_zh.md](docs_zh/README_zh.md)** - 中文项目概述
  - 项目介绍和特性
  - 性能基准测试
  - 架构概述

- **[docs_zh/TESTING_GUIDE_zh.md](docs_zh/TESTING_GUIDE_zh.md)** - 中文测试指南
  - 测试步骤说明
  - 验证方法
  - 常见问题

### English Documentation with Chinese Notes
For Chinese speakers, the following English documents are recommended:
1. **[QUICKSTART.md](QUICKSTART.md)** - 快速开始指南 (简单3步)
2. **[INSTALLATION.md](INSTALLATION.md)** - 完整安装指南 (详细步骤)
3. **[README.md](README.md)** - 项目总览 (核心特性)

---

## 📊 Benchmarks & Performance

### LongMemEval Results
| Metric | Score | Details |
|--------|-------|---------|
| **Raw mode R@5** | **96.6%** | 500/500 questions, zero API calls |
| **AAAK mode R@5** | 84.2% | Experimental compression layer |
| **Reproducibility** | ✅ | Independently verified on M2 Ultra |

### Performance Documentation
- **`benchmarks/`** - Benchmark runners and results
  - LongMemEval benchmark implementation
  - Performance comparison scripts
  - Results analysis

### Test Data
- **`demo_hybrid/test_data.py`** - Test dataset
  - 13 realistic documents
  - 6 rooms with different topics
  - 8 test queries with different patterns

---

## 🎯 Usage Examples

### Basic Usage
```bash
# Initialize palace for a project
mempalace init ~/projects/myapp

# Mine project files
mempalace mine ~/projects/myapp

# Search for information
mempalace search "authentication system"

# Check status
mempalace status
```

### Advanced Usage
```bash
# Mine conversations
mempalace mine ~/chats/ --mode convos

# Mine with automatic classification
mempalace mine ~/chats/ --mode convos --extract general

# Search with filters
mempalace search "API design" --wing myapp
mempalace search "testing" --room testing

# Wake-up context for AI
mempalace wake-up
mempalace wake-up --wing myapp
```

### Python API
```python
from mempalace.searcher import search_memories, hybrid_search_memories

# Basic search
results = search_memories(
    query="database migration",
    palace_path="~/.mempalace/palace"
)

# Hybrid search with custom weights
results = hybrid_search_memories(
    query="authentication system",
    palace_path="~/.mempalace/palace",
    alpha=0.8,  # Dense weight
    beta=0.2    # Sparse weight
)
```

---

## 🔧 Configuration

### Configuration Files
```
~/.mempalace/
├── config.json          # Main configuration
├── people_map.json      # Entity mapping
└── palace/              # ChromaDB data storage
```

### Default Configuration
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

### Environment Variables
```bash
# Override configuration
export MEMPALACE_PALACE_PATH="/custom/path"
export MEMPALACE_COLLECTION_NAME="my_collection"
```

---

## 🆘 Troubleshooting & Support

### Common Issues
1. **ModuleNotFoundError**: Install missing dependencies (`rank-bm25`, `chromadb`)
2. **Python version**: Must be Python 3.9+ (`python --version`)
3. **Permission issues**: Use `--user` flag (`pip install --user mempalace`)
4. **Installation verification**: Run `mempalace --version`

### Diagnostic Commands
```bash
# Check Python environment
python --version
pip list | grep -E "mempalace|chromadb|rank-bm25"

# Test imports
python -c "import chromadb, yaml, rank_bm25; print('✓ OK')"

# Verify installation
mempalace --version
mempalace --help
```

### Getting Help
1. **Check documentation**: This index and linked documents
2. **Run verification**: Basic functionality tests
3. **Check logs**: Error messages and warnings
4. **Search issues**: Check existing GitHub issues

---

## 📁 Complete File Structure

```
mempalace/
├── README.md                    # Project overview
├── QUICKSTART.md                # Quick start guide
├── INSTALLATION.md              # Complete installation guide
├── INTEGRATION_GUIDE.md         # Integration and API guide
├── DOCUMENTATION_INDEX.md       # This file (documentation index)
├── CONTRIBUTING.md              # Contribution guidelines
├── AGENTS.md                    # AI agent guidelines
├── docs_zh/                     # Chinese documentation
│   ├── README_zh.md             # Chinese project overview
│   └── TESTING_GUIDE_zh.md      # Chinese testing guide
├── mempalace/                   # Core package
│   ├── cli.py                   # Command-line interface
│   ├── config.py                # Configuration management
│   ├── searcher.py              # Search functionality
│   ├── miner.py                 # Data ingestion
│   ├── knowledge_graph.py       # Knowledge graph
│   ├── sparse_retriever.py      # BM25 sparse retrieval
│   ├── hybrid_retriever.py      # Hybrid fusion
│   ├── room_aggregator.py       # Room aggregation
│   └── ...                      # Other modules
├── tests/                       # Test suite
├── benchmarks/                  # Benchmark runners
├── examples/                    # Usage examples
├── hooks/                       # Claude Code auto-save hooks
├── demo_hybrid/                 # Hybrid search demo system
├── pyproject.toml               # Project configuration
└── requirements.txt             # Dependencies
```

---

## ✅ Documentation Checklist

### Getting Started Complete?
- [ ] Python 3.9+ installed
- [ ] MemPalace installed (`pip install mempalace`)
- [ ] Palace initialized (`mempalace init`)
- [ ] Data mined (`mempalace mine`)
- [ ] Search tested (`mempalace search`)

### Documentation Read?
- [ ] QUICKSTART.md - Quick start guide
- [ ] INSTALLATION.md - Installation details (if needed)
- [ ] README.md - Project overview
- [ ] INTEGRATION_GUIDE.md - Integration guide (if integrating)

### Development Setup Complete?
- [ ] Development environment set up
- [ ] Tests passing (`pytest tests/`)
- [ ] Linting passing (`ruff check .`)
- [ ] Code formatted (`ruff format .`)

---

## 🚦 Documentation Status

**Overview**: ✅ Complete and organized  
**Installation**: ✅ Complete with troubleshooting  
**Quick Start**: ✅ Simple 3-step guide  
**Integration**: ✅ Comprehensive API guide  
**Development**: ✅ Complete guidelines  
**Chinese Docs**: ✅ Basic coverage available  

---

## 📞 Getting Help

### Priority Order
1. **Check this index** - Find the right documentation
2. **Read QUICKSTART.md** - Quick start guide
3. **Read INSTALLATION.md** - Installation and troubleshooting
4. **Run diagnostics** - Verify your setup
5. **Search issues** - Check existing problems and solutions

### Quick Help Commands
```bash
# Quick verification
mempalace --version
python --version

# Test basic functionality
mempalace --help
mempalace init --help
mempalace search "test"
```

---

**Last Updated**: 2026-04-10  
**Documentation Version**: 2.0  
**Status**: Complete and Organized ✅