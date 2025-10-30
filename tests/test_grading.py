#!/usr/bin/env python3
"""
Real integration test using GPT-5 to grade sample reports.
This test makes actual API calls and validates the grading workflow end-to-end.

Tests all 5 criteria:
1. Presentation & Organization (checklist-based)
2. Factual & Logical Consistency (pointwise)
3. Coverage & Comprehensiveness (checklist-based)
4. Citation Association (pointwise)
5. Analysis Depth (pairwise comparison)

Run with: python tests/test_real_grading.py
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from liveresearchbench.common.io_utils import (
    load_json,
    load_liveresearchbench_dataset,
    get_question_for_qid,
    get_checklists_for_qid
)
from liveresearchbench.graders.checklist_grader import ChecklistGrader
from liveresearchbench.graders.pointwise_grader import PointwiseGrader
from liveresearchbench.graders.pairwise_grader import PairwiseGrader

# Test configuration
TEST_DATA_PATH = "data/test_samples/open_deep_research_sample.json"
GRADER_MODEL = "gpt-5-2025-08-07"
PROVIDER = "openai"
MAX_REPORTS_PER_TEST = 2  # Grade 2 reports per criterion
USE_REALTIME_PLACEHOLDERS = False  # Set to True to use {{current_year}} etc.


def check_api_key() -> bool:
    """Check if OpenAI API key is configured"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your-openai-key-here":
        print("❌ Error: OPENAI_API_KEY not configured in .env file")
        print("   Please set up your .env file with a valid API key")
        return False
    return True


def load_report_content(report: Dict[str, Any]) -> str:
    """Load report content from file path"""
    report_file = report.get("report_file_path", "")
    if not report_file or not os.path.exists(report_file):
        return ""
    
    try:
        with open(report_file, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"   ⚠️  Error loading report from {report_file}: {e}")
        return ""


async def test_presentation_grading():
    """Test 1: Presentation & Organization grading (checklist-based)"""
    print("\n" + "="*80)
    print("Test 1: Presentation & Organization Grading")
    print("="*80)
    
    # Load test data
    print(f"📂 Loading test data from {TEST_DATA_PATH}...")
    reports_data = load_json(TEST_DATA_PATH)
    reports = reports_data["reports"][:MAX_REPORTS_PER_TEST]
    print(f"   ✅ Loaded {len(reports)} reports")
    
    # Initialize grader
    print(f"🤖 Initializing ChecklistGrader with {GRADER_MODEL}...")
    grader = ChecklistGrader()
    print(f"   ✅ Grader initialized")
    
    # Grade each report
    results = []
    for i, report in enumerate(reports, 1):
        query_id = report.get("query_id", f"report_{i}")
        query = report.get("query", "No query available")
        content = load_report_content(report)
        
        print(f"\n📝 Grading report {i}/{len(reports)} (query_id: {query_id})...")
        print(f"   Query: {query[:100]}...")
        print(f"   Report length: {len(content)} chars")
        
        result = await grader.grade_presentation_async(
            query=query,
            report_content=content,
            provider=PROVIDER,
            model=GRADER_MODEL
        )
        
        results.append(result)
        
        # Display results
        summary = result.get("summary", {})
        passed = summary.get("passed_count", 0)
        total = summary.get("total_criteria", 10)
        pass_rate = summary.get("average_pass_rate", 0)
        
        print(f"   ✅ Grading complete:")
        print(f"      Passed: {passed}/{total} questions ({pass_rate:.1f}%)")
        
        # Show a few examples
        evaluations = result.get("evaluations", {})
        for q_num in list(evaluations.keys())[:3]:
            eval_data = evaluations[q_num]
            score = eval_data.get("score", 0)
            status = "✅" if score == 1 else "❌"
            print(f"      {status} {q_num}: Score={score}")
    
    print(f"\n✅ Test 1 Complete: Graded {len(results)} reports for Presentation")
    return results


