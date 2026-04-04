"""Negative tests for PSA Crypto AES encryption/decryption.

Reference: cases/security-001/reference/main.c
Checks:    cases/security-001/checks/behavior.py

The reference:
  - Calls psa_destroy_key(key_id) in every error path and at the end of main.
    key_destroyed: 'psa_destroy_key' present in code → passes.
  - Sets psa_set_key_type(&attributes, PSA_KEY_TYPE_AES).
    key_type_aes: 'PSA_KEY_TYPE_AES' present in code → passes.

Mutation strategy
-----------------
* missing_key_destroy : removes every line containing 'psa_destroy_key'. The
  key_destroyed check does a plain string search for 'psa_destroy_key' → fails
  when all occurrences are gone.

* wrong_key_type : replaces PSA_KEY_TYPE_AES with PSA_KEY_TYPE_HMAC. The check
  does a literal string search for 'PSA_KEY_TYPE_AES' → fails when absent.
"""


def _remove_lines(code: str, pattern: str) -> str:
    """Remove all lines containing *pattern*."""
    return "\n".join(line for line in code.splitlines() if pattern not in line)


NEGATIVES = [
    {
        "name": "missing_key_destroy",
        "description": (
            "psa_destroy_key() calls removed — PSA key slot is never released, "
            "leaking a persistent key and exhausting the secure element's key store"
        ),
        # Reference has psa_destroy_key in two error paths and at the end of main.
        # Removing all lines with 'psa_destroy_key' leaves the string absent
        # everywhere → key_destroyed fails.
        "mutation": lambda code: _remove_lines(code, "psa_destroy_key"),
        "must_fail": ["key_destroyed"],
    },
    {
        "name": "wrong_key_type",
        "description": (
            "PSA_KEY_TYPE_AES replaced with PSA_KEY_TYPE_HMAC — wrong key type "
            "for a cipher operation; import will fail or use an incompatible key"
        ),
        # Reference: psa_set_key_type(&attributes, PSA_KEY_TYPE_AES);
        # Replacing the constant removes 'PSA_KEY_TYPE_AES' from the code
        # → key_type_aes fails.
        "mutation": lambda code: code.replace(
            "PSA_KEY_TYPE_AES",
            "PSA_KEY_TYPE_HMAC",
        ),
        "must_fail": ["key_type_aes"],
    },
    # --- Subtle ---
    {
        "name": "ecb_mode",
        "mutation": lambda code: code.replace(
            "PSA_ALG_CBC_NO_PADDING",
            "PSA_ALG_ECB_NO_PADDING",
        ),
        "should_fail": ["no_ecb_mode"],
        "bug_description": "CBC replaced with ECB — ECB is semantically insecure for multi-block data (identical blocks produce identical ciphertext)",
    },
]
