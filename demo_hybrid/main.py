#!/usr/bin/env python3
"""
main.py — Main demo program for hybrid room routing.

Demonstrates the complete hybrid room routing pipeline:
    Query
     ↓
    Dense Retrieval (embedding similarity)
     +
    Sparse Retrieval (BM25 keyword match)
     ↓
    Score Fusion (α * dense + β * sparse)
     ↓
    Aggregate scores → Room level
     ↓
    Select Top-K Rooms

Run: python demo_hybrid/main.py
"""

import sys
import os
import logging

# Add parent directory to path to import mempalace modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mempalace.sparse_retriever import BM25Retriever
from mempalace.hybrid_retriever import HybridRetriever
from mempalace.room_aggregator import RoomAggregator
from demo_hybrid.test_data import TEST_DOCUMENTS, TEST_METADATAS, TEST_QUERIES

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("demo_hybrid")


def simulate_dense_retrieval(query: str, k: int = 10):
    """Simulate dense retrieval results.

    In a real implementation, this would query ChromaDB for semantic similarity.
    For this demo, we simulate results based on keyword overlap and semantic hints.

    Args:
        query: Query string.
        k: Number of results.

    Returns:
        List of (doc_index, similarity_score) tuples.
    """
    # Simple simulation: documents containing query keywords get higher scores
    query_lower = query.lower()
    query_words = set(query_lower.split())

    scores = []
    for i, doc in enumerate(TEST_DOCUMENTS):
        doc_lower = doc.lower()

        # Compute a simulated similarity score
        word_overlap = sum(1 for word in query_words if word in doc_lower)

        # Base semantic similarity (random-ish for demo)
        semantic_score = 0.3 + (0.1 * (i % 5))  # Some variation

        # Boost if keywords match
        keyword_boost = word_overlap * 0.15

        score = min(1.0, semantic_score + keyword_boost)
        scores.append((i, score))

    # Sort by score and return top k
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores[:k]


