#!/usr/bin/env python3
"""
sparse_retriever.py — BM25-based sparse retrieval for keyword matching.

This module implements sparse retrieval using the BM25 algorithm, which excels at
exact keyword matching and can complement dense embedding-based semantic search.
"""

import logging
import re
from typing import List, Dict, Tuple, Optional

from rank_bm25 import BM25Okapi

logger = logging.getLogger("mempalace_sparse")


class BM25Retriever:
    """BM25-based sparse retriever for keyword matching.

    BM25 is a probabilistic retrieval model that ranks documents based on
    term frequency, document length, and corpus statistics. It's particularly
    effective for queries with specific keywords that embeddings might underweight.

    Attributes:
        documents: List of document texts to search.
        metadatas: Optional list of metadata dicts for each document.
        bm25: The BM25 index built from tokenized documents.
    """

    # Common English stop words to filter out during tokenization
    STOP_WORDS = {
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "by",
        "for",
        "from",
        "has",
        "he",
        "in",
        "is",
        "it",
        "its",
        "of",
        "on",
        "that",
        "the",
        "to",
        "was",
        "were",
        "will",
        "with",
        "the",
        "this",
        "but",
        "they",
        "have",
        "had",
        "what",
        "when",
        "where",
        "who",
        "which",
        "why",
        "how",
        "all",
        "each",
        "every",
        "both",
        "few",
        "more",
        "most",
        "other",
        "some",
        "such",
        "no",
        "nor",
        "not",
        "only",
        "own",
        "same",
        "so",
        "than",
        "too",
        "very",
        "can",
        "just",
        "should",
        "now",
        "i",
        "me",
        "my",
        "myself",
        "we",
        "our",
        "ours",
        "you",
        "your",
        "yours",
        "he",
        "him",
        "his",
        "she",
        "her",
        "hers",
        "they",
        "them",
        "their",
        "what",
        "which",
        "who",
        "whom",
        "this",
        "that",
        "these",
        "those",
        "am",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "have",
        "has",
        "had",
        "having",
        "do",
        "does",
        "did",
        "doing",
        "would",
        "could",
        "should",
        "may",
        "might",
        "must",
        "shall",
        "can",
        "need",
        "dare",
        "ought",
        "used",
    }

    def __init__(self, documents: List[str], metadatas: Optional[List[Dict]] = None):
        """Initialize BM25 retriever with documents.

        Args:
            documents: List of document texts to index.
            metadatas: Optional list of metadata dicts for each document.
                       If provided, must have same length as documents.

        Raises:
            ValueError: If documents is empty or metadatas length doesn't match.
        """
        if not documents:
            raise ValueError("Documents list cannot be empty")

        if metadatas and len(metadatas) != len(documents):
            raise ValueError(
                f"Metadatas length ({len(metadatas)}) must match "
                f"documents length ({len(documents)})"
            )

        self.documents = documents
        self.metadatas = metadatas or [{} for _ in documents]

        # Tokenize documents
        logger.info(f"Tokenizing {len(documents)} documents for BM25 index...")
        self.tokenized_docs = [self._tokenize(doc) for doc in documents]

        # Build BM25 index
        logger.info("Building BM25 index...")
        self.bm25 = BM25Okapi(self.tokenized_docs)

        # Cache for normalized scores
        self._score_cache = {}

    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into meaningful keywords.

        Lowercases text, splits on whitespace and punctuation, filters out
        stop words and short tokens (< 2 chars).

        Args:
            text: Text to tokenize.

        Returns:
            List of meaningful tokens.
        """
        # Lowercase and split on whitespace/punctuation
        text = text.lower()
        tokens = re.findall(r"\b\w+\b", text)

        # Filter out stop words and short tokens
        tokens = [token for token in tokens if token not in self.STOP_WORDS and len(token) >= 2]

        return tokens

    def search(
        self, query: str, k: int = 10, normalize_scores: bool = True
    ) -> List[Tuple[int, float]]:
        """Search for documents matching the query.

        Args:
            query: Query string to search for.
            k: Number of results to return.
            normalize_scores: Whether to normalize scores to [0, 1] range.
                             Raw BM25 scores can vary widely; normalization
                             makes them comparable with dense similarity scores.

        Returns:
            List of (document_index, score) tuples, sorted by score descending.
            Scores are normalized to [0, 1] if normalize_scores=True.
        """
        # Tokenize query
        tokenized_query = self._tokenize(query)

        if not tokenized_query:
            logger.warning(f"Query '{query}' produced no meaningful tokens")
            return []

        # Get BM25 scores for all documents
        scores = self.bm25.get_scores(tokenized_query)

        # Normalize scores if requested
        if normalize_scores:
            scores = self._normalize_scores(scores)

        # Sort by score descending and get top k
        indexed_scores = list(enumerate(scores))
        indexed_scores.sort(key=lambda x: x[1], reverse=True)

        return indexed_scores[:k]

    def _normalize_scores(self, scores: List[float]) -> List[float]:
        """Normalize BM25 scores to [0, 1] range using min-max normalization.

        BM25 scores can be negative and vary widely. Normalization makes them
        comparable with dense similarity scores from ChromaDB (which are in
        [0, 1] range).

        Args:
            scores: Raw BM25 scores (numpy array or list).

        Returns:
            Normalized scores in [0, 1] range as list.
        """
        # Convert numpy array to list if needed
        if hasattr(scores, "tolist"):
            scores = scores.tolist()

        if not scores or len(scores) == 0:
            return []

        min_score = min(scores)
        max_score = max(scores)

        # Handle case where all scores are the same
        if max_score == min_score:
            return [0.5 if score > 0 else 0.0 for score in scores]

        # Min-max normalization
        normalized = [(score - min_score) / (max_score - min_score) for score in scores]

        return normalized

    def get_document(self, index: int) -> Tuple[str, Dict]:
        """Get document and metadata by index.

        Args:
            index: Document index.

        Returns:
            Tuple of (document_text, metadata_dict).

        Raises:
            IndexError: If index is out of range.
        """
        if index < 0 or index >= len(self.documents):
            raise IndexError(f"Index {index} out of range (0-{len(self.documents) - 1})")

        return self.documents[index], self.metadatas[index]

    def update_documents(self, documents: List[str], metadatas: Optional[List[Dict]] = None):
        """Update the document index with new documents.

        Rebuilds the entire BM25 index. Useful when documents change significantly.

        Args:
            documents: New list of documents.
            metadatas: Optional new list of metadatas.

        Raises:
            ValueError: If documents is empty or metadatas length doesn't match.
        """
        if not documents:
            raise ValueError("Documents list cannot be empty")

        if metadatas and len(metadatas) != len(documents):
            raise ValueError(
                f"Metadatas length ({len(metadatas)}) must match "
                f"documents length ({len(documents)})"
            )

        logger.info(f"Updating BM25 index with {len(documents)} documents...")
        self.documents = documents
        self.metadatas = metadatas or [{} for _ in documents]
        self.tokenized_docs = [self._tokenize(doc) for doc in documents]
        self.bm25 = BM25Okapi(self.tokenized_docs)
        self._score_cache = {}

    def get_stats(self) -> Dict:
        """Get statistics about the indexed corpus.

        Returns:
            Dict with corpus statistics:
            - num_documents: Total number of documents
            - avg_doc_length: Average document length (in tokens)
            - total_tokens: Total number of unique tokens
        """
        avg_length = sum(len(tokens) for tokens in self.tokenized_docs) / len(self.tokenized_docs)
        unique_tokens = set(token for tokens in self.tokenized_docs for token in tokens)

        return {
            "num_documents": len(self.documents),
            "avg_doc_length": round(avg_length, 2),
            "total_unique_tokens": len(unique_tokens),
        }


def create_bm25_retriever_from_collection(
    collection, include_metadata: bool = True
) -> BM25Retriever:
    """Create a BM25 retriever from a ChromaDB collection.

    Convenience function to extract documents and metadatas from a ChromaDB
    collection and initialize a BM25Retriever.

    Args:
        collection: ChromaDB collection object.
        include_metadata: Whether to include metadata in the retriever.

    Returns:
        BM25Retriever initialized with collection data.

    Raises:
        ValueError: If collection has no documents.
    """
    # Get all documents from collection
    results = collection.get(include=["documents", "metadatas"])

    if not results["documents"]:
        raise ValueError("Collection has no documents")

    documents = results["documents"]
    metadatas = results["metadatas"] if include_metadata else None

    return BM25Retriever(documents, metadatas)


# Example usage and testing
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

    # Create retriever
    retriever = BM25Retriever(test_docs, test_metadata)

    # Test search
    print("BM25 Retriever Test")
    print("=" * 60)

    queries = ["database migration", "authentication", "frontend framework"]

    for query in queries:
        print(f"\nQuery: {query}")
        results = retriever.search(query, k=3)

        for idx, score in results:
            doc, meta = retriever.get_document(idx)
            room = meta.get("room", "unknown")
            print(f"  [{idx}] Score: {score:.3f} | Room: {room}")
            print(f"      Text: {doc[:80]}...")

    # Stats
    print("\n" + "=" * 60)
    print("Corpus Statistics:")
    stats = retriever.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
