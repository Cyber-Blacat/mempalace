#!/usr/bin/env python3
"""
room_aggregator.py — Aggregate document-level scores to room-level scores.

This module implements the final step of hybrid room routing: aggregating
document-level hybrid scores to room-level scores to select the most relevant
rooms for a query.

The aggregation can use different strategies:
- Average: Room score = average of all document scores in that room
- Max: Room score = highest document score in that room
- Weighted: Room score weighted by document position/rank
"""

import logging
from typing import List, Dict, Tuple
from collections import defaultdict

logger = logging.getLogger("mempalace_room")


class RoomAggregator:
    """Aggregate document-level scores to room-level scores.

    Takes document-level hybrid search results and aggregates them by room
    to determine which rooms are most relevant to a query.

    Attributes:
        aggregation_method: Method for aggregating scores ('average', 'max', 'weighted').
    """

    VALID_METHODS = {"average", "max", "weighted"}

    def __init__(self, aggregation_method: str = "average"):
        """Initialize room aggregator.

        Args:
            aggregation_method: Aggregation method to use. Valid options:
                - 'average': Average score of all documents in room
                - 'max': Maximum score of any document in room
                - 'weighted': Weighted average based on document rank

        Raises:
            ValueError: If aggregation_method is not valid.
        """
        if aggregation_method not in self.VALID_METHODS:
            raise ValueError(
                f"Invalid aggregation method '{aggregation_method}'. "
                f"Valid methods: {self.VALID_METHODS}"
            )

        self.aggregation_method = aggregation_method
        logger.info(f"Initialized room aggregator with method: {aggregation_method}")

    def aggregate(
        self,
        doc_results: List[Tuple[int, float]],
        documents: List[str],
        metadatas: List[Dict],
        top_k_rooms: int = 5,
    ) -> List[Dict]:
        """Aggregate document results to room-level results.

        Args:
            doc_results: List of (doc_index, score) tuples from hybrid search.
            documents: List of all document texts.
            metadatas: List of all document metadatas.
            top_k_rooms: Number of top rooms to return.

        Returns:
            List of room result dicts, each containing:
            - 'room': Room name
            - 'wing': Wing name (if available)
            - 'score': Aggregated room score
            - 'doc_count': Number of matching documents in room
            - 'documents': List of document details in this room
        """
        # Group documents by room
        room_docs = defaultdict(list)

        for doc_idx, score in doc_results:
            if doc_idx >= len(documents) or doc_idx >= len(metadatas):
                logger.warning(f"Document index {doc_idx} out of range, skipping")
                continue

            doc = documents[doc_idx]
            meta = metadatas[doc_idx]

            room = meta.get("room", "unknown")
            wing = meta.get("wing", "unknown")

            room_docs[room].append(
                {
                    "index": doc_idx,
                    "score": score,
                    "document": doc,
                    "wing": wing,
                    "metadata": meta,
                }
            )

        # Aggregate scores for each room
        room_scores = []

        for room, docs in room_docs.items():
            room_score = self._aggregate_scores(docs)

            # Get wing (should be consistent for all docs in room, or take first)
            wing = docs[0]["wing"] if docs else "unknown"

            room_scores.append(
                {
                    "room": room,
                    "wing": wing,
                    "score": round(room_score, 4),
                    "doc_count": len(docs),
                    "documents": [
                        {
                            "index": d["index"],
                            "score": round(d["score"], 4),
                            "text": d["document"][:100] + "..."
                            if len(d["document"]) > 100
                            else d["document"],
                            "full_text": d["document"],
                        }
                        for d in sorted(docs, key=lambda x: x["score"], reverse=True)
                    ],
                }
            )

        # Sort by room score and return top K
        room_scores.sort(key=lambda x: x["score"], reverse=True)

        return room_scores[:top_k_rooms]

    def _aggregate_scores(self, docs: List[Dict]) -> float:
        """Aggregate document scores using the configured method.

        Args:
            docs: List of document dicts with 'score' field.

        Returns:
            Aggregated score for the room.
        """
        scores = [d["score"] for d in docs]

        if not scores:
            return 0.0

        if self.aggregation_method == "average":
            return sum(scores) / len(scores)

        elif self.aggregation_method == "max":
            return max(scores)

        elif self.aggregation_method == "weighted":
            # Weighted average: earlier (higher-ranked) documents get more weight
            # Weight = 1 / (position + 1)
            weights = [1.0 / (i + 1) for i in range(len(scores))]
            weighted_sum = sum(score * weight for score, weight in zip(scores, weights))
            total_weight = sum(weights)

            return weighted_sum / total_weight

        else:
            # Fallback to average
            return sum(scores) / len(scores)

    def aggregate_with_details(
        self,
        doc_results: List[Tuple[int, float, float, float]],
        documents: List[str],
        metadatas: List[Dict],
        top_k_rooms: int = 5,
    ) -> Dict:
        """Aggregate with full breakdown of dense/sparse contributions.

        Args:
            doc_results: List of (doc_index, fused_score, dense_score, sparse_score) tuples.
            documents: List of all documents.
            metadatas: List of all metadatas.
            top_k_rooms: Number of top rooms.

        Returns:
            Dict with:
            - 'rooms': List of room results with detailed breakdown
            - 'aggregation_method': Method used
            - 'total_docs': Total number of documents considered
            - 'total_rooms': Total number of unique rooms found
        """
        # Group by room
        room_docs = defaultdict(list)

        for doc_idx, fused_score, dense_score, sparse_score in doc_results:
            if doc_idx >= len(documents) or doc_idx >= len(metadatas):
                continue

            doc = documents[doc_idx]
            meta = metadatas[doc_idx]

            room = meta.get("room", "unknown")
            wing = meta.get("wing", "unknown")

            room_docs[room].append(
                {
                    "index": doc_idx,
                    "fused": fused_score,
                    "dense": dense_score,
                    "sparse": sparse_score,
                    "document": doc,
                    "wing": wing,
                }
            )

        # Aggregate for each room
        room_results = []

        for room, docs in room_docs.items():
            room_fused = self._aggregate_scores([{"score": d["fused"]} for d in docs])

            room_dense = self._aggregate_scores([{"score": d["dense"]} for d in docs])

            room_sparse = self._aggregate_scores([{"score": d["sparse"]} for d in docs])

            wing = docs[0]["wing"] if docs else "unknown"

            room_results.append(
                {
                    "room": room,
                    "wing": wing,
                    "score": round(room_fused, 4),
                    "dense_score": round(room_dense, 4),
                    "sparse_score": round(room_sparse, 4),
                    "doc_count": len(docs),
                    "documents": [
                        {
                            "index": d["index"],
                            "fused": round(d["fused"], 4),
                            "dense": round(d["dense"], 4),
                            "sparse": round(d["sparse"], 4),
                            "text": d["document"][:100] + "..."
                            if len(d["document"]) > 100
                            else d["document"],
                        }
                        for d in sorted(docs, key=lambda x: x["fused"], reverse=True)
                    ],
                }
            )

        # Sort and return top K
        room_results.sort(key=lambda x: x["score"], reverse=True)

        return {
            "rooms": room_results[:top_k_rooms],
            "aggregation_method": self.aggregation_method,
            "total_docs": len(doc_results),
            "total_rooms": len(room_docs),
        }