def run_hybrid_search_demo(
    query: str,
    documents: list,
    metadatas: list,
    alpha: float = 0.7,
    beta: float = 0.3,
    doc_top_k: int = 10,
    room_top_k: int = 3,
    aggregation_method: str = "average",
):
    """Run complete hybrid room routing pipeline.

    Args:
        query: Query string.
        documents: List of documents.
        metadatas: List of metadata dicts.
        alpha: Dense retrieval weight.
        beta: Sparse retrieval weight.
        doc_top_k: Number of document results to consider.
        room_top_k: Number of room results to return.
        aggregation_method: Room aggregation method.

    Returns:
        Dict with complete results at each stage.
    """
    print(f"\n{'=' * 70}")
    print(f"  Query: {query}")
    print(f"{'=' * 70}")

    # Stage 1: Dense Retrieval (simulated)
    print("\n[Stage 1] Dense Retrieval (Embedding Similarity)")
    print("-" * 70)

    dense_results = simulate_dense_retrieval(query, k=doc_top_k)

    print(f"  Top {len(dense_results)} documents (simulated ChromaDB results):")
    for idx, score in dense_results[:5]:
        doc = documents[idx]
        room = metadatas[idx]["room"]
        print(f"    [{idx}] Score: {score:.3f} | Room: {room}")
        print(f"        Text: {doc[:60]}...")

    # Stage 2: Sparse Retrieval (BM25)
    print("\n[Stage 2] Sparse Retrieval (BM25 Keyword Match)")
    print("-" * 70)

    sparse_retriever = BM25Retriever(documents, metadatas)
    sparse_results = sparse_retriever.search(query, k=doc_top_k, normalize_scores=True)

    print(f"  Top {len(sparse_results)} documents (BM25 keyword match):")
    for idx, score in sparse_results[:5]:
        doc, meta = sparse_retriever.get_document(idx)
        room = meta["room"]
        print(f"    [{idx}] Score: {score:.3f} | Room: {room}")
        print(f"        Text: {doc[:60]}...")

    # Stage 3: Score Fusion
    print(f"\n[Stage 3] Score Fusion (α={alpha:.2f} * dense + β={beta:.2f} * sparse)")
    print("-" * 70)

    hybrid_retriever = HybridRetriever(documents, metadatas, alpha=alpha, beta=beta)
    fused_results = hybrid_retriever.fuse_results(dense_results, sparse_results, k=doc_top_k)

    print(f"  Top {len(fused_results)} documents (fused scores):")
    for idx, fused_score, dense_score, sparse_score in fused_results[:5]:
        doc = documents[idx]
        room = metadatas[idx]["room"]

        print(f"    [{idx}] Room: {room}")
        print(f"        Fused:   {fused_score:.3f}")
        print(
            f"          Dense contribution:  {alpha * dense_score:.3f} (score: {dense_score:.3f})"
        )
        print(
            f"          Sparse contribution: {beta * sparse_score:.3f} (score: {sparse_score:.3f})"
        )
        print(f"        Text: {doc[:50]}...")

    # Stage 4: Room Aggregation
    print(f"\n[Stage 4] Room-Level Aggregation (method: {aggregation_method})")
    print("-" * 70)

    aggregator = RoomAggregator(aggregation_method=aggregation_method)
    room_results = aggregator.aggregate(fused_results, documents, metadatas, top_k_rooms=room_top_k)

    print(f"  Top {len(room_results)} rooms:")
    for i, room in enumerate(room_results, 1):
        print(f"\n    [{i}] Room: {room['room']} (Wing: {room['wing']})")
        print(f"        Score: {room['score']:.3f}")
        print(f"        Documents in room: {room['doc_count']}")

        for doc in room["documents"][:2]:  # Show top 2 docs per room
            print(f"          - Doc {doc['index']}: {doc['score']:.3f} | {doc['text'][:40]}...")

    # Return complete results
    return {
        "query": query,
        "dense_results": dense_results,
        "sparse_results": sparse_results,
        "fused_results": fused_results,
        "room_results": room_results,
        "config": {
            "alpha": alpha,
            "beta": beta,
            "doc_top_k": doc_top_k,
            "room_top_k": room_top_k,
            "aggregation_method": aggregation_method,
        },
    }


def compare_methods(query: str, documents: list, metadatas: list):
    """Compare different aggregation methods for a query.

    Args:
        query: Query string.
        documents: List of documents.
        metadatas: List of metadatas.

    Returns:
        Comparison results.
    """
    print(f"\n{'=' * 70}")
    print(f"  Comparing Aggregation Methods for: {query}")
    print(f"{'=' * 70}")

    # Get base results
    dense_results = simulate_dense_retrieval(query, k=10)
    sparse_retriever = BM25Retriever(documents, metadatas)
    sparse_results = sparse_retriever.search(query, k=10)

    hybrid_retriever = HybridRetriever(documents, metadatas)
    fused_results = hybrid_retriever.fuse_results(dense_results, sparse_results, k=10)

    # Test each aggregation method
    methods = ["average", "max", "weighted"]

    for method in methods:
        print(f"\n  {method.upper()} aggregation:")

        aggregator = RoomAggregator(aggregation_method=method)
        room_results = aggregator.aggregate(fused_results, documents, metadatas, top_k_rooms=3)

        rooms_list = [r["room"] for r in room_results]
        scores_list = [f"{r['score']:.3f}" for r in room_results]

        print(f"    Top rooms: {', '.join(rooms_list)}")
        print(f"    Scores:    {', '.join(scores_list)}")


