#!/usr/bin/env python3
"""Mock test for grading workflow (no API calls)."""

import json
import tempfile
import os
from pathlib import Path

print("=" * 60)
print("Testing Mock Grading Workflow")
print("=" * 60)

# Create a mock report JSON file
print("\n1. Creating mock report data...")
mock_report = {
    "metadata": {
        "total_reports": 2,
        "generated_at": "2025-01-01T00:00:00"
    },
    "reports": [
        {
            "query_id": "test_qid_1",
            "query": "What is the impact of AI on healthcare?",
            "exp_name": "test_experiment",
            "task": "test_task",
            "config_name": "default",
            "model_name": "test-model",
            "report_file_path": "/tmp/test_report_1.md"
        },
        {
            "query_id": "test_qid_2", 
            "query": "How does climate change affect agriculture?",
            "exp_name": "test_experiment",
            "task": "test_task",
            "config_name": "default",
            "model_name": "test-model",
            "report_file_path": "/tmp/test_report_2.md"
        }
    ]
}

# Create mock report markdown files
print("2. Creating mock report files...")
for i, report in enumerate(mock_report["reports"], 1):
    report_path = report["report_file_path"]
    with open(report_path, 'w') as f:
        f.write(f"""# Research Report {i}

## Introduction
This is a test report about {report['query']}.

## Main Content
- Point 1: Some analysis
- Point 2: More analysis
- Point 3: Conclusion

## References
[1] Test Source 1
[2] Test Source 2
""")
    print(f"   ✅ Created {report_path}")

# Save mock JSON
with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
    mock_json_path = f.name
    json.dump(mock_report, f, indent=2)

print(f"   ✅ Created mock JSON: {mock_json_path}")

# Test criteria definitions
print("\n3. Testing criteria configurations...")
from liveresearchbench.criteria.presentation import PRESENTATION_QUESTIONS
from liveresearchbench.criteria.consistency import CONSISTENCY_EVALUATION_SCHEMA
from liveresearchbench.criteria.citation import CITATION_EVALUATION_SCHEMA

print(f"   ✅ Presentation: {len(PRESENTATION_QUESTIONS)} questions")
print(f"   ✅ Consistency schema: {list(CONSISTENCY_EVALUATION_SCHEMA['properties'].keys())}")
print(f"   ✅ Citation schema: {list(CITATION_EVALUATION_SCHEMA['properties'].keys())}")

# Test grader instantiation
print("\n4. Testing grader instantiation...")
from liveresearchbench.graders import ChecklistGrader, PointwiseGrader

checklist_grader = ChecklistGrader()
pointwise_grader = PointwiseGrader()
print("   ✅ Checklist grader created")
print("   ✅ Pointwise grader created")

# Test prompt creation
print("\n5. Testing prompt generation...")
from liveresearchbench.criteria.presentation import create_presentation_prompt
from liveresearchbench.criteria.consistency import create_consistency_prompt

test_query = mock_report["reports"][0]["query"]
test_content = "Test report content"

sys_prompt, user_prompt = create_presentation_prompt(test_query, test_content)
print(f"   ✅ Presentation prompt created ({len(sys_prompt)} chars system, {len(user_prompt)} chars user)")

sys_prompt, user_prompt = create_consistency_prompt(test_query, test_content)
print(f"   ✅ Consistency prompt created ({len(sys_prompt)} chars system, {len(user_prompt)} chars user)")

# Test batch config loading
print("\n6. Testing batch config...")
import yaml

try:
    with open('configs/batch_config.yaml') as f:
        config = yaml.safe_load(f)
    print(f"   ✅ Batch config loaded")
    print(f"   ✅ Found {len(config.get('input_files', []))} input files configured")
    print(f"   ✅ Criteria: {', '.join(config.get('criteria', []))}")
except FileNotFoundError:
    print("   ⚠️  batch_config.yaml not found (expected for testing)")

# Cleanup
print("\n7. Cleaning up...")
for report in mock_report["reports"]:
    if os.path.exists(report["report_file_path"]):
        os.unlink(report["report_file_path"])
os.unlink(mock_json_path)
print("   ✅ Cleanup complete")

print("\n" + "=" * 60)
print("✅ All mock tests passed!")
print("=" * 60)
print("\nTo test with real API:")
print("  1. Set up .env with GEMINI_API_KEY or OPENAI_API_KEY")
print("  2. Run: python main.py --input <your_file.json> --criteria presentation --provider gemini")

