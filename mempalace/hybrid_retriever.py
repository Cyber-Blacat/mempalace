#!/usr/bin/env python3
"""
hybrid_retriever.py — Hybrid retrieval combining dense and sparse signals.

This module implements hybrid retrieval that combines:
1. Dense retrieval (semantic similarity via embeddings)
2. Sparse retrieval (keyword matching via BM25)

The fusion algorithm: fused_score = α * dense_score + β * sparse_score
where α and β are configurable weights.
"""

import logging
from typing import List, Dict, Tuple
from collections import defaultdict

logger = logging.getLogger("mempalace_hybrid")


class HybridRetriever:
    """Hybrid retriever combining dense and sparse retrieval.

    Combines semantic similarity (dense embeddings) with keyword matching
    (sparse BM25) to improve retrieval accuracy. Some queries benefit more
    from exact keyword matches (e.g., "PostgreSQL", "Dr. Chen") while others
    benefit from semantic understanding.

    Attributes:
        alpha: Weight for dense retrieval scores (0.0 to 1.0).
        beta: Weight for sparse retrieval scores (0.0 to 1.0).
        documents: List of all documents.
        metadatas: List of metadata for each document.
    """

    def __init__(
        self, documents: List[str], metadatas: List[Dict], alpha: float = 0.7, beta: float = 0.3
    ):
        """Initialize hybrid retriever.

        Args:
            documents: List of document texts.
            metadatas: List of metadata dicts for each document.
            alpha: Weight for dense retrieval (default: 0.7).
            beta: Weight for sparse retrieval (default: 0.3).

        Raises:
            ValueError: If alpha + beta != 1.0 or weights are invalid.
        """
        if not 0.0 <= alpha <= 1.0 or not 0.0 <= beta <= 1.0:
            raise ValueError(f"Alpha ({alpha}) and beta ({beta}) must be in [0, 1]")

        # Allow alpha + beta != 1.0, but warn if they don't sum to ~1.0
        weight_sum = alpha + beta
        if abs(weight_sum - 1.0) > 0.01:
            logger.warning(
                f"Alpha + beta = {weight_sum:.2f}, not 1.0. Scores may be amplified or reduced."
            )

        self.alpha = alpha
        self.beta = beta
        self.documents = documents
        self.metadatas = metadatas

        logger.info(f"Initialized hybrid retriever with α={alpha:.2f}, β={beta:.2f}")

    def fuse_results(
        self,
        dense_results: List[Tuple[int, float]],
        sparse_results: List[Tuple[int, float]],
        k: int = 10,
    ) -> List[Tuple[int, float, float, float]]:
        """Fuse dense and sparse retrieval results.

        Args:
            dense_results: List of (doc_index, dense_score) tuples.
            sparse_results: List of (doc_index, sparse_score) tuples.
            k: Number of top results to return.

        Returns:
            List of (doc_index, fused_score, dense_score, sparse_score) tuples,
            sorted by fused_score descending.
        """
        # Convert to dicts for easier lookup
        dense_dict = {idx: score for idx, score in dense_results}
        sparse_dict = {idx: score for idx, score in sparse_results}

        # Get all unique document indices
        all_indices = set(dense_dict.keys()) | set(sparse_dict.keys())

        # Fuse scores for each document
        fused_results = []
        for idx in all_indices:
            dense_score = dense_dict.get(idx, 0.0)
            sparse_score = sparse_dict.get(idx, 0.0)

            # Fusion: weighted sum
            fused_score = self.alpha * dense_score + self.beta * sparse_score

            fused_results.append((idx, fused_score, dense_score, sparse_score))

        # Sort by fused score descending
        fused_results.sort(key=lambda x: x[1], reverse=True)

        return fused_results[:k]

    def search_with_components(
        self,
        dense_results: List[Tuple[int, float]],
        sparse_results: List[Tuple[int, float]],
        k: int = 10,
    ) -> Dict:
        """Search and return detailed results with component scores.

        Args:
            dense_results: Dense retrieval results.
            sparse_results: Sparse retrieval results.
            k: Number of results to return.

        Returns:
            Dict with:
            - "results": List of result dicts with document info and all scores
            - "alpha": Alpha weight used
            - "beta": Beta weight used
            - "query_components": Breakdown of how each score contributed
        """
        fused_results = self.fuse_results(dense_results, sparse_results, k)

        results = []
        for idx, fused_score, dense_score, sparse_score in fused_results:
            doc = self.documents[idx]
            meta = self.metadatas[idx]

            results.append(
                {
                    "index": idx,
                    "document": doc,
                    "metadata": meta,
                    "fused_score": round(fused_score, 4),
                    "dense_score": round(dense_score, 4),
                    "sparse_score": round(sparse_score, 4),
                    "dense_contribution": round(self.alpha * dense_score, 4),
                    "sparse_contribution": round(self.beta * sparse_score, 4),
                }
            )

        return {
            "results": results,
            "alpha": self.alpha,
            "beta": self.beta,
            "total_docs_considered": len(
                set([idx for idx, _ in dense_results] + [idx for idx, _ in sparse_results])
            ),
        }

    def get_document(self, index: int) -> Tuple[str, Dict]:
        """Get document and metadata by index.

        Args:
            index: Document index.

        Returns:
            Tuple of (document_text, metadata_dict).
        """
        if index < 0 or index >= len(self.documents):
            raise IndexError(f"Index {index} out of range")

        return self.documents[index], self.metadatas[index]


