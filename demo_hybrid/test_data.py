"""
test_data.py — Test data for hybrid room routing demo.

Provides realistic document collections organized by wings and rooms
to demonstrate the hybrid room routing concept.
"""

# Test documents representing realistic MemPalace content
TEST_DOCUMENTS = [
    # Database room (3 documents)
    "The team decided to migrate from MySQL to PostgreSQL for better JSON support. "
    "PostgreSQL's JSONB type allows us to store and query nested data structures efficiently. "
    "The migration will start in Q2 2026.",
    "We discussed using Alembic for database migrations during the sprint planning. "
    "Alembic provides version control for our database schema and handles rollback gracefully. "
    "All developers need to familiarize themselves with the Alembic CLI commands.",
    "Database backup strategy includes daily snapshots and weekly full backups. "
    "We'll use AWS RDS automated backups for production and pg_dump for development environments. "
    "Backup retention policy is 30 days for daily and 90 days for weekly backups.",
    # Auth room (2 documents)
    "The authentication system uses JWT tokens with 24-hour expiration. "
    "We're implementing refresh tokens stored in HttpOnly cookies to maintain session continuity. "
    "The auth flow follows OAuth 2.0 best practices.",
    "We need to add rate limiting to the authentication endpoints. "
    "Proposed: 100 requests per minute per IP address for login attempts. "
    "This prevents brute force attacks while allowing legitimate retry attempts.",
    # Frontend room (2 documents)
    "Frontend development uses React with TypeScript and Tailwind CSS. "
    "The component library is built on Radix UI primitives for accessibility. "
    "State management is handled by TanStack Query for server state and Zustand for client state.",
    "The frontend team agreed to use Storybook for component documentation. "
    "Each component should have at least 3 stories: default, interactive, and edge cases. "
    "Storybook deployment will be integrated into our CI/CD pipeline.",
    # API room (2 documents)
    "REST API endpoints follow OpenAPI 3.0 specification. "
    "All endpoints return JSON with consistent error structure: {error, message, details}. "
    "API versioning uses URL path prefix: /api/v1/, /api/v2/",
    "GraphQL API is available for complex queries that span multiple resources. "
    "The schema is defined using Nexus schema builder. "
    "Subscriptions are implemented via WebSocket for real-time updates.",
    # Deployment room (2 documents)
    "Deployment pipeline uses GitHub Actions with staging and production environments. "
    "Staging deploys on every PR merge, production requires manual approval. "
    "Rollback procedure: revert commit and redeploy within 5 minutes.",
    "We're migrating to Kubernetes for container orchestration. "
    "Helm charts manage deployments with environment-specific values files. "
    "Kubernetes provides better scaling and self-healing capabilities compared to Docker Compose.",
    # Testing room (2 documents)
    "Unit tests use pytest with 80% coverage minimum requirement. "
    "Integration tests run against a test database seeded with fixtures. "
    "E2E tests use Playwright for browser automation and run nightly.",
    "Performance testing revealed database queries as the bottleneck. "
    "Added indexes on frequently queried columns improved response time by 40%. "
    "Connection pooling via pgbouncer handles concurrent requests efficiently.",
]

# Metadata for each document
TEST_METADATAS = [
    # Database room
    {"wing": "project", "room": "database", "source": "meeting_notes.md", "date": "2026-01-15"},
    {"wing": "project", "room": "database", "source": "sprint_plan.md", "date": "2026-01-20"},
    {"wing": "project", "room": "database", "source": "ops_guide.md", "date": "2026-01-25"},
    # Auth room
    {"wing": "project", "room": "auth", "source": "auth_design.md", "date": "2026-02-01"},
    {"wing": "project", "room": "auth", "source": "security_review.md", "date": "2026-02-05"},
    # Frontend room
    {"wing": "project", "room": "frontend", "source": "tech_stack.md", "date": "2026-02-10"},
    {"wing": "project", "room": "frontend", "source": "component_guide.md", "date": "2026-02-15"},
    # API room
    {"wing": "project", "room": "api", "source": "api_spec.md", "date": "2026-02-20"},
    {"wing": "project", "room": "api", "source": "graphql_design.md", "date": "2026-02-25"},
    # Deployment room
    {"wing": "project", "room": "deployment", "source": "ci_cd.md", "date": "2026-03-01"},
    {"wing": "project", "room": "deployment", "source": "k8s_plan.md", "date": "2026-03-05"},
    # Testing room
    {"wing": "project", "room": "testing", "source": "test_strategy.md", "date": "2026-03-10"},
    {"wing": "project", "room": "testing", "source": "perf_results.md", "date": "2026-03-15"},
]

