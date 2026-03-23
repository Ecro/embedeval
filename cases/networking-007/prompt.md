Write a Zephyr RTOS application that resolves a hostname via DNS with a timeout.

Requirements:
1. Include zephyr/net/dns_resolve.h, zephyr/net/socket.h, and zephyr/kernel.h
2. Define the hostname to resolve as "example.com"
3. Define a DNS timeout of 3000 milliseconds (not K_FOREVER or 0)
4. Implement a DNS callback function with signature:
   static void dns_result_cb(enum dns_resolve_status status,
                             struct dns_addrinfo *info,
                             void *user_data)
5. In the callback, handle DNS_EAI_NONAME for NXDOMAIN (not found) with printk
6. In the callback, handle DNS_EAI_ALLDONE for query complete
7. In the callback, print the resolved IP address when status is 0
8. Register the callback with dns_get_default_context()
9. Call dns_resolve_name() with the hostname, DNS_QUERY_TYPE_A, a timeout, the callback, and user_data
10. Check the return value of dns_resolve_name — print error and return if negative
11. Wait for DNS resolution to complete using k_sem_take or k_msleep
12. Do NOT use gethostbyname() — that is a POSIX API not available in Zephyr
13. Do NOT use dns_lookup() — that function does not exist in Zephyr

Output ONLY the complete C source file.
