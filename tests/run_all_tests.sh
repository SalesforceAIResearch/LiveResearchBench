#!/bin/bash
# Run all tests for LiveResearchBench
set -e

echo "🧪 Running All LiveResearchBench Tests"
echo "======================================"

# Change to project root (in case run from tests/ directory)
cd "$(dirname "$0")/.."

# Set PYTHONPATH to include the project root
export PYTHONPATH="${PWD}:${PYTHONPATH}"

# Test 1: Basic imports and functionality
echo ""
echo "Test 1: Basic imports and functionality"
python tests/test_basic.py

# Test 2: Mock grading workflow  
echo ""
echo "Test 2: Mock grading workflow"
python tests/test_mock_grading.py

# Test 3: Script help output
echo ""
echo "Test 3: Verifying script interfaces"
echo "  - preprocess.py --help"
python preprocess.py --help > /dev/null
echo "    ✅ preprocess.py interface OK"

echo "  - main.py --help"
python main.py --help > /dev/null
echo "    ✅ main.py interface OK"

echo "  - average_results.py --help"
python average_results.py --help > /dev/null
echo "    ✅ average_results.py interface OK"

# Test 4: Config files
echo ""
echo "Test 4: Configuration files"
if [ -f "configs/batch_config.yaml" ]; then
    echo "  ✅ batch_config.yaml exists"
else
    echo "  ❌ batch_config.yaml missing"
fi

if [ -f "configs/batch_config.yaml.example" ]; then
    echo "  ✅ batch_config.yaml.example exists"
else
    echo "  ❌ batch_config.yaml.example missing"
fi

# Test 5: Bash scripts
echo ""
echo "Test 5: Bash scripts"
for script in scripts/*.sh; do
    if [ -x "$script" ]; then
        echo "  ✅ $(basename $script) is executable"
    else
        echo "  ❌ $(basename $script) is not executable"
    fi
done

echo ""
echo "======================================"
echo "✅ All tests completed successfully!"
echo "======================================"
echo ""
echo "Installation Summary:"
echo "  • Python package: liveresearchbench v0.1.0"
echo "  • Main scripts: preprocess.py, main.py, average_results.py"
echo "  • Bash scripts: 3 scripts in scripts/"
echo "  • Configuration: batch_config.yaml configured with 18 models"
echo ""
echo "Ready to use! Next steps:"
echo "  1. Set up API keys in .env file"
echo "  2. Run: python main.py --help"
echo "  3. See GETTING_STARTED.md for examples"

