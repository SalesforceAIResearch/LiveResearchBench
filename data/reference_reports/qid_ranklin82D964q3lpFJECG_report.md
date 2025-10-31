# Top Robotic Vacuums as of Sep 16, 2025 — Data Requirements, Method, and Gaps

## Executive Summary
The research brief requires ranking the top 12 robot vacuum cleaners available for purchase (as of Sep 16, 2025) using an aggregate score that equally weights three metrics: suction power (Pa), battery runtime (minutes), and Consumer Reports (CR) overall score from 2023–2024 testing. Each metric must be verifiable with a direct URL, and availability must be confirmed on official manufacturer stores or major authorized U.S. retailers.

This deliverable cannot be completed to spec with the current research record because:
- No external sources were collected in the research phase.
- Consumer Reports overall scores are typically behind a member paywall; no member-access data was provided.
- The brief prohibits including models without all three metrics verified via URLs.

Below is a complete methodology, data schema, normalization and scoring formulas, and a ready-to-fill structure to finalize the ranking as soon as URLs and score numbers are supplied. It also details the most common inclusion/exclusion pitfalls and how to handle borderline cases (e.g., iRobot models lacking Pa specs).

## Scope and Eligibility Rules
- Include only robot vacuums (with or without mop) that Consumer Reports classifies and scores as robot vacuums.
- The exact model/variant must match across:
  - Consumer Reports model page (with 2023–2024 test score),
  - Manufacturer specs page (suction in Pa and runtime in minutes),
  - Availability page (manufacturer store or authorized U.S. retailer).
- Exclude models missing any of the three metrics or unverifiable via direct URLs. List excluded models separately with reasons and citations.

## Required Evidence for Each Included Model
- Suction pressure (Pa): Product page or spec sheet URL, with the exact figure and mode context.
- Battery runtime (minutes): Product page or spec sheet URL; prefer “standard/auto” mode; clearly state mode context.
- Consumer Reports overall score: Direct CR model page URL showing the overall score and test year (2023 or 2024). Note: Access may require CR membership.
- Availability verification: Direct buy page link (manufacturer or authorized U.S. retailer), with “Accessed Sep 16, 2025” noted.

## Normalization and Scoring
- For N included models, compute min–max normalization to 0–100 within the cohort for suction and runtime:
  - suction_norm = 100 × (Pa_i − Pa_min) / (Pa_max − Pa_min)
  - runtime_norm = 100 × (min_i − min_min) / (min_max − min_min)
- Normalize CR score to 0–100 if CR uses a 0–100 scale:
  - If CR overall score is already 0–100, use CR_norm = CR_i (no rescale).
  - If CR used a different scale (rare), apply min–max as above across included models.
- Aggregate score (equal weights):
  - aggregate = (suction_norm + runtime_norm + CR_norm) / 3
- Handle ties by assigning the same rank number to tied models; then skip the next rank number accordingly.

## Data Table Template (Fill for Each Included Model)
- Exact model name/number (matching CR)
- Suction (Pa) + URL + mode context
- Runtime (minutes) + URL + mode context
- Consumer Reports overall score + test year + CR URL (member access may be required)
- Availability URL (manufacturer or authorized U.S. retailer) + “Accessed Sep 16, 2025”
- Normalized suction, runtime, CR score
- Aggregate score
- Notes (variant equivalency, if applicable and cited)

## Candidate Models Likely to Meet Evidence Requirements (Pending URL and Score Verification)
Note: The following are examples of models and families that typically publish Pa and runtime and that Consumer Reports has covered in recent years. Do not include any in the ranking until exact model, Pa, runtime, and CR 2023–2024 score URLs are confirmed. Model naming must exactly match CR.

- Roborock: S8 MaxV Ultra, S8 Pro Ultra, S8+, Q Revo, Q8 Max, Q5+. Roborock typically publishes Pa and runtimes. Confirm CR model pages and exact variants.
- Ecovacs: Deebot X2 Omni, T30 Omni, T20 Omni, N10+. Ecovacs typically publishes Pa and runtimes. Confirm CR classification as robot vacuum (not mop-only) and 2023–2024 test pages.
- Dreame (Dreametech): L20 Ultra, L10s Ultra, L10s Pro. Dreame typically publishes Pa and runtime; confirm CR pages for exact U.S. variants tested in 2023–2024.
- Eufy (Anker): X9 Pro, X8 Pro, G30/G40 series. Eufy usually publishes Pa and runtime. Confirm exact CR pages and years.
- Yeedi: vac 2 pro, vac station, Cube (mop-vac). Yeedi typically publishes Pa/runtime; verify CR coverage and classification.
- TP-Link Tapo: RV30, RV30 Plus. TP-Link publishes Pa/runtime; verify CR pages and years.
- Shark: AI Ultra/Matrix. Shark often does not publish Pa in Pascals; if Pa not verifiable from a primary source or credible lab measure, these models must be excluded.
- iRobot Roomba: j7/j9/s9/i7/i5 families. iRobot does not publish suction in Pascals; unless a credible lab Pa measurement with methodology is available and cited, these models will be excluded under the “Pa required” rule.