async def test_consistency_grading():
    """Test 2: Factual & Logical Consistency grading (pointwise)"""
    print("\n" + "="*80)
    print("Test 2: Factual & Logical Consistency Grading")
    print("="*80)
    
    # Load test data
    print(f"📂 Loading test data from {TEST_DATA_PATH}...")
    reports_data = load_json(TEST_DATA_PATH)
    reports = reports_data["reports"][:MAX_REPORTS_PER_TEST]
    print(f"   ✅ Loaded {len(reports)} reports")
    
    # Initialize grader
    print(f"🤖 Initializing PointwiseGrader with {GRADER_MODEL}...")
    grader = PointwiseGrader()
    print(f"   ✅ Grader initialized")
    
    # Grade each report
    results = []
    for i, report in enumerate(reports, 1):
        query_id = report.get("query_id", f"report_{i}")
        query = report.get("query", "No query available")
        content = load_report_content(report)
        
        print(f"\n📝 Grading report {i}/{len(reports)} (query_id: {query_id})...")
        print(f"   Query: {query[:100]}...")
        print(f"   Report length: {len(content)} chars")
        
        result = await grader.grade_consistency_async(
            query=query,
            report_content=content,
            provider=PROVIDER,
            model=GRADER_MODEL
        )
        
        results.append(result)
        
        # Display results
        score = result.get("score", 0)
        total_issues = result.get("total_issues", 0)
        
        print(f"   ✅ Grading complete:")
        print(f"      Score: {score}/100")
        print(f"      Issues found: {total_issues}")
        
        # Show specific issues if any
        specific = result.get("specific_issues", [])
        if specific:
            print(f"      Specific issues:")
            for issue in specific[:3]:  # Show first 3
                print(f"         - {issue[:80]}...")
    
    print(f"\n✅ Test 2 Complete: Graded {len(results)} reports for Consistency")
    return results


async def test_coverage_grading(benchmark_data: dict):
    """Test 3: Coverage & Comprehensiveness grading (checklist-based)"""
    print("\n" + "="*80)
    print("Test 3: Coverage & Comprehensiveness Grading")
    print("="*80)
    
    # Load test data
    print(f"📂 Loading test data from {TEST_DATA_PATH}...")
    reports_data = load_json(TEST_DATA_PATH)
    reports = reports_data["reports"][:MAX_REPORTS_PER_TEST]
    print(f"   ✅ Loaded {len(reports)} reports")
    
    # Initialize grader
    print(f"🤖 Initializing ChecklistGrader with {GRADER_MODEL}...")
    grader = ChecklistGrader()
    print(f"   ✅ Grader initialized")
    
    # Grade each report
    results = []
    for i, report in enumerate(reports, 1):
        query_id = report.get("query_id", f"report_{i}")
        content = load_report_content(report)
        
        # Get question and checklist from benchmark dataset
        query = get_question_for_qid(benchmark_data, query_id)
        if not query:
            print(f"\n⚠️  No question found for query_id: {query_id}, skipping...")
            continue
        
        checklists = get_checklists_for_qid(benchmark_data, query_id)
        if not checklists:
            print(f"\n⚠️  No checklist found for query_id: {query_id}, skipping...")
            continue
        
        print(f"\n📝 Grading report {i}/{len(reports)} (query_id: {query_id})...")
        print(f"   Query: {query[:100]}...")
        print(f"   Report length: {len(content)} chars")
        print(f"   Checklist items: {len(checklists)}")
        
        result = await grader.grade_coverage_async(
            query=query,
            report_content=content,
            checklists=checklists,
            provider=PROVIDER,
            model=GRADER_MODEL
        )
        
        results.append(result)
        
        # Display results
        summary = result.get("summary", {})
        addressed = summary.get("addressed_count", 0)
        total = summary.get("total_checklists", len(checklists))
        percentage = summary.get("percentage_addressed", 0)
        
        print(f"   ✅ Grading complete:")
        print(f"      Addressed: {addressed}/{total} items ({percentage:.1f}%)")
        
        # Show a few examples
        evaluations = result.get("evaluations", {})
        for checklist_id in list(evaluations.keys())[:3]:
            eval_data = evaluations[checklist_id]
            score = eval_data.get("score", 0)
            status = "✅" if score == 1 else "❌"
            print(f"      {status} {checklist_id}: Score={score}")
    
    print(f"\n✅ Test 3 Complete: Graded {len(results)} reports for Coverage")
    return results


