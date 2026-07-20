# ClearGlass Financial Influence Watchdog v2.2

Production-oriented, auditable entity extraction for Ontario and Canadian governance records.

## Guarantees

- Strict Pydantic models with discriminated entity types and forbidden unknown fields.
- OpenAI structured parsing, Anthropic forced tool output, and OpenAI-compatible JSON routing.
- Exact document, prompt, prompt-template, system-prompt, and schema SHA-256 hashes.
- Model/provider identity, attempts, token usage, latency, timestamps, truncation state, and warnings.
- Strict grounding by default: unsupported entities are removed rather than merely down-ranked.
- Production fail-closed behavior. Deterministic fallback requires explicit operator opt-in.
- Dict-style and object-style `Evidence` integration.
- Parallel batch processing that preserves input order.
- Installable command-line agent.

## Install

```bash
pip install -e ".[providers]"
```

Use only the provider extra required by the deployment when minimizing dependencies:

```bash
pip install -e ".[openai]"
pip install -e ".[anthropic]"
```

## Python integration

```python
from intelligence import LLMEntityExtractor, enrich_evidence_with_llm_entities

extractor = LLMEntityExtractor(
    provider="openai",
    model_name="gpt-4o-mini",
    enable_local_fallback=False,
    strict_grounding=True,
)

evidence = enrich_evidence_with_llm_entities(evidence, extractor)
```

## Groq, Ollama, or vLLM

```python
extractor = LLMEntityExtractor(
    provider="compatible",
    model_name="llama-3.3-70b-versatile",
    base_url="https://api.groq.com/openai/v1",
)
```

Environment variables:

- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `GROQ_API_KEY`
- `OPENAI_COMPATIBLE_API_KEY`
- `OPENAI_COMPATIBLE_BASE_URL`

Credentials belong in the runtime secret manager. Never commit them.

## Agent command

```bash
clearglass-watchdog minutes.txt \
  --document-id burlington-2024-03-04 \
  --source-type council_minutes \
  --jurisdiction "Burlington, Ontario" \
  --output extraction.json
```

Production execution fails when the provider fails. `--allow-dev-fallback` exists solely for local development and CI fixtures; output records `fallback_used=true`.

## Validation

```bash
pip install -e ".[providers,dev]"
ruff check intelligence tests/test_entity_extractor.py
pytest tests/test_entity_extractor.py --cov=intelligence --cov-fail-under=75
```
