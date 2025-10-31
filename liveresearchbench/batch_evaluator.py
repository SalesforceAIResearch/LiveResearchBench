"""Batch evaluator for grading multiple JSON files across multiple criteria."""

import os
import json
import asyncio
import logging
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from liveresearchbench.common.io_utils import load_json, save_json, load_report_content
from liveresearchbench.graders.checklist_grader import ChecklistGrader
from liveresearchbench.graders.pointwise_grader import PointwiseGrader
from liveresearchbench.graders.pairwise_grader import PairwiseGrader
from liveresearchbench.common.io_utils import (
    load_liveresearchbench_dataset,
    get_checklists_for_qid
)

logger = logging.getLogger(__name__)


class BatchEvaluator:
    """Batch evaluator for grading multiple reports across multiple criteria."""
    
    def __init__(self, provider: str, model: str = None, output_dir: str = "results",
                 max_concurrent: int = 5, verbose: bool = False):
        """
        Initialize batch evaluator.
        
        Args:
            provider: AI provider (gemini or openai)
            model: Specific model to use
            output_dir: Output directory for results
            max_concurrent: Maximum concurrent evaluations
            verbose: Enable verbose logging
        """
        self.provider = provider
        self.model = model
        self.output_dir = output_dir
        self.max_concurrent = max_concurrent
        
        if verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        
        # Initialize graders
        self.checklist_grader = ChecklistGrader()
        self.pointwise_grader = PointwiseGrader()
        self.pairwise_grader = PairwiseGrader()
        
        # Semaphore for concurrency control
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def grade_single_report(self, report_data: Dict[str, Any], criterion: str,
                                 skip_existing: bool = True, **kwargs) -> Dict[str, Any]:
        """
        Grade a single report on a single criterion.
        
        Args:
            report_data: Report data dictionary
            criterion: Criterion name
            skip_existing: Skip if already graded
            **kwargs: Additional criterion-specific arguments
            
        Returns:
            Updated report data with grading results
        """
        # Check if already graded
        result_key = f"{criterion}_grading_results"
        if skip_existing and result_key in report_data:
            logger.info(f"⏭️  Skipping already graded: {report_data.get('query_id', 'unknown')} - {criterion}")
            return report_data
        
        # Load report content
        report_file_path = report_data.get('report_file_path', '')
        report_content = load_report_content(report_file_path)
        
        if not report_content:
            logger.error(f"Could not load report: {report_file_path}")
            return report_data
        
        # Get query
        query = report_data.get('query', '')
        if not query:
            logger.error(f"No query for {report_data.get('query_id', 'unknown')}")
            return report_data
        
        # Use semaphore for concurrency control
        async with self.semaphore:
            try:
                # Grade based on criterion type
                if criterion in ['presentation', 'coverage']:
                    result = await self._grade_checklist(report_data, criterion, query, report_content, **kwargs)
                elif criterion in ['consistency', 'citation']:
                    result = await self._grade_pointwise(report_data, criterion, query, report_content)
                elif criterion == 'depth':
                    # Load reference report for pairwise comparison
                    from liveresearchbench.common.reference_reports import load_reference_report, REFERENCE_MODEL_NAME
                    
                    query_id = report_data.get('query_id', '')
                    reference_content = load_reference_report(query_id)
                    
                    if not reference_content:
                        logger.warning(f"No reference report found for {query_id} - skipping depth comparison")
                        return report_data
                    
                    # Don't compare reference model against itself
                    if report_data.get('model_name') == REFERENCE_MODEL_NAME:
                        logger.info(f"Skipping depth comparison for reference model itself")
                        return report_data
                    
                    result = await self._grade_pairwise(report_data, criterion, query, report_content, reference_content)
                else:
                    logger.error(f"Unknown criterion: {criterion}")
                    return report_data
                
                # Add results to report data
                report_data_copy = report_data.copy()
                report_data_copy[result_key] = result
                
                logger.info(f"✅ Graded {report_data.get('query_id', 'unknown')} - {criterion}")
                return report_data_copy
                
            except Exception as e:
                logger.error(f"Error grading {report_data.get('query_id', 'unknown')} - {criterion}: {e}")
                return report_data
    
    async def _grade_checklist(self, report_data: Dict, criterion: str, query: str, 
                              report_content: str, **kwargs) -> Dict[str, Any]:
        """Grade using checklist grader."""
        if criterion == 'coverage':
            # Get benchmark data (should be pre-loaded with correct use_realtime setting)
            benchmark_data = kwargs.get('benchmark_data')
            if not benchmark_data:
                # Fallback: load with default settings (should not happen in normal flow)
                logger.warning("Benchmark data not pre-loaded, loading with use_realtime=False")
                benchmark_data = load_liveresearchbench_dataset(use_realtime=False)
            
            qid = report_data.get('query_id', '')
            checklists_for_qid = get_checklists_for_qid(benchmark_data, qid)
            
            if not checklists_for_qid:
                logger.warning(f"No checklists found for qid: {qid}")
                return {
                    'provider': self.provider,
                    'model': self.model or 'default',
                    'graded_at': datetime.now().isoformat(),
                    'error': f'No checklists found for qid: {qid}',
                    'evaluations': {},
                    'summary': {}
                }
            
            result = await self.checklist_grader.grade_coverage_async(
                query, report_content, checklists_for_qid,
                self.provider, self.model
            )
        else:  # presentation
            result = await self.checklist_grader.grade_presentation_async(
                query, report_content, self.provider, self.model
            )
        
        result['provider'] = self.provider
        result['model'] = self.model or 'default'
        result['graded_at'] = datetime.now().isoformat()
        return result
    
    async def _grade_pointwise(self, report_data: Dict, criterion: str, query: str,
                              report_content: str) -> Dict[str, Any]:
        """Grade using pointwise grader."""
        result = await self.pointwise_grader.grade_async(
            query, report_content, criterion, self.provider, self.model
        )
        
        result['provider'] = self.provider
        result['model'] = self.model or 'default'
        result['graded_at'] = datetime.now().isoformat()
        return result
    
    async def _grade_pairwise(self, report_data: Dict, criterion: str, query: str,
                             report_content: str, reference_content: str) -> Dict[str, Any]:
        """Grade using pairwise grader (compare against reference report with position-swap)."""
        from liveresearchbench.common.reference_reports import REFERENCE_MODEL_NAME
        
        result = await self.pairwise_grader.compare_depth_async(
            query=query,
            report_a=report_content,  # The model being evaluated
            report_b=reference_content,  # Reference report (open-deep-research)
            provider=self.provider,
            model=self.model,
            swap_positions=True  # Position-swap averaging to mitigate bias (default)
        )
        
        # Add metadata about comparison
        result['comparison_type'] = 'vs_reference'
        result['reference_model'] = REFERENCE_MODEL_NAME
        result['evaluated_model'] = report_data.get('model_name')
        result['provider'] = self.provider
        result['model'] = self.model or 'default'
        result['graded_at'] = datetime.now().isoformat()
        
        return result
    
    def _generate_summary(self, data: Dict[str, Any], criteria: List[str]) -> Dict[str, Any]:
        """
        Generate summary statistics from graded data.
        
        Args:
            data: Full graded data
            criteria: List of criteria that were evaluated
            
        Returns:
            Summary dictionary with aggregated metrics
        """
        from collections import defaultdict
        
        reports = data.get('reports', [])
        metadata = data.get('metadata', {})
        
        # Initialize statistics
        model_stats = defaultdict(lambda: defaultdict(list))
        overall_stats = defaultdict(list)
        
        # Collect metrics per model and criterion
        for report in reports:
            model_name = report.get('model_name', 'unknown')
            query_id = report.get('query_id', 'unknown')
            
            for criterion in criteria:
                result_key = f"{criterion}_grading_results"
                if result_key not in report:
                    continue
                
                results = report[result_key]
                
                # Extract metrics based on criterion type
                if criterion in ['presentation', 'coverage']:
                    # Checklist-based: use pass rate
                    summary = results.get('summary', {})
                    if 'average_pass_rate' in summary:
                        score = summary['average_pass_rate']
                    elif 'percentage_addressed' in summary:
                        score = summary['percentage_addressed']
                    else:
                        continue
                    model_stats[model_name][criterion].append(score)
                    overall_stats[criterion].append(score)
                    
                elif criterion in ['consistency', 'citation']:
                    # Pointwise: use score
                    score = results.get('score')
                    if score is None:
                        continue
                    model_stats[model_name][criterion].append(score)
                    overall_stats[criterion].append(score)
                    
                elif criterion == 'depth':
                    # Pairwise with position-swap: count winners from both comparisons
                    # winner = 'evaluated_model' means evaluated model beats reference → win
                    # winner = 'reference_model' means reference beats evaluated model → loss
                    # winner = 'tie' means neither wins → tie
                    
                    winner_1 = results.get('winner_comparison_1', 'tie')
                    winner_2 = results.get('winner_comparison_2', 'tie')
                    reference_model = results.get('reference_model', 'open-deep-research')
                    
                    # Initialize depth stats if not exists
                    if 'depth' not in model_stats[model_name]:
                        model_stats[model_name]['depth'] = {
                            'wins': 0,  # Evaluated model beats reference
                            'losses': 0,  # Reference beats evaluated model
                            'ties': 0,
                            'total': 0,
                            'reference_model': reference_model
                        }
                    if 'depth' not in overall_stats:
                        overall_stats['depth'] = {
                            'wins': 0,
                            'losses': 0,
                            'ties': 0,
                            'total': 0,
                        }
                    
                    # Count wins/losses/ties from BOTH comparisons
                    for winner in [winner_1, winner_2]:
                        if winner == 'evaluated_model':
                            model_stats[model_name]['depth']['wins'] += 1
                            overall_stats['depth']['wins'] += 1
                        elif winner == 'reference_model':
                            model_stats[model_name]['depth']['losses'] += 1
                            overall_stats['depth']['losses'] += 1
                        else:  # tie
                            model_stats[model_name]['depth']['ties'] += 1
                            overall_stats['depth']['ties'] += 1
                        
                        model_stats[model_name]['depth']['total'] += 1
                        overall_stats['depth']['total'] += 1
        
        # Calculate averages
        model_averages = {}
        for model_name, criteria_scores in model_stats.items():
            model_averages[model_name] = {}
            for criterion, data in criteria_scores.items():
                if criterion == 'depth':
                    # Depth: calculate win rate vs reference (excluding ties)
                    total = data['total']
                    wins = data['wins']
                    losses = data['losses']
                    ties = data['ties']
                    decisive_games = wins + losses  # Exclude ties
                    
                    if total > 0:
                        model_averages[model_name][criterion] = {
                            'wins': wins,  # Times this model beat reference
                            'losses': losses,  # Times reference beat this model
                            'ties': ties,
                            'total': total,
                            'decisive_games': decisive_games,
                            'win_rate': (wins / decisive_games * 100) if decisive_games > 0 else 0,
                            'reference_model': data.get('reference_model', 'open-deep-research')
                        }
                elif isinstance(data, list) and data:
                    # Other criteria: standard statistics
                    model_averages[model_name][criterion] = {
                        'mean': sum(data) / len(data),
                        'count': len(data),
                        'min': min(data),
                        'max': max(data)
                    }
        
        overall_averages = {}
        for criterion, data in overall_stats.items():
            if criterion == 'depth':
                # Depth: calculate overall win rate (excluding ties)
                total = data['total']
                wins = data['wins']
                losses = data['losses']
                ties = data['ties']
                decisive_games = wins + losses  # Exclude ties
                
                if total > 0:
                    overall_averages[criterion] = {
                        'wins': wins,
                        'losses': losses,
                        'ties': ties,
                        'total': total,
                        'decisive_games': decisive_games,
                        'win_rate': (wins / decisive_games * 100) if decisive_games > 0 else 0,
                    }
            elif isinstance(data, list) and data:
                # Other criteria: standard statistics
                overall_averages[criterion] = {
                    'mean': sum(data) / len(data),
                    'count': len(data),
                    'min': min(data),
                    'max': max(data)
                }
        
        # Build summary
        summary = {
            'metadata': {
                'provider': self.provider,
                'model': self.model or 'default',
                'graded_at': datetime.now().isoformat(),
                'total_reports': len(reports),
                'criteria_evaluated': criteria,
                'input_metadata': metadata
            },
            'results_by_model': model_averages,
            'overall_results': overall_averages
        }
        
        return summary
    
    def _print_summary_to_terminal(self, summary_data: Dict[str, Any], output_dir: str):
        """
        Print summary results to terminal in a readable format.
        
        Args:
            summary_data: Summary dictionary
            output_dir: Output directory path
        """
        print("\n" + "="*80)
        print("📊 GRADING SUMMARY")
        print("="*80)
        
        metadata = summary_data.get('metadata', {})
        print(f"\n🔍 Provider: {metadata.get('provider', 'unknown')}")
        print(f"🤖 Model: {metadata.get('model', 'unknown')}")
        print(f"📅 Graded at: {metadata.get('graded_at', 'unknown')}")
        print(f"📝 Total reports: {metadata.get('total_reports', 0)}")
        print(f"🎯 Criteria: {', '.join(metadata.get('criteria_evaluated', []))}")
        
        # Print overall results
        overall_results = summary_data.get('overall_results', {})
        if overall_results:
            print("\n" + "-"*80)
            print("📈 OVERALL RESULTS (across all models)")
            print("-"*80)
            for criterion, stats in overall_results.items():
                print(f"\n{criterion.upper()}:")
                if criterion == 'depth':
                    # Depth: show win rate (excluding ties)
                    wins = stats.get('wins', 0)
                    losses = stats.get('losses', 0)
                    ties = stats.get('ties', 0)
                    decisive = stats.get('decisive_games', wins + losses)
                    print(f"  Win Rate (vs reference): {stats.get('win_rate', 0):.2f}% ({wins}/{decisive}, {ties} ties)")
                else:
                    # Other criteria: standard stats
                    print(f"  Mean:  {stats.get('mean', 0):.2f}")
                    print(f"  Min:   {stats.get('min', 0):.2f}")
                    print(f"  Max:   {stats.get('max', 0):.2f}")
                    print(f"  Count: {stats.get('count', 0)}")
        
        # Print per-model results
        results_by_model = summary_data.get('results_by_model', {})
        if results_by_model:
            print("\n" + "-"*80)
            print("🏆 RESULTS BY MODEL")
            print("-"*80)
            for model_name, criteria_stats in results_by_model.items():
                print(f"\n📦 {model_name}:")
                for criterion, stats in criteria_stats.items():
                    if criterion == 'depth':
                        # Depth: show win rate vs reference (excluding ties)
                        ref_model = stats.get('reference_model', 'reference')
                        decisive = stats.get('decisive_games', 0)
                        wins = stats.get('wins', 0)
                        losses = stats.get('losses', 0)
                        ties = stats.get('ties', 0)
                        
                        print(f"  {criterion} (vs {ref_model}):")
                        print(f"    Win Rate: {stats.get('win_rate', 0):.2f}% ({wins}/{decisive}) "
                              f"[W:{wins} L:{losses} T:{ties}]")
                    else:
                        # Other criteria: standard stats
                        print(f"  {criterion}:")
                        print(f"    Mean: {stats.get('mean', 0):.2f} | "
                              f"Min: {stats.get('min', 0):.2f} | "
                              f"Max: {stats.get('max', 0):.2f} | "
                              f"Count: {stats.get('count', 0)}")
        
        # Print output location
        print("\n" + "="*80)
        print("💾 RESULTS SAVED TO:")
        print("="*80)
        print(f"📁 Directory: {output_dir}")
        print(f"   ├── summary_{summary_data.get('metadata', {}).get('graded_at', '').replace(':', '-')}.json")
        print(f"   └── detailed_results_{summary_data.get('metadata', {}).get('graded_at', '').replace(':', '-')}.json")
        print("="*80 + "\n")
    
    async def grade_json_file(self, json_file: str, criteria: List[str],
                             force_regrade: bool = False, **kwargs) -> str:
        """
        Grade all reports in a JSON file for specified criteria.
        
        Args:
            json_file: Path to JSON file
            criteria: List of criteria to evaluate
            force_regrade: Force re-grading even if already graded
            **kwargs: Additional arguments (e.g., benchmark_data for coverage)
            
        Returns:
            Path to output JSON file
        """
        logger.info(f"📄 Loading JSON file: {json_file}")
        data = load_json(json_file)
        
        reports = data.get('reports', [])
        logger.info(f"Found {len(reports)} reports")
        
        # Get use_realtime setting from metadata (for coverage criterion)
        metadata = data.get('metadata', {})
        use_realtime = metadata.get('use_realtime', False)
        logger.info(f"📊 Using realtime mode: {use_realtime}")
        
        # Load benchmark data once for all coverage evaluations if needed
        if 'coverage' in criteria and 'benchmark_data' not in kwargs:
            logger.info(f"📥 Loading benchmark dataset (use_realtime={use_realtime})...")
            kwargs['benchmark_data'] = load_liveresearchbench_dataset(use_realtime=use_realtime)
        
        # Grade each report for each criterion
        for criterion in criteria:
            logger.info(f"\n🎯 Grading criterion: {criterion}")
            
            tasks = [
                self.grade_single_report(report, criterion, skip_existing=not force_regrade, **kwargs)
                for report in reports
            ]
            
            graded_reports = await asyncio.gather(*tasks)
            
            # Update reports in data
            reports = graded_reports
        
        # Update metadata
        data['reports'] = reports
        if 'metadata' not in data:
            data['metadata'] = {}
        data['metadata'][f'{self.provider}_grading_completed_at'] = datetime.now().isoformat()
        
        # Create output directory based on input file name
        input_path = Path(json_file)
        model_suffix = f"_{self.model.replace('/', '__')}" if self.model else ""
        run_dir_name = f"{input_path.stem}_graded_{self.provider}{model_suffix}"
        run_output_dir = os.path.join(self.output_dir, run_dir_name)
        os.makedirs(run_output_dir, exist_ok=True)
        
        timestamp = datetime.now().isoformat().replace(':', '-')
        
        detailed_filename = f"detailed_results_{timestamp}.json"
        detailed_output_path = os.path.join(run_output_dir, detailed_filename)
        save_json(data, detailed_output_path)
        logger.info(f"✅ Saved detailed results to: {detailed_output_path}")
        
        summary_data = self._generate_summary(data, criteria)
        summary_filename = f"summary_{timestamp}.json"
        summary_output_path = os.path.join(run_output_dir, summary_filename)
        save_json(summary_data, summary_output_path)
        logger.info(f"📊 Saved summary to: {summary_output_path}")
        
        # Print summary to terminal
        self._print_summary_to_terminal(summary_data, run_output_dir)
        
        return run_output_dir
    
    def evaluate_single(self, input_file: str, criteria: List[str], force_regrade: bool = False):
        """
        Evaluate a single JSON file (synchronous wrapper).
        
        Args:
            input_file: Path to input JSON file
            criteria: List of criteria to evaluate
            force_regrade: Force re-grading
        """
        asyncio.run(self.grade_json_file(input_file, criteria, force_regrade))
    
    def evaluate_batch(self, config: Dict[str, Any], run_id: str = None, force_regrade: bool = False):
        """
        Evaluate multiple JSON files in batch mode (synchronous wrapper).
        
        Args:
            config: Configuration dictionary with 'input_files' and 'criteria'
            run_id: Optional run ID for output naming
            force_regrade: Force re-grading
        """
        input_files = config.get('input_files', [])
        criteria = config.get('criteria', [])
        
        if not input_files:
            raise ValueError("No input files specified in config")
        if not criteria:
            raise ValueError("No criteria specified in config")
        
        logger.info(f"🚀 Starting batch evaluation")
        logger.info(f"  Files: {len(input_files)}")
        logger.info(f"  Criteria: {', '.join(criteria)}")
        logger.info(f"  Provider: {self.provider}")
        if self.model:
            logger.info(f"  Model: {self.model}")
        
        # Process each file
        for i, json_file in enumerate(input_files, 1):
            logger.info(f"\n{'='*60}")
            logger.info(f"Processing file {i}/{len(input_files)}: {Path(json_file).name}")
            logger.info(f"{'='*60}")
            
            try:
                asyncio.run(self.grade_json_file(json_file, criteria, force_regrade))
            except Exception as e:
                logger.error(f"Error processing {json_file}: {e}")
                continue
        
        logger.info(f"\n✅ Batch evaluation complete!")
        logger.info(f"📁 Results saved to: {self.output_dir}")