def reciprocal_rank_fusion(
    dense_results: List[Tuple[int, float]],
    sparse_results: List[Tuple[int, float]],
    k: int = 60,
    final_k: int = 10,
) -> List[Tuple[int, float]]:
    """Alternative fusion method using Reciprocal Rank Fusion (RRF).

    RRF is a simple yet effective fusion method that combines rankings
    rather than scores. It's useful when scores from different retrievers
    are on different scales and hard to normalize.

    RRF score = 1 / (k + rank)

    Args:
        dense_results: List of (doc_index, score) from dense retrieval.
        sparse_results: List of (doc_index, score) from sparse retrieval.
        k: RRF parameter (default: 60, common value from literature).
        final_k: Number of final results to return.

    Returns:
        List of (doc_index, rrf_score) tuples, sorted by RRF score descending.
    """
    # Convert to ranked lists
    dense_ranked = sorted(dense_results, key=lambda x: x[1], reverse=True)
    sparse_ranked = sorted(sparse_results, key=lambda x: x[1], reverse=True)

    # Compute RRF scores
    rrf_scores = defaultdict(float)

    for rank, (idx, _) in enumerate(dense_ranked):
        rrf_scores[idx] += 1.0 / (k + rank + 1)

    for rank, (idx, _) in enumerate(sparse_ranked):
        rrf_scores[idx] += 1.0 / (k + rank + 1)

    # Sort and return top results
    results = [(idx, score) for idx, score in rrf_scores.items()]
    results.sort(key=lambda x: x[1], reverse=True)

    return results[:final_k]


def normalize_and_fuse(
    dense_scores: Dict[int, float],
    sparse_scores: Dict[int, float],
    alpha: float = 0.7,
    beta: float = 0.3,
) -> Dict[int, float]:
    """Normalize scores from both retrievers and fuse them.

    This function normalizes scores to [0, 1] range before fusion,
    handling cases where raw scores might be on different scales.

    Args:
        dense_scores: Dict of {doc_index: dense_score}.
        sparse_scores: Dict of {doc_index: sparse_score}.
        alpha: Dense weight.
        beta: Sparse weight.

    Returns:
        Dict of {doc_index: fused_score}.
    """
    # Normalize dense scores (assumed to be in [0, 1] already from ChromaDB)
    # ChromaDB returns distances, convert to similarity: similarity = 1 - distance
    dense_normalized = {idx: max(0.0, min(1.0, score)) for idx, score in dense_scores.items()}

    # Normalize sparse scores (BM25 scores vary widely)
    if sparse_scores:
        min_sparse = min(sparse_scores.values())
        max_sparse = max(sparse_scores.values())

        if max_sparse > min_sparse:
            sparse_normalized = {
                idx: (score - min_sparse) / (max_sparse - min_sparse)
                for idx, score in sparse_scores.items()
            }
        else:
            # All scores are the same
            sparse_normalized = {
                idx: 0.5 if score > 0 else 0.0 for idx, score in sparse_scores.items()
            }
    else:
        sparse_normalized = {}

    # Fuse scores
    all_indices = set(dense_normalized.keys()) | set(sparse_normalized.keys())

    fused_scores = {}
    for idx in all_indices:
        dense = dense_normalized.get(idx, 0.0)
        sparse = sparse_normalized.get(idx, 0.0)

        fused_scores[idx] = alpha * dense + beta * sparse

    return fused_scores


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

    # Simulated dense results (ChromaDB similarity scores)
    dense_results = [
        (0, 0.85),  # PostgreSQL doc
        (1, 0.75),  # Alembic doc
        (4, 0.70),  # Backup doc
        (2, 0.30),  # Auth doc
        (3, 0.20),  # Frontend doc
    ]

    # Simulated sparse results (BM25 scores normalized)
    sparse_results = [
        (1, 0.90),  # Alembic doc - high keyword match
        (0, 0.85),  # PostgreSQL doc
        (4, 0.70),  # Backup doc
        (2, 0.50),  # Auth doc
        (3, 0.30),  # Frontend doc
    ]

    # Test hybrid fusion
    print("Hybrid Retriever Test")
    print("=" * 60)

    retriever = HybridRetriever(test_docs, test_metadata, alpha=0.7, beta=0.3)

    query = "database migration"
    print(f"\nQuery: {query}")
    print(f"Alpha: {retriever.alpha}, Beta: {retriever.beta}")

    fused_results = retriever.fuse_results(dense_results, sparse_results, k=3)

    print("\nTop 3 Fused Results:")
    for idx, fused_score, dense_score, sparse_score in fused_results:
        doc = test_docs[idx]
        room = test_metadata[idx]["room"]

        print(f"\n  [{idx}] Room: {room}")
        print(f"      Fused Score:   {fused_score:.3f}")
        print(
            f"      Dense Score:   {dense_score:.3f} (contribution: {retriever.alpha * dense_score:.3f})"
        )
        print(
            f"      Sparse Score:  {sparse_score:.3f} (contribution: {retriever.beta * sparse_score:.3f})"
        )
        print(f"      Document: {doc[:70]}...")

    # Test detailed results
    print("\n" + "=" * 60)
    print("Detailed Results:")

    detailed = retriever.search_with_components(dense_results, sparse_results, k=3)

    print(f"Alpha: {detailed['alpha']}, Beta: {detailed['beta']}")
    print(f"Total docs considered: {detailed['total_docs_considered']}")

    for result in detailed["results"]:
        print(f"\n  Document {result['index']}:")
        print(
            f"    Fused: {result['fused_score']:.3f} = {result['dense_contribution']:.3f} (dense) + {result['sparse_contribution']:.3f} (sparse)"
        )

    # Test RRF fusion
    print("\n" + "=" * 60)
    print("Reciprocal Rank Fusion Test:")

    rrf_results = reciprocal_rank_fusion(dense_results, sparse_results, k=60, final_k=3)

    for idx, rrf_score in rrf_results:
        print(f"  [{idx}] RRF Score: {rrf_score:.4f} | Room: {test_metadata[idx]['room']}")
