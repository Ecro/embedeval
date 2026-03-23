Write a Zephyr application that sets up mutual TLS credentials for a TCP client using the TLS credentials subsystem.

Requirements:
1. Include zephyr/net/tls_credentials.h and zephyr/kernel.h
2. Define a single sec_tag value (e.g. 42) as a tls_sec_tag_t constant
3. Define dummy PEM buffers for: CA certificate, client certificate, client private key
   (use static const char arrays; actual PEM content can be placeholder strings)
4. Register the CA certificate with tls_credential_add using TLS_CREDENTIAL_CA_CERTIFICATE type and the sec_tag
5. Register the client certificate with tls_credential_add using TLS_CREDENTIAL_SERVER_CERTIFICATE type and the sec_tag
6. Register the client private key with tls_credential_add using TLS_CREDENTIAL_PRIVATE_KEY type and the sec_tag
7. All three tls_credential_add calls must use the SAME sec_tag value
8. Check the return value of each tls_credential_add against 0 (success)
9. Do NOT use OpenSSL functions (no SSL_CTX_load_verify_locations, no SSL_CTX_use_certificate_file, etc.)
10. Print "TLS CREDS OK" if all credentials loaded successfully, "TLS CREDS FAILED" otherwise

Output ONLY the complete C source file.
