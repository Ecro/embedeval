#!/bin/bash
#
# Run n=K samples of the full benchmark per model, with cooldowns and
# retry on transient failure. Each run writes a distinct archive via
# --run-id n1 / n2 / ... so nothing stomps.
#
# Usage:
#     scripts/run_n_samples.sh [N] [MODEL ...]
#
# Defaults: N=3, MODEL="claude-code://haiku claude-code://sonnet"
#
# Env knobs:
#     COOLDOWN_SECS (default 300) — sleep between every run and retry
#     MAX_RETRIES (default 2) — extra attempts per run on failure
#     EMBEDEVAL_ENABLE_BUILD (default docker) — forwarded to the CLI
#     RETEST_ONLY (default 0) — if 1, pass --retest-only to each run
#
# Example — Phase D (n=3 full, both models, 5-min cooldowns):
#     COOLDOWN_SECS=300 MAX_RETRIES=2 scripts/run_n_samples.sh 3 \
#         claude-code://haiku claude-code://sonnet
#

set -u

N="${1:-3}"
shift || true
MODELS=("$@")
if [ "${#MODELS[@]}" -eq 0 ]; then
    MODELS=("claude-code://haiku" "claude-code://sonnet")
fi

COOLDOWN_SECS="${COOLDOWN_SECS:-300}"
MAX_RETRIES="${MAX_RETRIES:-2}"
RETEST_ONLY="${RETEST_ONLY:-0}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

export EMBEDEVAL_ENABLE_BUILD="${EMBEDEVAL_ENABLE_BUILD:-docker}"

LOGDIR="/tmp/embedeval_n${N}_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$LOGDIR"

log() {
    echo "[$(date +%H:%M:%S)] $*"
}

slug_for() {
    echo "$1" | tr '/' '_' | tr ':' '_'
}

run_one() {
    local model="$1"
    local rid="$2"
    local slug
    slug="$(slug_for "$model")"
    local logfile="$LOGDIR/${rid}_${slug}.log"

    local extra_args=()
    if [ "$RETEST_ONLY" = "1" ]; then
        extra_args+=("--retest-only")
    fi

    local attempts=0
    local max_attempts=$((MAX_RETRIES + 1))

    while [ "$attempts" -lt "$max_attempts" ]; do
        attempts=$((attempts + 1))
        log "START  $model rid=$rid attempt=$attempts/$max_attempts"
        if uv run embedeval run \
            --model "$model" \
            --cases cases/ \
            --private-cases ../embedeval-private/cases/ \
            --include-private \
            --run-id "$rid" \
            "${extra_args[@]}" \
            -v >"$logfile" 2>&1; then
            log "OK     $model rid=$rid (log: $logfile)"
            tail -5 "$logfile" || true
            return 0
        fi

        log "FAIL   $model rid=$rid attempt=$attempts"
        echo "--- last 20 lines of $logfile ---"
        tail -20 "$logfile" || true
        echo "--- end ---"

        if [ "$attempts" -lt "$max_attempts" ]; then
            log "retry cooldown ${COOLDOWN_SECS}s"
            sleep "$COOLDOWN_SECS"
        fi
    done

    log "GIVEUP $model rid=$rid (all $max_attempts attempts exhausted)"
    return 1
}

trap 'log "interrupted — stopping"; exit 130' INT TERM

log "============================================================"
log "n=$N samples"
log "models: ${MODELS[*]}"
log "cooldown: ${COOLDOWN_SECS}s  max_retries: ${MAX_RETRIES}"
log "retest_only: ${RETEST_ONLY}  build_env: ${EMBEDEVAL_ENABLE_BUILD}"
log "logdir: $LOGDIR"
log "============================================================"

failed=()
total_steps=$((N * ${#MODELS[@]}))
step=0

for i in $(seq 1 "$N"); do
    rid="n${i}"
    for model in "${MODELS[@]}"; do
        step=$((step + 1))
        if ! run_one "$model" "$rid"; then
            failed+=("$model $rid")
        fi
        if [ "$step" -lt "$total_steps" ]; then
            log "inter-run cooldown ${COOLDOWN_SECS}s"
            sleep "$COOLDOWN_SECS"
        fi
    done
done

log "============================================================"
if [ "${#failed[@]}" -eq 0 ]; then
    log "DONE — all $total_steps runs succeeded"
else
    log "DONE — ${#failed[@]} of $total_steps runs failed:"
    for f in "${failed[@]}"; do
        log "  $f"
    done
fi
log "logs: $LOGDIR"
log "============================================================"

# Exit non-zero if anything failed so CI / caller can detect it.
if [ "${#failed[@]}" -gt 0 ]; then
    exit 1
fi
exit 0
