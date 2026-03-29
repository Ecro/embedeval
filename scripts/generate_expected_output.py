"""Generate expected_output.txt for native_sim cases from reference printk strings.

Scans each case's reference/main.c for printk/printf/LOG_* calls, extracts
the literal string prefix (before any % format specifier), and writes
1-3 distinctive keywords to checks/expected_output.txt.

Skips:
- Cases without platform: native_sim
- Kconfig-only cases (no C code in main.c)
- Cases with no printk output
- Cases that already have expected_output.txt (unless --overwrite)
"""

import re
import sys
from pathlib import Path

CASES_DIR = Path(__file__).parent.parent / "cases"

# Patterns that match printk/printf/LOG_* calls
PRINT_PATTERNS = [
    r'printk\s*\(\s*"([^"]*)"',
    r'printf\s*\(\s*"([^"]*)"',
    r'LOG_(?:INF|ERR|WRN|DBG)\s*\(\s*"([^"]*)"',
]

# Words that indicate error/failure messages — these should be deprioritized
ERROR_INDICATORS = [
    "failed", "fail:", "fail ", "error", "err:", "fault", "invalid",
    "could not", "unable to", "cannot", "not found", "not ready",
    "not supported", "rejected", "timed out", "timeout",
    "critical", "warn:", "warning", "mismatch",
]


def is_kconfig_only(code: str) -> bool:
    """Check if the file is Kconfig fragment, not C code."""
    lines = [ln.strip() for ln in code.splitlines() if ln.strip()]
    if not lines:
        return True
    config_lines = sum(1 for ln in lines if ln.startswith("CONFIG_"))
    has_include = any("#include" in ln for ln in lines)
    has_main = any("main" in ln for ln in lines)
    return config_lines > 0 and not has_include and not has_main


def extract_print_string(line: str) -> str | None:
    """Extract the first printk/LOG_* literal string from a line."""
    for pattern in PRINT_PATTERNS:
        m = re.search(pattern, line)
        if m:
            for g in m.groups():
                if g is not None:
                    return g
    return None


def string_to_keyword(fmt_string: str) -> str | None:
    """Convert a format string to a keyword (prefix before first %)."""
    # Extract prefix before first format specifier (including width/precision)
    prefix = re.split(r'%[-+0 #]*\d*\.?\d*[dusxXlfcpzh]', fmt_string)[0]
    # Clean escape sequences and trailing whitespace
    prefix = prefix.replace("\\n", "").replace("\\t", "")
    prefix = prefix.replace('\\"', "").rstrip().rstrip("\\")
    if len(prefix) >= 6:
        return prefix
    return None


def is_error_message(keyword: str) -> bool:
    """Check if a keyword looks like an error/failure message."""
    lower = keyword.lower()
    return any(ind in lower for ind in ERROR_INDICATORS)


def is_in_error_block(lines: list[str], line_idx: int) -> bool:
    """Heuristic: check if line is inside an if-error block."""
    # Look back for if (err/ret/rc) pattern within 2 lines
    for i in range(max(0, line_idx - 2), line_idx):
        ln = lines[i].strip()
        if re.match(
            r'if\s*\(\s*(?:err|ret|rc|result|status|!dev|!device|!wdt|'
            r'!sock|!fd|\w+\s*==\s*NULL|\w+\s*<\s*0|'
            r'\w+\s*!=\s*\w+)',
            ln,
        ):
            return True
        if re.match(r'if\s*\(\s*(?:err|ret|rc|status)\s*\)', ln):
            return True
    return False


def extract_keywords(code: str) -> list[str]:
    """Extract printk/LOG_* literal string prefixes from C code."""
    lines = code.splitlines()
    happy_path: list[str] = []
    error_path: list[str] = []

    for i, line in enumerate(lines):
        fmt_string = extract_print_string(line)
        if fmt_string is None:
            continue

        keyword = string_to_keyword(fmt_string)
        if keyword is None:
            continue

        if is_error_message(keyword) or is_in_error_block(lines, i):
            error_path.append(keyword)
        else:
            happy_path.append(keyword)

    # Deduplicate
    seen: set[str] = set()
    unique_happy: list[str] = []
    for kw in happy_path:
        if kw not in seen:
            seen.add(kw)
            unique_happy.append(kw)

    # Select up to 3 non-overlapping keywords from happy path
    selected: list[str] = []
    # Sort by length descending for distinctiveness
    # Prefer prefix-style keywords (ending with : = ( ) over full sentences
    # — more robust to LLM wording variations
    def _sort_key(kw: str) -> tuple[int, int]:
        is_prefix = kw.rstrip().endswith((":", "=", "("))
        return (0 if is_prefix else 1, -len(kw))

    unique_happy.sort(key=_sort_key)
    for kw in unique_happy:
        if any(kw in existing for existing in selected):
            continue
        selected.append(kw)
        if len(selected) >= 3:
            break

    # If no happy-path keywords found, fall back to error-path
    # (some cases only print on errors, e.g., "assert failed")
    if not selected and error_path:
        return []  # No useful output to validate

    return selected


def get_platform(case_dir: Path) -> str:
    """Read platform from metadata.yaml."""
    meta = case_dir / "metadata.yaml"
    if not meta.exists():
        return "unknown"
    for line in meta.read_text(encoding="utf-8").splitlines():
        if line.startswith("platform:"):
            return line.split(":", 1)[1].strip()
    return "unknown"


def main() -> None:
    overwrite = "--overwrite" in sys.argv
    dry_run = "--dry-run" in sys.argv

    created = 0
    skipped_platform = 0
    skipped_kconfig = 0
    skipped_no_printk = 0
    skipped_exists = 0

    for case_dir in sorted(CASES_DIR.iterdir()):
        if not case_dir.is_dir():
            continue

        platform = get_platform(case_dir)
        if platform != "native_sim":
            skipped_platform += 1
            continue

        ref_file = case_dir / "reference" / "main.c"
        if not ref_file.exists():
            continue

        code = ref_file.read_text(encoding="utf-8")

        if is_kconfig_only(code):
            skipped_kconfig += 1
            continue

        keywords = extract_keywords(code)
        if not keywords:
            skipped_no_printk += 1
            continue

        output_file = case_dir / "checks" / "expected_output.txt"
        if output_file.exists() and not overwrite:
            skipped_exists += 1
            continue

        content = "\n".join(keywords) + "\n"

        if dry_run:
            print(f"  {case_dir.name}: {keywords}")
        else:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(content, encoding="utf-8")
            print(f"  {case_dir.name}: {keywords}")

        created += 1

    print(f"\n{'DRY RUN — ' if dry_run else ''}Summary:")
    print(f"  Created:          {created}")
    print(f"  Skipped (exists): {skipped_exists}")
    print(f"  Skipped (platform): {skipped_platform}")
    print(f"  Skipped (kconfig): {skipped_kconfig}")
    print(f"  Skipped (no printk): {skipped_no_printk}")


if __name__ == "__main__":
    main()
