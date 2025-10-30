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

# Install dependencies with uv
uv sync

# Configure API keys
cp .env.example .env
# Edit .env and add your API keys:
#   OPENAI_API_KEY=your-key
#   GEMINI_API_KEY=your-key

# Run tests to verify installation
./tests/run_all_tests.sh
```

### Basic Usage

**1. Preprocess Reports** (Extract MD files to JSON)

```bash
# Process all models in a directory
python preprocess.py /path/to/model_outputs

# Or process specific models only
python preprocess.py /path/to/model_outputs -m gpt-5-search gemini-pro

# With custom output directory
python preprocess.py /path/to/model_outputs -o extracted_reports/
```

**Expected directory structure:**
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

**2. Grade Single File**

```bash
# Single criterion
python main.py \
    --input extracted_reports/reports_20250101_120000.json \
    --criteria presentation \
    --provider gemini

# Multiple criteria
python main.py \
    --input extracted_reports/reports_20250101_120000.json \
    --criteria presentation,consistency,citation,coverage \
    --provider openai --model gpt-5-2025-08-07
```

**3. Batch Grade All Models**

```bash
# Single provider
./scripts/batch_grade.sh my_experiment

# Both providers (GPT-5 + Gemini) with averaging
./scripts/batch_grade_multi_provider.sh my_experiment
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
- **Three judges**: Majority voting for reliability

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
  # Note: Questions and checklists are automatically loaded from HuggingFace
```

## Advanced Usage

### Multi-Provider Grading & Averaging

For more reliable results, grade with both GPT-5 and Gemini-2.5-Pro, then average:

```bash
# Method 1: Automated script
./scripts/batch_grade_multi_provider.sh my_experiment

# Method 2: Manual
python main.py --batch --config configs/batch_config.yaml \
    --provider openai --model gpt-5-2025-08-07 \
    --output-dir results/gpt5

python main.py --batch --config configs/batch_config.yaml \
    --provider gemini --model gemini-2.5-pro \
    --output-dir results/gemini

python average_results.py \
    --input-a results/gpt5/reports_graded.json \
    --input-b results/gemini/reports_graded.json \
    --output results/reports_averaged.json
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

### JSON Output

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
@article{liveresearchbench2025,
  title={LiveResearchBench: A Comprehensive Evaluation Benchmark for AI-Generated Research Reports},
  author={Your Name et al.},
  journal={arXiv preprint},
  year={2025}
}
```
