#!/bin/bash
# Auto-generated verification script for embedeval
# Used by /autoloop — do not edit unless updating TECH_SPEC phases
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Color output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

pass() { echo -e "${GREEN}PASS${NC}: $1"; }
fail() { echo -e "${RED}FAIL${NC}: $1"; exit 1; }

verify_phase_1() {
    echo "=== Phase 1: Project Scaffold & Docker Environment ==="

    # uv sync
    uv sync || fail "uv sync failed"
    pass "uv sync"

    # Import check
    uv run python -c "from embedeval.models import CaseMetadata, EvalResult, BenchmarkReport" || fail "model imports failed"
    pass "Pydantic models importable"

    # Lint + type check
    uv run ruff check src/ || fail "ruff check failed"
    pass "ruff check"

    uv run ruff format --check src/ || fail "ruff format failed"
    pass "ruff format"

    uv run mypy src/ || fail "mypy failed"
    pass "mypy"

    # Directory structure
    test -d src/embedeval || fail "src/embedeval missing"
    test -d cases || fail "cases/ missing"
    test -d tests || fail "tests/ missing"
    test -d results || fail "results/ missing"
    test -d docs || fail "docs/ missing"
    test -f LICENSE || fail "LICENSE missing"
    test -f README.md || fail "README.md missing"
    pass "directory structure"

    # Docker build
    docker build -t embedeval . || fail "Docker build failed"
    pass "Docker build"

    # CI workflows
    test -f .github/workflows/ci.yml || fail "ci.yml missing"
    test -f .github/workflows/benchmark.yml || fail "benchmark.yml missing"
    test -f .github/workflows/validate-cases.yml || fail "validate-cases.yml missing"
    pass "CI workflows exist"

    pass "Phase 1 complete"
}

verify_phase_2() {
    echo "=== Phase 2: Benchmark Harness Core ==="

    # All unit tests pass
    uv run pytest tests/ -v --tb=short || fail "pytest failed"
    pass "unit tests"

    # CLI works
    uv run embedeval --help || fail "CLI --help failed"
    uv run embedeval run --help || fail "run --help failed"
    uv run embedeval validate --help || fail "validate --help failed"
    pass "CLI commands"

    # Lint + type check
    uv run ruff check src/ || fail "ruff check failed"
    uv run mypy src/ || fail "mypy failed"
    pass "code quality"

    pass "Phase 2 complete"
}

verify_phase_3() {
    echo "=== Phase 3: Test Case Framework & Pilot Cases ==="

    # Pilot cases exist
    test -d cases/kconfig-001 || fail "kconfig-001 missing"
    test -d cases/device-tree-001 || fail "device-tree-001 missing"
    test -d cases/isr-concurrency-001 || fail "isr-concurrency-001 missing"
    pass "pilot case directories"

    # Each case has required files
    for case in kconfig-001 device-tree-001 isr-concurrency-001; do
        test -f "cases/$case/prompt.md" || fail "$case/prompt.md missing"
        test -f "cases/$case/metadata.yaml" || fail "$case/metadata.yaml missing"
        test -d "cases/$case/reference" || fail "$case/reference/ missing"
        test -f "cases/$case/test_validate.py" || fail "$case/test_validate.py missing"
    done
    pass "case file structure"

    # Validate reference solutions (requires Docker)
    if docker info >/dev/null 2>&1; then
        uv run embedeval validate --case kconfig-001 || fail "kconfig validation failed"
        uv run embedeval validate --case device-tree-001 || fail "device-tree validation failed"
        uv run embedeval validate --case isr-concurrency-001 || fail "isr validation failed"
        pass "reference solution validation"
    else
        echo "SKIP: Docker not available, skipping reference validation"
    fi

    # Unit + integration tests
    uv run pytest tests/ -v --tb=short || fail "pytest failed"
    pass "all tests"

    pass "Phase 3 complete"
}

