#!/bin/bash
# Download LiveResearchBench dataset from HuggingFace
# This caches the dataset locally for offline use

echo "📥 Downloading LiveResearchBench dataset from HuggingFace..."
echo "Dataset: https://huggingface.co/datasets/Salesforce/LiveResearchBench"
echo ""

python3 << 'EOF'
from datasets import load_dataset

print("Downloading question_with_checklist subset...")
dataset = load_dataset("Salesforce/LiveResearchBench", "question_with_checklist", split="test")
print(f"✅ Downloaded {len(dataset)} entries with checklists")

print("\nDownloading question_only subset...")
dataset_q = load_dataset("Salesforce/LiveResearchBench", "question_only", split="test")
print(f"✅ Downloaded {len(dataset_q)} questions")

print("\n✅ Dataset cached successfully!")
print("Location: ~/.cache/huggingface/datasets/")
EOF

