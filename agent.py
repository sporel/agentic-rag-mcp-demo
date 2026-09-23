"""
A minimal RAG agent that talks to the docs-search MCP server (server.py)
over stdio, retrieves relevant knowledge-base passages via the
`search_docs` tool, and answers a question grounded in that context.

This is the piece that mirrors how MCP is used in production: the agent
doesn't hard-code retrieval logic — it discovers and calls tools exposed by
an MCP server, so the same agent works against any MCP-compliant data
source without code changes.

Usage:
    python agent.py "What's the SLA for Gold-layer freshness?"

If OPENAI_API_KEY is set, the retrieved passages are handed to an LLM to
compose a grounded answer. Without a key, the agent falls back to an
extractive answer (the top-ranked passage) so the demo still runs
end-to-end with zero external dependencies.
"""

import asyncio
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def retrieve(question: str) -> list[dict]:
    server_params = StdioServerParameters(command=sys.executable, args=["server.py"])
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("search_docs", {"query": question})
            # FastMCP returns tool results as structured content blocks.
            return result.structuredContent["result"] if result.structuredContent else []


def compose_answer(question: str, passages: list[dict]) -> str:
    if not passages:
        return "I couldn't find anything in the knowledge base relevant to that question."

    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        context = "\n\n".join(f"[{p['source']}] {p['text']}" for p in passages)
        prompt = (
            "Answer the question using only the context below. "
            "Cite the source file in parentheses.\n\n"
            f"Context:\n{context}\n\nQuestion: {question}"
        )
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    # No LLM configured — fall back to a plain extractive answer.
    top = passages[0]
    return f"(extractive fallback, no OPENAI_API_KEY set)\nFrom {top['source']}:\n{top['text']}"


async def main():
    question = " ".join(sys.argv[1:]) or "What's the SLA for Gold-layer freshness?"
    passages = await retrieve(question)
    print(f"Retrieved {len(passages)} passage(s) via MCP search_docs tool:\n")
    for p in passages:
        print(f"  [{p['score']}] {p['source']}")
    print("\n--- Answer ---")
    print(compose_answer(question, passages))


if __name__ == "__main__":
    asyncio.run(main())
