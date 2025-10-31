# Multi-Provider Evaluation Guide

## Overview

The `run_multi_provider_evaluation.py` script provides a robust, production-ready solution for evaluating research reports with multiple LLM judges (e.g., GPT-5 and Gemini), with automatic state tracking and resume capability.

## Features

✅ **Automatic State Tracking**: Saves progress after each step
✅ **Resume Capability**: Continue from where you left off after interruptions  
✅ **Multi-Provider Support**: Grade with OpenAI, Gemini, or both
✅ **Automatic Averaging**: Combines results from multiple judges
✅ **Progress Tracking**: Per-file and per-provider completion tracking
✅ **Error Recovery**: Gracefully handles API errors and interruptions

## Quick Start

### 1. Configure Evaluation

```bash
# Copy example config
cp configs/multi_provider_config.yaml.example configs/my_eval.yaml

# Edit with your settings
vim configs/my_eval.yaml
```

**Example Configuration:**

```yaml
run_name: "my_evaluation_v1"

input_files:
  - extracted_reports/reports_20250101_120000.json
  - extracted_reports/reports_20250102_130000.json

criteria:
  - presentation
  - consistency
  - coverage
  - citation

providers:
  - openai
  - gemini

models:
  openai: gpt-5-2025-08-07
  gemini: gemini-2.5-pro

output_dir: results
state_dir: evaluation_state
max_concurrent: 5
```

### 2. Run Evaluation

```bash
python run_multi_provider_evaluation.py --config configs/my_eval.yaml
```

### 3. Resume After Interruption

If the script is interrupted (Ctrl+C, network error, API rate limit, etc.), simply run the same command again:

```bash
python run_multi_provider_evaluation.py --config configs/my_eval.yaml
```

The script will:
- Load the saved state
- Skip already-completed providers
- Skip already-graded files
- Continue from where it left off

### 4. Force Restart

To start over from the beginning:

```bash
python run_multi_provider_evaluation.py --config configs/my_eval.yaml --restart
```

## How It Works

### State Management

The script creates a state file in `evaluation_state/{run_name}_state.json`:

```json
{
  "started_at": "2025-10-31T01:38:49.407295",
  "status": "in_progress",
  "completed_providers": ["openai"],
  "completed_files": {
    "openai:extracted_reports/reports_20250101_120000.json": "2025-10-31T02:15:33.123456"
  },
  "output_dirs": {
    "openai": "results/openai",
    "gemini": "results/gemini"
  },
  "last_updated": "2025-10-31T02:15:33.123456"
}
```

### Execution Flow

1. **Load Configuration**: Read YAML config file
2. **Load/Create State**: Check for existing state or create new
3. **For Each Provider**:
   - Check if provider already completed → skip if yes
   - For each input file:
     - Check if file already graded by this provider → skip if yes
     - Run grading with `main.py`
     - Save state after completion
   - Mark provider as completed
4. **Average Results**: If multiple providers, average their summary files
5. **Mark Complete**: Update state to "completed"

### Output Structure

```
results/
├── openai/
│   └── reports_20250101_120000_graded_openai_gpt-5-2025-08-07/
│       ├── summary_2025-10-31T01-38-49.407295.json
│       └── detailed_results_2025-10-31T01-38-49.407295.json
├── gemini/
│   └── reports_20250101_120000_graded_gemini_gemini-2.5-pro/
│       ├── summary_2025-10-31T01-45-23.123456.json
│       └── detailed_results_2025-10-31T01-45-23.123456.json
└── averaged/
    └── summary_multi_judge_2025-10-31T02-00-15.789012.json

evaluation_state/
└── my_evaluation_v1_state.json
```

## Advanced Usage

### Multiple Input Files

Process multiple JSON files in one run:

```yaml
input_files:
  - extracted_reports/batch1.json
  - extracted_reports/batch2.json
  - extracted_reports/batch3.json
```

Each file is tracked independently in the state.

### Custom Output Directory

```yaml
output_dir: custom_results_dir
```

### Adjust Concurrency

Control API rate limits:

```yaml
max_concurrent: 10  # More concurrent calls (faster but higher rate limit risk)
max_concurrent: 2   # Fewer concurrent calls (slower but safer)
```

### Single Provider Mode

