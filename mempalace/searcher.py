#!/usr/bin/env python3
"""
searcher.py — Find anything. Exact words.

Semantic search against the palace.
Returns verbatim text — the actual words, never summaries.

Supports both:
- Dense search (embedding similarity via ChromaDB)
- Hybrid search (dense + sparse BM25 + room aggregation)
"""

import logging
from pathlib import Path
from typing import Optional

import chromadb

from .config import MempalaceConfig
from .embedding_function import get_embedding_function
from .sparse_retriever import BM25Retriever
from .hybrid_retriever import HybridRetriever
from .room_aggregator import RoomAggregator


def _get_collection_with_embeddings(client, collection_name: str):
    """Get ChromaDB collection with local embedding function.

    This ensures models are loaded from local assets/ directory
    instead of system cache (~/.cache/huggingface/).
    """
    embedding_fn = get_embedding_function()
    return client.get_or_create_collection(
        name=collection_name,
        embedding_function=embedding_fn,
    )


logger = logging.getLogger("mempalace_mcp")


class SearchError(Exception):
    """Raised when search cannot proceed (e.g. no palace found)."""


def search(
    query: str,
    palace_path: str,
    wing: Optional[str] = None,
    room: Optional[str] = None,
    n_results: int = 5,
):
    """
    Search the palace. Returns verbatim drawer content.
    Optionally filter by wing (project) or room (aspect).
    """
    try:
        client = chromadb.PersistentClient(path=palace_path)
        col = _get_collection_with_embeddings(client, "mempalace_drawers")
    except Exception:
        print(f"\n  No palace found at {palace_path}")
        print("  Run: mempalace init <dir> then mempalace mine <dir>")
        raise SearchError(f"No palace found at {palace_path}")

    # Build where filter
    where = {}
    if wing and room:
        where = {"$and": [{"wing": wing}, {"room": room}]}
    elif wing:
        where = {"wing": wing}
    elif room:
        where = {"room": room}

    try:
        kwargs = {
            "query_texts": [query],
            "n_results": n_results,
            "include": ["documents", "metadatas", "distances"],
        }
        if where:
            kwargs["where"] = where

        results = col.query(**kwargs)

    except Exception as e:
        print(f"\n  Search error: {e}")
        raise SearchError(f"Search error: {e}") from e

    docs = results["documents"][0]
    metas = results["metadatas"][0]
    dists = results["distances"][0]

    if not docs:
        print(f'\n  No results found for: "{query}"')
        return

    print(f"\n{'=' * 60}")
    print(f'  Results for: "{query}"')
    if wing:
        print(f"  Wing: {wing}")
    if room:
        print(f"  Room: {room}")
    print(f"{'=' * 60}\n")

    for i, (doc, meta, dist) in enumerate(zip(docs, metas, dists), 1):
        similarity = round(1 - dist, 3)
        source = Path(meta.get("source_file", "?")).name
        wing_name = meta.get("wing", "?")
        room_name = meta.get("room", "?")

        print(f"  [{i}] {wing_name} / {room_name}")
        print(f"      Source: {source}")
        print(f"      Match:  {similarity}")
        print()
        # Print the verbatim text, indented
        for line in doc.strip().split("\n"):
            print(f"      {line}")
        print()
        print(f"  {'─' * 56}")

    print()


def search_memories(
    query: str,
    palace_path: str,
    wing: Optional[str] = None,
    room: Optional[str] = None,
    n_results: int = 5,
) -> dict:
    """
    Programmatic search — returns a dict instead of printing.
    Used by the MCP server and other callers that need data.
    """
    try:
        client = chromadb.PersistentClient(path=palace_path)
        col = _get_collection_with_embeddings(client, "mempalace_drawers")
    except Exception as e:
        logger.error("No palace found at %s: %s", palace_path, e)
        return {
            "error": "No palace found",
            "hint": "Run: mempalace init <dir> && mempalace mine <dir>",
        }

    # Build where filter
    where = {}
    if wing and room:
        where = {"$and": [{"wing": wing}, {"room": room}]}
    elif wing:
        where = {"wing": wing}
    elif room:
        where = {"room": room}

    try:
        kwargs = {
            "query_texts": [query],
            "n_results": n_results,
            "include": ["documents", "metadatas", "distances"],
        }
        if where:
            kwargs["where"] = where

        results = col.query(**kwargs)
    except Exception as e:
        return {"error": f"Search error: {e}"}

    docs = results["documents"][0]
    metas = results["metadatas"][0]
    dists = results["distances"][0]

    hits = []
    for doc, meta, dist in zip(docs, metas, dists):
        hits.append(
            {
                "text": doc,
                "wing": meta.get("wing", "unknown"),
                "room": meta.get("room", "unknown"),
                "source_file": Path(meta.get("source_file", "?")).name,
                "similarity": round(1 - dist, 3),
            }
        )

    return {
        "query": query,
        "filters": {"wing": wing, "room": room},
        "results": hits,
    }


