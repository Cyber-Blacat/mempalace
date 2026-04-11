# Hybrid Room Routing Demo

This demo demonstrates the hybrid room routing concept for MemPalace.

## Overview

Hybrid room routing combines:
1. **Dense Retrieval** - Semantic similarity via embeddings (ChromaDB)
2. **Sparse Retrieval** - Keyword matching via BM25
3. **Score Fusion** - Weighted combination: α * dense + β * sparse
4. **Room Aggregation** - Aggregate document scores to room level
5. **Top-K Selection** - Select most relevant rooms

## Files

- `sparse_retriever.py` - BM25-based sparse retrieval implementation
- `hybrid_retriever.py` - Hybrid score fusion implementation
- `room_aggregator.py` - Room-level score aggregation
- `test_data.py` - Test dataset with realistic documents
- `main.py` - Main demo program
- `evaluate.py` - Evaluation script
- `verify_demo.py` - Quick verification script

## Quick Start

### 1. Install Dependencies

```bash
pip install rank-bm25
```

### 2. Run Verification

```bash
python demo_hybrid/verify_demo.py
```

This will run a quick test to verify all components work correctly.

### 3. Run Full Demo

```bash
python demo_hybrid/main.py
```

Options:
- **Option 1**: Run all test queries (automated)
- **Option 2**: Run single query demo
- **Option 3**: Compare aggregation methods
- **Option 4**: Interactive mode (enter your own queries)
- **Option 5**: Exit

### 4. Run Evaluation

```bash
python demo_hybrid/evaluate.py
```

This will:
- Compare dense-only, sparse-only, hybrid, and RRF search
- Tune α and β weights for optimal performance
- Compare aggregation methods (average, max, weighted)

## Example Output

```
======================================================================
  Query: database migration strategy
======================================================================

[Stage 1] Dense Retrieval (Embedding Similarity)
----------------------------------------------------------------------
  Top 10 documents (simulated ChromaDB results):
    [0] Score: 0.850 | Room: database
        Text: The team decided to migrate from MySQL to PostgreSQL...
    [1] Score: 0.810 | Room: database
        Text: We discussed using Alembic for database migrations...

[Stage 2] Sparse Retrieval (BM25 Keyword Match)
----------------------------------------------------------------------
  Top 10 documents (BM25 keyword match):
    [1] Score: 0.900 | Room: database
        Text: We discussed using Alembic for database migrations...
    [0] Score: 0.850 | Room: database
        Text: The team decided to migrate from MySQL to PostgreSQL...

[Stage 3] Score Fusion (α=0.70 * dense + β=0.30 * sparse)
----------------------------------------------------------------------
  Top 10 documents (fused scores):
    [0] Room: database
        Fused:   0.850
          Dense contribution:  0.595 (score: 0.850)
          Sparse contribution: 0.255 (score: 0.850)

[Stage 4] Room-Level Aggregation (method: average)
----------------------------------------------------------------------
  Top 3 rooms:
    [1] Room: database (Wing: project)
        Score: 0.820
        Documents in room: 3
```

## Test Data

The demo includes 13 realistic documents across 6 rooms:
- **database** (3 docs): Migration, backup, optimization
- **auth** (2 docs): JWT, OAuth, rate limiting
- **frontend** (2 docs): React, TypeScript, components
- **api** (2 docs): REST, GraphQL, versioning
- **deployment** (2 docs): CI/CD, Kubernetes
- **testing** (2 docs): Unit tests, performance

## Test Queries

8 test queries demonstrate different patterns:
1. **keyword_heavy** - Specific terms (e.g., "JWT tokens")
2. **semantic_heavy** - Broad concepts (e.g., "how do we handle authentication")
3. **mixed** - Combination of keywords and semantics

## Configuration

Default configuration:
```python
HYBRID_CONFIG = {
    'alpha': 0.7,           # Dense retrieval weight
    'beta': 0.3,            # Sparse retrieval weight
    'doc_top_k': 20,        # Number of documents to consider
    'room_top_k': 5,        # Number of rooms to return
    'aggregation_method': 'average'  # Room aggregation method
}
```

## Architecture

```
Query
 ↓
Dense Retrieval (ChromaDB embeddings)
   +
Sparse Retrieval (BM25 keywords)
 ↓
Score Fusion (α * dense + β * sparse)
 ↓
Document-level results (top-k)
 ↓
Room Aggregation (by room metadata)
 ↓
Room-level results (top-k rooms)
```

## Integration with MemPalace

To integrate with the main MemPalace system:

1. Import modules:
```python
from mempalace.sparse_retriever import BM25Retriever
from mempalace.hybrid_retriever import HybridRetriever
from mempalace.room_aggregator import RoomAggregator
```

2. Create retrievers from ChromaDB collection:
```python
sparse_retriever = create_bm25_retriever_from_collection(collection)
```

3. Run hybrid search:
```python
hybrid_retriever = HybridRetriever(docs, metas, alpha=0.7, beta=0.3)
fused_results = hybrid_retriever.fuse_results(dense_results, sparse_results)
```

4. Aggregate to room level:
```python
aggregator = RoomAggregator(method='average')
room_results = aggregator.aggregate(fused_results, docs, metas)
```

## Performance Notes

- BM25 indexing is fast (O(n) for n documents)
- Sparse search is efficient for keyword-heavy queries
- Dense search excels at semantic matching
- Hybrid combines strengths of both approaches
- Room aggregation reduces noise by grouping related documents

## Next Steps

After successful demo verification:
1. Integrate hybrid search into `searcher.py`
2. Add configuration support to `config.py`
3. Create MCP tool for hybrid search
4. Run benchmarks on real datasets
5. Tune parameters based on benchmark results

## References

- BM25: [Okapi BM25](https://en.wikipedia.org/wiki/Okapi_BM25)
- Hybrid Search: [Combining dense and sparse retrieval](https://www.pinecone.io/learn/hybrid-search/)
- Reciprocal Rank Fusion: [RRF paper](https://plg.uwaterloo.ca/~gvcormac/cormack-rrf.pdf)