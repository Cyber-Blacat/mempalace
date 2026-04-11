#!/usr/bin/env python3
"""
evaluate.py — Evaluation script for hybrid room routing.

Measures the effectiveness of hybrid search vs pure dense or pure sparse
search on the test dataset.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mempalace.sparse_retriever import BM25Retriever
from mempalace.hybrid_retriever import HybridRetriever, reciprocal_rank_fusion
from mempalace.room_aggregator import RoomAggregator
from demo_hybrid.test_data import TEST_DOCUMENTS, TEST_METADATAS, TEST_QUERIES


def simulate_dense_retrieval(query: str, k: int = 10):
    """Simulate dense retrieval."""
    query_lower = query.lower()
    query_words = set(query_lower.split())

    scores = []
    for i, doc in enumerate(TEST_DOCUMENTS):
        doc_lower = doc.lower()
        word_overlap = sum(1 for word in query_words if word in doc_lower)
        semantic_score = 0.3 + (0.1 * (i % 5))
        keyword_boost = word_overlap * 0.15
        score = min(1.0, semantic_score + keyword_boost)
        scores.append((i, score))

    scores.sort(key=lambda x: x[1], reverse=True)
    return scores[:k]


def evaluate_retrieval_accuracy():
    """Evaluate retrieval accuracy across all test queries.

    Returns:
        Dict with accuracy metrics for each search method.
    """
    print("\n" + "=" * 70)
    print("  Hybrid Room Routing Evaluation")
    print("=" * 70)

    # Initialize retrievers
    sparse_retriever = BM25Retriever(TEST_DOCUMENTS, TEST_METADATAS)
    hybrid_retriever = HybridRetriever(TEST_DOCUMENTS, TEST_METADATAS, alpha=0.7, beta=0.3)
    aggregator = RoomAggregator(aggregation_method="average")

    results = {
        "dense_only": [],
        "sparse_only": [],
        "hybrid": [],
        "rrf": [],
    }

    print("\n  Evaluating {} test queries...".format(len(TEST_QUERIES)))

    for query_data in TEST_QUERIES:
        query = query_data["query"]
        expected_rooms = query_data["expected_rooms"]

        # Dense-only search
        dense_results = simulate_dense_retrieval(query, k=20)
        dense_docs = [(idx, score) for idx, score in dense_results]
        dense_room_results = aggregator.aggregate(
            dense_docs, TEST_DOCUMENTS, TEST_METADATAS, top_k_rooms=5
        )
        dense_top_rooms = [r["room"] for r in dense_room_results]
        dense_matches = [r for r in expected_rooms if r in dense_top_rooms]
        dense_accuracy = len(dense_matches) / len(expected_rooms) if expected_rooms else 0
        results["dense_only"].append(dense_accuracy)

        # Sparse-only search (BM25)
        sparse_results = sparse_retriever.search(query, k=20)
        sparse_docs = [(idx, score) for idx, score in sparse_results]
        sparse_room_results = aggregator.aggregate(
            sparse_docs, TEST_DOCUMENTS, TEST_METADATAS, top_k_rooms=5
        )
        sparse_top_rooms = [r["room"] for r in sparse_room_results]
        sparse_matches = [r for r in expected_rooms if r in sparse_top_rooms]
        sparse_accuracy = len(sparse_matches) / len(expected_rooms) if expected_rooms else 0
        results["sparse_only"].append(sparse_accuracy)

        # Hybrid search (weighted fusion)
        fused_results = hybrid_retriever.fuse_results(dense_results, sparse_results, k=20)

        # For aggregation, we need (index, score) tuples
        fused_simple = [(idx, fused) for idx, fused, _, _ in fused_results]
        hybrid_room_results = aggregator.aggregate(
            fused_simple, TEST_DOCUMENTS, TEST_METADATAS, top_k_rooms=5
        )
        hybrid_top_rooms = [r["room"] for r in hybrid_room_results]
        hybrid_matches = [r for r in expected_rooms if r in hybrid_top_rooms]
        hybrid_accuracy = len(hybrid_matches) / len(expected_rooms) if expected_rooms else 0
        results["hybrid"].append(hybrid_accuracy)

        # RRF fusion
        rrf_results = reciprocal_rank_fusion(dense_results, sparse_results, k=60, final_k=20)
        rrf_room_results = aggregator.aggregate(
            rrf_results, TEST_DOCUMENTS, TEST_METADATAS, top_k_rooms=5
        )
        rrf_top_rooms = [r["room"] for r in rrf_room_results]
        rrf_matches = [r for r in expected_rooms if r in rrf_top_rooms]
        rrf_accuracy = len(rrf_matches) / len(expected_rooms) if expected_rooms else 0
        results["rrf"].append(rrf_accuracy)

        # Print individual query results
        print(f"\n  Query: {query}")
        print(f"    Expected:     {expected_rooms}")
        print(f"    Dense-only:   {dense_top_rooms[:3]} (accuracy: {dense_accuracy:.1%})")
        print(f"    Sparse-only:  {sparse_top_rooms[:3]} (accuracy: {sparse_accuracy:.1%})")
        print(f"    Hybrid:       {hybrid_top_rooms[:3]} (accuracy: {hybrid_accuracy:.1%})")
        print(f"    RRF:          {rrf_top_rooms[:3]} (accuracy: {rrf_accuracy:.1%})")

    # Compute average accuracies
    print("\n" + "=" * 70)
    print("  Summary Results")
    print("=" * 70)

    for method, accuracies in results.items():
        avg_accuracy = sum(accuracies) / len(accuracies)
        print(f"\n  {method:15s}: Average accuracy = {avg_accuracy:.1%}")

    # Return results
    return results


def compare_alpha_beta_weights():
    """Compare different α and β weight combinations.

    Returns:
        Dict with results for each weight combination.
    """
    print("\n" + "=" * 70)
    print("  Weight Tuning: α vs β")
    print("=" * 70)

    weight_combinations = [
        (0.5, 0.5),
        (0.6, 0.4),
        (0.7, 0.3),
        (0.8, 0.2),
        (0.9, 0.1),
    ]

    sparse_retriever = BM25Retriever(TEST_DOCUMENTS, TEST_METADATAS)
    aggregator = RoomAggregator(aggregation_method="average")

    results = {}

    for alpha, beta in weight_combinations:
        print(f"\n  Testing α={alpha:.1f}, β={beta:.1f}")

        accuracies = []
        hybrid_retriever = HybridRetriever(TEST_DOCUMENTS, TEST_METADATAS, alpha=alpha, beta=beta)

        for query_data in TEST_QUERIES:
            query = query_data["query"]
            expected_rooms = query_data["expected_rooms"]

            dense_results = simulate_dense_retrieval(query, k=20)
            sparse_results = sparse_retriever.search(query, k=20)

            fused_results = hybrid_retriever.fuse_results(dense_results, sparse_results, k=20)
            fused_simple = [(idx, fused) for idx, fused, _, _ in fused_results]

            room_results = aggregator.aggregate(
                fused_simple, TEST_DOCUMENTS, TEST_METADATAS, top_k_rooms=5
            )
            top_rooms = [r["room"] for r in room_results]

            matches = [r for r in expected_rooms if r in top_rooms]
            accuracy = len(matches) / len(expected_rooms) if expected_rooms else 0
            accuracies.append(accuracy)

        avg_accuracy = sum(accuracies) / len(accuracies)
        results[(alpha, beta)] = avg_accuracy

        print(f"    Average accuracy: {avg_accuracy:.1%}")

    # Find best combination
    best_combo = max(results.items(), key=lambda x: x[1])

    print("\n" + "-" * 70)
    print(f"\n  Best combination: α={best_combo[0][0]:.1f}, β={best_combo[0][1]:.1f}")
    print(f"  Accuracy: {best_combo[1]:.1%}")

    return results


def compare_aggregation_methods():
    """Compare different room aggregation methods.

    Returns:
        Dict with results for each aggregation method.
    """
    print("\n" + "=" * 70)
    print("  Aggregation Method Comparison")
    print("=" * 70)

    methods = ["average", "max", "weighted"]

    sparse_retriever = BM25Retriever(TEST_DOCUMENTS, TEST_METADATAS)
    hybrid_retriever = HybridRetriever(TEST_DOCUMENTS, TEST_METADATAS, alpha=0.7, beta=0.3)

    results = {}

    for method in methods:
        print(f"\n  Testing {method} aggregation")

        aggregator = RoomAggregator(aggregation_method=method)
        accuracies = []

        for query_data in TEST_QUERIES:
            query = query_data["query"]
            expected_rooms = query_data["expected_rooms"]

            dense_results = simulate_dense_retrieval(query, k=20)
            sparse_results = sparse_retriever.search(query, k=20)
            fused_results = hybrid_retriever.fuse_results(dense_results, sparse_results, k=20)

            fused_simple = [(idx, fused) for idx, fused, _, _ in fused_results]
            room_results = aggregator.aggregate(
                fused_simple, TEST_DOCUMENTS, TEST_METADATAS, top_k_rooms=5
            )

            top_rooms = [r["room"] for r in room_results]
            matches = [r for r in expected_rooms if r in top_rooms]
            accuracy = len(matches) / len(expected_rooms) if expected_rooms else 0
            accuracies.append(accuracy)

        avg_accuracy = sum(accuracies) / len(accuracies)
        results[method] = avg_accuracy

        print(f"    Average accuracy: {avg_accuracy:.1%}")

    # Find best method
    best_method = max(results.items(), key=lambda x: x[1])

    print("\n" + "-" * 70)
    print(f"\n  Best method: {best_method[0]}")
    print(f"  Accuracy: {best_method[1]:.1%}")

    return results


def main():
    """Run all evaluations."""
    print("\n" + "=" * 70)
    print("  Hybrid Room Routing Evaluation Suite")
    print("=" * 70)

    print("\n  This evaluation measures:")
    print("    1. Retrieval accuracy for different search methods")
    print("    2. Optimal α and β weight combinations")
    print("    3. Best room aggregation method")

    # Run evaluations
    print("\n\n" + "=" * 70)
    print("  [1] Retrieval Accuracy Comparison")
    print("=" * 70)

    accuracy_results = evaluate_retrieval_accuracy()

    print("\n\n" + "=" * 70)
    print("  [2] Weight Tuning (α vs β)")
    print("=" * 70)

    weight_results = compare_alpha_beta_weights()

    print("\n\n" + "=" * 70)
    print("  [3] Aggregation Method Comparison")
    print("=" * 70)

    method_results = compare_aggregation_methods()

    # Final summary
    print("\n\n" + "=" * 70)
    print("  Final Summary")
    print("=" * 70)

    print("\n  Recommendations:")

    # Best search method
    best_search = max(accuracy_results.items(), key=lambda x: sum(x[1]) / len(x[1]))
    print(f"    • Best search method: {best_search[0]}")

    # Best weights
    best_weights = max(weight_results.items(), key=lambda x: x[1])
    print(f"    • Recommended weights: α={best_weights[0][0]:.1f}, β={best_weights[0][1]:.1f}")

    # Best aggregation
    best_agg = max(method_results.items(), key=lambda x: x[1])
    print(f"    • Recommended aggregation: {best_agg[0]}")

    print("\n  Configuration for production use:")
    print("    HYBRID_CONFIG = {")
    print(f"        'alpha': {best_weights[0][0]},")
    print(f"        'beta': {best_weights[0][1]},")
    print(f"        'aggregation_method': '{best_agg[0]}',")
    print("        'room_top_k': 5,")
    print("        'doc_top_k': 20")
    print("    }")


if __name__ == "__main__":
    main()
