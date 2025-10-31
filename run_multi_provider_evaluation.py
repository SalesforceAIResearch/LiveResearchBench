#!/usr/bin/env python3
"""
Multi-provider evaluation with automatic state tracking and resume capability.

This script orchestrates grading with multiple providers (OpenAI, Gemini) and
automatically handles interruptions, resuming from where it left off.

Usage:
    # Start or resume evaluation
    python run_multi_provider_evaluation.py --config configs/multi_provider_config.yaml
    
    # Force restart from beginning
    python run_multi_provider_evaluation.py --config configs/multi_provider_config.yaml --restart
"""

import argparse
import yaml
import json
import sys
import subprocess
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional


class MultiProviderEvaluator:
    """Orchestrates multi-provider evaluation with state tracking."""
    
    def __init__(self, config_path: str, restart: bool = False):
        """
        Initialize evaluator.
        
        Args:
            config_path: Path to YAML config file
            restart: If True, ignore existing state and restart
        """
        self.config_path = config_path
        self.config = self._load_config(config_path)
        self.restart = restart
        
        # Create state directory
        self.state_dir = Path(self.config.get('state_dir', 'evaluation_state'))
        self.state_dir.mkdir(exist_ok=True)
        
        # State file path
        run_name = self.config.get('run_name', 'default_run')
        self.state_file = self.state_dir / f"{run_name}_state.json"
        
        # Load or initialize state
        self.state = self._load_state()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load YAML configuration."""
        print(f"📋 Loading config from: {config_path}")
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        # Validate required fields
        required = ['input_files', 'criteria', 'providers']
        for field in required:
            if field not in config:
                raise ValueError(f"Missing required field in config: {field}")
        
        return config
    
    def _load_state(self) -> Dict[str, Any]:
        """Load state from file or create new."""
        if self.restart or not self.state_file.exists():
            print("🆕 Starting new evaluation")
            return {
                'started_at': datetime.now().isoformat(),
                'status': 'in_progress',
                'completed_providers': [],
                'completed_files': {},
                'output_dirs': {}
            }
        else:
            print(f"📂 Loading state from: {self.state_file}")
            with open(self.state_file) as f:
                state = json.load(f)
            print(f"   Status: {state.get('status', 'unknown')}")
            print(f"   Completed providers: {', '.join(state.get('completed_providers', []))}")
            return state
    
    def _save_state(self):
        """Save current state to file."""
        self.state['last_updated'] = datetime.now().isoformat()
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
        print(f"💾 State saved to: {self.state_file}")
    
    def run_grading_for_provider(self, provider: str, model: Optional[str] = None) -> str:
        """
        Run grading for a single provider.
        
        Args:
            provider: Provider name (openai, gemini)
            model: Optional specific model
            
        Returns:
            Output directory path
        """
        # Check if already completed
        if provider in self.state['completed_providers'] and not self.restart:
            print(f"⏭️  Provider '{provider}' already completed, skipping")
            return self.state['output_dirs'].get(provider, '')
        
        print("\n" + "="*80)
        print(f"🚀 Starting grading with provider: {provider}")
        if model:
            print(f"   Model: {model}")
        print("="*80)
        
        # Get config
        input_files = self.config['input_files']
        criteria = self.config['criteria']
        output_dir = self.config.get('output_dir', 'results')
        max_concurrent = self.config.get('max_concurrent', 5)
        
        # Create provider-specific output directory
        provider_output_dir = os.path.join(output_dir, provider)
        os.makedirs(provider_output_dir, exist_ok=True)
        
        # Process each input file
        for input_file in input_files:
            file_key = f"{provider}:{input_file}"
            
            # Check if file already processed
            if file_key in self.state.get('completed_files', {}) and not self.restart:
                print(f"   ⏭️  File already processed: {Path(input_file).name}")
                continue
            
            print(f"\n📄 Processing: {Path(input_file).name}")
            
            # Build command
            cmd = [
                'python', 'main.py',
                '--input', input_file,
                '--criteria', ','.join(criteria),
                '--provider', provider,
                '--output-dir', provider_output_dir,
                '--max-concurrent', str(max_concurrent)
            ]
            
            if model:
                cmd.extend(['--model', model])
            
            # Run grading
            try:
                result = subprocess.run(cmd, check=True, capture_output=False)
                
                # Mark as completed
                if 'completed_files' not in self.state:
                    self.state['completed_files'] = {}
                self.state['completed_files'][file_key] = datetime.now().isoformat()
                self._save_state()
                
            except subprocess.CalledProcessError as e:
                print(f"\n❌ Error processing {input_file} with {provider}: {e}")
                print("   State saved. You can resume by running the script again.")
                raise
            except KeyboardInterrupt:
                print(f"\n⏸️  Interrupted by user")
                print("   State saved. Resume by running the script again.")
                self._save_state()
                raise
        
        # Mark provider as completed
        if provider not in self.state['completed_providers']:
            self.state['completed_providers'].append(provider)
        self.state['output_dirs'][provider] = provider_output_dir
        self._save_state()
        
        print(f"\n✅ Completed grading with {provider}")
        return provider_output_dir
    
    def average_results(self):
        """Average results from multiple providers."""
        providers = self.config['providers']
        
        if len(providers) < 2:
            print("⏭️  Only one provider, skipping averaging")
            return
        
        print("\n" + "="*80)
        print("📊 Averaging results from multiple providers")
        print("="*80)
        
        # Get output directories
        output_dirs = self.state.get('output_dirs', {})
        
        if len(output_dirs) < 2:
            print("⚠️  Not enough provider results to average")
            return
        
        # Find summary files from each provider
        provider_summaries = {}
        for provider, output_dir in output_dirs.items():
            # Look for summary files
            provider_path = Path(output_dir)
            summary_files = list(provider_path.glob("*/summary_*.json"))
            
            if summary_files:
                # Use the most recent summary file
                latest_summary = max(summary_files, key=lambda p: p.stat().st_mtime)
                provider_summaries[provider] = str(latest_summary)
                print(f"   {provider}: {latest_summary.name}")
        
        if len(provider_summaries) < 2:
            print("⚠️  Not enough summary files found for averaging")
            return
        
        # Average pairwise (for now, just average first two)
        providers_list = list(provider_summaries.keys())
        provider_a = providers_list[0]
        provider_b = providers_list[1]
        
        summary_a = provider_summaries[provider_a]
        summary_b = provider_summaries[provider_b]
        
        # Create averaged output directory
        averaged_dir = os.path.join(self.config.get('output_dir', 'results'), 'averaged')
        os.makedirs(averaged_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
        output_file = os.path.join(averaged_dir, f"summary_multi_judge_{timestamp}.json")
        
        print(f"\n🔄 Averaging: {provider_a} + {provider_b}")
        
        # Run averaging
        cmd = [
            'python', 'average_results.py',
            '--input-a', summary_a,
            '--input-b', summary_b,
            '--output', output_file
        ]
        
        try:
            subprocess.run(cmd, check=True)
            
            self.state['averaged_output'] = output_file
            self.state['averaged_at'] = datetime.now().isoformat()
            self._save_state()
            
            print(f"\n✅ Averaged results saved to: {output_file}")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error averaging results: {e}")
            raise
    
    def run(self):
        """Run the complete multi-provider evaluation."""
        try:
            providers = self.config['providers']
            models = self.config.get('models', {})
            
            print(f"\n📋 Evaluation Plan:")
            print(f"   Providers: {', '.join(providers)}")
            print(f"   Criteria: {', '.join(self.config['criteria'])}")
            print(f"   Input files: {len(self.config['input_files'])}")
            
            # Grade with each provider
            for provider in providers:
                model = models.get(provider)
                self.run_grading_for_provider(provider, model)
            
            # Average results
            if len(providers) > 1:
                self.average_results()
            
            # Mark as completed
            self.state['status'] = 'completed'
            self.state['completed_at'] = datetime.now().isoformat()
            self._save_state()
            
            print("\n" + "="*80)
            print("🎉 EVALUATION COMPLETE!")
            print("="*80)
            print(f"📁 Results location: {self.config.get('output_dir', 'results')}")
            
            if 'averaged_output' in self.state:
                print(f"📊 Averaged summary: {self.state['averaged_output']}")
            
            return True
            
        except KeyboardInterrupt:
            print("\n⏸️  Evaluation interrupted")
            print("   Run the script again to resume from where you left off")
            return False
        except Exception as e:
            print(f"\n❌ Error during evaluation: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    parser = argparse.ArgumentParser(
        description="Multi-provider evaluation with automatic resume capability"
    )
    
    parser.add_argument(
        "--config",
        required=True,
        help="Path to YAML configuration file"
    )
    
    parser.add_argument(
        "--restart",
        action="store_true",
        help="Restart evaluation from beginning (ignore existing state)"
    )
    
    args = parser.parse_args()
    
    # Create and run evaluator
    evaluator = MultiProviderEvaluator(args.config, restart=args.restart)
    success = evaluator.run()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

