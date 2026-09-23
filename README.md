# Agentic RAG over MCP

A minimal but fully working example of a retrieval-augmented agent that talks
to its data source through **MCP (Model Context Protocol)** instead of
hard-coded retrieval logic.

## Why MCP here

In a typical RAG script, the retrieval step is baked directly into the
agent's code. This repo instead splits it into two independent pieces:

- **`server.py`** — an MCP server that exposes one tool, `search_docs`,
  backed by a TF-IDF similarity search over a small local knowledge base
  (`knowledge_base/*.md`).
- **`agent.py`** — an MCP client that connects to that server over stdio,
  discovers and calls `search_docs`, and composes an answer from the
  returned passages.

Because the agent only knows about the MCP tool interface — not the
retrieval implementation — the same `agent.py` would work unmodified against
a completely different `search_docs` implementation (a vector database, an
API, a different corpus) as long as it speaks MCP. That decoupling is the
actual point of the demo, and mirrors how MCP is used to connect LLM agents
to enterprise data sources in production.

## Architecture

```
 agent.py  --(MCP stdio, call_tool "search_docs")-->  server.py
    |                                                      |
    |  question                                    TF-IDF search
    |                                              over knowledge_base/*.md
    |<---------------- ranked passages -------------------|
    |
    v
 compose_answer()
    - OPENAI_API_KEY set  -> LLM answers, grounded in retrieved passages
    - no key              -> extractive fallback (top passage), so the
                              demo runs fully offline with zero external
                              dependencies
```

## Running it

```bash
pip install -r requirements.txt

# Quick retrieval-only smoke test (no MCP transport, no LLM)
python server.py --selftest "What's the SLA for Gold-layer freshness?"

# Full agent flow over the MCP stdio transport
python agent.py "How do I report a data quality issue?"

# With an LLM composing the final answer instead of the extractive fallback
export OPENAI_API_KEY=sk-...
python agent.py "How do I report a data quality issue?"
```

## Knowledge base

`knowledge_base/` contains a handful of synthetic markdown docs (pipeline
architecture, an onboarding FAQ, and a governance policy) standing in for an
internal data-platform wiki — invented for this demo, not sourced from any
employer's real documentation.

## Stack

Python, [`mcp`](https://pypi.org/project/mcp/) (Anthropic's official MCP
SDK, using `FastMCP`), scikit-learn (TF-IDF + cosine similarity), OpenAI API
(optional, for the LLM-composed answer path).
