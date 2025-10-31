# Depth Evaluation - Position-Swap Averaging

## Overview

The **Analysis Depth** criterion uses **pairwise comparison** to evaluate how deeply a report analyzes a topic. To mitigate **position bias** (where LLM judges favor reports in certain positions), we implement **position-swap averaging**.

## Position Bias Problem

LLM-as-judge systems can exhibit position bias:
- Reports in "position A" might be favored over "position B" (or vice versa)
- This creates unfair comparisons

## Our Solution: Position-Swap Averaging

### How It Works

For each model's report being evaluated:

1. **Comparison 1**: Compare (Model as A, Reference as B)
   - Model gets `score_A1` on each dimension
   - Reference gets `score_B1` on each dimension

2. **Comparison 2**: Compare (Reference as A, Model as B) — **Positions Swapped**
   - Reference gets `score_A2` on each dimension
   - Model gets `score_B2` on each dimension

3. **Average the scores**:
   - **Model's final score** = average(`score_A1`, `score_B2`)
   - **Reference's final score** = average(`score_B1`, `score_A2`)

4. **Determine winner** based on averaged scores:
   - If difference > 1 point: clear winner
   - If difference ≤ 1 point: tie

### Example

```
Comparison 1 (Model as A, Reference as B):
  Model (A):     Granularity=4, Insight=3, Critique=4, Evidence=4, Density=3 → Total=18
  Reference (B): Granularity=5, Insight=5, Critique=5, Evidence=5, Density=5 → Total=25

Comparison 2 (Reference as A, Model as B) — SWAPPED:
  Reference (A): Granularity=5, Insight=4, Critique=5, Evidence=5, Density=4 → Total=23
  Model (B):     Granularity=3, Insight=3, Critique=3, Evidence=4, Density=3 → Total=16

Final Averaged Scores:
  Model:     avg(18, 16) = 17.0 / 25
  Reference: avg(25, 23) = 24.0 / 25
  
Winner: Reference (B)
```

## Implementation Details

### In Code

```python
# Position-swap is enabled by default in batch grading
result = await grader.compare_depth_async(
    query=query,
    report_a=model_report,
    report_b=reference_report,
    provider="openai",
    model="gpt-5-2025-08-07",
    swap_positions=True  # Enable position-swap averaging (default)
)
```

### Output Fields

The result includes:
- `winner`: "A", "B", or "tie"
- `scores`: Final averaged scores for both reports
- `position_swap_used`: True (indicates swap was performed)
- `raw_comparison_1`: Results from first comparison (A vs B)
- `raw_comparison_2`: Results from second comparison (B vs A)
- `justification`: Combined explanation

### Multi-Provider Averaging

For even more robust evaluation:

1. Run with **GPT-5** → Get position-swap averaged scores
2. Run with **Gemini-2.5-Pro** → Get position-swap averaged scores
3. **Average across providers** → Final score

This gives you:
```
Final Score = avg(
    position_swap_avg(GPT-5 judgments),
    position_swap_avg(Gemini-2.5-Pro judgments)
)
```

## Benefits

✅ **Mitigates position bias**: Each report is judged in both positions
✅ **More robust**: Less susceptible to random LLM quirks
✅ **Fairer comparisons**: Both reports get equal treatment
✅ **Automatic**: Enabled by default in `batch_evaluator.py`

## Usage

### Batch Grading (Automatic)

```bash
# Position-swap is automatically enabled
python main.py \
  --input reports.json \
  --criteria depth \
  --provider openai
```

### Single Comparison (Manual)

```python
from liveresearchbench.graders.pairwise_grader import PairwiseGrader

grader = PairwiseGrader()

result = await grader.compare_depth_async(
    query="Your research query",
    report_a=model_report_content,
    report_b=reference_report_content,
    provider="openai",
    model="gpt-5-2025-08-07",
    swap_positions=True  # Enable position-swap
)

print(f"Winner: {result['winner']}")
print(f"Model score: {result['scores']['A']['total']}/25")
print(f"Reference score: {result['scores']['B']['total']}/25")
```

## Computational Cost

⚠️ **Note**: Position-swap **doubles** the number of API calls for depth evaluation.

- Without swap: 1 comparison per report
- With swap: 2 comparisons per report (default)

This is a worthwhile trade-off for more reliable results.

## References

Position bias in LLM-as-judge evaluations is a known issue in the literature. Our implementation follows best practices for pairwise comparison evaluation.

