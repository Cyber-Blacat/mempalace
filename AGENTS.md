# MemPalace Agent Guidelines

This document provides guidelines for AI coding agents working in the MemPalace repository.

## Project Overview

MemPalace is an AI memory system that stores projects and conversations in a searchable "palace" using ChromaDB for vector storage. Key characteristics:
- **Python Version**: 3.9+
- **Build System**: Hatchling
- **Core Dependencies**: chromadb, pyyaml, rank-bm25
- **Architecture**: Hybrid retrieval (dense + sparse), room-based organization, temporal knowledge graph

## Build & Development Commands

### Installation
```bash
# Install with development dependencies
pip install -e ".[dev]"

# Install core only
pip install mempalace
```

### Package Management
```bash
# Build package
python -m build

# Run tests with coverage (minimum 30% required)
python -m pytest tests/ -v --cov=mempalace --cov-report=term-missing --cov-fail-under=30
```

## Testing Commands

### Running Tests
```bash
# All tests (excluding benchmarks, slow, and stress tests)
pytest tests/ -v

# All tests including benchmarks
pytest tests/ -v -m "not slow and not stress"

# Single test file
pytest tests/test_config.py -v

# Single test function
pytest tests/test_config.py::test_default_config -v

# Single test with specific marker
pytest tests/test_config.py::test_default_config -v -m "not slow"

# Tests with coverage reporting
pytest tests/ -v --cov=mempalace --cov-report=term-missing

# Run specific test module
python -m pytest tests.test_config -v
```

### Test Markers
Tests use pytest markers defined in `pyproject.toml`:
- `@pytest.mark.benchmark`: Scale/performance benchmark tests
- `@pytest.mark.slow`: Tests that take > 30 seconds
- `@pytest.mark.stress`: Destructive scale tests (100K+ drawers)

### Benchmark Execution
```bash
# Run benchmark tests (separate from unit tests)
pytest tests/benchmarks/ -v -m benchmark

# Run specific benchmark script
python benchmarks/longmemeval_bench.py /path/to/data.json
```

### Test Isolation
Tests run in isolation with HOME redirected to temp directory. See `tests/conftest.py` for fixtures:
- `tmp_dir`: Temporary directory
- `palace_path`: Empty palace directory
- `config`: MempalaceConfig with temp palace
- `collection`: ChromaDB collection
- `seeded_collection`: Pre-populated collection
- `kg`: Isolated KnowledgeGraph

## Linting & Formatting

### Ruff Commands
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

### Pre-commit Hooks
Pre-commit hooks are configured in `.pre-commit-config.yaml`:
- `ruff`: Linting with auto-fix
- `ruff-format`: Formatting check

### Style Configuration (pyproject.toml)
- **Line length**: 100 characters
- **Quote style**: Double quotes (`quote-style = "double"`)
- **Target Python version**: 3.9+
- **Lint rules**: Selects E, F, W codes, ignores E501 (line length)

## Code Style Guidelines

### Naming Conventions
- **Functions/Variables**: `snake_case`
- **Classes**: `PascalCase` (e.g., `MempalaceConfig`, `HybridRetriever`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_PALACE_PATH`)
- **Private methods**: `_private_method()` (single underscore)
- **Module names**: `snake_case` (e.g., `knowledge_graph.py`)

### Import Organization
Follow this order with blank lines between groups:
```python
# 1. Standard library imports
import json
import os
from pathlib import Path

# 2. Third-party imports
import chromadb
import yaml

# 3. Local imports (absolute imports preferred)
from .config import MempalaceConfig
from .embedding_function import get_embedding_function
```

### Type Hints
- Use type hints on all public functions and methods
- Import from `typing` module: `List`, `Dict`, `Optional`, `Tuple`, `Any`
- Include return type annotations

### Error Handling
1. **Custom Exceptions**: Define specific exception classes
2. **Exception Chaining**: Use `raise ... from e` pattern
3. **User-friendly Messages**: Provide helpful error messages
4. **Graceful Degradation**: Continue operation when possible
5. **Input Validation**: Use `ValueError` for invalid arguments

### Docstrings
All public modules, classes, and functions must have docstrings with Args, Returns, and Raises sections.

## Agent Configuration

### AI Agent Plugins
- `.agents/plugins/marketplace.json`: Configuration for AI agent plugins
- `.claude-plugin/`: Claude Code plugin configuration
- `.codex-plugin/`: Cursor plugin configuration

## Architecture Patterns

### Hybrid Retrieval
- **Dense search**: ChromaDB embeddings
- **Sparse search**: BM25 keyword matching
- **Fusion**: α * dense_score + β * sparse_score
- Default weights: α=0.7 (dense), β=0.3 (sparse)

## Key Principles

1. **Verbatim First**: Never summarize user content - store exact words
2. **Local First**: Everything runs on user's machine, no cloud dependencies
3. **Zero API by Default**: Core features work without API keys
4. **Minimal Dependencies**: ChromaDB + PyYAML only as core dependencies

---

*Last updated based on analysis of MemPalace v3.0.14*