# Test queries to demonstrate different retrieval patterns
TEST_QUERIES = [
    {
        "query": "database migration strategy",
        "description": "Keyword-heavy query: specific terms 'database' and 'migration'",
        "expected_rooms": ["database"],
        "type": "keyword_heavy",
    },
    {
        "query": "how do we handle user authentication",
        "description": "Semantic query: 'handle user authentication' semantically matches auth documents",
        "expected_rooms": ["auth"],
        "type": "semantic_heavy",
    },
    {
        "query": "JWT tokens and OAuth",
        "description": "Mixed query: both keywords (JWT, OAuth) and semantic concept",
        "expected_rooms": ["auth"],
        "type": "mixed",
    },
    {
        "query": "frontend component library",
        "description": "Specific technical terms: should match frontend room",
        "expected_rooms": ["frontend"],
        "type": "keyword_heavy",
    },
    {
        "query": "deploying to production environment",
        "description": "Semantic query about deployment process",
        "expected_rooms": ["deployment"],
        "type": "semantic_heavy",
    },
    {
        "query": "testing and coverage requirements",
        "description": "Mixed query with specific terms",
        "expected_rooms": ["testing"],
        "type": "mixed",
    },
    {
        "query": "API versioning and REST endpoints",
        "description": "Technical query with specific API terms",
        "expected_rooms": ["api"],
        "type": "keyword_heavy",
    },
    {
        "query": "improving application performance",
        "description": "Broad semantic query: could match testing (performance results) or database (optimization)",
        "expected_rooms": ["testing", "database"],
        "type": "semantic_heavy",
    },
]

# Statistics about the test data
TEST_DATA_STATS = {
    "total_documents": len(TEST_DOCUMENTS),
    "total_rooms": len(set(m["room"] for m in TEST_METADATAS)),
    "rooms": {
        "database": 3,
        "auth": 2,
        "frontend": 2,
        "api": 2,
        "deployment": 2,
        "testing": 2,
    },
    "wing": "project",
}


def get_test_data():
    """Get test documents and metadatas.

    Returns:
        Tuple of (documents, metadatas, queries, stats)
    """
    return TEST_DOCUMENTS, TEST_METADATAS, TEST_QUERIES, TEST_DATA_STATS


def print_data_summary():
    """Print summary of test data."""
    print("\nTest Data Summary")
    print("=" * 60)
    print(f"Total Documents: {TEST_DATA_STATS['total_documents']}")
    print(f"Total Rooms: {TEST_DATA_STATS['total_rooms']}")
    print(f"Wing: {TEST_DATA_STATS['wing']}")
    print("\nRoom Distribution:")

    for room, count in TEST_DATA_STATS["rooms"].items():
        print(f"  {room:15s}: {count} documents")

    print(f"\nTotal Queries: {len(TEST_QUERIES)}")
    print("\nQuery Types:")

    type_counts = {}
    for q in TEST_QUERIES:
        q_type = q["type"]
        type_counts[q_type] = type_counts.get(q_type, 0) + 1

    for q_type, count in sorted(type_counts.items()):
        print(f"  {q_type:15s}: {count} queries")


if __name__ == "__main__":
    print_data_summary()

    print("\n" + "=" * 60)
    print("Sample Documents:")
    print("-" * 60)

    # Show a few sample documents
    for i in [0, 3, 5]:  # database, auth, frontend
        doc = TEST_DOCUMENTS[i]
        meta = TEST_METADATAS[i]
        print(f"\n[{i}] Room: {meta['room']}")
        print(f"    Source: {meta['source']}")
        print(f"    Text: {doc[:120]}...")
