# Getting Started with LiveResearchBench

## Installation 

```bash
# 1. Navigate to the project
cd LiveResearchBench

# 2. Install dependencies with uv
uv sync

# 3. Set up API keys
# Create .env file and add your keys:
cat > .env << EOF
OPENAI_API_KEY=your-openai-key-here
GEMINI_API_KEY=your-gemini-key-here
EOF
```

## Quick Test With a Single Report



```bash
# Test preprocessing
python preprocess.py my_test_experiment \
    --base-path /path/to/your/test/data \
    --output-dir test_output

# Test single file grading
python main.py \
    --input test_output/reports_*.json \
    --criteria presentation \
    --provider gemini
```

## Batch Processing

### Step 1: Preprocess Your Reports

```bash
# Extract MD reports to JSON
# Replace with your actual experiment names and data path
python preprocess.py gpt4_deep_research gpt5_deep_research \
    --base-path /path/to/your/research_outputs \
    --output-dir extracted_reports
```

**Output**: `extracted_reports/reports_YYYYMMDD_HHMMSS.json`

### Step 2: Configure Batch Grading

Edit `configs/batch_config.yaml`:

```yaml
input_files:
  - extracted_reports/reports_20250101_120000.json
  # Add all your JSON files here

criteria:
  - presentation
  - consistency
  - citation
  - coverage
```

### Step 3: Grade with Both Providers

```bash
# Automated: Both providers + averaging
./scripts/batch_grade_multi_provider.sh my_experiment_v1

# Results will be in:
# - results/my_experiment_v1/gpt5/
# - results/my_experiment_v1/gemini/
# - results/my_experiment_v1/averaged/
```

### Step 4: Analyze Results

Results are in JSON format with grading results added to each report:

```json
{
  "reports": [
    {
      "query_id": "qid_123",
      "presentation_grading_results": {
        "summary": {"passed_count": 8, "average_pass_rate": 80.0}
      },
      "consistency_grading_results": {
        "score": 90,
        "total_issues": 2
      }
    }
  ]
}
```

## Common Commands

```bash
# Grade single file with one criterion
python main.py --input reports.json --criteria presentation --provider gemini

# Grade single file with multiple criteria
python main.py --input reports.json \
    --criteria presentation,consistency,citation \
    --provider openai --model gpt-5-2025-08-07

# Batch grade (single provider)
./scripts/batch_grade.sh my_run_v1

# Batch grade (both providers + averaging)
./scripts/batch_grade_multi_provider.sh my_run_v1

# Average existing results
python average_results.py \
    --input-a results/gpt5/reports_graded.json \
    --input-b results/gemini/reports_graded.json \
    --output results/reports_averaged.json
```

## Troubleshooting

### API Key Not Found

```bash
# Check .env file exists and has correct keys
cat .env

# Keys should be:
# OPENAI_API_KEY=sk-...
# GEMINI_API_KEY=AIza...
```

### No Reports Found During Preprocessing

```bash
# Check the directory structure matches:
# <base_path>/<exp_name>/same_bb/<task>/<config>/<model>/sd0/report_*.md

# Or check the base path:
python preprocess.py my_exp \
    --base-path /correct/path/to/reports \
    --verbose
```

### Coverage Criterion Requires Internet Connection

Coverage checklists are automatically loaded from the [Salesforce/LiveResearchBench](https://huggingface.co/datasets/Salesforce/LiveResearchBench) dataset on HuggingFace. No local files needed!

## Evaluation Criteria Reference

| Criterion | Protocol | Score Range | Description |
|-----------|----------|-------------|-------------|
| **Presentation** | Checklist | 0-10 (binary) | 10 formatting/structure questions |
| **Consistency** | Pointwise | 10-100 | Count logical/factual contradictions |
| **Coverage** | Checklist | 0-N (binary) | Check if report addresses each item |
| **Citation** | Pointwise | 10-100 | Count missing citations |
| **Depth** | Pairwise | A/B/tie | Compare 5 dimensions (requires 2 reports) |

## Next Steps

1. ✅ Preprocess your reports
2. ✅ Configure `batch_config.yaml` with your JSON files
3. ✅ Run batch grading with both providers
4. ✅ Analyze averaged results
5. 📊 Generate summary statistics (see `average_results.py`)

## Support

- **Documentation**: See [README.md](README.md) for full documentation
- **Issues**: Check GitHub Issues or create a new one
- **Configuration**: See [configs/batch_config.yaml.example](configs/batch_config.yaml.example)

