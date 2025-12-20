[Runbooks Index](../index.md) / [DNS](index.md)

# DNS Search List — Linux Resolution Behavior Runbook

## Purpose
- Explain what a DNS search list is
- Show where it is configured on Linux
- Demonstrate how name resolution actually works
- Provide validation and troubleshooting steps
- Include hardening and best-practice guidance

---

## Background
### What is a DNS search list
A DNS search list is a set of domain suffixes automatically appended to UNQUALIFIED hostnames (names without dots) during DNS resolution.

Example:
- Command:   ping web01
- Resolver tries:
  - web01.prod.corp.example.com
  - web01.corp.example.com
  - web01

This behavior trades convenience for possible ambiguity, latency, and security exposure.

---

## Configuration locations
### Traditional glibc resolver

**File location**
```bash
cat /etc/resolv.conf
```

> expected (example):
> search prod.corp.example.com corp.example.com
> nameserver 10.10.10.10
> nameserver 10.10.10.11

Notes:
- "search" overrides "domain" if both are present
- Max 6 domains, total length ≤ 256 chars

---

### systemd-resolved systems (RHEL 8+, Ubuntu 20+, etc.)

**Check effective configuration**
```bash
resolvectl status
```

> expected (example):
> Link 2 (eth0)
>     DNS Servers: 10.10.10.10
>     DNS Domain: prod.corp.example.com corp.example.com

**Verify resolv.conf is managed by systemd**
```bash
ls -l /etc/resolv.conf
```
> expected: symlink to /run/systemd/resolve/stub-resolv.conf

---

## Resolution behavior
### Qualified vs unqualified names

| Name entered                         | Search list applied |
|-------------------------------------|---------------------|
| web01                               | YES                 |
| web01.prod.corp.example.com         | NO                  |
| web01.prod.corp.example.com.        | NO (absolute FQDN)  |

NOTE:
- Trailing dot (.) forces absolute resolution
- This bypasses search list expansion

---

### Resolution order example

Given search list:
```bash
search prod.corp.example.com corp.example.com
```

```bash
ping db01
```

Resolver attempts (in order):
- db01.prod.corp.example.com
- db01.corp.example.com
- db01

First successful answer is used.

---

## ndots behavior
### Understanding ndots

**Check ndots setting**
```bash
grep options /etc/resolv.conf
```

> expected (example):
> options ndots:1

Meaning:
- If hostname has >= ndots dots, try as absolute first
- Default: ndots:1

Examples:
- api.dev        (1 dot)
- With ndots:1 → absolute first
- With ndots:5 → search list applied first

---

## Validation
### Test resolution with search list applied

```bash
dig db01 +search
```

> expected:
> ;; QUESTION SECTION:
> ;db01.prod.corp.example.com. IN A

---

### Test absolute FQDN (no search list)

```bash
dig db01.prod.corp.example.com.
```

> expected:
> ;; QUESTION SECTION:
> ;db01.prod.corp.example.com. IN A

---

### Observe resolver behavior (advanced)

```bash
strace -e trace=network ping db01
```

> expected:
> multiple DNS queries for each search suffix

---

## Common issues
### Slow commands (ssh, sudo, dnf, curl)

Cause:
- Multiple failed DNS attempts per command
- Large or invalid search lists

Symptoms:
- Delays of 1–5 seconds per hostname resolution

---

### Unexpected name resolution

Example:
```bash
ping google
```

Resolver tries:
- google.corp.example.com
- NOT google.com

This can break scripts and tools silently.

---

## Security considerations
### Why search lists can be risky

- Internal hostnames may leak via DNS queries
- Overlapping suffixes (corp, local) are dangerous
- Public DNS interception risk

Hardened systems often:
- Limit search list to ONE domain
- Or remove it entirely

---

## Best practices
### Operational guidance

- Use FQDNs in scripts and automation
- Keep search list short (1–2 domains max)
- Avoid generic suffixes (corp, local, internal)
- Use trailing dot for correctness:
  curl https://api.prod.example.com./health

---

## Change control
### Modifying search list (example)

**Temporary test (non-persistent)**
```bash
sudo vi /etc/resolv.conf
```

**Persistent change depends on:**
- NetworkManager
- systemd-resolved
- DHCP options
- Cloud-init

ALWAYS identify the source before editing.

---

## One-line summary
### Key takeaway

DNS search lists expand short hostnames by appending domain suffixes, which is convenient for humans but can cause ambiguity, delays, and security issues in production systems.