def run_all_queries():
    """Run demo on all test queries."""
    print("\n" + "=" * 70)
    print("  Hybrid Room Routing Demo - All Test Queries")
    print("=" * 70)

    for query_data in TEST_QUERIES:
        query = query_data["query"]
        expected_rooms = query_data["expected_rooms"]
        query_type = query_data["type"]

        print(f"\n\n{'=' * 70}")
        print(f"  Query Type: {query_type}")
        print(f"  Expected Rooms: {', '.join(expected_rooms)}")
        print(f"{'=' * 70}")

        results = run_hybrid_search_demo(
            query,
            TEST_DOCUMENTS,
            TEST_METADATAS,
            alpha=0.7,
            beta=0.3,
            doc_top_k=10,
            room_top_k=3,
            aggregation_method="average",
        )

        # Check if expected rooms are in top results
        top_rooms = [r["room"] for r in results["room_results"]]

        print("\n  Expected vs Actual:")
        print(f"    Expected: {expected_rooms}")
        print(f"    Actual:   {top_rooms}")

        # Compute match
        matches = [room for room in expected_rooms if room in top_rooms]
        match_ratio = len(matches) / len(expected_rooms) if expected_rooms else 0

        print(f"    Match: {len(matches)}/{len(expected_rooms)} ({match_ratio:.1%})")


def interactive_demo():
    """Run interactive demo where user can input queries."""
    print("\n" + "=" * 70)
    print("  Interactive Hybrid Room Routing Demo")
    print("=" * 70)
    print("\n  Enter queries to test the hybrid search system.")
    print("  Type 'quit' to exit.")
    print("\n  Example queries:")
    print("    - database migration strategy")
    print("    - authentication system")
    print("    - frontend components")
    print("    - deployment process")

    # Initialize retrievers once
    sparse_retriever = BM25Retriever(TEST_DOCUMENTS, TEST_METADATAS)
    hybrid_retriever = HybridRetriever(TEST_DOCUMENTS, TEST_METADATAS, alpha=0.7, beta=0.3)
    aggregator = RoomAggregator(aggregation_method="average")

    while True:
        print("\n" + "-" * 70)
        query = input("\n  Enter query: ").strip()

        if query.lower() in ["quit", "exit", "q"]:
            print("\n  Goodbye!")
            break

        if not query:
            print("  Please enter a query.")
            continue

        # Run search
        dense_results = simulate_dense_retrieval(query, k=10)
        sparse_results = sparse_retriever.search(query, k=10)
        fused_results = hybrid_retriever.fuse_results(dense_results, sparse_results, k=10)
        room_results = aggregator.aggregate(
            fused_results, TEST_DOCUMENTS, TEST_METADATAS, top_k_rooms=3
        )

        # Display results
        print(f"\n  Results for: '{query}'")
        print("-" * 70)

        print("\n  Top 3 Rooms:")
        for i, room in enumerate(room_results, 1):
            print(f"\n    [{i}] {room['room']} - Score: {room['score']:.3f}")
            print(f"        Documents: {room['doc_count']}")

            for doc in room["documents"][:2]:
                print(f"          • {doc['text'][:60]}...")


def main():
    """Main entry point for demo."""
    print("\n" + "=" * 70)
    print("  MemPalace Hybrid Room Routing Demo")
    print("=" * 70)
    print("\n  This demo demonstrates the hybrid room routing concept:")
    print("    1. Dense Retrieval (semantic embeddings)")
    print("    2. Sparse Retrieval (BM25 keyword matching)")
    print("    3. Score Fusion (α * dense + β * sparse)")
    print("    4. Room-Level Aggregation")
    print("    5. Top-K Room Selection")

    print("\n  Options:")
    print("    1. Run all test queries")
    print("    2. Run single query demo")
    print("    3. Compare aggregation methods")
    print("    4. Interactive mode")
    print("    5. Exit")

    choice = input("\n  Select option (1-5): ").strip()

    if choice == "1":
        run_all_queries()
    elif choice == "2":
        # Single query demo
        query = "database migration strategy"
        run_hybrid_search_demo(query, TEST_DOCUMENTS, TEST_METADATAS)
    elif choice == "3":
        # Compare methods
        query = "authentication and JWT tokens"
        compare_methods(query, TEST_DOCUMENTS, TEST_METADATAS)
    elif choice == "4":
        interactive_demo()
    elif choice == "5":
        print("\n  Goodbye!")
    else:
        # Default: run all queries
        print("\n  Running all test queries...")
        run_all_queries()


if __name__ == "__main__":
    main()
