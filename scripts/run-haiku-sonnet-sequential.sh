#!/bin/bash
# Sequential retest-only run: Haiku first, then Sonnet.
# Both runs use --retest-only (skip unchanged cases) and include private cases.
# Invoked in background so results arrive when complete.

set -u
cd /home/noel/embedeval

export EMBEDEVAL_ENABLE_BUILD=docker
LOGDIR="/tmp/embedeval_b1b2_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$LOGDIR"

run_model() {
	local model="$1"
	local tag="$2"
	local logfile="$LOGDIR/${tag}.log"

	echo "============================================================"
	echo "[$(date +%H:%M:%S)] Starting ${tag}"
	echo "============================================================"

	uv run embedeval run \
		--model "claude-code://${model}" \
		--cases cases/ \
		--private-cases ../embedeval-private/cases/ \
		--include-private \
		--retest-only \
		-v \
		>"$logfile" 2>&1
	local rc=$?

	echo "[$(date +%H:%M:%S)] Finished ${tag} (exit=$rc)"
	echo "--- Last 40 lines of ${tag} log ---"
	tail -40 "$logfile"
	echo ""
	return $rc
}

echo "Log directory: $LOGDIR"
echo ""

run_model haiku haiku
HAIKU_RC=$?

run_model sonnet sonnet
SONNET_RC=$?

echo "============================================================"
echo "[$(date +%H:%M:%S)] Sequential run complete"
echo "  Haiku exit:  $HAIKU_RC"
echo "  Sonnet exit: $SONNET_RC"
echo "  Logs:        $LOGDIR"
echo "============================================================"

exit $((HAIKU_RC | SONNET_RC))
