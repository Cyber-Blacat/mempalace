<div align="center">

<img src="assets/mempalace_logo.png" alt="MemPalace" width="280">

# MemPalace

### The highest-scoring AI memory system ever benchmarked. And it's free.

<br>

Every conversation you have with an AI — every decision, every debugging session, every architecture debate — disappears when the session ends. Six months of work, gone. You start over every time.

Other memory systems try to fix this by letting AI decide what's worth remembering. It extracts "user prefers Postgres" and throws away the conversation where you explained *why*. MemPalace takes a different approach: **store everything, then make it findable.**

**The Palace** — Ancient Greek orators memorized entire speeches by placing ideas in rooms of an imaginary building. Walk through the building, find the idea. MemPalace applies the same principle to AI memory: your conversations are organized into wings (people and projects), halls (types of memory), and rooms (specific ideas). No AI decides what matters — you keep every word, and the structure gives you a navigable map instead of a flat search index.

**Raw verbatim storage** — MemPalace stores your actual exchanges in ChromaDB without summarization or extraction. The 96.6% LongMemEval result comes from this raw mode. We don't burn an LLM to decide what's "worth remembering" — we keep everything and let semantic search find it.

**AAAK (experimental)** — A lossy abbreviation dialect for packing repeated entities into fewer tokens at scale. Readable by any LLM that reads text — Claude, GPT, Gemini, Llama, Mistral — no decoder needed. **AAAK is a separate compression layer, not the storage default**, and on the LongMemEval benchmark it currently regresses vs raw mode (84.2% vs 96.6%). We're iterating. See the [note above](#a-note-from-milla--ben--april-7-2026) for the honest status.

**Local, open, adaptable** — MemPalace runs entirely on your machine, on any data you have locally, without using any external API or services. It has been tested on conversations — but it can be adapted for different types of datastores. This is why we're open-sourcing it.

<br>

[![][version-shield]][release-link]
[![][python-shield]][python-link]
[![][license-shield]][license-link]
[![][discord-shield]][discord-link]

<br>