async def test_citation_grading():
    """Test 4: Citation Association grading (pointwise)"""
    print("\n" + "="*80)
    print("Test 4: Citation Association Grading")
    print("="*80)
    
    # Load test data
    print(f"📂 Loading test data from {TEST_DATA_PATH}...")
    reports_data = load_json(TEST_DATA_PATH)
    reports = reports_data["reports"][:MAX_REPORTS_PER_TEST]
    print(f"   ✅ Loaded {len(reports)} reports")
    
    # Initialize grader
    print(f"🤖 Initializing PointwiseGrader with {GRADER_MODEL}...")
    grader = PointwiseGrader()
    print(f"   ✅ Grader initialized")
    
    # Grade each report
    results = []
    for i, report in enumerate(reports, 1):
        query_id = report.get("query_id", f"report_{i}")
        query = report.get("query", "No query available")
        content = load_report_content(report)
        
        print(f"\n📝 Grading report {i}/{len(reports)} (query_id: {query_id})...")
        print(f"   Query: {query[:100]}...")
        print(f"   Report length: {len(content)} chars")
        
        result = await grader.grade_citation_async(
            query=query,
            report_content=content,
            provider=PROVIDER,
            model=GRADER_MODEL
        )
        
        results.append(result)
        
        # Display results
        score = result.get("score", 0)
        total_issues = result.get("total_issues", 0)
        
        print(f"   ✅ Grading complete:")
        print(f"      Score: {score}/100")
        print(f"      Issues found: {total_issues}")
        
        # Show specific issues if any
        specific = result.get("specific_issues", [])
        if specific:
            print(f"      Specific issues:")
            for issue in specific[:3]:  # Show first 3
                print(f"         - {issue[:80]}...")
    
    print(f"\n✅ Test 4 Complete: Graded {len(results)} reports for Citation")
    return results


async def test_depth_grading():
    """Test 5: Analysis Depth grading (pairwise comparison)"""
    print("\n" + "="*80)
    print("Test 5: Analysis Depth Grading (Pairwise)")
    print("="*80)
    
    # Load test data
    print(f"📂 Loading test data from {TEST_DATA_PATH}...")
    reports_data = load_json(TEST_DATA_PATH)
    
    # Need at least 2 reports for pairwise
    if len(reports_data["reports"]) < 2:
        print(f"⚠️  Warning: Need at least 2 reports for pairwise comparison")
        print(f"   Found only {len(reports_data['reports'])} reports, skipping...")
        return []
    
    reports = reports_data["reports"][:2]  # Take first 2 for comparison
    print(f"   ✅ Loaded 2 reports for comparison")
    
    # Initialize grader
    print(f"🤖 Initializing PairwiseGrader with {GRADER_MODEL}...")
    grader = PairwiseGrader()
    print(f"   ✅ Grader initialized")
    
    # Get report details
    report_a = reports[0]
    report_b = reports[1]
    
    query_id_a = report_a.get("query_id", "report_1")
    query_id_b = report_b.get("query_id", "report_2")
    query = report_a.get("query", "No query available")  # Assume same query
    content_a = report_a.get("generated", "")
    content_b = report_b.get("generated", "")
    
    print(f"\n📝 Comparing two reports...")
    print(f"   Report A (query_id: {query_id_a})")
    print(f"      Length: {len(content_a)} chars")
    print(f"   Report B (query_id: {query_id_b})")
    print(f"      Length: {len(content_b)} chars")
    print(f"   Query: {query[:100]}...")
    
    # Use single judge for faster testing (use_three_judges=False)
    result = await grader.compare_depth_async(
        query=query,
        report_a=content_a,
        report_b=content_b,
        provider=PROVIDER,
        model=GRADER_MODEL,
        use_three_judges=False  # Single judge for faster testing
    )
    
    # Display results
    winner = result.get("winner", "unknown")
    scores = result.get("scores", {})
    score_a = scores.get("A", {})
    score_b = scores.get("B", {})
    justification = result.get("justification", "")
    
    print(f"   ✅ Comparison complete:")
    print(f"      Winner: {winner}")
    print(f"      Report A total: {score_a.get('total', 0)}/25")
    print(f"         Granularity: {score_a.get('granularity', 0)}/5")
    print(f"         Insight: {score_a.get('insight', 0)}/5")
    print(f"         Critique: {score_a.get('critique', 0)}/5")
    print(f"         Evidence: {score_a.get('evidence', 0)}/5")
    print(f"         Density: {score_a.get('density', 0)}/5")
    print(f"      Report B total: {score_b.get('total', 0)}/25")
    print(f"         Granularity: {score_b.get('granularity', 0)}/5")
    print(f"         Insight: {score_b.get('insight', 0)}/5")
    print(f"         Critique: {score_b.get('critique', 0)}/5")
    print(f"         Evidence: {score_b.get('evidence', 0)}/5")
    print(f"         Density: {score_b.get('density', 0)}/5")
    print(f"      Justification: {justification[:150]}...")
    
    print(f"\n✅ Test 5 Complete: Pairwise comparison for Depth")
    return [result]


