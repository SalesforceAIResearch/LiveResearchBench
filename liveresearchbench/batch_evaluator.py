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
from liveresearchbench.criteria.coverage import load_coverage_checklist, get_checklists_for_qid

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
                    # Pairwise requires special handling (compare with another report)
                    logger.warning(f"Depth comparison requires pairwise setup - skipping for single report grading")
                    return report_data
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
            # Load checklists
            checklist_csv = kwargs.get('checklist_csv', 'data/checklists/coverage_checklist.csv')
            checklist_data = load_coverage_checklist(checklist_csv)
            
            qid = report_data.get('query_id', '')
            checklists_for_qid = get_checklists_for_qid(checklist_data, qid)
            
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
                query, report_content, checklists_for_qid['checklists'],
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
    
    async def grade_json_file(self, json_file: str, criteria: List[str],
                             force_regrade: bool = False, **kwargs) -> str:
        """
        Grade all reports in a JSON file for specified criteria.
        
        Args:
            json_file: Path to JSON file
            criteria: List of criteria to evaluate
            force_regrade: Force re-grading even if already graded
            **kwargs: Additional arguments (e.g., checklist_csv for coverage)
            
        Returns:
            Path to output JSON file
        """
        logger.info(f"📄 Loading JSON file: {json_file}")
        data = load_json(json_file)
        
        reports = data.get('reports', [])
        logger.info(f"Found {len(reports)} reports")
        
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
        
        # Save output
        os.makedirs(self.output_dir, exist_ok=True)
        
        input_path = Path(json_file)
        model_suffix = f"_{self.model.replace('/', '-')}" if self.model else ""
        output_filename = f"{input_path.stem}_graded_{self.provider}{model_suffix}.json"
        output_path = os.path.join(self.output_dir, output_filename)
        
        save_json(data, output_path)
        logger.info(f"✅ Saved graded results to: {output_path}")
        
        return output_path
    
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

