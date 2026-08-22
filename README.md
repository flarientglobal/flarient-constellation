# Flarient Constellation

The GitHub-native distribution network for Flarient space-weather intelligence.

## Architecture

~~~
NASA / NOAA / ESA / USGS  ->  Event Engine  ->  State Change Detector
                                          |
                                Event Significance Engine
                                          |
                                Viral Information Score
                                          |
                                Distribution Compiler
                                          |
                  GitHub Pages - Badges - Event Ledger - RSS
                                          |
                                Flarient (deep links back)
~~~

## Zero-Cost Operating Principle

This system runs entirely on GitHub Actions, GitHub Pages, and GitHub Releases.
It fetches upstream data (NOAA SWPC, NASA NeoWS) directly from public APIs.
AI enhancement uses external free providers (Groq, Cloudflare Workers AI) with
deterministic template fallback. If all AI providers are unavailable, the system
publishes template-based content rather than failing.

**All automated processes run entirely on GitHub Actions — no external paid services.**

## Cost Classification

Every workflow carries cost metadata:

| Field | Value |
|-------|-------|
| cost_classification | ZERO |
| external_credit_dependency | false |
| external_paid_dependency | false |
| fallback_available | true |

If a dependency stops being free, the adapter disables itself without disrupting the core.

## Canonical Event Object

All significant changes become structured JSON objects (event_schema.json).
Events are stored in the public event ledger:

~~~
events/year/month/day/event-id/event.json
events/year/month/day/event-id/observations.json
events/year/month/day/event-id/forecasts.json
events/year/month/day/event-id/outcome.json
~~~

## Viral Information Score (VIS)

| VIS Range | Distribution Level |
|-----------|-------------------|
| 0-29 | No distribution |
| 30-49 | Update badges only |
| 50-69 | Short explanation + limited distribution |
| 70-84 | Social content + cards + event updates |
| 85-94 | Full distribution package |
| 95-100 | Breaking Space Weather package |

Weights are configurable in config/vis_weights.json.

## Badge Network

Dynamic SVG badges are generated in docs/badges/ and served via GitHub Pages:

- latest/kp.svg — current Kp index
- latest/aurora.svg — aurora potential
- latest/flare.svg — latest flare class
- latest/storm.svg — geomagnetic storm level
- latest/solarwind.svg — solar wind speed
- latest/bz.svg — Bz magnetic field
- latest/neo.svg — near-Earth object count
- latest/space-weather.svg — overall space environment

Badges are regenerated only when values change.

## AI Router

The AI router tries providers in order:
1. Deterministic templates (always available)
2. Groq free tier (if GROQ_API_KEY is set)
3. Cloudflare Workers AI (if CLOUDFLARE_API_TOKEN is set)

If all AI providers fail, templates are used. Publishing never fails due to AI unavailability.

## Configuration

All thresholds and weights are in config/ and editable via pull requests:
- significance_thresholds.json — what constitutes a significant event
- vis_weights.json — Viral Information Score component weights
- cost_classification.json — cost state metadata
- ai_providers.json — AI router provider configuration

## Schedule

The main workflow runs every 30 minutes. Most runs detect no changes and exit immediately.

## Deep Links

Every generated asset deep-links to the relevant Flarient experience:
- Badges -> https://flarient.com (specific page per badge type)
- Event pages -> https://flarient.com/space-events/{slug}
- Forecast markets -> https://flarient.com/market/{slug}

## License

MIT