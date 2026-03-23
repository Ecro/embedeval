Write a Zephyr RTOS application that monitors network interface up/down events.

Requirements:
1. Include zephyr/net/net_mgmt.h, zephyr/net/net_if.h, and zephyr/kernel.h
2. Implement a net_mgmt event handler callback with signature:
   static void net_event_handler(struct net_mgmt_event_callback *cb,
                                 uint32_t mgmt_event,
                                 struct net_if *iface)
3. In the handler, check mgmt_event for NET_EVENT_IF_UP and print "Interface UP"
4. In the handler, check mgmt_event for NET_EVENT_IF_DOWN and print "Interface DOWN"
5. Declare a static struct net_mgmt_event_callback net_cb
6. Call net_mgmt_init_event_callback() to initialize the callback struct with the handler
   and the event mask (NET_EVENT_IF_UP | NET_EVENT_IF_DOWN)
7. Call net_mgmt_add_event_callback() to register the callback BEFORE checking initial state
8. After registering, check the initial state of the default interface with net_if_is_up()
9. Obtain the default interface with net_if_get_default()
10. Run a main loop using k_sleep to keep the application alive

Output ONLY the complete C source file.
