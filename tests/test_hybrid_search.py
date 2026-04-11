#!/usr/bin/env python3
"""
test_hybrid_search.py - Integration tests for hybrid search functionality.

Tests the integration of BM25 sparse retrieval, hybrid fusion, and room aggregation
with the main searcher module.
"""

import os
import tempfile
import shutil

import chromadb
import pytest

from mempalace.searcher import hybrid_search_memories
from mempalace.config import MempalaceConfig
from mempalace.embedding_function import get_embedding_function


class TestHybridSearch:
    """Test hybrid search integration with ChromaDB."""

    @pytest.fixture
    def temp_palace(self):
        """Create a temporary palace for testing."""
        tmpdir = tempfile.mkdtemp(prefix="mempalace_hybrid_test_")
        palace_path = os.path.join(tmpdir, "palace")
        os.makedirs(palace_path)

        # Create ChromaDB client and collection with embedding function
        client = chromadb.PersistentClient(path=palace_path)
        embedding_fn = get_embedding_function()
        collection = client.get_or_create_collection(
            "mempalace_drawers", embedding_function=embedding_fn
        )

        # Add test documents
        documents = [
            "The team decided to migrate from MySQL to PostgreSQL for better JSON support.",
            "We discussed using Alembic for database migrations during the sprint planning.",
            "The authentication system uses JWT tokens with 24-hour expiration.",
            "Frontend development uses React with TypeScript and Tailwind CSS.",
            "Database backup strategy includes daily snapshots and weekly full backups.",
        ]

        metadatas = [
            {"wing": "project", "room": "database", "source_file": "meeting.md"},
            {"wing": "project", "room": "database", "source_file": "sprint.md"},
            {"wing": "project", "room": "auth", "source_file": "auth.md"},
            {"wing": "project", "room": "frontend", "source_file": "frontend.md"},
            {"wing": "project", "room": "database", "source_file": "backup.md"},
        ]

        ids = [f"doc_{i}" for i in range(len(documents))]

        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
        )

        yield palace_path

        # Cleanup
        client.delete_collection("mempalace_drawers")
        del client
        shutil.rmtree(tmpdir, ignore_errors=True)

    def test_hybrid_search_basic(self, temp_palace):
        """Test basic hybrid search functionality."""
        result = hybrid_search_memories(
            query="database migration",
            palace_path=temp_palace,
            n_results=3,
            room_top_k=3,
        )

        # Check basic structure
        assert "query" in result
        assert result["query"] == "database migration"
        assert result["mode"] == "hybrid"

        # Check config
        assert "config" in result
        assert result["config"]["alpha"] == 0.7
        assert result["config"]["beta"] == 0.3

        # Check results
        assert "room_results" in result
        assert "document_results" in result
        assert len(result["room_results"]) > 0
        assert len(result["document_results"]) > 0

    def test_hybrid_search_returns_rooms(self, temp_palace):
        """Test that hybrid search returns room-level results."""
        result = hybrid_search_memories(
            query="database",
            palace_path=temp_palace,
            room_top_k=3,
        )

        # Check room results structure
        assert len(result["room_results"]) > 0

        for room in result["room_results"]:
            assert "room" in room
            assert "wing" in room
            assert "score" in room
            assert "doc_count" in room
            assert "documents" in room

            # Score should be between 0 and 1
            assert 0.0 <= room["score"] <= 1.0

            # Doc count should be positive
            assert room["doc_count"] > 0

    def test_hybrid_search_returns_documents(self, temp_palace):
        """Test that hybrid search returns document-level results."""
        result = hybrid_search_memories(
            query="authentication",
            palace_path=temp_palace,
            n_results=3,
        )

        # Check document results structure
        assert len(result["document_results"]) > 0

        for doc in result["document_results"]:
            assert "text" in doc
            assert "wing" in doc
            assert "room" in doc
            assert "fused_score" in doc
            assert "dense_score" in doc
            assert "sparse_score" in doc

            # Scores should be between 0 and 1
            assert 0.0 <= doc["fused_score"] <= 1.0
            assert 0.0 <= doc["dense_score"] <= 1.0
            assert 0.0 <= doc["sparse_score"] <= 1.0

    def test_hybrid_search_config_customization(self, temp_palace):
        """Test that custom configuration parameters work."""
        result = hybrid_search_memories(
            query="database",
            palace_path=temp_palace,
            alpha=0.8,
            beta=0.2,
            doc_top_k=10,
            room_top_k=2,
            aggregation_method="max",
        )

        # Check that custom config is applied
        assert result["config"]["alpha"] == 0.8
        assert result["config"]["beta"] == 0.2
        assert result["config"]["doc_top_k"] == 10
        assert result["config"]["room_top_k"] == 2
        assert result["config"]["aggregation_method"] == "max"

        # Should return at most 2 rooms
        assert len(result["room_results"]) <= 2

    def test_hybrid_search_wing_filter(self, temp_palace):
        """Test hybrid search with wing filter."""
        result = hybrid_search_memories(
            query="database",
            palace_path=temp_palace,
            wing="project",
        )

        # All results should be in 'project' wing
        for room in result["room_results"]:
            assert room["wing"] == "project"

        for doc in result["document_results"]:
            assert doc["wing"] == "project"

    def test_hybrid_search_room_filter(self, temp_palace):
        """Test hybrid search with room filter."""
        result = hybrid_search_memories(
            query="database",
            palace_path=temp_palace,
            room="database",
        )

        # All results should be in 'database' room
        for room in result["room_results"]:
            assert room["room"] == "database"

        for doc in result["document_results"]:
            assert doc["room"] == "database"

    def test_hybrid_search_aggregation_methods(self, temp_palace):
        """Test different aggregation methods."""
        methods = ["average", "max", "weighted"]

        for method in methods:
            result = hybrid_search_memories(
                query="database",
                palace_path=temp_palace,
                aggregation_method=method,
                room_top_k=3,
            )

            # Should return results for each method
            assert len(result["room_results"]) > 0
            assert result["config"]["aggregation_method"] == method

    def test_hybrid_search_no_palace(self, tmp_path):
        """Test hybrid search when palace doesn't exist."""
        # Use a truly non-existent path (not /nonexistent/path which may have cached data)
        nonexistent_path = str(tmp_path / "nonexistent_palace")
        result = hybrid_search_memories(
            query="test",
            palace_path=nonexistent_path,
        )

        # Should return error
        assert "error" in result
        assert "No palace found" in result["error"]

    def test_hybrid_search_empty_query(self, temp_palace):
        """Test hybrid search with empty query."""
        # Empty query should still work (BM25 will handle it)
        result = hybrid_search_memories(
            query="",
            palace_path=temp_palace,
        )

        # Should return results (or empty results, not error)
        assert "error" not in result or result.get("error") is None

    def test_hybrid_search_score_fusion(self, temp_palace):
        """Test that score fusion is working correctly."""
        result = hybrid_search_memories(
            query="database migration",
            palace_path=temp_palace,
            alpha=0.7,
            beta=0.3,
        )

        # For each document, verify fusion formula
        for doc in result["document_results"]:
            expected_fused = 0.7 * doc["dense_score"] + 0.3 * doc["sparse_score"]
            # Allow small floating point tolerance
            assert abs(doc["fused_score"] - expected_fused) < 0.01

    def test_hybrid_search_ranking_order(self, temp_palace):
        """Test that results are properly ranked."""
        result = hybrid_search_memories(
            query="database",
            palace_path=temp_palace,
            n_results=5,
        )

        # Document results should be sorted by fused_score descending
        doc_scores = [doc["fused_score"] for doc in result["document_results"]]
        assert doc_scores == sorted(doc_scores, reverse=True)

        # Room results should be sorted by score descending
        room_scores = [room["score"] for room in result["room_results"]]
        assert room_scores == sorted(room_scores, reverse=True)


