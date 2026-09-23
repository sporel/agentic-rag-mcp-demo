"""
MCP server exposing a `search_docs` tool over a small local knowledge base.

Retrieval uses a lightweight TF-IDF + cosine similarity search (scikit-learn)
over markdown files in ./knowledge_base — no external services required, so
the demo runs fully offline.

Run standalone for a quick smoke test:
    python server.py --selftest "What's the Gold layer SLA?"

Run as an MCP server (stdio transport), e.g. from Claude Desktop or any
MCP client:
    python server.py
"""

import argparse
import glob
import os

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from mcp.server.fastmcp import FastMCP

KB_DIR = os.path.join(os.path.dirname(__file__), "knowledge_base")

mcp = FastMCP("docs-search")


def _load_chunks():
    """Split each knowledge-base file into paragraph-sized chunks."""
    chunks = []
    for path in sorted(glob.glob(os.path.join(KB_DIR, "*.md"))):
        text = open(path, encoding="utf-8").read()
        for para in text.split("\n\n"):
            para = para.strip()
            if para:
                chunks.append({"source": os.path.basename(path), "text": para})
    return chunks


_CHUNKS = _load_chunks()
_VECTORIZER = TfidfVectorizer(stop_words="english")
_MATRIX = _VECTORIZER.fit_transform([c["text"] for c in _CHUNKS])


def search(query: str, top_k: int = 3):
    query_vec = _VECTORIZER.transform([query])
    scores = cosine_similarity(query_vec, _MATRIX)[0]
    ranked = sorted(zip(scores, _CHUNKS), key=lambda x: x[0], reverse=True)
    results = []
    for score, chunk in ranked[:top_k]:
        if score <= 0:
            continue
        results.append(
            {
                "source": chunk["source"],
                "text": chunk["text"],
                "score": round(float(score), 4),
            }
        )
    return results


@mcp.tool()
def search_docs(query: str) -> list[dict]:
    """Search the internal knowledge base and return the most relevant passages.

    Args:
        query: A natural-language question or keyword search.
    """
    return search(query)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--selftest", help="Run a one-off local query and exit, skipping the MCP transport.")
    args = parser.parse_args()

    if args.selftest:
        for r in search(args.selftest):
            print(f"[{r['score']}] ({r['source']}) {r['text'][:200]}")
    else:
        mcp.run()