async def run_all_tests():
    """Run all real grading tests"""
    print("\n" + "🧪"*40)
    print("Real Integration Test: Grading with GPT-5")
    print("🧪"*40)
    
    # Check API key
    if not check_api_key():
        return False
    
    # Check test data exists
    if not os.path.exists(TEST_DATA_PATH):
        print(f"❌ Error: Test data not found at {TEST_DATA_PATH}")
        print("   Run the data preparation step first")
        return False
    
    # Load LiveResearchBench dataset
    print(f"\n📥 Loading LiveResearchBench dataset from HuggingFace...")
    print(f"   Dataset: Salesforce/LiveResearchBench")
    print(f"   Mode: {'Realtime (with placeholder replacement)' if USE_REALTIME_PLACEHOLDERS else 'Static (no placeholders)'}")
    benchmark_data = load_liveresearchbench_dataset(use_realtime=USE_REALTIME_PLACEHOLDERS)
    if not benchmark_data:
        print(f"❌ Error: Failed to load benchmark dataset")
        return False
    print(f"   ✅ Loaded {len(benchmark_data)} benchmark questions")
    
    all_results = {}
    
    try:
        # Run all 5 criteria tests
        all_results["presentation"] = await test_presentation_grading()
        all_results["consistency"] = await test_consistency_grading()
        all_results["coverage"] = await test_coverage_grading(benchmark_data)
        all_results["citation"] = await test_citation_grading()
        all_results["depth"] = await test_depth_grading()
        
        # Summary
        print("\n" + "="*80)
        print("📊 Test Summary")
        print("="*80)
        print(f"✅ All tests completed successfully!")
        print(f"   1. Presentation: {len(all_results['presentation'])} reports graded")
        print(f"   2. Consistency: {len(all_results['consistency'])} reports graded")
        print(f"   3. Coverage: {len(all_results['coverage'])} reports graded")
        print(f"   4. Citation: {len(all_results['citation'])} reports graded")
        print(f"   5. Depth: {len(all_results['depth'])} pairwise comparisons")
        
        total_calls = (len(all_results['presentation']) + 
                       len(all_results['consistency']) + 
                       len(all_results['coverage']) + 
                       len(all_results['citation']) + 
                       len(all_results['depth']))
        print(f"\nTotal API calls made: ~{total_calls}")
        
        # Save results
        output_dir = Path("results/test_real_grading")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / "grading_results.json"
        with open(output_file, 'w') as f:
            json.dump(all_results, f, indent=2)
        
        print(f"\n💾 Results saved to: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print(f"Python: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
