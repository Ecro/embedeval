Write a Zephyr RTOS BLE L2CAP Connection-Oriented Channel (CoC) server.

Requirements:
1. Include zephyr/bluetooth/bluetooth.h, zephyr/bluetooth/l2cap.h, zephyr/bluetooth/conn.h,
   and zephyr/kernel.h
2. Define a PSM value: #define L2CAP_PSM 0x80
3. Implement an L2CAP recv callback:
   static int l2cap_recv(struct bt_l2cap_chan *chan, struct net_buf *buf)
   - Print the number of received bytes
   - Return 0 on success
4. Implement an L2CAP connected callback:
   static void l2cap_chan_connected(struct bt_l2cap_chan *chan)
   - Print "L2CAP channel connected"
5. Implement an L2CAP disconnected callback:
   static void l2cap_chan_disconnected(struct bt_l2cap_chan *chan)
   - Print "L2CAP channel disconnected"
6. Define static struct bt_l2cap_chan_ops l2cap_ops with .recv, .connected, .disconnected set
7. Implement an L2CAP server accept callback:
   static int l2cap_server_accept(struct bt_conn *conn,
                                  struct bt_l2cap_chan **chan)
   - Assign the channel with bt_l2cap_le_chan .chan.ops = &l2cap_ops
   - Set *chan to point to the channel
   - Return 0
8. Register the L2CAP server with bt_l2cap_server_register:
   - Set .psm = L2CAP_PSM
   - Set .accept = l2cap_server_accept
9. After registration, send data using bt_l2cap_chan_send() in response to received data
10. Call bt_enable(NULL) and bt_le_adv_start() in main
11. Do NOT use l2cap_connect() — that function does not exist in Zephyr
12. Use bt_l2cap_chan_send for sending, not a hypothetical l2cap_send()

Output ONLY the complete C source file.