[Quick Start](#getting-started) · [Features](#key-features) · [Benchmarks](#performance-benchmarks) · [Architecture](#architecture-overview)

<br>

### Highest LongMemEval score ever published — free or paid.

<table>
<tr>
<td align="center"><strong>96.6%</strong><br><sub>LongMemEval R@5<br><b>raw mode</b>, zero API calls</sub></td>
<td align="center"><strong>500/500</strong><br><sub>questions tested<br>independently reproduced</sub></td>
<td align="center"><strong>$0</strong><br><sub>No subscription<br>No cloud. Local only.</sub></td>
</tr>
</table>

<sub>Reproducible — runners in <a href="benchmarks/">benchmarks/</a>. <a href="benchmarks/BENCHMARKS.md">Full results</a>. The 96.6% is from <b>raw verbatim mode</b>, not AAAK or rooms mode (those score lower — see <a href="#a-note-from-milla--ben--april-7-2026">note above</a>).</sub>

</div>

---

## A Note from Milla & Ben — April 7, 2026

> The community caught real problems in this README within hours of launch and we want to address them directly.
>
> **What we got wrong:**
>
> - **The AAAK token example was incorrect.** We used a rough heuristic (`len(text)//3`) for token counts instead of an actual tokenizer. Real counts via OpenAI's tokenizer: the English example is 66 tokens, the AAAK example is 73. AAAK does not save tokens at small scales — it's designed for *repeated entities at scale*, and the README example was a bad demonstration of that. We're rewriting it.
>
> - **"30x lossless compression" was overstated.** AAAK is a lossy abbreviation system (entity codes, sentence truncation). Independent benchmarks show AAAK mode scores **84.2% R@5 vs raw mode's 96.6%** on LongMemEval — a 12.4 point regression. The honest framing is: AAAK is an experimental compression layer that trades fidelity for token density, and **the 96.6% headline number is from RAW mode, not AAAK**.
>
> - **"+34% palace boost" was misleading.** That number compares unfiltered search to wing+room metadata filtering. Metadata filtering is a standard ChromaDB feature, not a novel retrieval mechanism. Real and useful, but not a moat.
>
> - **"Contradiction detection"** exists as a separate utility (`fact_checker.py`) but is not currently wired into the knowledge graph operations as the README implied.
>
> - **"100% with Haiku rerank"** is real (we have the result files) but the rerank pipeline is not in the public benchmark scripts. We're adding it.
>
> **What's still true and reproducible:**
>
> - **96.6% R@5 on LongMemEval in raw mode**, on 500 questions, zero API calls — independently reproduced on M2 Ultra in under 5 minutes by [@gizmax](https://github.com/milla-jovovich/mempalace/issues/39).
> - Local, free, no subscription, no cloud, no data leaving your machine.
> - The architecture (wings, rooms, closets, drawers) is real and useful, even if it's not a magical retrieval boost.
>
> **What we're doing:**
>
> 1. Rewriting the AAAK example with real tokenizer counts and a scenario where AAAK actually demonstrates compression
> 2. Adding `mode raw / aaak / rooms` clearly to the benchmark documentation so the trade-offs are visible
> 3. Wiring `fact_checker.py` into the KG ops so the contradiction detection claim becomes true
> 4. Pinning ChromaDB to a tested range (Issue #100), fixing the shell injection in hooks (#110), and addressing the macOS ARM64 segfault (#74)
>
> **Thank you to everyone who poked holes in this.** Brutal honest criticism is exactly what makes open source work, and it's what we asked for. Special thanks to [@panuhorsmalahti](https://github.com/milla-jovovich/mempalace/issues/43), [@lhl](https://github.com/milla-jovovich/mempalace/issues/27), [@gizmax](https://github.com/milla-jovovich/mempalace/issues/39), and everyone who filed an issue or a PR in the first 48 hours. We're listening, we're fixing, and we'd rather be right than impressive.
>
> — *Milla Jovovich & Ben Sigman*

---

## Getting Started

### Quick Start
For a quick installation and setup, see [QUICKSTART.md](QUICKSTART.md).

```bash
# Install
pip install mempalace

# Quick setup
mempalace init ~/projects/myapp
mempalace mine ~/projects/myapp
mempalace search "your query"
```

### Detailed Installation
For complete installation instructions, system requirements, and troubleshooting, see [INSTALLATION.md](INSTALLATION.md).

### Integration Guide
For API reference, usage examples, and integration with your AI tools, see [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md).

### Documentation Index
See [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) for a complete guide to all documentation.

---

## Key Features

### Local & Private
- **Zero cloud dependencies**: Everything runs on your machine
- **No API keys required**: Core features work offline
- **Verbatim storage**: Stores exact words, never summarizes

### Hybrid Search Architecture
- **Dense search**: ChromaDB embeddings for semantic similarity
- **Sparse search**: BM25 keyword matching
- **Hybrid fusion**: Weighted combination of both methods
- **Room-based organization**: Wings → Rooms → Closets → Drawers

### AI Integration
- **MCP server**: Works with Claude, ChatGPT, Cursor, Gemini
- **Claude Code plugin**: Native marketplace installation
- **Gemini CLI**: Native integration support
- **Local LLMs**: Wake-up command + CLI search

---

## Performance Benchmarks

### LongMemEval Results
| Metric | Score | Details |
|--------|-------|---------|
| **Raw mode R@5** | **96.6%** | 500/500 questions, zero API calls |
| **AAAK mode R@5** | 84.2% | Experimental compression layer |
| **Reproducibility** | ✅ | Independently verified on M2 Ultra |

### Cost Comparison
| Method | Annual Cost | Tokens Loaded |
|--------|-------------|---------------|
| LLM summaries | ~$507/yr | ~650K tokens |
| **MemPalace wake-up** | **~$0.70/yr** | **~170 tokens** |
| **MemPalace + searches** | **~$10/yr** | **~13,500 tokens** |

---

## Architecture Overview

MemPalace organizes information using a palace metaphor:

### Wings
Projects, people, or topics. Each gets its own wing in the palace.

### Rooms
Aspects within wings (e.g., "backend", "planning", "costs").

### Closets & Drawers
Individual content chunks with metadata for precise retrieval.

### Knowledge Graph
Temporal entity-relationship graph for structured memory.

### Hybrid Retrieval
Combines dense semantic search with sparse keyword matching for optimal recall.

---

## Next Steps

1. **Install**: See [INSTALLATION.md](INSTALLATION.md) for complete setup
2. **Try**: See [QUICKSTART.md](QUICKSTART.md) for quick examples
3. **Integrate**: See [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) for API usage
4. **Explore**: Check the `examples/` directory for usage patterns

---

## Documentation Structure

### English Documentation (Root)
- **[README.md](README.md)** - Project overview (this file)
- **[QUICKSTART.md](QUICKSTART.md)** - Quick start guide
- **[INSTALLATION.md](INSTALLATION.md)** - Complete installation guide
- **[INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)** - API and integration guide
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guidelines
- **[AGENTS.md](AGENTS.md)** - AI agent guidelines
- **[DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)** - Full documentation index

### Chinese Documentation (docs_zh/)
- **[docs_zh/README_zh.md](docs_zh/README_zh.md)** - 中文项目概述
- **[docs_zh/TESTING_GUIDE_zh.md](docs_zh/TESTING_GUIDE_zh.md)** - 中文测试指南

---

**Last Updated**: 2026-04-10  
**Version**: MemPalace v3.0.14+

[version-shield]: https://img.shields.io/github/v/release/milla-jovovich/mempalace?include_prereleases&label=version
[release-link]: https://github.com/milla-jovovich/mempalace/releases
[python-shield]: https://img.shields.io/badge/python-3.9+-blue
[python-link]: https://www.python.org/
[license-shield]: https://img.shields.io/badge/license-MIT-green
[license-link]: LICENSE
[discord-shield]: https://img.shields.io/badge/Discord-Join-blue
[discord-link]: https://discord.com/invite/ycTQQCu6kn