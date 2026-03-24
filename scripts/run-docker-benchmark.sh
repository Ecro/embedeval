#!/bin/bash
set -euo pipefail

MODEL="${1:-claude-code://sonnet}"
VISIBILITY="${2:-public}"

echo "Building Docker image..."
docker-compose build embedeval

echo "Running benchmark: model=$MODEL visibility=$VISIBILITY"
docker-compose run --rm \
  -e EMBEDEVAL_ENABLE_BUILD=1 \
  embedeval run \
  --model "$MODEL" \
  --cases cases/ \
  --visibility "$VISIBILITY" \
  -v

echo "Results saved to results/"