## Common Exclusions and Rationale
Anticipate excluding the following unless Pa in Pascals is verified via an authoritative source and the exact tested variant matches CR:
- iRobot Roomba models (e.g., j7+, j9+, s9+): iRobot typically does not publish suction in Pa; many third-party numbers are unverified. Without a primary spec or credible lab Pa measurement, exclude.
- Shark robot vacuums: Often do not publish Pa; they may use relative claims (e.g., “X times suction”). Exclude unless an authoritative Pa source is provided for the exact CR-tested variant.
- Dyson 360 Vis Nav or Omni-glide robots: Dyson tends to publish Air Watts, not Pascals; exclude unless a reliable Pa measurement is available and mapped to the exact CR variant.
- Samsung Jet Bot series: Often publish power consumption, not Pa; exclude unless Pa is verified for the exact model.
- Neato Robotics (D8/D9/D10): Company ceased operations; CR may have older coverage; verify 2023–2024 test pages and Pa specs if any. Likely exclude for Pa gaps and/or availability constraints.

For each excluded model, record:
- Exact model name
- Missing metric(s)
- Reason and citations (e.g., manufacturer specs page shows no Pa; CR page not from 2023–2024; unavailable for purchase as of Sep 16, 2025)

## Availability Verification (U.S. Market)
- Acceptable: Manufacturer’s U.S. store page, or major authorized U.S. retailers (e.g., Amazon listing “Ships from and sold by [Brand]” or Amazon’s official brand store, Best Buy, Walmart).
- Not acceptable: Marketplace resellers without brand authorization, overseas-only variants, or discontinued pages without a purchase option.
- Record the availability URL and “Accessed Sep 16, 2025.”

## Calculation Walkthrough (Worked Example Template)
After collecting the dataset for all included models:

1) Gather raw metrics:
- Roborock S8 Pro Ultra — Pa: 6000; Runtime: 180 min; CR: 82 (2023)
- Ecovacs Deebot T20 Omni — Pa: 6000; Runtime: 170 min; CR: 79 (2024)
- Dreame L20 Ultra — Pa: 7000; Runtime: 180 min; CR: 80 (2024)
- … (at least 12 total with URLs)

2) Compute min–max bounds across included models:
- Pa_min, Pa_max
- min_min, min_max
- CR_min, CR_max (if not already on 0–100 scale; otherwise CR_norm=CR)

3) Normalize per model:
- suction_norm = 100 × (Pa_i − Pa_min) / (Pa_max − Pa_min)
- runtime_norm = 100 × (min_i − min_min) / (min_max − min_min)
- CR_norm = CR_i (if 0–100)

4) Aggregate and rank:
- aggregate = (suction_norm + runtime_norm + CR_norm)/3
- Sort descending; assign ties to shared ranks.

5) Publish:
- A Top 12 table with: model, Pa (+URL), runtime (+URL), CR score/year (+URL), normalized values, aggregate score, availability URL w/ accessed date.
- An Appendix with the full dataset and calculations.

## Handling Variant Mismatches and Bundles
- Only include the exact variant CR tested. If CR tested “Roborock S8 Pro Ultra” and the manufacturer’s page/specs apply equally across a “bundle” (e.g., added bags or extra mop pads), include only if the manufacturer explicitly states the core robot hardware and performance specs are identical across the bundle and base model. Cite that statement.
- If the U.S. availability uses a retailer-exclusive SKU (e.g., a “.01” suffix) but the core unit is functionally identical, cite a primary source that confirms identical suction and runtime.

## Deliverables Checklist (What remains to finalize)
To produce the final ranked Top 12 list to spec:
- For each included model:
  - URL with suction in Pa for the exact variant.
  - URL with runtime (mode context) for the exact variant.
  - CR model page URL that shows the overall score and Tested 2023–2024. Member access may be required; supply score and year.
  - Availability URL (manufacturer or authorized U.S. retailer), accessed Sep 16, 2025.
- After URLs are provided/validated, the normalized scores and final ranking will be calculated and published with all citations.

## Appendix A — Template Top 12 Output (Fill Once Data Are Verified)
For each row:
- Rank
- Model (exact)
- Suction (Pa) [URL]
- Runtime (min) [URL]
- CR overall score, Tested [Year] [CR URL]
- suction_norm / runtime_norm / CR_norm
- Aggregate score
- Availability URL (Accessed Sep 16, 2025)
- Notes

Example row format (illustrative only; do not use without verified URLs and values):
- 1 — Dreame L20 Ultra — 7000 Pa [link] — 180 min (Auto) [link] — CR 80, Tested 2024 [CR link] — 100 / 100 / 80 — 93.3 — [availability link] (Accessed Sep 16, 2025) — U.S. model confirmed identical to CR-tested variant [link]

## Appendix B — Excluded Models (Examples of Common Reasons)
- iRobot Roomba j9+ — Excluded: suction in Pascals not published by manufacturer; no authoritative Pa lab measurement found; cannot satisfy “Pa with URL” requirement.
- Shark AI Ultra — Excluded: manufacturer does not publish suction in Pascals for this exact model; third-party claims lack methodology; cannot satisfy “Pa with URL.”
- Samsung Jet Bot AI+ — Excluded: no Pa spec published on manufacturer page; cannot verify “Pa with URL.”
For each excluded model in the final report, include exact model, reason, and citations to the pages that fail to provide the required metric.

## Next Steps
- Provide Consumer Reports member-accessible overall score numbers and “Tested in 2023/2024” for the exact model pages (direct URLs).
- Provide Pa and runtime spec URLs for the exact variants.
- Provide availability URLs for U.S. purchase as of Sep 16, 2025.
- Once supplied, the final Top 12 ranking, normalized values, aggregate scores, and complete citations will be produced immediately.

### Sources
[1] No sources were captured during the research phase. To complete the deliverable, direct URLs are required for: (a) suction Pa and runtime specs per model, (b) Consumer Reports model pages showing the 2023–2024 overall score, and (c) live U.S. availability pages (manufacturer or authorized retailers) accessed on Sep 16, 2025.