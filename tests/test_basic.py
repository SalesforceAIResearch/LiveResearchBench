#!/usr/bin/env python3
"""Basic tests to verify the implementation works."""

import sys
import os

print("=" * 60)
print("Testing LiveResearchBench Basic Functionality")
print("=" * 60)

# Test 1: Import main package
print("\n1. Testing package imports...")
try:
    import liveresearchbench
    print(f"   ✅ Package version: {liveresearchbench.__version__}")
except Exception as e:
    print(f"   ❌ Failed to import package: {e}")
    sys.exit(1)

# Test 2: Import common utilities
print("\n2. Testing common utilities...")
try:
    from liveresearchbench.common.model_clients import create_ai_client, GeminiClient, OpenAIClient
    from liveresearchbench.common.io_utils import load_json, save_json
    print("   ✅ Common utilities imported successfully")
except Exception as e:
    print(f"   ❌ Failed to import common utilities: {e}")
    sys.exit(1)

# Test 3: Import criteria
print("\n3. Testing criteria definitions...")
try:
    from liveresearchbench.criteria.presentation import PRESENTATION_QUESTIONS
    from liveresearchbench.criteria.consistency import CONSISTENCY_RUBRIC
    from liveresearchbench.criteria.citation import CITATION_RUBRIC
    print(f"   ✅ Found {len(PRESENTATION_QUESTIONS)} presentation questions")
    print("   ✅ Criteria definitions loaded")
except Exception as e:
    print(f"   ❌ Failed to import criteria: {e}")
    sys.exit(1)

# Test 4: Import graders
print("\n4. Testing grader imports...")
try:
    from liveresearchbench.graders import ChecklistGrader, PointwiseGrader, PairwiseGrader
    checklist_grader = ChecklistGrader()
    pointwise_grader = PointwiseGrader()
    pairwise_grader = PairwiseGrader()
    print("   ✅ All graders instantiated successfully")
except Exception as e:
    print(f"   ❌ Failed to import graders: {e}")
    sys.exit(1)

# Test 5: Import batch evaluator
print("\n5. Testing batch evaluator...")
try:
    from liveresearchbench.batch_evaluator import BatchEvaluator
    # Don't instantiate with real provider to avoid API key requirement
    print("   ✅ Batch evaluator imported successfully")
except Exception as e:
    print(f"   ❌ Failed to import batch evaluator: {e}")
    sys.exit(1)

# Test 6: Test JSON operations
print("\n6. Testing I/O utilities...")
try:
    import tempfile
    import json
    
    test_data = {"test": "data", "number": 42}
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        test_file = f.name
        json.dump(test_data, f)
    
    loaded_data = load_json(test_file)
    assert loaded_data == test_data, "Data mismatch"
    
    os.unlink(test_file)
    print("   ✅ JSON I/O working correctly")
except Exception as e:
    print(f"   ❌ Failed JSON I/O test: {e}")
    sys.exit(1)

# Test 7: Test prompt creation
print("\n7. Testing prompt creation...")
try:
    from liveresearchbench.criteria.presentation import create_presentation_prompt
    from liveresearchbench.criteria.consistency import create_consistency_prompt
    
    system_prompt, user_prompt = create_presentation_prompt(
        "Test query",
        "Test report content"
    )
    assert "presentation" in system_prompt.lower()
    assert "Test query" in user_prompt
    print("   ✅ Prompt creation working")
except Exception as e:
    print(f"   ❌ Failed prompt creation test: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ All basic tests passed!")
print("=" * 60)
print("\nNext steps:")
print("  1. Set up .env with API keys")
print("  2. Run: python main.py --help")
print("  3. Test with real data")

