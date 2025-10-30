"""I/O utilities for loading, saving, and preprocessing reports."""

import os
import json
import logging
import re
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from datasets import load_dataset

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# HuggingFace dataset configuration
HF_DATASET_NAME = "Salesforce/LiveResearchBench"
HF_SUBSET = "question_with_checklist"
HF_SPLIT = "test"


def replace_placeholders(text: str, use_realtime: bool = False) -> str:
    """
    Replace temporal placeholders in text.
    
    Args:
        text: Text with potential placeholders
        use_realtime: If True, replace with current values; if False, return as-is
        
    Returns:
        Text with placeholders replaced (if use_realtime=True)
    """
    if not use_realtime or not text:
        return text
    
    now = datetime.now()
    current_year = now.year
    last_year = current_year - 1
    current_date = now.strftime("%B %d, %Y")
    
    replacements = {
        "{{current_year}}": str(current_year),
        "{{last_year}}": str(last_year),
        "{{date}}": current_date,
    }
    
    result = text
    for placeholder, value in replacements.items():
        result = result.replace(placeholder, value)
    
    return result


def load_liveresearchbench_dataset(
    dataset_name: str = HF_DATASET_NAME,
    subset: str = HF_SUBSET,
    split: str = HF_SPLIT,
    use_realtime: bool = False
) -> Dict[str, Dict[str, Any]]:
    """
    Load LiveResearchBench dataset from HuggingFace.
    
    Args:
        dataset_name: HuggingFace dataset name
        subset: Dataset subset name (default: question_with_checklist)
        split: Dataset split name (default: test)
        use_realtime: If True, use questions/checklists with placeholders filled;
                     if False, use no_placeholder versions
        
    Returns:
        Dictionary mapping qid to data:
        {
            'qid': {
                'question': 'research query',
                'checklists': ['checklist item 1', 'checklist item 2', ...] (if available)
            }
        }
    """
    try:
        logger.info(f"Loading dataset {dataset_name}/{subset}/{split} from HuggingFace...")
        dataset = load_dataset(dataset_name, subset, split=split)
        
        benchmark_data = {}
        
        for row in dataset:
            qid = row['qid']
            
            # Choose version based on use_realtime flag
            if use_realtime:
                question = replace_placeholders(row.get('question', ''), use_realtime=True)
                checklists_raw = row.get('checklist', [])
                checklists = [replace_placeholders(item, use_realtime=True) for item in (checklists_raw or [])]
            else:
                question = row.get('question_no_placeholder', '')
                checklists = row.get('checklist_no_placeholder', []) or []
            
            benchmark_data[qid] = {
                'qid': qid,
                'question': question,
                'checklists': checklists
            }
        
        logger.info(f"Loaded {len(benchmark_data)} entries from HuggingFace")
        return benchmark_data
        
    except Exception as e:
        logger.error(f"Error loading dataset from HuggingFace: {e}")
        return {}


def get_question_for_qid(benchmark_data: Dict, qid: str) -> Optional[str]:
    """Get question for a specific query ID."""
    if qid in benchmark_data:
        return benchmark_data[qid].get('question')
    
    # Try with qid_ prefix removed
    if qid.startswith('qid_'):
        clean_qid = qid[4:]
        if clean_qid in benchmark_data:
            return benchmark_data[clean_qid].get('question')
    
    # Try adding qid_ prefix
    prefixed_qid = f"qid_{qid}"
    if prefixed_qid in benchmark_data:
        return benchmark_data[prefixed_qid].get('question')
    
    return None


def get_checklists_for_qid(benchmark_data: Dict, qid: str) -> Optional[List[str]]:
    """Get checklist items for a specific query ID."""
    if qid in benchmark_data:
        return benchmark_data[qid].get('checklists', [])
    
    # Try with qid_ prefix removed
    if qid.startswith('qid_'):
        clean_qid = qid[4:]
        if clean_qid in benchmark_data:
            return benchmark_data[clean_qid].get('checklists', [])
    
    # Try adding qid_ prefix
    prefixed_qid = f"qid_{qid}"
    if prefixed_qid in benchmark_data:
        return benchmark_data[prefixed_qid].get('checklists', [])
    
    return None

# Model name mapping
MODEL_NAME_MAPPING = {
    "openai__gpt-4.1": "gpt-4.1",
    "openai__gpt-4o-2024-08-06": "gpt-4o",
    "gemini-2.5-pro": "gemini-2.5-pro"
}