def compare_aggregation_methods(
    doc_results: List[Tuple[int, float]],
    documents: List[str],
    metadatas: List[Dict],
    top_k: int = 5,
) -> Dict:
    """Compare all aggregation methods to see how they differ.

    Useful for understanding which aggregation method works best for a query.

    Args:
        doc_results: Document results.
        documents: All documents.
        metadatas: All metadatas.
        top_k: Top rooms to compare.

    Returns:
        Dict with results from each aggregation method.
    """
    methods = ["average", "max", "weighted"]
    results = {}

    for method in methods:
        aggregator = RoomAggregator(aggregation_method=method)
        room_results = aggregator.aggregate(doc_results, documents, metadatas, top_k)

        results[method] = {
            "top_rooms": [r["room"] for r in room_results],
            "top_scores": [r["score"] for r in room_results],
            "details": room_results,
        }

    return results


# Example usage
if __name__ == "__main__":
    # Test data
    test_docs = [
        "The team decided to migrate from MySQL to PostgreSQL for better JSON support.",
        "We discussed using Alembic for database migrations during the sprint planning.",
        "The authentication system uses JWT tokens with 24-hour expiration.",
        "Frontend development uses React with TypeScript and Tailwind CSS.",
        "Database backup strategy includes daily snapshots and weekly full backups.",
    ]

    test_metadata = [
        {"wing": "project", "room": "database"},
        {"wing": "project", "room": "database"},
        {"wing": "project", "room": "auth"},
        {"wing": "project", "room": "frontend"},
        {"wing": "project", "room": "database"},
    ]

    # Simulated hybrid search results
    doc_results = [
        (0, 0.850),  # PostgreSQL doc - highest score
        (1, 0.810),  # Alembic doc
        (4, 0.720),  # Backup doc
        (2, 0.300),  # Auth doc
        (3, 0.210),  # Frontend doc
    ]

    print("Room Aggregator Test")
    print("=" * 60)

    query = "database migration"
    print(f"\nQuery: {query}")
    print(f"Documents: {len(test_docs)}, Rooms: {len(set(m['room'] for m in test_metadata))}")

    # Test each aggregation method
    for method in ["average", "max", "weighted"]:
        print(f"\n{method.upper()} Aggregation:")
        print("-" * 60)

        aggregator = RoomAggregator(aggregation_method=method)
        room_results = aggregator.aggregate(doc_results, test_docs, test_metadata, top_k_rooms=3)

        for i, room in enumerate(room_results, 1):
            print(f"\n  [{i}] Room: {room['room']} (Wing: {room['wing']})")
            print(f"      Score: {room['score']:.3f}")
            print(f"      Documents in room: {room['doc_count']}")

            for doc in room["documents"]:
                print(f"        - Doc {doc['index']}: {doc['score']:.3f} | {doc['text'][:60]}...")

    # Compare all methods
    print("\n" + "=" * 60)
    print("Method Comparison:")
    print("-" * 60)

    comparison = compare_aggregation_methods(doc_results, test_docs, test_metadata, top_k=3)

    for method, result in comparison.items():
        rooms = ", ".join(result["top_rooms"])
        scores = ", ".join(f"{s:.3f}" for s in result["top_scores"])
        print(f"\n  {method:8s}: Rooms: [{rooms}] | Scores: [{scores}]")

    # Test with detailed breakdown
    print("\n" + "=" * 60)
    print("Detailed Breakdown (with dense/sparse components):")
    print("-" * 60)

    # Simulated results with component scores
    detailed_results = [
        (0, 0.850, 0.700, 0.150),  # fused, dense, sparse
        (1, 0.810, 0.650, 0.160),
        (4, 0.720, 0.600, 0.120),
        (2, 0.300, 0.250, 0.050),
        (3, 0.210, 0.180, 0.030),
    ]

    aggregator = RoomAggregator(aggregation_method="average")
    detailed = aggregator.aggregate_with_details(
        detailed_results, test_docs, test_metadata, top_k_rooms=2
    )

    print(f"\nMethod: {detailed['aggregation_method']}")
    print(f"Total docs: {detailed['total_docs']}, Total rooms: {detailed['total_rooms']}")

    for room in detailed["rooms"]:
        print(f"\n  Room: {room['room']}")
        print(f"    Fused Score: {room['score']:.3f}")
        print(f"    Dense Score: {room['dense_score']:.3f}")
        print(f"    Sparse Score: {room['sparse_score']:.3f}")
        print(f"    Documents: {room['doc_count']}")

        for doc in room["documents"]:
            print(
                f"      Doc {doc['index']}: F={doc['fused']:.3f}, D={doc['dense']:.3f}, S={doc['sparse']:.3f}"
            )
