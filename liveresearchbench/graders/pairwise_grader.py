"""Pairwise grader for comparative evaluation."""

import logging
from typing import Dict, Any, Optional, Tuple

from .base_grader import BaseGrader
from liveresearchbench.criteria.depth import (
    DEPTH_COMPARISON_SCHEMA,
    create_depth_comparison_prompt,
    create_depth_user_prompt
)

logger = logging.getLogger(__name__)


class PairwiseGrader(BaseGrader):
    """Grader for pairwise comparison evaluation (Analysis Depth)."""
    
    def __init__(self):
        """Initialize the pairwise grader."""
        super().__init__()
    
    async def compare_depth_async(self, query: str, report_a: str, report_b: str,
                                 provider: str = "gemini", model: str = None,
                                 use_three_judges: bool = True) -> Dict[str, Any]:
        """
        Compare two reports for analysis depth.
        
        Args:
            query: Original research query
            report_a: First report content
            report_b: Second report content
            provider: AI provider (gemini or openai)
            model: Specific model to use
            use_three_judges: If True, use 3 judges with majority voting; if False, use single judge
            
        Returns:
            Dictionary with comparison results
        """
        client = self._create_client(provider, model)
        
        # Create prompts
        system_prompt = create_depth_comparison_prompt()
        user_prompt = create_depth_user_prompt(query, report_a, report_b)
        
        if use_three_judges:
            return await self._compare_with_three_judges(client, system_prompt, user_prompt)
        else:
            return await self._compare_single_judge(client, system_prompt, user_prompt)
    
    async def _compare_single_judge(self, client, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """Compare reports using a single judge."""
        try:
            result = await client.generate_with_schema_async(
                user_prompt=user_prompt,
                system_prompt=system_prompt,
                schema=DEPTH_COMPARISON_SCHEMA
            )
            
            return {
                'winner': result.get('winner', 'tie'),
                'scores': result.get('scores', {}),
                'justification': result.get('justification', ''),
                'major_flaws': result.get('major_flaws', {'A': [], 'B': []}),
                'judge_count': 1
            }
            
        except Exception as e:
            logger.error(f"Error in depth comparison: {e}")
            raise
    
    async def _compare_with_three_judges(self, client, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """Compare reports using three independent judges with majority voting."""
        import asyncio
        
        # Run three judges in parallel
        judge_tasks = [
            client.generate_with_schema_async(user_prompt, system_prompt, DEPTH_COMPARISON_SCHEMA)
            for _ in range(3)
        ]
        
        try:
            judge_results = await asyncio.gather(*judge_tasks)
            
            # Extract winners from each judge
            individual_winners = [result.get('winner', 'tie') for result in judge_results]
            
            # Count votes
            winner_counts = {'A': 0, 'B': 0, 'tie': 0}
            for winner in individual_winners:
                winner_counts[winner] += 1
            
            # Determine final winner by majority vote
            final_winner = max(winner_counts, key=winner_counts.get)
            
            # Average scores across judges
            avg_scores = {'A': {}, 'B': {}}
            dimensions = ['granularity', 'insight', 'critique', 'evidence', 'density']
            
            for report in ['A', 'B']:
                for dim in dimensions:
                    scores = [result['scores'][report][dim] for result in judge_results]
                    avg_scores[report][dim] = sum(scores) / len(scores)
                avg_scores[report]['total'] = sum(avg_scores[report].values())
            
            # Collect all major flaws
            all_flaws = {'A': set(), 'B': set()}
            for result in judge_results:
                for report in ['A', 'B']:
                    all_flaws[report].update(result.get('major_flaws', {}).get(report, []))
            
            # Combine justifications
            justifications = [result.get('justification', '') for result in judge_results]
            combined_justification = f"Majority vote: {final_winner}. " + " | ".join(justifications)
            
            return {
                'winner': final_winner,
                'scores': avg_scores,
                'justification': combined_justification,
                'major_flaws': {k: list(v) for k, v in all_flaws.items()},
                'judge_count': 3,
                'three_judge_details': {
                    'individual_winners': individual_winners,
                    'winner_counts': winner_counts,
                    'individual_results': judge_results
                }
            }
            
        except Exception as e:
            logger.error(f"Error in three-judge depth comparison: {e}")
            raise
    
    async def grade_async(self, query: str, report_content: str, criterion: str,
                         provider: str = "gemini", model: str = None,
                         current_date: str = None, **kwargs) -> Dict[str, Any]:
        """
        Grade using pairwise comparison (requires two reports).
        
        Args:
            query: Original research query
            report_content: First report (report_a)
            criterion: Criterion name ('depth')
            provider: AI provider
            model: Specific model to use
            current_date: Current date (unused for pairwise)
            **kwargs: Must include 'report_b' and optionally 'use_three_judges'
            
        Returns:
            Dictionary with comparison results
        """
        if criterion.lower() != 'depth':
            raise ValueError(f"Unknown pairwise criterion: {criterion}")
        
        report_b = kwargs.get('report_b')
        if not report_b:
            raise ValueError("report_b required for pairwise depth comparison")
        
        use_three_judges = kwargs.get('use_three_judges', True)
        
        return await self.compare_depth_async(
            query, report_content, report_b, provider, model, use_three_judges
        )

