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
from typing import List, Optional, Union, Dict, Any

from chromadb.api.types import Space

from .config import MempalaceConfig

logger = logging.getLogger("mempalace_mcp")

# Global model cache to avoid reloading
_model_cache = {}
_embedding_function_cache = {}


class LocalEmbeddingFunction:
    """Custom embedding function that loads models from local assets/ directory.

    This avoids using system cache directories like ~/.cache/huggingface/
    by explicitly specifying the cache_folder to the assets/ directory.

    Implements ChromaDB 1.x EmbeddingFunction protocol.
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

    # ==================== ChromaDB 1.x EmbeddingFunction Protocol ====================

    @staticmethod
    def name() -> str:
        """Return the name of this embedding function for ChromaDB API.

        This is a static method as required by ChromaDB 1.x protocol.
        """
        return "local_sentence_transformers"

    @staticmethod
    def is_legacy() -> bool:
        """Return False to indicate this is a modern embedding function."""
        return False

    @staticmethod
    def default_space() -> Space:
        """Return the default space for this embedding function."""
        return "cosine"

    @staticmethod
    def supported_spaces() -> List[Space]:
        """Return the list of supported spaces for this embedding function."""
        return ["cosine", "l2", "ip"]

    def embed_query(self, input: Union[str, List[str]]) -> List[List[float]]:
        """Embed query texts.

        Args:
            input: The query string or list of strings to embed.

        Returns:
            List of embedding vectors.
        """
        if isinstance(input, str):
            return [self._embed_single(input)]
        return [self._embed_single(text) for text in input]

    def _embed_single(self, text: str) -> List[float]:
        """Embed a single text string.

        Args:
            text: The text string to embed.

        Returns:
            List of floats representing the embedding.
        """
        embeddings = self.model.encode(
            [text],
            normalize_embeddings=self.normalize_embeddings,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        return embeddings[0].tolist()

    def embed_with_retries(
        self,
        texts: List[str],
        attempt: int = 0,
        max_attempts: int = 3,
        **kwargs: Any,
    ) -> List[List[float]]:
        """Embed texts with retry logic.

        Args:
            texts: List of texts to embed.
            attempt: Current attempt number.
            max_attempts: Maximum number of retry attempts.
            **kwargs: Additional arguments.

        Returns:
            List of embedding vectors.
        """
        try:
            return self(texts)
        except Exception as e:
            if attempt >= max_attempts - 1:
                raise e
            logger.warning(f"Embedding attempt {attempt + 1} failed, retrying: {e}")
            return self.embed_with_retries(texts, attempt + 1, max_attempts, **kwargs)

    def get_config(self) -> Dict[str, Any]:
        """Return the configuration for this embedding function.

        Used for serialization and persistence.
        """
        return {
            "type": "local_sentence_transformers",
            "model_name": self.model_name,
            "cache_folder": self.cache_folder,
            "device": self.device,
            "normalize_embeddings": self.normalize_embeddings,
        }

    @staticmethod
    def build_from_config(config: Dict[str, Any]) -> "LocalEmbeddingFunction":
        """Build an embedding function from a configuration dict.

        Args:
            config: Configuration dictionary.

        Returns:
            A new LocalEmbeddingFunction instance.
        """
        return LocalEmbeddingFunction(
            model_name=config.get("model_name", "sentence-transformers/all-MiniLM-L6-v2"),
            cache_folder=config.get("cache_folder"),
            device=config.get("device", "cpu"),
            normalize_embeddings=config.get("normalize_embeddings", True),
        )

    @staticmethod
    def validate_config(config: Dict[str, Any], strict: bool = False) -> None:
        """Validate the configuration.

        Args:
            config: Configuration dictionary to validate.
            strict: Whether to enforce strict validation.

        Raises:
            ValueError: If the configuration is invalid.
        """
        required_keys = ["type", "model_name"]
        for key in required_keys:
            if key not in config:
                if strict:
                    raise ValueError(f"Missing required config key: {key}")
                else:
                    logger.warning(f"Missing config key: {key}")

    def validate_config_update(
        self,
        old_config: Dict[str, Any],
        new_config: Dict[str, Any],
        strict: bool = False,
    ) -> None:
        """Validate a configuration update.

        Args:
            old_config: Old configuration dictionary.
            new_config: New configuration dictionary.
            strict: Whether to enforce strict validation.
        """
        # For now, we allow any updates
        pass

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

    # Use provided values or fall back to config (ensure non-None)
    effective_model_name = model_name if model_name is not None else config.embedding_model
    effective_cache_folder = cache_folder if cache_folder is not None else config.assets_path

    # Create cache key
    cache_key = f"{effective_model_name}:{effective_cache_folder}:{device}"

    # Return cached instance if available
    if cache_key not in _embedding_function_cache:
        logger.info(f"Creating new embedding function (cache key: {cache_key})")
        _embedding_function_cache[cache_key] = LocalEmbeddingFunction(
            model_name=effective_model_name,
            cache_folder=effective_cache_folder,
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
    effective_model_name = model_name if model_name is not None else config.embedding_model
    effective_cache_folder = cache_folder if cache_folder is not None else config.assets_path

    logger.info(f"Preloading embedding model to {effective_cache_folder}...")

    embedding_fn = get_embedding_function(
        model_name=effective_model_name,
        cache_folder=effective_cache_folder,
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