class TestHybridSearchIntegration:
    """Test hybrid search integration with config system."""

    def test_config_default_values(self):
        """Test that config provides default values."""
        from mempalace.config import DEFAULT_HYBRID_CONFIG

        assert "alpha" in DEFAULT_HYBRID_CONFIG
        assert "beta" in DEFAULT_HYBRID_CONFIG
        assert "doc_top_k" in DEFAULT_HYBRID_CONFIG
        assert "room_top_k" in DEFAULT_HYBRID_CONFIG
        assert "aggregation_method" in DEFAULT_HYBRID_CONFIG

        # Check default values
        assert DEFAULT_HYBRID_CONFIG["alpha"] == 0.7
        assert DEFAULT_HYBRID_CONFIG["beta"] == 0.3
        assert DEFAULT_HYBRID_CONFIG["doc_top_k"] == 20
        assert DEFAULT_HYBRID_CONFIG["room_top_k"] == 5
        assert DEFAULT_HYBRID_CONFIG["aggregation_method"] == "average"

    @pytest.fixture
    def temp_config(self, tmp_path):
        """Create a temporary config for testing."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        config = MempalaceConfig(config_dir=str(config_dir))
        config.init()

        yield config

        shutil.rmtree(config_dir, ignore_errors=True)

    def test_config_hybrid_search_property(self, temp_config):
        """Test that config has hybrid_search_config property."""
        hybrid_config = temp_config.hybrid_search_config

        assert isinstance(hybrid_config, dict)
        assert "alpha" in hybrid_config
        assert "beta" in hybrid_config


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
