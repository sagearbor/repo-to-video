#!/bin/bash
# Test runner script for repo-to-video
# Usage: ./run_tests.sh [options]
#
# Options:
#   -u, --unit          Run only unit tests
#   -i, --integration   Run only integration tests
#   -c, --coverage      Run with coverage report
#   -f, --fast          Run fast tests only (skip slow tests)
#   -v, --verbose       Verbose output
#   --help              Show this help message

set -e

# Default options
COVERAGE=""
MARKERS=""
VERBOSE=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -u|--unit)
            MARKERS="-m unit"
            shift
            ;;
        -i|--integration)
            MARKERS="-m integration"
            shift
            ;;
        -c|--coverage)
            COVERAGE="--cov=src --cov-report=html --cov-report=term"
            shift
            ;;
        -f|--fast)
            MARKERS="-m 'not slow'"
            shift
            ;;
        -v|--verbose)
            VERBOSE="-vv"
            shift
            ;;
        --help)
            echo "Test runner for repo-to-video"
            echo ""
            echo "Usage: ./run_tests.sh [options]"
            echo ""
            echo "Options:"
            echo "  -u, --unit          Run only unit tests"
            echo "  -i, --integration   Run only integration tests"
            echo "  -c, --coverage      Run with coverage report"
            echo "  -f, --fast          Run fast tests only (skip slow tests)"
            echo "  -v, --verbose       Verbose output"
            echo "  --help              Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Run tests
echo "Running tests..."
python -m pytest tests/ $MARKERS $COVERAGE $VERBOSE

echo ""
echo "✓ All tests passed!"
