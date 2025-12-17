# Netcat Usage

## Scope and goal
Use this runbook to validate connectivity, transfer data, and troubleshoot services with `nc`/`netcat`.

## 1) Confirm netcat availability
- Command: `nc -h` or `nc -h 2>&1 | head -n 1`
- Expected: Help output showing either traditional or OpenBSD syntax.
- If missing: Install via the OS package manager (e.g., `apt install netcat-openbsd`, `yum install nc`, `apk add netcat-openbsd`).

## 2) Basic connectivity check
- Purpose: Quickly test if a TCP port is reachable.
- Command: `nc -vz <host> <port>`
- Expected:
  - Success: `succeeded!`
  - Failure: `Connection refused` (service down) or `timed out` (filtered/path issue).
- Tip: Add `-w <seconds>` to set a timeout (e.g., `-w 3`).

## 3) Listen for incoming connections
- Purpose: Validate inbound reachability or collect raw requests.
- Command: `nc -lv <port>`
- Notes:
  - Use `-k` to keep the listener alive after a single connection.
  - Run with `sudo` if binding to ports <1024.
  - Expect inbound data echoed to the terminal; type to respond.

## 4) Simple data transfer between hosts
**On the receiver:**
- Command: `nc -lv <port> > /tmp/received.file`

**On the sender:**
- Command: `nc <receiver_host> <port> < /path/to/source.file`

Expect the file to appear at `/tmp/received.file` on the receiver. Use `sha256sum` on both sides to confirm integrity.

## 5) Banner grabbing / HTTP request
- Purpose: Inspect service banners or make quick HTTP calls.
- Command: `printf 'GET / HTTP/1.0\r\nHost: <host>\r\n\r\n' | nc -w 5 <host> 80`
- Expected: Server banner and response headers followed by body (if any).

## 6) Port sweep (lightweight)
- Purpose: Quickly check a small set of ports when full scans are unavailable.
- Command: `nc -zv -w 2 <host> 22 80 443 8080`
- Expected: Success/failed status per port.
- Caution: For larger scans, use approved tools (`nmap`) that align with policy.

## 7) UDP check (best-effort)
- Purpose: Send a UDP packet and watch for a response.
- Command: `echo 'ping' | nc -u -w 3 <host> <port>`
- Expected: Often silent; success depends on the service replying. Use packet captures (`tcpdump`) if unsure.

## 8) Cleanup and safety
- Stop listeners with `Ctrl+C`.
- Avoid running as root unless binding to privileged ports.
- Do not expose listeners on untrusted networks unless necessary for the test.