def load_json(file_path: str) -> Dict[str, Any]:
    """Load JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading JSON file {file_path}: {e}")
        raise


def save_json(data: Dict[str, Any], file_path: str, indent: int = 2) -> None:
    """Save data to JSON file."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)
    logger.info(f"Saved JSON to: {file_path}")


def load_report_content(report_file_path: str) -> str:
    """Load content from a report markdown file."""
    try:
        if not os.path.exists(report_file_path):
            logger.warning(f"Report file not found: {report_file_path}")
            return ""
        
        with open(report_file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading report file {report_file_path}: {e}")
        return ""


def load_query_mapping(use_realtime: bool = False) -> Dict[str, str]:
    """
    Load query mapping from HuggingFace.
    
    Args:
        use_realtime: If True, replace placeholders with current values
        
    Returns:
        Dictionary mapping qid to question text
    """
    # Load from HuggingFace
    benchmark_data = load_liveresearchbench_dataset(use_realtime=use_realtime)
    query_mapping = {qid: data['question'] for qid, data in benchmark_data.items()}
    logger.info(f"Loaded {len(query_mapping)} query mappings from HuggingFace")
    return query_mapping


def parse_report_metadata(content: str) -> Dict[str, Any]:
    """Parse metadata from the markdown report content."""
    metadata = {}
    
    parts = content.split('---', 2)
    if len(parts) < 3:
        logging.warning("Could not find metadata section separator")
        return metadata
    
    metadata_section = parts[1].strip()
    report_content = parts[2].strip()
    
    current_section = None
    
    for line in metadata_section.split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
            
        if line.endswith(':') and not line.startswith('-'):
            if line.startswith('**') and line.endswith(':**'):
                current_section = line[2:-3].strip()
            else:
                current_section = line[:-1].strip()
            metadata[current_section] = {}
            continue
        
        if ':' in line:
            if line.startswith('-'):
                key, value = line[1:].split(':', 1)
                key = key.strip()
                value = value.strip()
                
                if current_section and isinstance(metadata.get(current_section), dict):
                    metadata[current_section][key] = value
                else:
                    metadata[key] = value
            elif line.startswith('**') and ':**' in line:
                key_value_split = line.split(':**', 1)
                key_part = key_value_split[0].strip('*').strip()
                if len(key_value_split) > 1:
                    value = key_value_split[1].strip()
                    metadata[key_part] = value
            else:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                metadata[key] = value
    
    metadata['report_content'] = report_content
    
    return metadata


def extract_and_save_report(file_path: str, report_content: str, query_id: str, copy_entire_file: bool = False) -> str:
    """Extract report content and save to separate file."""
    base_path = Path(file_path).parent
    new_filename = f"report_{query_id}_sd0_only_report.md"
    new_file_path = base_path / new_filename
    
    try:
        if copy_entire_file:
            with open(file_path, 'r', encoding='utf-8') as source_f:
                content = source_f.read()
            with open(new_file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        else:
            with open(new_file_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
        return str(new_file_path)
    except Exception as e:
        logger.error(f"Error saving extracted report to {new_file_path}: {e}")
        return ""


def extract_query_id(filename: str) -> Optional[str]:
    """Extract query ID from filename: report_<qid>_sd0.md"""
    match = re.match(r'report_(.+)_sd0\.md$', filename)
    return match.group(1) if match else None


def find_report_files(base_path: str, exp_names: List[str]) -> List[Dict[str, Any]]:
    """Find all report files matching the directory structure."""
    report_files = []
    base_path = Path(base_path)
    
    for exp_name in exp_names:
        exp_path = base_path / exp_name / "same_bb"
        
        if not exp_path.exists():
            logger.warning(f"Experiment path does not exist: {exp_path}")
            continue
            
        logger.info(f"Processing experiment: {exp_name}")
        
        for task_path in exp_path.iterdir():
            if not task_path.is_dir():
                continue
                
            task = task_path.name
            
            for config_path in task_path.iterdir():
                if not config_path.is_dir():
                    continue
                    
                config_name = config_path.name
                
                for model_path in config_path.iterdir():
                    if not model_path.is_dir():
                        continue
                        
                    model_name = model_path.name
                    
                    sd0_path = model_path / "sd0"
                    if not sd0_path.exists():
                        continue
                    
                    for report_file in sd0_path.glob("report_*_sd0.md"):
                        query_id = extract_query_id(report_file.name)
                        if not query_id:
                            logger.warning(f"Could not extract query ID from: {report_file.name}")
                            continue
                            
                        report_files.append({
                            'file_path': str(report_file),
                            'exp_name': exp_name,
                            'task': task,
                            'config_name': config_name,
                            'model_name': model_name,
                            'query_id': query_id
                        })
    
    logger.info(f"Found {len(report_files)} report files")
    return report_files


def process_report_file(file_info: Dict[str, Any], query_mapping: Dict[str, str], base_path: str = "") -> Optional[Dict[str, Any]]:
    """Process a single report file and extract all data."""
    try:
        with open(file_info['file_path'], 'r', encoding='utf-8') as f:
            content = f.read()
        
        needs_metadata_extraction = ("deerflow" in base_path.lower() or "open_deep_research" in base_path.lower())
        
        original_model = file_info['model_name']
        mapped_model = MODEL_NAME_MAPPING.get(original_model, original_model)
        
        query_id = file_info['query_id']
        
        query_text = query_mapping.get(query_id, '')
        if not query_text and query_id.startswith('qid_'):
            clean_query_id = query_id[4:]
            query_text = query_mapping.get(clean_query_id, '')
        
        if not query_text:
            logger.warning(f"No query found for {query_id} in benchmark dataset")
        
        result = {
            'exp_name': file_info['exp_name'],
            'task': file_info['task'],
            'config_name': file_info['config_name'],
            'model_name': mapped_model,
            'original_model_name': original_model,
            'query_id': file_info['query_id'],
            'query': query_text,
            'original_file_path': file_info['file_path'],
        }
        
        if needs_metadata_extraction:
            metadata = parse_report_metadata(content)
            report_content = metadata.get('report_content', '')
            extracted_report_path = ""
            if report_content:
                extracted_report_path = extract_and_save_report(
                    file_info['file_path'], 
                    report_content, 
                    file_info['query_id'],
                    copy_entire_file=False
                )
            
            result.update({
                'report_file_path': extracted_report_path,
                'generated': metadata.get('Generated', ''),
                'seed_id': metadata.get('Seed ID', '0')
            })
        else:
            extracted_report_path = extract_and_save_report(
                file_info['file_path'], 
                "", 
                file_info['query_id'],
                copy_entire_file=True
            )
            
            result.update({
                'report_file_path': extracted_report_path,
                'generated': '',
                'seed_id': '0'
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing {file_info['file_path']}: {e}")
        return None


def remove_duplicates(reports: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove duplicate reports based on key identifiers."""
    seen = set()
    unique_reports = []
    
    for report in reports:
        identifier = (
            report['exp_name'],
            report['task'], 
            report['config_name'],
            report['model_name'],
            report['query_id']
        )
        
        if identifier not in seen:
            seen.add(identifier)
            unique_reports.append(report)
    
    logger.info(f"Removed {len(reports) - len(unique_reports)} duplicates")
    return unique_reports


def preprocess_reports(base_path: str, exp_names: List[str], output_dir: str, 
                      verbose: bool = False, use_realtime: bool = False) -> str:
    """
    Main preprocessing function to extract reports from directory structure to JSON.
    
    Args:
        base_path: Base directory containing experiment folders
        exp_names: List of experiment names to process
        output_dir: Output directory for JSON file
        verbose: Enable verbose logging
        use_realtime: If True, replace placeholders with current values
    
    Returns:
        Path to the generated JSON file
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    os.makedirs(output_dir, exist_ok=True)
    
    logger.info(f"Loading query mappings from HuggingFace (LiveResearchBench)")
    query_mapping = load_query_mapping(use_realtime=use_realtime)
    
    if not query_mapping:
        raise ValueError("Failed to load query mappings!")
    
    logger.info(f"Searching for reports in experiments: {', '.join(exp_names)}")
    report_files = find_report_files(base_path, exp_names)
    
    if not report_files:
        raise ValueError("No report files found!")
    
    logger.info(f"Processing {len(report_files)} report files...")
    reports = []
    
    for i, file_info in enumerate(report_files, 1):
        if i % 10 == 0:
            logger.info(f"  Processed {i}/{len(report_files)} files...")
        
        result = process_report_file(file_info, query_mapping, base_path)
        if result:
            reports.append(result)
    
    logger.info(f"Successfully processed {len(reports)}/{len(report_files)} files")
    
    reports = remove_duplicates(reports)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_file = os.path.join(output_dir, f"reports_{timestamp}.json")
    
    output_data = {
        'metadata': {
            'total_reports': len(reports),
            'generated_at': datetime.now().isoformat(),
            'model_name_mapping': MODEL_NAME_MAPPING
        },
        'reports': reports
    }
    
    save_json(output_data, json_file)
    
    logger.info(f"✅ Preprocessing completed successfully!")
    logger.info(f"📄 JSON file: {json_file}")
    
    return json_file

