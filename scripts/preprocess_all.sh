#!/bin/bash
# Preprocess multiple experiments at once
# Usage: ./scripts/preprocess_all.sh

set -e

# Configuration - Set these variables to your actual paths
BASE_PATH="${BASE_PATH:-/path/to/your/experiments}"
OUTPUT_DIR="extracted_reports_$(date +%Y%m%d_%H%M%S)"

if [ "$BASE_PATH" = "/path/to/your/experiments" ]; then
    echo "❌ Error: Please set BASE_PATH to your actual data location"
    echo "   Either:"
    echo "     1. Edit this script and change BASE_PATH variable"
    echo "     2. Set environment variable: export BASE_PATH=/your/path"
    echo ""
    echo "   Example:"
    echo "     export BASE_PATH=/home/user/research_data"
    echo "     ./scripts/preprocess_all.sh"
    exit 1
fi

echo "🔍 Preprocessing all experiments..."
echo "📁 Base path: ${BASE_PATH}"
echo "💾 Output: ${OUTPUT_DIR}"

# List of experiments to preprocess
# Modify this list based on your experiments
EXPERIMENTS=(
    "experiment1"
    "experiment2"
    "experiment3"
)

# Run preprocessing
python preprocess.py "${EXPERIMENTS[@]}" \
    --base-path "${BASE_PATH}" \
    --output-dir "${OUTPUT_DIR}" \
    --verbose

echo ""
echo "✅ Preprocessing complete!"
echo "📄 JSON files created in: ${OUTPUT_DIR}"
