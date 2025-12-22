[Runbooks Index](../index.md) / [Linux](index.md)

# Troubleshoot outbound connections with tcpdump

## Scope and goal
Use this runbook to capture and interpret outbound traffic with `tcpdump` when applications cannot reach remote hosts. The goal is to determine whether packets are leaving the host, whether responses return, and where drops or resets occur.

## 1) Collect target details and interface
- Identify the destination host/IP and port (e.g., `example.com:443`).
- Resolve the destination IP: `getent hosts <host>`.
- Find the egress interface and next hop: `ip route get <dest_ip>` (note the `dev` and `via` values).
- Ensure you have sudo/root for packet capture.

## 2) Start a focused capture
Run the capture on the egress interface with minimal scope to avoid noise:
- Example (TCP): `sudo tcpdump -nni <iface> host <dest_ip> and tcp port <port> -vvv -tttt`
- Example (UDP): `sudo tcpdump -nni <iface> host <dest_ip> and udp port <port> -vvv -tttt`
- Save to a file if needed: add `-w /tmp/outbound.pcap`.

Leave the capture running, then reproduce the failing request from another terminal.

## 3) Interpret common TCP patterns
- **Nothing captured:** Traffic never left the host. Check local firewall (`iptables -S`, `nft list ruleset`), routing, proxy variables, or process binding to the wrong interface.
- **SYN retransmits with no SYN-ACK:** Upstream firewall, security group, or path drop. Validate default gateway, security controls, or blocked egress.
- **SYN → RST from remote:** Port closed on destination or middlebox actively rejecting. Confirm service/port and ACLs.
- **SYN → SYN-ACK → RST from client:** Local process resetting (maybe no listener) or security software terminating. Check app logs or host firewalls.
- **Handshake succeeds but stalls mid-stream:** Look for zero-window, FIN/RST mid-connection, or MTU/PMTU issues (ICMP fragmentation needed). Try smaller payloads or disable offloading temporarily for testing.

## 4) Interpret common UDP patterns
- **No responses:** UDP is often silent. Capture both egress and ingress: `sudo tcpdump -nni <iface> host <dest_ip> and udp port <port>` plus `sudo tcpdump -nni any dst port <port>` to see replies.
- **ICMP errors:** `icmp port unreachable` from remote means the service is closed; `icmp admin prohibited` indicates filtering; `frag needed` suggests MTU issues.

## 5) Compare multiple interfaces or NAT
- If the host has multiple NICs or NAT, capture on each relevant interface (`any`, `eth0`, `eth1`) to confirm which path carries the traffic.
- To verify NAT translation, capture on the inside interface for the original source IP and on the outside interface for the translated IP; ensure packets match in sequence and timing.

## 6) Capture DNS when name resolution is suspect
- Run alongside the main capture: `sudo tcpdump -nni <iface> udp port 53 and host <dns_server>`.
- Look for `NXDomain`, `SERVFAIL`, or timeouts to decide if the failure is DNS-related.

## 7) Save, share, and clean up
- Stop captures with `Ctrl+C`; summarize with `tcpdump -nr /tmp/outbound.pcap | head` before sharing.
- Remove temporary files when done: `rm /tmp/outbound.pcap`.
- If captures contain sensitive data, trim with focused filters before distribution.
