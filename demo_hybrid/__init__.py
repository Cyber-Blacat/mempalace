"""
demo_hybrid — Demonstration of hybrid room routing.

This demo showcases the hybrid room routing concept:
1. Dense retrieval (semantic embeddings)
2. Sparse retrieval (BM25 keyword matching)
3. Score fusion (α * dense + β * sparse)
4. Room-level aggregation

Run the demo:
    python demo_hybrid/main.py
"""

__version__ = "0.1.0"
