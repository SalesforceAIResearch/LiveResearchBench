#!/usr/bin/env python3
"""
Grade research reports across multiple criteria.

Usage:
    # Single file, single criterion
    python main.py --input reports.json --criteria presentation --provider gemini
    
    # Single file, multiple criteria
    python main.py --input reports.json \
        --criteria presentation,coverage,consistency,citation,depth \
        --provider openai --model gpt-5-2025-08-07
    
    # Batch grade all models (from config)
    python main.py --batch --config configs/batch_config.yaml \
        --provider gemini --model gemini-2.5-pro
    
    # Resume existing run
    python main.py --batch --config configs/batch_config.yaml \
        --provider gemini --run-id experiment_v1
"""

import argparse
import yaml
import sys
from pathlib import Path
from liveresearchbench.batch_evaluator import BatchEvaluator


def main():
    parser = argparse.ArgumentParser(description="Grade research reports")
    
    # Mode selection
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Batch mode: grade multiple JSON files from config"
    )
    
    # Single file mode
    parser.add_argument(
        "--input",
        help="Input JSON file (for single file mode)"
    )
    
    parser.add_argument(
        "--criteria",
        help="Comma-separated criteria: presentation,coverage,consistency,citation,depth"
    )
    
    # Provider settings (required)
    parser.add_argument(
        "--provider",
        required=True,
        choices=['openai', 'gemini'],
        help="AI provider: openai or gemini"
    )
    
    parser.add_argument(
        "--model",
        help="Specific model (e.g., gpt-5-2025-08-07, gemini-2.5-pro)"
    )
    
    # Batch mode
    parser.add_argument(
        "--config",
        help="Batch config YAML file (for batch mode)"
    )
    
    parser.add_argument(
        "--run-id",
        help="Run ID for resuming/debugging (optional)"
    )
    
    # Common options
    parser.add_argument(
        "--output-dir",
        default="results",
        help="Output directory for results"
    )
    
    parser.add_argument(
        "--max-concurrent",
        type=int,
        default=5,
        help="Maximum concurrent API calls"
    )
    
    parser.add_argument(
        "--force-regrade",
        action="store_true",
        help="Force re-grading even if already graded"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Create evaluator
    evaluator = BatchEvaluator(
        provider=args.provider,
        model=args.model,
        output_dir=args.output_dir,
        max_concurrent=args.max_concurrent,
        verbose=args.verbose
    )
    
    try:
        if args.batch:
            # Batch mode
            if not args.config:
                parser.error("--config required for batch mode")
            
            print(f"📋 Loading batch config: {args.config}")
            with open(args.config) as f:
                config = yaml.safe_load(f)
            
            evaluator.evaluate_batch(
                config=config,
                run_id=args.run_id,
                force_regrade=args.force_regrade
            )
        else:
            # Single file mode
            if not args.input or not args.criteria:
                parser.error("--input and --criteria required for single file mode")
            
            criteria = args.criteria.split(",")
            
            print(f"📄 Processing single file: {args.input}")
            print(f"🎯 Criteria: {', '.join(criteria)}")
            
            evaluator.evaluate_single(
                input_file=args.input,
                criteria=criteria,
                force_regrade=args.force_regrade
            )
        
        print("\n✅ Grading completed successfully!")
        return 0
        
    except Exception as e:
        print(f"\n❌ Error during grading: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

