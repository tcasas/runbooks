# `curl` Proxy Usage

## Scope and goal
Use this runbook to send `curl` traffic through HTTP(S) proxies, including authenticated proxies, with tips for bypassing specific hosts and persisting settings.

## 1) Confirm proxy endpoint and credentials
- Format: `http://proxy.example.com:3128` or `https://proxy.example.com:3128`
- If authentication is needed, collect a username/password or a token that can be embedded as `http://user:pass@proxy:3128`.

## 2) Use a one-off proxy for a single request
- HTTP proxy: `curl -v --proxy http://proxy.example.com:3128 http://httpbin.org/get`
- HTTPS proxy (tunnels with CONNECT): `curl -v --proxy https://proxy.example.com:3128 https://ifconfig.me`
- SOCKS proxy (if supported): `curl -v --socks5-hostname proxy.example.com:1080 https://ifconfig.me`

## 3) Send credentials to the proxy
- Inline auth: `curl -v --proxy http://user:pass@proxy.example.com:3128 https://ifconfig.me`
- Prompted auth: `curl -v --proxy http://proxy.example.com:3128 --proxy-user user https://ifconfig.me` (prompts for password)
- NTLM/Negotiate: `curl -v --proxy-negotiate --proxy-user : https://target.example.com`

## 4) Persist proxy settings for repeated use
Set environment variables before running `curl` to avoid repeating flags.
- Bash/Zsh (HTTP and HTTPS):
  - `export http_proxy=http://proxy.example.com:3128`
  - `export https_proxy=http://proxy.example.com:3128`
- Lowercase and uppercase are both honored; lowercase is preferred.
- Unset to disable: `unset http_proxy https_proxy`

## 5) Bypass the proxy for specific hosts
Use `no_proxy` (or `NO_PROXY`) to list hosts, domains, or CIDRs that should connect directly.
- Example: `export no_proxy=localhost,127.0.0.1,.example.local,10.0.0.0/8`
- Verify behavior: `curl -v https://service.example.local` (should not show `CONNECT` to proxy)

## 6) Trust the proxy's certificate (HTTPS proxies only)
If the proxy MITMs TLS and uses a custom CA, point `curl` at the CA bundle.
- `curl -v --proxy-cacert /path/to/corp-ca.pem https://ifconfig.me`
- For strict verification errors, use `--proxy-insecure` temporarily (avoid for production).

## 7) Use a `.curlrc` for defaults
Add recurring options to `~/.curlrc` so they apply automatically.
- Example contents:
  - `proxy = http://proxy.example.com:3128`
  - `noproxy = localhost,127.0.0.1,.example.local`
  - `proxy-user = user:pass`
- Test: `curl -v https://ifconfig.me` (should show proxy usage without extra flags)

## 8) Troubleshoot common proxy errors
- `Received HTTP code 407 from proxy after CONNECT`: proxy credentials missing or wrong; re-test with `--proxy-user`.
- `CONNECT tunnel failed, response 403`: proxy blocked the destination; confirm allowlists.
- `connection refused`: proxy host/port incorrect or firewall blocked.
- `SSL certificate problem`: provide the proxy's CA with `--proxy-cacert` or temporarily use `--proxy-insecure`.

End.
