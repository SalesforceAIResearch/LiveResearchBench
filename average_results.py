#!/usr/bin/env python3
"""
Average results from multiple provider runs.

Usage:
    # Average two CSV summary files
    python average_results.py \
        --input-a results/run_gpt5/summary.csv \
        --input-b results/run_gemini/summary.csv \
        --output results/averaged_summary.csv
    
    # Average two JSON result files
    python average_results.py \
        --input-a results/reports_graded_gpt5.json \
        --input-b results/reports_graded_gemini.json \
        --output results/reports_averaged.json
"""

import argparse
import json
import sys
import pandas as pd
from pathlib import Path


def average_criterion_scores(results_a: dict, results_b: dict) -> dict:
    """
    Average scores from two provider results for a single criterion.
    
    Args:
        results_a: Results from provider A
        results_b: Results from provider B
        
    Returns:
        Averaged results
    """
    averaged = {
        'provider_a': results_a.get('provider', 'unknown'),
        'provider_b': results_b.get('provider', 'unknown'),
        'averaged_at': pd.Timestamp.now().isoformat()
    }
    
    # Average score
    if 'score' in results_a and 'score' in results_b:
        averaged['score'] = (results_a['score'] + results_b['score']) / 2
        averaged['score_a'] = results_a['score']
        averaged['score_b'] = results_b['score']
    
    # Average issue count if present
    if 'total_issues' in results_a and 'total_issues' in results_b:
        averaged['total_issues'] = (results_a['total_issues'] + results_b['total_issues']) / 2
        averaged['total_issues_a'] = results_a['total_issues']
        averaged['total_issues_b'] = results_b['total_issues']
    
    # Combine specific issues
    if 'specific_issues' in results_a and 'specific_issues' in results_b:
        averaged['specific_issues_a'] = results_a['specific_issues']
        averaged['specific_issues_b'] = results_b['specific_issues']
    
    return averaged


def average_json_results(json_a_path: str, json_b_path: str, output_path: str):
    """Average two JSON result files."""
    print(f"📄 Loading JSON files...")
    with open(json_a_path) as f:
        data_a = json.load(f)
    with open(json_b_path) as f:
        data_b = json.load(f)
    
    reports_a = {r['query_id']: r for r in data_a.get('reports', [])}
    reports_b = {r['query_id']: r for r in data_b.get('reports', [])}
    
    print(f"Found {len(reports_a)} reports in file A, {len(reports_b)} reports in file B")
    
    # Find common query IDs
    common_qids = set(reports_a.keys()) & set(reports_b.keys())
    print(f"Found {len(common_qids)} matching reports")
    
    # Average results
    averaged_reports = []
    for qid in common_qids:
        report = reports_a[qid].copy()
        
        # Find grading result keys (e.g., presentation_grading_results, consistency_grading_results)
        grading_keys = [k for k in report.keys() if k.endswith('_grading_results')]
        
        for key in grading_keys:
            if key in reports_b[qid]:
                report[key] = average_criterion_scores(
                    report[key],
                    reports_b[qid][key]
                )
        
        averaged_reports.append(report)
    
    # Save averaged results
    output_data = {
        'metadata': {
            'averaged_from': {
                'file_a': json_a_path,
                'file_b': json_b_path
            },
            'total_reports': len(averaged_reports),
            'averaged_at': pd.Timestamp.now().isoformat()
        },
        'reports': averaged_reports
    }
    
    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"✅ Averaged {len(averaged_reports)} reports")
    print(f"📄 Saved to: {output_path}")


def average_csv_summaries(csv_a_path: str, csv_b_path: str, output_path: str):
    """Average two CSV summary files."""
    print(f"📄 Loading CSV files...")
    df_a = pd.read_csv(csv_a_path)
    df_b = pd.read_csv(csv_b_path)
    
    # Merge on model column (or first column)
    merge_col = 'model' if 'model' in df_a.columns else df_a.columns[0]
    merged = df_a.merge(df_b, on=merge_col, suffixes=('_a', '_b'))
    
    print(f"Found {len(merged)} matching rows")
    
    # Average numeric columns
    numeric_cols = df_a.select_dtypes(include=['number']).columns
    for col in numeric_cols:
        if col != merge_col:
            if f'{col}_a' in merged.columns and f'{col}_b' in merged.columns:
                merged[f'{col}_avg'] = (merged[f'{col}_a'] + merged[f'{col}_b']) / 2
    
    # Save
    merged.to_csv(output_path, index=False)
    print(f"✅ Averaged CSV summary")
    print(f"📄 Saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Average multi-provider results")
    
    parser.add_argument(
        "--input-a",
        required=True,
        help="First input file (JSON or CSV)"
    )
    
    parser.add_argument(
        "--input-b",
        required=True,
        help="Second input file (JSON or CSV)"
    )
    
    parser.add_argument(
        "--output",
        required=True,
        help="Output file"
    )
    
    args = parser.parse_args()
    
    try:
        # Determine file type
        if args.input_a.endswith('.csv'):
            average_csv_summaries(args.input_a, args.input_b, args.output)
        else:
            average_json_results(args.input_a, args.input_b, args.output)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

