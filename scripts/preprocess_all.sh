#!/bin/bash
# Preprocess multiple experiments at once
# Usage: ./scripts/preprocess_all.sh

set -e

BASE_PATH="/export/xgen-small/mas_eval"
OUTPUT_DIR="extracted_reports_$(date +%Y%m%d_%H%M%S)"

echo "🔍 Preprocessing all experiments..."
echo "📁 Base path: ${BASE_PATH}"
echo "💾 Output: ${OUTPUT_DIR}"

# List of experiments to preprocess
# Modify this list based on your experiments
EXPERIMENTS=(
    "multi_agent_odr_oai"
    "single_agent_gpt_4.1"
    "single_agent_gpt_5"
)

# Run preprocessing
python preprocess.py "${EXPERIMENTS[@]}" \
    --base-path "${BASE_PATH}" \
    --output-dir "${OUTPUT_DIR}" \
    --verbose

echo ""
echo "✅ Preprocessing complete!"
echo "📄 JSON files created in: ${OUTPUT_DIR}"