verify_phase_4() {
    echo "=== Phase 4: CI/CD Pipeline & Reporting ==="

    # Workflow files complete
    test -f .github/workflows/ci.yml || fail "ci.yml missing"
    test -f .github/workflows/benchmark.yml || fail "benchmark.yml missing"
    test -f .github/workflows/validate-cases.yml || fail "validate-cases.yml missing"
    grep "workflow_dispatch" .github/workflows/benchmark.yml || fail "benchmark.yml missing workflow_dispatch"
    pass "CI/CD workflows"

    # Tests pass
    uv run pytest tests/ -v --tb=short || fail "pytest failed"
    pass "tests"

    # Code quality
    uv run ruff check src/ || fail "ruff check failed"
    uv run mypy src/ || fail "mypy failed"
    pass "code quality"

    pass "Phase 4 complete"
}

verify_phase_5() {
    echo "=== Phase 5: Integration, Documentation & Polish ==="

    # Documentation
    test -f README.md || fail "README.md missing"
    test -f docs/METHODOLOGY.md || fail "METHODOLOGY.md missing"
    test -f docs/CONTRIBUTING.md || fail "CONTRIBUTING.md missing"
    test -f LICENSE || fail "LICENSE missing"
    grep "Quick Start" README.md || fail "README missing Quick Start"
    grep "Leaderboard" README.md || fail "README missing Leaderboard"
    pass "documentation"

    # Full code quality
    uv run ruff check src/ || fail "ruff check failed"
    uv run ruff format --check src/ tests/ || fail "ruff format failed"
    uv run mypy src/ || fail "mypy failed"
    pass "code quality"

    # Full test suite
    uv run pytest tests/ -v --tb=short || fail "pytest failed"
    pass "all tests"

    # CLI end-to-end
    uv run embedeval --help || fail "CLI failed"
    uv run embedeval list || fail "list failed"
    pass "CLI end-to-end"

    pass "Phase 5 complete"
}

verify_all() {
    echo "=== Final Acceptance Verification ==="

    # Code quality
    uv run ruff check src/ || fail "ruff check"
    uv run ruff format --check src/ tests/ || fail "ruff format"
    uv run mypy src/ || fail "mypy"

    # Tests
    uv run pytest tests/ -v --tb=short || fail "pytest"

    # CLI
    uv run embedeval --help || fail "CLI --help"
    uv run embedeval list || fail "embedeval list"

    # Docker validation (if available)
    if docker info >/dev/null 2>&1; then
        uv run embedeval validate --case kconfig-001 || fail "kconfig validation"
        uv run embedeval validate --case device-tree-001 || fail "device-tree validation"
        uv run embedeval validate --case isr-concurrency-001 || fail "isr validation"

        uv run embedeval run --model mock --output results/acceptance-test.json || fail "mock benchmark"
        uv run embedeval report results/ || fail "report generation"
    else
        echo "SKIP: Docker not available, skipping Docker-dependent checks"
    fi

    # Documentation
    test -f README.md || fail "README.md"
    test -f docs/METHODOLOGY.md || fail "METHODOLOGY.md"
    test -f docs/CONTRIBUTING.md || fail "CONTRIBUTING.md"
    test -f LICENSE || fail "LICENSE"

    pass "All acceptance criteria"
}

# Dispatch
case "${1:-all}" in
    phase_1) verify_phase_1 ;;
    phase_2) verify_phase_2 ;;
    phase_3) verify_phase_3 ;;
    phase_4) verify_phase_4 ;;
    phase_5) verify_phase_5 ;;
    all)
        verify_phase_1
        verify_phase_2
        verify_phase_3
        verify_phase_4
        verify_phase_5
        verify_all
        ;;
    *) echo "Usage: $0 [phase_1|phase_2|phase_3|phase_4|phase_5|all]"; exit 1 ;;
esac

echo ""
echo -e "${GREEN}=== VERIFICATION PASSED ===${NC}"
