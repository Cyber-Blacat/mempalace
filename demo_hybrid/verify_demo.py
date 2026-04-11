#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_demo.py - Quick verification script for hybrid room routing.

Runs a simple test to verify all components work correctly.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mempalace.sparse_retriever import BM25Retriever
from mempalace.hybrid_retriever import HybridRetriever
from mempalace.room_aggregator import RoomAggregator
from demo_hybrid.test_data import TEST_DOCUMENTS, TEST_METADATAS


def verify_sparse_retriever():
    """Verify BM25 retriever works."""
    print("\n[1] Testing BM25Retriever...")
    print("-" * 60)

    try:
        retriever = BM25Retriever(TEST_DOCUMENTS, TEST_METADATAS)
        results = retriever.search("database migration", k=5)

        print("  [OK] BM25 index created successfully")
        print("  [OK] Search returned {} results".format(len(results)))

        # Check first result
        idx, score = results[0]
        doc, meta = retriever.get_document(idx)

        print("  [OK] Top result: Room '{}', Score {:.3f}".format(meta["room"], score))
        print("    Document: {}...".format(doc[:60]))

        return True
    except Exception as e:
        print("  [FAIL] Error: {}".format(e))
        return False


def verify_hybrid_retriever():
    """Verify hybrid retriever works."""
    print("\n[2] Testing HybridRetriever...")
    print("-" * 60)

    try:
        # Create sparse retriever
        sparse_retriever = BM25Retriever(TEST_DOCUMENTS, TEST_METADATAS)
        sparse_results = sparse_retriever.search("database", k=10)

        # Simulate dense results
        dense_results = [(i, 0.3 + i * 0.05) for i in range(10)]

        # Create hybrid retriever
        hybrid_retriever = HybridRetriever(TEST_DOCUMENTS, TEST_METADATAS, alpha=0.7, beta=0.3)
        fused_results = hybrid_retriever.fuse_results(dense_results, sparse_results, k=10)

        print("  [OK] Hybrid retriever created")
        print("  [OK] Fusion returned {} results".format(len(fused_results)))

        # Check first result
        idx, fused, dense, sparse = fused_results[0]

        print(
            "  [OK] Top result: Fused={:.3f}, Dense={:.3f}, Sparse={:.3f}".format(
                fused, dense, sparse
            )
        )

        return True
    except Exception as e:
        print("  [FAIL] Error: {}".format(e))
        return False


def verify_room_aggregator():
    """Verify room aggregator works."""
    print("\n[3] Testing RoomAggregator...")
    print("-" * 60)

    try:
        # Create sample results
        doc_results = [(0, 0.85), (1, 0.80), (4, 0.70)]

        # Create aggregator
        aggregator = RoomAggregator(aggregation_method="average")
        room_results = aggregator.aggregate(
            doc_results, TEST_DOCUMENTS, TEST_METADATAS, top_k_rooms=3
        )

        print("  [OK] Aggregator created with method='average'")
        print("  [OK] Aggregation returned {} rooms".format(len(room_results)))

        # Check first room
        room = room_results[0]

        print(
            "  [OK] Top room: '{}', Score={:.3f}, Docs={}".format(
                room["room"], room["score"], room["doc_count"]
            )
        )

        return True
    except Exception as e:
        print("  [FAIL] Error: {}".format(e))
        return False


def verify_complete_pipeline():
    """Verify complete hybrid room routing pipeline."""
    print("\n[4] Testing Complete Pipeline...")
    print("-" * 60)

    try:
        query = "database migration strategy"

        print("  Query: {}".format(query))

        # Stage 1: Sparse retrieval
        sparse_retriever = BM25Retriever(TEST_DOCUMENTS, TEST_METADATAS)
        sparse_results = sparse_retriever.search(query, k=20)

        print("  [OK] Stage 1 (Sparse): {} documents".format(len(sparse_results)))

        # Stage 2: Simulated dense retrieval
        dense_results = [(i, 0.3 + (i % 5) * 0.1) for i in range(20)]

        print("  [OK] Stage 2 (Dense): {} documents (simulated)".format(len(dense_results)))

        # Stage 3: Fusion
        hybrid_retriever = HybridRetriever(TEST_DOCUMENTS, TEST_METADATAS, alpha=0.7, beta=0.3)
        fused_results = hybrid_retriever.fuse_results(dense_results, sparse_results, k=20)
        fused_simple = [(idx, fused) for idx, fused, _, _ in fused_results]

        print("  [OK] Stage 3 (Fusion): {} documents".format(len(fused_results)))

        # Stage 4: Room aggregation
        aggregator = RoomAggregator(aggregation_method="average")
        room_results = aggregator.aggregate(
            fused_simple, TEST_DOCUMENTS, TEST_METADATAS, top_k_rooms=3
        )

        print("  [OK] Stage 4 (Aggregation): {} rooms".format(len(room_results)))

        # Show top rooms
        print("\n  Top 3 Rooms:")
        for i, room in enumerate(room_results, 1):
            print(
                "    [{}] {}: Score={:.3f}, Docs={}".format(
                    i, room["room"], room["score"], room["doc_count"]
                )
            )

        # Check if expected room is in results
        expected_room = "database"
        top_rooms = [r["room"] for r in room_results]

        if expected_room in top_rooms:
            print("  [OK] Expected room '{}' found in top results".format(expected_room))
            return True
        else:
            print("  [FAIL] Expected room '{}' not in top results".format(expected_room))
            print("    Top rooms: {}".format(top_rooms))
            return False

    except Exception as e:
        print("  [FAIL] Error: {}".format(e))
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all verification tests."""
    print("\n" + "=" * 60)
    print("  Hybrid Room Routing Verification")
    print("=" * 60)

    print("\n  Verifying all components...")

    results = []

    # Test each component
    results.append(("BM25Retriever", verify_sparse_retriever()))
    results.append(("HybridRetriever", verify_hybrid_retriever()))
    results.append(("RoomAggregator", verify_room_aggregator()))
    results.append(("Complete Pipeline", verify_complete_pipeline()))

    # Summary
    print("\n" + "=" * 60)
    print("  Verification Summary")
    print("=" * 60)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for component, success in results:
        status = "[OK] PASS" if success else "[FAIL] FAIL"
        print("  {:20s}: {}".format(component, status))

    print("\n" + "-" * 60)
    print("  Total: {}/{} tests passed".format(passed, total))

    if passed == total:
        print("\n  [OK] All components verified successfully!")
        print("  Demo is ready to use.")
        print("\n  Run: python demo_hybrid/main.py")
        return 0
    else:
        print("\n  [FAIL] Some tests failed. Check errors above.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