To use only one provider (no averaging):

```yaml
providers:
  - openai  # Only use OpenAI
```

## Error Handling

### API Errors

If an API call fails:
- The error is logged
- State is saved
- Script exits with error code
- Re-run to retry failed operations

### Interruptions (Ctrl+C)

- State is saved immediately
- Re-run to resume from last checkpoint

### Network Issues

- Automatic retry logic in underlying graders
- State tracking ensures no duplicate work

## State File Details

### Status Values

- `in_progress`: Evaluation ongoing
- `completed`: All providers finished and results averaged

### Completed Files Format

```json
"completed_files": {
  "provider:file_path": "completion_timestamp"
}
```

Example:
```json
"openai:extracted_reports/reports.json": "2025-10-31T01:38:49.407295"
```

### Cleaning Up State

To start fresh:

```bash
# Option 1: Use --restart flag
python run_multi_provider_evaluation.py --config configs/my_eval.yaml --restart

# Option 2: Delete state file manually
rm evaluation_state/my_evaluation_v1_state.json
python run_multi_provider_evaluation.py --config configs/my_eval.yaml
```

## Best Practices

### 1. Use Descriptive Run Names

```yaml
run_name: "gpt5_gemini_full_dataset_v2"  # Good
run_name: "test"  # Bad - not descriptive
```

### 2. Start with Small Batches

Test with 1-2 files first:

```yaml
input_files:
  - extracted_reports/sample.json  # Test with one file first
```

### 3. Monitor Progress

The script prints progress after each file:

```
📄 Processing: reports_20250101_120000.json
✅ Completed grading with openai
```

### 4. Keep State Files

State files are small (< 10KB). Keep them for audit trail.

### 5. Use Consistent Config Names

Match config names to run names:

```
configs/my_evaluation_v1.yaml
evaluation_state/my_evaluation_v1_state.json
```

## Troubleshooting

### "Provider already completed, skipping"

This is normal resume behavior. To force re-grading:

```bash
python run_multi_provider_evaluation.py --config configs/my_eval.yaml --restart
```

### "Not enough summary files found for averaging"

Check that both providers completed successfully:
- Look in `results/openai/` and `results/gemini/`
- Check for `summary_*.json` files
- Review state file for completion status

### State File Corruption

If state file is corrupted:

```bash
rm evaluation_state/my_run_state.json
python run_multi_provider_evaluation.py --config configs/my_eval.yaml --restart
```

## Comparison with Manual Workflow

### Manual (Old Way)

```bash
# Step 1: Grade with OpenAI
python main.py --input file1.json --criteria ... --provider openai
python main.py --input file2.json --criteria ... --provider openai
python main.py --input file3.json --criteria ... --provider openai

# Step 2: Grade with Gemini
python main.py --input file1.json --criteria ... --provider gemini
python main.py --input file2.json --criteria ... --provider gemini
python main.py --input file3.json --criteria ... --provider gemini

# Step 3: Average (manually find the right files)
python average_results.py --input-a ... --input-b ... --output ...
```

**Problems:**
- ❌ Manual tracking of which files are done
- ❌ No resume capability
- ❌ Error-prone file path management
- ❌ Manual averaging step

### Automated (New Way)

```bash
# One command, everything handled automatically
python run_multi_provider_evaluation.py --config configs/my_eval.yaml
```

**Benefits:**
- ✅ Automatic progress tracking
- ✅ Resume on any interruption
- ✅ Automatic averaging
- ✅ Clean, reproducible workflow

## Integration with CI/CD

### Example GitHub Actions

```yaml
name: Evaluate Reports

on:
  push:
    paths:
      - 'extracted_reports/**'

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run evaluation
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        run: |
          python run_multi_provider_evaluation.py --config configs/ci_eval.yaml
      
      - name: Upload results
        uses: actions/upload-artifact@v2
        with:
          name: evaluation-results
          path: results/
```

## Future Enhancements

Planned features:
- [ ] Support for 3+ providers with pairwise averaging
- [ ] Parallel provider execution (instead of sequential)
- [ ] Email/Slack notifications on completion
- [ ] Web dashboard for monitoring progress
- [ ] Automatic retry with exponential backoff
- [ ] Cost tracking per provider




