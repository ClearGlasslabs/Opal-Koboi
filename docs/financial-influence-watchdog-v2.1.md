# ClearGlass Financial Influence Watchdog v2.1

Production-oriented, auditable entity extraction for Ontario and Canadian governance records.

## Install

```bash
pip install "pydantic>=2.7" "openai>=1.40" pytest
# Optional Anthropic provider
pip install "anthropic>=0.34"
```

## Usage

```python
from intelligence import LLMEntityExtractor, enrich_evidence_with_llm_entities

extractor = LLMEntityExtractor(
    model_name="gpt-4o-mini",
    provider="openai",
    enable_local_fallback=False,
)

evidence = enrich_evidence_with_llm_entities(evidence, extractor)
```

Set `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` in the runtime secret manager. Never commit credentials.
For Groq, Ollama, or vLLM, use `provider="compatible"`, provide `base_url`, and select an OpenAI-compatible model.

## Audit guarantees

Each extraction records the provider, model, prompt version, SHA-256 prompt hashes, token usage, latency, timestamp, document metadata, validation warnings, and whether deterministic fallback was used. Every entity carries confidence and a verbatim context snippet.

## Production policy

Keep `enable_local_fallback=False` in production. The fallback is deterministic development scaffolding, not an LLM replacement. Failed provider calls must fail closed unless an operator intentionally enables fallback.

## Test

```bash
pytest -q tests/test_entity_extractor.py
```
