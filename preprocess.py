#!/usr/bin/env python3
"""
Preprocess research reports from MD files to JSON format.

Usage:
    # Preprocess single experiment
    python preprocess.py exp_name1 exp_name2 --output-dir extracted_reports/
    
    # With custom base path
    python preprocess.py exp_name --base-path /path/to/reports/ --output-dir out/
"""

import argparse
import sys
from liveresearchbench.common.io_utils import preprocess_reports


def main():
    parser = argparse.ArgumentParser(
        description="Preprocess research reports from directory structure to JSON"
    )
    
    parser.add_argument("exp_names", nargs="+", help="Experiment names to process")
    
    parser.add_argument(
        "--base-path",
        default="/export/xgen-small/mas_eval/openmas_link/open_deep_research/research_outputs",
        help="Base path to experiments"
    )
    
    parser.add_argument(
        "--output-dir",
        default="extracted_reports",
        help="Output directory for JSON files"
    )
    
    parser.add_argument(
        "--query-csv",
        default=None,
        help="Path to query mapping CSV file (optional, defaults to HuggingFace dataset)"
    )
    
    parser.add_argument(
        "--use-realtime",
        action="store_true",
        help="Replace temporal placeholders ({{current_year}}, etc.) with current values"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    try:
        json_file = preprocess_reports(
            base_path=args.base_path,
            exp_names=args.exp_names,
            output_dir=args.output_dir,
            query_csv=args.query_csv,
            verbose=args.verbose,
            use_realtime=args.use_realtime
        )
        
        print(f"\n✅ Preprocessing completed successfully!")
        print(f"📄 Output JSON: {json_file}")
        return 0
        
    except Exception as e:
        print(f"\n❌ Error during preprocessing: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

