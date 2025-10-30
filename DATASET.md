# LiveResearchBench Dataset

## Overview

This project uses the **[Salesforce/LiveResearchBench](https://huggingface.co/datasets/Salesforce/LiveResearchBench)** dataset from HuggingFace.

## Dataset Structure

The dataset contains 100 benchmark questions with checklists for evaluating AI-generated research reports across different criteria:

- **Total questions**: 100
- **Total checklist items**: 672 (varies per question)
- **Subsets**: 
  - `question_with_checklist`: Full dataset with questions and per-question checklists
  - `question_only`: Questions without checklists (100 rows)

## Loading the Dataset

### Default: Static Mode (No Placeholders)

By default, the system uses the `question_no_placeholder` and `checklist_no_placeholder` fields:

```python
from liveresearchbench.common.io_utils import load_liveresearchbench_dataset

# Load static version (2025 hardcoded)
benchmark_data = load_liveresearchbench_dataset(use_realtime=False)
```

**Example output:**
- Question: "What is the size, growth rate, and segmentation of the U.S. electric vehicle market in **2025**?"

### Realtime Mode (With Placeholder Replacement)

For dynamic evaluation with current dates, use realtime mode:

```python
# Load realtime version (replaces {{current_year}} etc.)
benchmark_data = load_liveresearchbench_dataset(use_realtime=True)
```

**Supported placeholders:**
- `{{current_year}}` → 2025 (current year)
- `{{last_year}}` → 2024 (current year - 1)
- `{{date}}` → October 29, 2025 (formatted date)

**Example output:**
- Question: "What is the size, growth rate, and segmentation of the U.S. electric vehicle market in **2025**?" (automatically updated each year)

## Accessing Questions and Checklists

```python
from liveresearchbench.common.io_utils import (
    load_liveresearchbench_dataset,
    get_question_for_qid,
    get_checklists_for_qid
)

# Load dataset
benchmark_data = load_liveresearchbench_dataset()

# Get question for a specific query ID
qid = "market6VWmPyxptfK47civ"
question = get_question_for_qid(benchmark_data, qid)

# Get checklist items for a specific query ID
checklists = get_checklists_for_qid(benchmark_data, qid)
print(f"Found {len(checklists)} checklist items")
```

## Dataset Fields

For each entry in the dataset:

```python
{
    'qid': 'market6VWmPyxptfK47civ',  # Unique query identifier
    'question': 'What is the size, growth rate...',  # Research question
    'checklists': [  # List of checklist items for coverage evaluation
        'Does the report provide data for the U.S. electric vehicle market...',
        'Does the report discuss the size, growth rate...',
        # ... more items
    ]
}
```

## Downloading for Offline Use

To cache the dataset locally for offline use:

```bash
# Option 1: Use the provided script
./scripts/download_dataset.sh

# Option 2: Manual download
python3 << 'EOF'
from datasets import load_dataset
dataset = load_dataset("Salesforce/LiveResearchBench", "question_with_checklist", split="test")
print(f"✅ Cached {len(dataset)} entries")
EOF
```

The dataset will be cached at: `~/.cache/huggingface/datasets/`

## Usage in Tests

The test script automatically loads the dataset:

```python
# In tests/test_real_grading.py
benchmark_data = load_liveresearchbench_dataset(use_realtime=USE_REALTIME_PLACEHOLDERS)

# Questions are fetched per report
for report in reports:
    query_id = report['query_id']
    question = get_question_for_qid(benchmark_data, query_id)
    checklists = get_checklists_for_qid(benchmark_data, query_id)
    
    # Use for grading...
```

## Integration with Grading Criteria

The loaded questions and checklists are used across all 5 grading criteria:

1. **Presentation & Organization**: Uses question for context
2. **Factual & Logical Consistency**: Uses question to verify report accuracy
3. **Coverage & Comprehensiveness**: Uses question + checklists to verify completeness
4. **Citation Association**: Uses question to identify required citations
5. **Analysis Depth**: Uses question for pairwise comparison context

## Citation

If you use this dataset, please cite:

```bibtex
@dataset{liveresearchbench2025,
  title={LiveResearchBench: A Benchmark for Evaluating AI-Generated Research Reports},
  author={Salesforce Research},
  year={2025},
  url={https://huggingface.co/datasets/Salesforce/LiveResearchBench}
}
```

