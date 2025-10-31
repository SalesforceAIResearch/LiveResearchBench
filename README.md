# LiveResearchBench

A comprehensive evaluation benchmark for AI-generated long-form research reports.

## Overview

LiveResearchBench evaluates research reports across **5 key criteria** using state-of-the-art LLM-as-a-judge methodologies:

- **❶ Presentation & Organization** (Checklist-based, binary 0/1)
- **❷ Factual & Logical Consistency** (Pointwise/additive, score 10-100)
- **❸ Coverage & Comprehensiveness** (Checklist-based, binary 0/1)
- **❹ Analysis Depth** (Pairwise comparison, 5 dimensions)
- **❺ Citation Association** (Pointwise/additive, score 10-100)

Each criterion uses the most appropriate evaluation protocol based on human alignment studies, ensuring high-quality, reliable assessments.

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/LiveResearchBench.git
cd LiveResearchBench

# Create virtual environment and install dependencies with uv
uv venv
source .venv/bin/activate
uv sync

# Configure API keys
cp .env.example .env
# Edit .env and add your API keys:
#   OPENAI_API_KEY=your-key
#   GEMINI_API_KEY=your-key
```

### Basic usage to evaluate long-form reports

**1. Preprocess Reports** (Create a JSON index mapping queries to report file locations)

```bash
# Process all models in a directory (recommended: use --use-realtime for live benchmark queries)
python preprocess.py /path/to/model_outputs --use-realtime

# Or process specific models (subdirectories) only
python preprocess.py /path/to/model_outputs -m gpt-5-search gemini-pro --use-realtime

# With custom output directory
python preprocess.py /path/to/model_outputs -o extracted_reports/ --use-realtime

# Optional: Use static queries without placeholder replacement (not recommended for live evaluation)
python preprocess.py /path/to/model_outputs
```

**Expected input directory structure:**
```
/path/to/model_outputs/
├── model_name_1/
│   ├── qid_<qid>_report.md
│   ├── qid_<qid>_report.md
│   └── ...
├── model_name_2/
│   ├── qid_<qid>_report.md
│   └── ...
```

**Expected output structure:**

After preprocessing, a JSON file will be created in `extracted_reports/` (or the specified output directory) with the naming pattern `reports_{timestamp}.json`.

The JSON structure includes:

```json
{
  "metadata": {
    "timestamp": "20250101_120000",              // When the preprocessing was performed
    "total_reports": 300,                         // Total number of reports contained and processed
    "total_models": 3,                           // Number of model outputs included
    "base_path": "/path/to/model_outputs",       // Base path to report outputs directory
    "use_realtime": true                        // Whether to replace query placeholders with real-time values
  },
  "reports": [
    {
      "model_name": "model-name-1",              // Model/system name (subdirectory name)
      "query_id": "abc123xyz",               // Query identifier from the benchmark
      "query": "Research query text...",         // Query loaded and processed from LiveResearchBench dataset
      "report_file_path": "/path/to/model_outputs/model-name-1/qid_abc123xyz_report.md"
    },
    {
      "model_name": "model-name-2",
      "query_id": "def456uvw",
      "query": "Another research query...",
      "report_file_path": "/path/to/model_outputs/model-name-2/qid_def456uvw_report.md"
    }
    // ... more report entries
  ]
}
```

Each report entry contains the model name, query ID, full query text (loaded and processed from the LiveResearchBench dataset on HuggingFace), and the absolute path to the markdown report file.

**2. Grade Single File**

```bash
# Single criterion
python main.py \
    --input extracted_reports/reports_20250101_120000.json \ # the json file created from preprocessing
    --criteria presentation \
    --provider gemini

# Multiple criteria
python main.py \
    --input extracted_reports/reports_20250101_120000.json \
    --criteria presentation,consistency,citation,coverage,depth \
    --provider openai --model gpt-5-2025-08-07
```

**3. Multi-Provider Evaluation** (Recommended for reliability)

```bash
# Automated: Grades with both providers and averages results
# With automatic resume on interruption
python run_multi_provider_evaluation.py --config configs/multi_provider_config.yaml
```

## Evaluation Protocols

Based on our human alignment study, we adopt three different protocols:

### 1. Checklist-Based (Presentation, Coverage)
- **Binary scoring**: 0 (fail) or 1 (pass) for each checklist item
- **Presentation**: 10 fixed quality questions
- **Coverage**: Custom checklist per query

### 2. Pointwise/Additive (Consistency, Citation)
- **Error counting**: Identify and count specific issues
- **Score**: 10-100 based on number of issues found
- **Consistency**: Count logical/factual contradictions
- **Citation**: Count missing citations

### 3. Pairwise Comparison (Depth)
- **Side-by-side comparison**: Compare two reports directly
- **5 dimensions**: Granularity, Insight, Critique, Evidence, Density
- **Position-swap averaging**: Mitigates position bias by comparing in both directions

## Directory Structure

```
LiveResearchBench/
├── liveresearchbench/          # Main Python package
│   ├── common/                 # Shared utilities
│   ├── graders/                # Grading implementations
│   ├── criteria/               # Criterion definitions
│   └── batch_evaluator.py      # Batch grading orchestrator
├── preprocess.py               # Preprocessing script
├── main.py                     # Main grading script
├── average_results.py          # Multi-provider averaging
├── scripts/                    # Bash convenience scripts
├── configs/                    # Configuration files
├── data/                       # Data files (checklists, etc.)
└── tests/                      # Test suite
    ├── test_basic.py           # Unit tests
    ├── test_mock_grading.py    # Integration tests
    └── run_all_tests.sh        # Test runner
