"""Context pack helpers for Context Quality Mode.

A "context pack" is a run-wide text payload (team's CLAUDE.md, expert pack,
or custom guidance) prepended to every LLM prompt. See
docs/CONTEXT-QUALITY-MODE.md for the full design.

This module owns three concerns:
- Resolving the user-supplied identifier to a real file path. The special
  value "expert" maps to the bundled pack at context_packs/expert.md.
- Hashing pack content so the tracker can refuse to mix incompatible runs.
  Hash uses raw bytes (not normalized text) so whitespace edits invalidate
  prior runs — that is intentional, a comma added to the pack is a different
  pack from the LLM's perspective.
- Length guard so accidentally pointing --context-pack at a multi-megabyte
  file fails loudly instead of silently exhausting the context window.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

# Soft limit. Above this we warn but proceed. The point is to catch the
# "user pointed --context-pack at the wrong file" case (e.g. a 2MB log),
# not to enforce token discipline — that's the user's call.
MAX_PACK_CHARS = 32_000

EXPERT_KEYWORD = "expert"


class ContextPackTooLargeError(ValueError):
    """Raised when a context pack exceeds MAX_PACK_CHARS."""


def bundled_expert_pack_path() -> Path:
    """Return the path to the bundled expert.md pack."""
    return Path(__file__).parent / "context_packs" / "expert.md"


def resolve_context_pack(identifier: str) -> Path:
    """Resolve a CLI --context-pack value to an actual file path.

    Args:
        identifier: Either a path to a context file, or the literal string
            "expert" to use the bundled expert pack.

    Returns:
        Path to a readable .md/.txt file.

    Raises:
        FileNotFoundError: identifier neither matches "expert" nor exists.
    """
    if identifier == EXPERT_KEYWORD:
        path = bundled_expert_pack_path()
        if not path.is_file():
            raise FileNotFoundError(
                f"Bundled expert pack missing at {path}. "
                f"Reinstall embedeval or run scripts/build_expert_pack.py."
            )
        return path

    path = Path(identifier).expanduser()
    if not path.is_file():
        raise FileNotFoundError(
            f"Context pack file not found: {path} "
            f"(use 'expert' for the bundled pack)"
        )
    return path


def _hash_raw(content: str) -> str:
    """Compute the canonical 16-char SHA256 prefix without size checking.

    Single source of truth for the hash format. Called by hash_context_pack
    after the size guard, and directly by CLI when the size guard is
    intentionally bypassed (e.g. user accepted the oversized-pack warning).
    Keeping this in one place prevents the cli.py fallback from drifting
    out of sync with the canonical algorithm.
    """
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


def hash_context_pack(content: str) -> str:
    """Return a 16-char SHA256 prefix of the pack content.

    16 chars (64 bits) is enough collision resistance for a tracker that
    holds at most a few dozen distinct packs across its lifetime, while
    staying short enough to read in tracker JSON.
    """
    if len(content) > MAX_PACK_CHARS:
        raise ContextPackTooLargeError(
            f"Context pack is {len(content)} chars, soft limit "
            f"{MAX_PACK_CHARS}. Excess content tends to dilute LLM attention."
        )
    return _hash_raw(content)
