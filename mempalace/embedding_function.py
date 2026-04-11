#!/usr/bin/env python3
"""
embedding_function.py — Custom embedding functions for ChromaDB.

This module provides embedding functions that explicitly load models from
local assets/ directory instead of system cache (~/.cache/huggingface/).

Usage:
    from mempalace.embedding_function import get_embedding_function

    # Get embedding function that loads from local assets/
    embedding_fn = get_embedding_function()

    # Use with ChromaDB
    client = chromadb.PersistentClient(path=palace_path)
    col = client.get_collection("mempalace_drawers", embedding_function=embedding_fn)
"""

import logging
from typing import List, Optional, Union


from .config import MempalaceConfig

logger = logging.getLogger("mempalace_mcp")

# Global model cache to avoid reloading
_model_cache = {}
_embedding_function_cache = {}


class LocalEmbeddingFunction:
    """Custom embedding function that loads models from local assets/ directory.

    This avoids using system cache directories like ~/.cache/huggingface/
    by explicitly specifying the cache_folder to the assets/ directory.
    """

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        cache_folder: Optional[str] = None,
        device: str = "cpu",
        normalize_embeddings: bool = True,
    ):
        """Initialize the embedding function.

        Args:
            model_name: The name of the sentence-transformers model.
            cache_folder: Local directory to cache models (default: assets/).
            device: Device to run model on ('cpu' or 'cuda').
            normalize_embeddings: Whether to normalize embeddings.
        """
        self.model_name = model_name
        self.cache_folder = cache_folder
        self.device = device
        self.normalize_embeddings = normalize_embeddings
        self._model = None

    @property
    def model(self):
        """Lazy-load the model from local cache folder."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer

                logger.info(
                    f"Loading embedding model '{self.model_name}' from local cache: {self.cache_folder}"
                )

                # Explicitly load from local cache folder
                # This will download to assets/ if not already there
                self._model = SentenceTransformer(
                    self.model_name,
                    cache_folder=self.cache_folder,
                    device=self.device,
                )

                logger.info(f"Successfully loaded embedding model: {self.model_name}")

            except ImportError:
                raise ImportError(
                    "sentence-transformers is required for embedding functions. "
                    "Install with: pip install sentence-transformers"
                )
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                raise

        return self._model

    def __call__(self, input: Union[List[str], str]) -> List[List[float]]:
        """Generate embeddings for the input text(s).

        Args:
            input: A single string or list of strings.

        Returns:
            List of embedding vectors (each vector is a list of floats).
        """
        if isinstance(input, str):
            input = [input]

        # Generate embeddings
        embeddings = self.model.encode(
            input,
            normalize_embeddings=self.normalize_embeddings,
            convert_to_numpy=True,
            show_progress_bar=False,
        )

        # Convert to list of lists
        return [embedding.tolist() for embedding in embeddings]


def get_embedding_function(
    model_name: Optional[str] = None,
    cache_folder: Optional[str] = None,
    device: str = "cpu",
) -> LocalEmbeddingFunction:
    """Get or create a cached embedding function.

    This function caches the embedding function to avoid reloading the model
    on every call. The model is loaded from the local assets/ directory.

    Args:
        model_name: Override the default model name.
        cache_folder: Override the default cache folder (assets/).
        device: Device to run model on ('cpu' or 'cuda').

    Returns:
        LocalEmbeddingFunction instance.
    """
    # Get config for defaults
    config = MempalaceConfig()

    # Use provided values or fall back to config
    model_name = model_name or config.embedding_model
    cache_folder = cache_folder or config.assets_path

    # Create cache key
    cache_key = f"{model_name}:{cache_folder}:{device}"

    # Return cached instance if available
    if cache_key not in _embedding_function_cache:
        logger.info(f"Creating new embedding function (cache key: {cache_key})")
        _embedding_function_cache[cache_key] = LocalEmbeddingFunction(
            model_name=model_name,
            cache_folder=cache_folder,
            device=device,
        )
    else:
        logger.debug(f"Using cached embedding function (cache key: {cache_key})")

    return _embedding_function_cache[cache_key]


def preload_model(
    model_name: Optional[str] = None,
    cache_folder: Optional[str] = None,
    device: str = "cpu",
) -> None:
    """Preload the embedding model to assets/ directory.

    Call this function once at application startup to ensure the model
    is downloaded to the local assets/ directory before any search operations.

    Args:
        model_name: Override the default model name.
        cache_folder: Override the default cache folder (assets/).
        device: Device to run model on ('cpu' or 'cuda').
    """
    config = MempalaceConfig()
    model_name = model_name or config.embedding_model
    cache_folder = cache_folder or config.assets_path

    logger.info(f"Preloading embedding model to {cache_folder}...")

    embedding_fn = get_embedding_function(
        model_name=model_name,
        cache_folder=cache_folder,
        device=device,
    )

    # Force model to load (triggers download if needed)
    _ = embedding_fn.model

    logger.info("Embedding model preloaded successfully")


def get_collection_with_local_embeddings(
    client,
    collection_name: str,
    model_name: Optional[str] = None,
    cache_folder: Optional[str] = None,
    device: str = "cpu",
):
    """Get or create a ChromaDB collection with local embedding function.

    This is a convenience function that combines getting/creating a collection
    with the local embedding function.

    Args:
        client: ChromaDB client instance.
        collection_name: Name of the collection.
        model_name: Override the default model name.
        cache_folder: Override the default cache folder (assets/).
        device: Device to run model on ('cpu' or 'cuda').

    Returns:
        ChromaDB collection with local embeddings.
    """
    embedding_fn = get_embedding_function(
        model_name=model_name,
        cache_folder=cache_folder,
        device=device,
    )

    return client.get_or_create_collection(
        name=collection_name,
        embedding_function=embedding_fn,
    )