```

## Configuration

### Batch Config (`configs/batch_config.yaml`)

```yaml
# List of JSON files to process
input_files:
  - /path/to/reports_model1.json
  - /path/to/reports_model2.json

# Criteria to evaluate
criteria:
  - presentation
  - consistency
  - coverage
  - citation
  - depth
```

## Advanced Usage

### Multi-Provider Grading & Averaging

For more reliable results, grade with both GPT-5 and Gemini-2.5-Pro, then average.

**Method 1: Automated with State Tracking (Recommended)**

```bash
# 1. Copy and configure the multi-provider config
cp configs/multi_provider_config.yaml.example configs/multi_provider_config.yaml
# Edit the config file with your settings

# 2. Run the evaluation (with automatic resume on interruption)
python run_multi_provider_evaluation.py --config configs/multi_provider_config.yaml

# If interrupted, simply run again to resume:
python run_multi_provider_evaluation.py --config configs/multi_provider_config.yaml

# Force restart from beginning:
python run_multi_provider_evaluation.py --config configs/multi_provider_config.yaml --restart
```

**Features:**
- ✅ Automatic state tracking and resume capability
- ✅ Grades with multiple providers sequentially
- ✅ Automatically averages results at the end
- ✅ Handles interruptions gracefully
- ✅ Tracks progress per file and per provider

**Method 2: Manual Step-by-Step**

```bash
# Step 1: Grade with OpenAI
python main.py \
    --input extracted_reports/reports_20250101_120000.json \
    --criteria presentation,consistency,citation,coverage \
    --provider openai --model gpt-5-2025-08-07

# Step 2: Grade with Gemini
python main.py \
    --input extracted_reports/reports_20250101_120000.json \
    --criteria presentation,consistency,citation,coverage \
    --provider gemini --model gemini-2.5-pro

# Step 3: Average the summary files
python average_results.py \
    --input-a results/reports_20250101_120000_graded_openai_gpt-5-2025-08-07/summary_*.json \
    --input-b results/reports_20250101_120000_graded_gemini_gemini-2.5-pro/summary_*.json \
    --output results/averaged/summary_multi_judge.json
```

### Resume Interrupted Runs

Grading automatically skips already-graded reports:

```bash
# Just run the same command again - it will resume
python main.py --batch --config configs/batch_config.yaml --provider gemini

# Or force re-grade everything
python main.py --batch --config configs/batch_config.yaml --provider gemini --force-regrade
```

### Filtering

Grade specific subsets of reports:

```bash
# Filter by experiment name (modify JSON before grading)
# Or process only specific JSON files in batch_config.yaml
```

## API Keys

Set in `.env` file:

```bash
# OpenAI (for GPT-5)
OPENAI_API_KEY=sk-...

# Google Gemini
GEMINI_API_KEY=AIza...
```

## Output Format

### Output Directory Structure

Grading results are organized by input file name, with timestamped result files inside:

```
results/
└── reports_{json_file_name}_graded_{provider}_{model_name}/
    ├── summary_{evaluation_timestamp}.json
    └── detailed_results_{evaluation_timestamp}.json
```

### Summary File (`summary.json`)

Contains aggregated statistics:

```json
{
  "metadata": {
    "provider": "openai",
    "model": "gpt-5-2025-08-07",
    "graded_at": "2025-10-31T01:38:49.407295",
    "total_reports": 10,
    "criteria_evaluated": ["presentation", "coverage", "consistency", "citation"]
  },
  "results_by_model": {
    "model-name-1": {
      "presentation": {
        "mean": 85.5,           // Average pass rate across all reports
        "count": 5,             // Number of reports graded
        "min": 70.0,
        "max": 100.0
      },
      "coverage": { ... },
      "consistency": { ... }
    },
    "model-name-2": { ... }
  },
  "overall_results": {
    "presentation": {
      "mean": 82.3,             // Average across all models/reports
      "count": 10,
      "min": 60.0,
      "max": 100.0
    },
    // ... other criteria
  }
}
```

### Detailed Results File (`detailed_results.json`)

Each report is augmented with grading results:

```json
{
  "reports": [
    {
      "query_id": "qid_123",
      "query": "What is...",
      "report_file_path": "/path/to/report.md",
      
      "presentation_grading_results": {
        "provider": "gemini",
        "model": "gemini-2.5-pro",
        "graded_at": "2025-...",
        "evaluations": {
          "p1": {"score": 1, "justification": "..."},
          "p2": {"score": 0, "justification": "..."}
        },
        "summary": {
          "total_criteria": 10,
          "passed_count": 8,
          "average_pass_rate": 80.0
        }
      },
      
      "consistency_grading_results": {
        "provider": "gemini",
        "model": "gemini-2.5-pro",
        "graded_at": "2025-...",
        "specific_issues": ["Issue 1...", "Issue 2..."],
        "total_issues": 2,
        "score": 90,
        "justification": "..."
      }
    }
  ]
}
```

## Citation

If you use LiveResearchBench in your research, please cite:

```bibtex
@article{liveresearchbench,
  title   = {LiveResearchBench: A Live Benchmark for User-Centric Deep Research in the Wild},
  author  = {Wang, Jiayu and Ming, Yifei and Dulepet, Riya and Chen, Qinglin and Xu, Austin and Ke, Zixuan and Sala, Frederic and Albarghouthi, Aws and Xiong, Caiming and Joty, Shafiq},
  journal = {arXiv preprint arXiv:2510.14240},
  year    = {2025},
  url     = {https://arxiv.org/abs/2510.14240}
}
```
