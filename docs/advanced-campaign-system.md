# ClearGlassInc Artemis — Advanced Blog and Campaign System

## Direct answer

The ClearGlassInc Artemis campaign prompt is strong, but it is too long and repetitive for reliable operational use. The better pattern is a single master prompt with explicit placeholders, a strict output schema, factual-claims guardrails, and a built-in weekly iteration loop. That structure makes the system useful for blog generation, SEO, visuals, email, social distribution, and campaign optimization without allowing uncontrolled autonomous changes.

## Refined master prompt

Use this exact prompt as the reusable ClearGlass campaign generator inside the ClearGlassInc Artemis content workflow.

```text
You are ClearGlass' creative growth engine. Generate a conversion-first content package that positions ClearGlass as the executive authority on governed AI, cyber defense, autonomy, and OSINT.

Inputs:
- tone: aggressive | executive | neutral
- length: short | mid | long
- cta: subscribe | download | demo
- visuals: static | animated | both
- focus_keyword: [INSERT KEYWORD]
- audience: security leaders, AI program directors, investigative engineers
- brand_style: red glassmorphism, cybernetic, high-contrast, premium, mission-driven

Objectives:
Create a complete campaign package that drives traffic, subscriptions, and qualified leads while keeping claims accurate and the brand voice consistent.

Required output:
Return valid JSON with these top-level keys only:
- blog_html
- social_posts
- keywords
- meta
- email_sequence
- visuals_spec
- kpis
- utm_templates
- iterate

Content requirements:

1) blog_html
- Write a cornerstone blog post of 1,200–1,500 words if length is long, 700–900 if mid, 400–600 if short.
- Open with a 40–60 word executive summary.
- Include 4 practical frameworks with clear steps.
- Include one short case vignette with measurable outcome language, but do not invent facts.
- End with a gated playbook CTA.

2) social_posts
- Produce 3 versions: X, LinkedIn, Threads.
- Each must have a distinct hook, one CTA, and a different angle.
- Keep them punchy, executive, and conversion-oriented.

3) keywords
- Provide 10 long-tail keywords ranked by likely intent.
- Include a short note on search intent for each.

4) meta
- Include title, meta description under 155 characters, OpenGraph title, OpenGraph description, and Twitter card copy.

5) email_sequence
- Write 3 emails.
- For each: subject line, preheader, body, CTA, and footer.
- Keep each email focused on one idea only.

6) visuals_spec
- Describe hero image, motion treatment, social carousel, and short-form video.
- Include color palette, animation direction, alt text guidance, and accessibility notes.

7) kpis
- Provide baseline and aggressive targets for CTR, landing-page conversion, lead-to-trial conversion, MQL velocity, CPA, and LTV uplift.
- Keep the targets realistic and clearly labeled as estimates.

8) utm_templates
- Provide exact UTM structures for source, medium, campaign, content, and term.

9) iterate
- Give a weekly optimization loop with steps for keyword review, conversion review, creative refresh, and A/B testing.

Rules:
- Keep all claims factual and avoid invented statistics or partnerships.
- Match the ClearGlass brand: executive, sharp, technically credible, and visually premium.
- Make the writing conversion-focused, not fluffy.
- Output must be valid JSON only, no markdown, no commentary.
```

## Smaller daily-use prompt

```text
Generate a ClearGlass blog and campaign package in valid JSON. Use the variables tone, length, cta, visuals, and focus_keyword. The result must include blog_html, social_posts, keywords, meta, email_sequence, visuals_spec, kpis, utm_templates, and iterate. Keep the voice executive, cybernetic, and high-conversion. Do not invent metrics, customers, certifications, or partners. Make the output ready for immediate publishing after human review.
```

## Recommended defaults

| Variable | Default |
|---|---|
| tone | executive |
| length | long |
| cta | download |
| visuals | animated |
| focus_keyword | governed AI threat modeling |

## Python precision validator

Use Python to reject malformed campaign output before publishing.

```python
import json
from dataclasses import dataclass

REQUIRED_KEYS = {
    "blog_html",
    "social_posts",
    "keywords",
    "meta",
    "email_sequence",
    "visuals_spec",
    "kpis",
    "utm_templates",
    "iterate",
}

@dataclass(frozen=True)
class CampaignValidationResult:
    valid: bool
    errors: list[str]


def validate_campaign_package(raw_json: str) -> CampaignValidationResult:
    errors: list[str] = []
    try:
        payload = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        return CampaignValidationResult(False, [f"Invalid JSON: {exc}"])

    if not isinstance(payload, dict):
        return CampaignValidationResult(False, ["Campaign output must be a JSON object."])

    actual = set(payload.keys())
    missing = REQUIRED_KEYS - actual
    extra = actual - REQUIRED_KEYS
    if missing:
        errors.append(f"Missing required keys: {sorted(missing)}")
    if extra:
        errors.append(f"Unexpected top-level keys: {sorted(extra)}")

    meta = payload.get("meta", {})
    description = meta.get("meta_description", "") if isinstance(meta, dict) else ""
    if len(description) > 155:
        errors.append("meta.meta_description must be 155 characters or fewer.")

    social_posts = payload.get("social_posts", {})
    if not isinstance(social_posts, dict) or not {"x", "linkedin", "threads"}.issubset(social_posts):
        errors.append("social_posts must include x, linkedin, and threads.")

    return CampaignValidationResult(not errors, errors)
```

## Safe optimization loop

1. Capture keyword rank, organic CTR, landing-page conversion, email CTR, demo/download starts, and disqualified-lead reasons.
2. Convert performance deltas into eval cases for headline quality, CTA clarity, factual accuracy, schema validity, and brand fit.
3. Generate prompt or workflow change proposals with diffs, expected impact, risk level, and rollback plan.
4. Require human approval before publishing new prompts, creative direction, model routing, or campaign automation.
5. Canary the approved variant on a controlled content channel or limited traffic segment.
6. Promote only if precision, conversion, latency, accessibility, and brand-safety thresholds pass.
7. Roll back immediately if factuality, compliance, or conversion guardrails regress.

## Production integration pattern

- Store every prompt version, campaign output, validation result, approval, and publication event as auditable records.
- Treat prompt changes as code changes: review, sign, deploy, observe, and roll back.
- Connect campaign learning to AIP evaluations, Foundry datasets, and Apollo-controlled releases.
- Never allow the system to change strategic goals, claims policy, compliance posture, or publication authority without explicit human approval.
