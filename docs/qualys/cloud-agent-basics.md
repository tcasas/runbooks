[Runbooks Index](../index.md) / [Qualys](index.md)

# Qualys Cloud Agent — Verification & On-Demand Scanning

## Purpose

This runbook is used to:

- verify Qualys Cloud Agent is installed and running
- confirm agent health and connectivity
- trigger immediate vulnerability and CIS/policy scans
- understand what results can (and cannot) be validated locally

Designed for operators with limited Qualys experience.

---

## Scope & Assumptions

- Linux host
- Qualys Cloud Agent is the scanning method
- Outbound HTTPS to Qualys cloud is permitted

This runbook does not apply to:
- scanner appliance–only environments
- offline hosts
- WAS-only deployments

---

## Step 1 — Verify Qualys Cloud Agent Is Installed & Running

    sudo systemctl status qualys-cloud-agent

Expected:

    Active: active (running)

### Interpretation

- Service exists → agent is installed
- Service running → agent is operational

If you see:

    Unit qualys-cloud-agent.service not found

Then:
- Qualys Cloud Agent is not installed
- This host relies on network scans only

Stop here if the agent is not present.

---

## Step 2 — Check Agent Health & Connectivity (Critical)

The Qualys Cloud Agent CLI `status` command may fail on some agent versions.
In that case, logs and service state are the authoritative indicators.

### 2.1 Verify Agent Service Is Running

    systemctl status qualys-cloud-agent

Expected:

    Active: active (running)

If the service is not running:
- scans will not execute
- results will not update in Qualys

---

### 2.2 Verify Agent Activity via Logs

    tail -n 50 /var/log/qualys/qualys-cloud-agent.log

Look for:
- assessment start messages
- upload or communication activity
- absence of repeated fatal errors

You are confirming **activity**, not specific results.

---

### 2.3 Known CLI Limitation

On some Qualys Cloud Agent versions, the following command may return an error:

    /usr/local/qualys/cloud-agent/bin/qualys-cloud-agent.sh status

Example error:

    Error: Invalid key name in status

This does **not** indicate agent failure.

When this occurs:
- rely on `systemctl status`
- rely on agent logs
- rely on successful execution of `scan` and `policy_eval`
- use the Qualys UI as the source of truth

---

### Step 2 Outcome

If:
- the service is running, and
- logs show recent activity

Then:
- the agent is healthy
- connectivity to Qualys is functioning

---

## Step 3 — Force Immediate Vulnerability Scan

    sudo /usr/local/qualys/cloud-agent/bin/qualys-cloud-agent.sh scan

Expected:

    Scan request submitted successfully

### What This Does

- Evaluates installed packages
- Checks known vulnerabilities
- Uploads results to Qualys

Expected result availability:
- 5–15 minutes in the Qualys UI

---

## Step 4 — Force CIS / Policy Evaluation (Required for Hardening)

    sudo /usr/local/qualys/cloud-agent/bin/qualys-cloud-agent.sh policy_eval

Expected:

    Policy evaluation started

### Important Notes

- CIS / compliance findings will not update without this step
- scan alone is insufficient for hardening verification

---

## Step 5 — Confirm Scan Execution Locally

    sudo /usr/local/qualys/cloud-agent/bin/qualys-cloud-agent.sh status

Expected:

    Last assessment: <new timestamp>

### Interpretation

- Timestamp updated → scan ran successfully
- Timestamp unchanged → scan did not execute

---

## Step 6 — Result Visibility Limitations

The CLI cannot show:

- vulnerability results
- pass/fail status
- QIDs
- compliance details

These are visible only in the Qualys UI.

CLI is used for:
- health checks
- triggering scans

UI is used for:
- reviewing results
- closing findings

---

## Common Operator Questions

### Did my fix work?

1. Apply fix
2. Run:
   - vulnerability scan
   - policy evaluation
3. Wait 10–15 minutes
4. Verify in Qualys UI

---

### Why is the finding still open?

Common reasons:
- policy evaluation not run
- agent has not checked in yet
- reboot required
- wrong scan type used

---

### Can I scan a single finding?

No.  
Qualys always evaluates all applicable controls.

---

## Non-Issues (Safe to Ignore)

Log entries such as:

    PAM-tacplus: user not authenticated by TACACS+
    su: (to root) root on none

Are:
- unrelated to Qualys
- normal authentication noise
- not scan failures

---

## Quick Reference — Commands Only

    systemctl status qualys-cloud-agent

    sudo /usr/local/qualys/cloud-agent/bin/qualys-cloud-agent.sh status

    sudo /usr/local/qualys/cloud-agent/bin/qualys-cloud-agent.sh scan

    sudo /usr/local/qualys/cloud-agent/bin/qualys-cloud-agent.sh policy_eval

---

## Key Takeaways

- Cloud Agent provides fast feedback
- scan and policy_eval serve different purposes
- CLI triggers scans; UI shows results
- Always allow time before checking the UI