def hybrid_search_memories(
    query: str,
    palace_path: str,
    wing: str = None,
    room: str = None,
    n_results: int = 5,
    alpha: float = 0.7,
    beta: float = 0.3,
    doc_top_k: int = 20,
    room_top_k: int = 5,
    aggregation_method: str = "average",
) -> dict:
    """Hybrid search combining dense and sparse retrieval with room aggregation.

    This implements the hybrid room routing concept:
        Query
         ↓
        Dense Retrieval (embedding similarity via ChromaDB)
         +
        Sparse Retrieval (BM25 keyword matching)
         ↓
        Score Fusion (α * dense + β * sparse)
         ↓
        Aggregate scores → Room level
         ↓
        Select Top-K Rooms

    Args:
        query: Search query string.
        palace_path: Path to the ChromaDB palace directory.
        wing: Optional wing filter (limits search to specific wing).
        room: Optional room filter (limits search to specific room).
        n_results: Number of document results to return (for backward compatibility).
        alpha: Weight for dense retrieval scores (default: 0.7).
        beta: Weight for sparse retrieval scores (default: 0.3).
        doc_top_k: Number of document candidates to consider (default: 20).
        room_top_k: Number of rooms to return (default: 5).
        aggregation_method: Method for room aggregation: 'average', 'max', or 'weighted'.

    Returns:
        Dict with:
        - "query": Original query
        - "mode": "hybrid"
        - "config": Search configuration (alpha, beta, etc.)
        - "room_results": List of room-level results with scores
        - "document_results": List of document-level results (top n_results)
        - "error": Error message if something went wrong (optional)

    Example:
        >>> results = hybrid_search_memories(
        ...     "database migration strategy",
        ...     palace_path="~/.mempalace/palace",
        ...     alpha=0.7,
        ...     beta=0.3
        ... )
        >>> for room in results["room_results"]:
        ...     print(f"{room['room']}: {room['score']:.3f}")
    """
    try:
        client = chromadb.PersistentClient(path=palace_path)
        col = _get_collection_with_embeddings(client, "mempalace_drawers")
    except Exception as e:
        logger.error("No palace found at %s: %s", palace_path, e)
        return {
            "error": "No palace found",
            "hint": "Run: mempalace init <dir> && mempalace mine <dir>",
        }

    # Build where filter
    where = {}
    if wing and room:
        where = {"$and": [{"wing": wing}, {"room": room}]}
    elif wing:
        where = {"wing": wing}
    elif room:
        where = {"room": room}

    try:
        # Stage 1: Dense Retrieval (ChromaDB)
        logger.info(f"Stage 1: Dense retrieval for query '{query}'")
        kwargs = {
            "query_texts": [query],
            "n_results": doc_top_k,
            "include": ["documents", "metadatas", "distances"],
        }
        if where:
            kwargs["where"] = where

        dense_results = col.query(**kwargs)

        docs = dense_results["documents"][0]
        metas = dense_results["metadatas"][0]
        dists = dense_results["distances"][0]

        if not docs:
            logger.warning(f"No documents found for query: {query}")
            return {
                "query": query,
                "mode": "hybrid",
                "config": {
                    "alpha": alpha,
                    "beta": beta,
                    "doc_top_k": doc_top_k,
                    "room_top_k": room_top_k,
                    "aggregation_method": aggregation_method,
                },
                "room_results": [],
                "document_results": [],
            }

        # Convert to (index, score) format
        # ChromaDB returns distances, convert to similarity: similarity = max(0, 1 - distance)
        # Use max(0, ...) to ensure non-negative scores
        dense_scores = [(i, max(0.0, 1 - dist)) for i, dist in enumerate(dists)]

        # Stage 2: Sparse Retrieval (BM25)
        logger.info("Stage 2: Sparse retrieval (BM25)")
        sparse_retriever = BM25Retriever(docs, metas)
        sparse_results = sparse_retriever.search(query, k=doc_top_k, normalize_scores=True)

        # Stage 3: Score Fusion
        logger.info(f"Stage 3: Score fusion (alpha={alpha}, beta={beta})")
        hybrid_retriever = HybridRetriever(docs, metas, alpha=alpha, beta=beta)
        fused_results = hybrid_retriever.fuse_results(dense_scores, sparse_results, k=doc_top_k)

        # Stage 4: Room Aggregation
        logger.info(f"Stage 4: Room aggregation (method={aggregation_method})")
        aggregator = RoomAggregator(aggregation_method=aggregation_method)

        # Convert fused results to simple (index, score) for aggregation
        fused_simple = [(idx, score) for idx, score, _, _ in fused_results]
        room_results = aggregator.aggregate(fused_simple, docs, metas, top_k_rooms=room_top_k)

        # Prepare document-level results (top n_results)
        document_results = []
        for idx, fused_score, dense_score, sparse_score in fused_results[:n_results]:
            document_results.append(
                {
                    "text": docs[idx],
                    "wing": metas[idx].get("wing", "unknown"),
                    "room": metas[idx].get("room", "unknown"),
                    "source_file": Path(metas[idx].get("source_file", "?")).name,
                    "fused_score": round(fused_score, 4),
                    "dense_score": round(dense_score, 4),
                    "sparse_score": round(sparse_score, 4),
                }
            )

        # Prepare room-level results
        formatted_room_results = []
        for room_data in room_results:
            formatted_room_results.append(
                {
                    "room": room_data["room"],
                    "wing": room_data["wing"],
                    "score": room_data["score"],
                    "doc_count": room_data["doc_count"],
                    "documents": room_data["documents"],
                }
            )

        logger.info(
            f"Hybrid search complete: {len(room_results)} rooms, {len(document_results)} documents"
        )

        return {
            "query": query,
            "mode": "hybrid",
            "config": {
                "alpha": alpha,
                "beta": beta,
                "doc_top_k": doc_top_k,
                "room_top_k": room_top_k,
                "aggregation_method": aggregation_method,
            },
            "room_results": formatted_room_results,
            "document_results": document_results,
        }

    except Exception as e:
        logger.error(f"Hybrid search error: {e}")
        return {"error": f"Hybrid search error: {e}"}
