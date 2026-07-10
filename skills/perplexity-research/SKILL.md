---
name: perplexity-research
description: Use Perplexity MCP for current, cited web research. Trigger when the user asks to use Perplexity, asks for deep research, market/vendor/provider research, current comparisons, current API/service capability checks, or wants citation-backed investigation beyond ordinary browsing.
---

# Perplexity Research

Use the Perplexity MCP server for research that benefits from current web search, source synthesis, and citations. Prefer it for vendor/provider comparisons, service capability research, recent API documentation checks, and broad market scans.

## MCP Setup Assumption

The local Codex MCP server is named `perplexity`.

If Perplexity tools are not already exposed, discover them with `tool_search` using a query like `perplexity research`. Expected tools from the MCP server:

- `perplexity_search`: ranked web search results.
- `perplexity_ask`: quick web-grounded answers.
- `perplexity_research`: deeper cited research reports.
- `perplexity_reason`: reasoning-heavy analysis.

If the server fails because `PERPLEXITY_API_KEY` is missing, tell the user to add a real key to `~/.perplexity-mcp.env` and restart Codex/MCP. Do not invent Perplexity results if the MCP is unavailable.

## Tool Choice

- Use `perplexity_research` for comprehensive vendor/provider research, due diligence, competitive comparisons, or questions with high business impact.
  - Deep research can take several minutes. If the current tool surface times out around 300 seconds and does not expose a per-call timeout, treat that as an environment/tooling limit, not a research answer.
  - On deep-research timeout, fall back to `perplexity_reason` with `search_context_size: "high"` for comparative analysis, or `perplexity_ask` with `search_context_size: "high"` for source-grounded factual summaries.
- Use `perplexity_search` first when you need a short source list before deeper investigation.
- Use `perplexity_ask` for narrow factual questions.
- Use `perplexity_reason` when the user asks for strategy, tradeoffs, ranking logic, or decision support after evidence has been gathered.

## Research Standards

- Prefer primary sources: official docs, pricing pages, API references, provider terms, and public product pages.
- Use secondary sources only to fill market context, not as proof of API capability.
- Distinguish confirmed facts from inference.
- Preserve source URLs in the final answer.
- For API/vendor work, verify:
  - supported input identifiers,
  - response objects/fields,
  - whether the provider finds people, relatives, owners, heirs, or only enriches known people,
  - pricing model,
  - API availability,
  - batch versus synchronous mode,
  - fit for the user's actual workflow.

## Output Shape

For vendor/provider research, return:

1. Short conclusion.
2. Ranked options with best use case and caveats.
3. Table of confirmed capabilities.
4. Recommended workflow or waterfall.
5. Open questions to verify with sales/support or API samples.
6. Source links.

Do not overstate "heir" capability. If a provider returns relatives, household members, associates, owners, or enriched person profiles, label that precisely.
