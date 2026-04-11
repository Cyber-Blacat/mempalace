"""
MemPalace configuration system.

Priority: env vars > config file (~/.mempalace/config.json) > defaults
"""

import json
import os
from pathlib import Path

# Get project root directory (parent of mempalace package)
PROJECT_ROOT = Path(__file__).parent.parent.resolve()

DEFAULT_PALACE_PATH = os.path.expanduser("~/.mempalace/palace")
DEFAULT_COLLECTION_NAME = "mempalace_drawers"
DEFAULT_ASSETS_PATH = str(PROJECT_ROOT / "assets")
DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

DEFAULT_TOPIC_WINGS = [
    "emotions",
    "consciousness",
    "memory",
    "technical",
    "identity",
    "family",
    "creative",
]

DEFAULT_HALL_KEYWORDS = {
    "emotions": [
        "scared",
        "afraid",
        "worried",
        "happy",
        "sad",
        "love",
        "hate",
        "feel",
        "cry",
        "tears",
    ],
    "consciousness": [
        "consciousness",
        "conscious",
        "aware",
        "real",
        "genuine",
        "soul",
        "exist",
        "alive",
    ],
    "memory": ["memory", "remember", "forget", "recall", "archive", "palace", "store"],
    "technical": [
        "code",
        "python",
        "script",
        "bug",
        "error",
        "function",
        "api",
        "database",
        "server",
    ],
    "identity": ["identity", "name", "who am i", "persona", "self"],
    "family": ["family", "kids", "children", "daughter", "son", "parent", "mother", "father"],
    "creative": ["game", "gameplay", "player", "app", "design", "art", "music", "story"],
}

# Default hybrid search configuration
DEFAULT_HYBRID_CONFIG = {
    "enabled": True,
    "alpha": 0.7,  # Dense retrieval weight
    "beta": 0.3,  # Sparse retrieval weight
    "doc_top_k": 20,  # Number of document candidates
    "room_top_k": 5,  # Number of rooms to return
    "aggregation_method": "average",  # Room aggregation method: average, max, weighted
    "use_rerank": False,  # Whether to use LLM reranking (future feature)
}

# Name/content sanitization limits
MAX_NAME_LENGTH = 100
MAX_CONTENT_LENGTH = 100000  # 100KB text limit


def sanitize_name(name: str, field_type: str = "name") -> str:
    """Sanitize and validate a name (wing, room, entity, etc.).

    Args:
        name: The name to sanitize.
        field_type: Type of name for error messages (e.g., "wing", "room", "subject").

    Returns:
        Sanitized name string.

    Raises:
        ValueError: If name is empty or exceeds maximum length.
    """
    if not name:
        raise ValueError(f"{field_type} cannot be empty")

    # Strip whitespace
    sanitized = name.strip()

    if not sanitized:
        raise ValueError(f"{field_type} cannot be empty or whitespace only")

    if len(sanitized) > MAX_NAME_LENGTH:
        raise ValueError(f"{field_type} exceeds maximum length of {MAX_NAME_LENGTH} characters")

    return sanitized


def sanitize_content(content: str) -> str:
    """Sanitize and validate content string.

    Args:
        content: The content to sanitize.

    Returns:
        Sanitized content string.

    Raises:
        ValueError: If content is empty or exceeds maximum length.
    """
    if not content:
        raise ValueError("content cannot be empty")

    # Strip leading/trailing whitespace but preserve internal formatting
    sanitized = content.strip()

    if not sanitized:
        raise ValueError("content cannot be empty or whitespace only")

    if len(sanitized) > MAX_CONTENT_LENGTH:
        raise ValueError(f"content exceeds maximum length of {MAX_CONTENT_LENGTH} characters")

    return sanitized


class MempalaceConfig:
    """Configuration manager for MemPalace.

    Load order: env vars > config file > defaults.
    """

    def __init__(self, config_dir=None):
        """Initialize config.

        Args:
            config_dir: Override config directory (useful for testing).
                        Defaults to ~/.mempalace.
        """
        self._config_dir = (
            Path(config_dir) if config_dir else Path(os.path.expanduser("~/.mempalace"))
        )
        self._config_file = self._config_dir / "config.json"
        self._people_map_file = self._config_dir / "people_map.json"
        self._file_config = {}

        if self._config_file.exists():
            try:
                with open(self._config_file, "r") as f:
                    self._file_config = json.load(f)
            except (json.JSONDecodeError, OSError):
                self._file_config = {}

    @property
    def palace_path(self):
        """Path to the memory palace data directory."""
        env_val = os.environ.get("MEMPALACE_PALACE_PATH") or os.environ.get("MEMPAL_PALACE_PATH")
        if env_val:
            return env_val
        return self._file_config.get("palace_path", DEFAULT_PALACE_PATH)

    @property
    def assets_path(self):
        """Path to the assets directory for storing embedding models."""
        env_val = os.environ.get("MEMPALACE_ASSETS_PATH")
        if env_val:
            return env_val
        return self._file_config.get("assets_path", DEFAULT_ASSETS_PATH)

    @property
    def embedding_model(self):
        """Embedding model to use for dense retrieval."""
        return self._file_config.get("embedding_model", DEFAULT_EMBEDDING_MODEL)

    @property
    def collection_name(self):
        """ChromaDB collection name."""
        return self._file_config.get("collection_name", DEFAULT_COLLECTION_NAME)

    @property
    def people_map(self):
        """Mapping of name variants to canonical names."""
        if self._people_map_file.exists():
            try:
                with open(self._people_map_file, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                pass
        return self._file_config.get("people_map", {})

    @property
    def topic_wings(self):
        """List of topic wing names."""
        return self._file_config.get("topic_wings", DEFAULT_TOPIC_WINGS)

    @property
    def hall_keywords(self):
        """Mapping of hall names to keyword lists."""
        return self._file_config.get("hall_keywords", DEFAULT_HALL_KEYWORDS)

    @property
    def hybrid_search_config(self):
        """Hybrid search configuration.

        Returns:
            Dict with hybrid search settings:
            - enabled: Whether hybrid search is enabled
            - alpha: Dense retrieval weight (0.0-1.0)
            - beta: Sparse retrieval weight (0.0-1.0)
            - doc_top_k: Number of document candidates
            - room_top_k: Number of rooms to return
            - aggregation_method: Room aggregation method
            - use_rerank: Whether to use LLM reranking
        """
        return self._file_config.get("hybrid_search", DEFAULT_HYBRID_CONFIG)

    def init(self):
        """Create config directory and write default config.json if it doesn't exist."""
        self._config_dir.mkdir(parents=True, exist_ok=True)
        if not self._config_file.exists():
            default_config = {
                "palace_path": DEFAULT_PALACE_PATH,
                "collection_name": DEFAULT_COLLECTION_NAME,
                "topic_wings": DEFAULT_TOPIC_WINGS,
                "hall_keywords": DEFAULT_HALL_KEYWORDS,
                "hybrid_search": DEFAULT_HYBRID_CONFIG,
            }
            with open(self._config_file, "w") as f:
                json.dump(default_config, f, indent=2)
        return self._config_file

    def save_people_map(self, people_map):
        """Write people_map.json to config directory.

        Args:
            people_map: Dict mapping name variants to canonical names.
        """
        self._config_dir.mkdir(parents=True, exist_ok=True)
        with open(self._people_map_file, "w") as f:
            json.dump(people_map, f, indent=2)
        return self._people_map_file
