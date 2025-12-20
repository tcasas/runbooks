[Runbooks Index](../../index.md) / [Linux](../index.md) / [Podman](index.md)

# Podman + systemd Deployment Models on RHEL 9

This platform supports **two supported deployment models** for running containerized services with Podman and systemd on hardened RHEL 9 hosts.

Both models are **production-grade and intentional**.
They differ primarily in **where authority lives** for container creation, upgrades, and rollback.

---

## Overview

| Model | Ownership | Summary |
|------|----------|--------|
| Model-A | systemd owns container | Immutable, declarative, unit-driven |
| Model-B | Operator owns container | Procedural, operationally flexible |

The correct choice depends on **how the host is built and operated**.

---

## Model-A: systemd Owns the Container

### Definition

In **Model-A**, the **systemd unit file is the single source of truth**.

- systemd executes `podman run`
- Containers are **created at service start**
- No persistent container definition exists outside systemd
- Image digests are pinned **inside the systemd unit**
- Operators do **not** manually create or replace containers

The container lifecycle is entirely defined by the unit.

---

### Rationale

Model-A is optimized for **immutability and declarative control**.

It aligns best with environments where:
- Hosts are built from **golden images**
- Services are deployed via **CI/CD**
- Configuration drift must be minimized
- Human interaction on production nodes is discouraged

If the unit file is correct, the service state is correct.

---

### Strengths

- Single authoritative source of truth
- No hidden Podman runtime state
- Predictable behavior on rebuild
- Strong auditability (unit file = reality)
- Excellent fit for immutable infrastructure

---

### Tradeoffs

- Upgrades require editing or regenerating unit files
- Rollback requires restoring a previous unit definition
- Less friendly to ad-hoc operational changes
- Requires disciplined unit management

---

### Best Fit

- Immutable or image-based hosts
- CI-generated deployments
- Golden image pipelines
- Strict change-control environments

---

## Model-B: Operator Creates the Container

### Definition

In **Model-B**, the **operator explicitly creates and replaces containers** using Podman.

- `podman create` defines the container
- systemd only starts/stops the named container
- Image digests are pinned in **Podman state**
- systemd never creates containers

systemd acts strictly as a **process supervisor**.

---

### Rationale

Model-B is optimized for **operational safety and clarity**.

It aligns best with environments where:
- Humans perform upgrades and rollbacks
- Change windows are controlled manually
- Live debugging may be required
- Rollback must be fast and low-risk

The lifecycle is explicit and observable:
- pull image
- pin digest
- create container
- start via systemd

Nothing happens implicitly.

---

### Strengths

- Very safe upgrade path
- Trivial rollback (recreate container)
- Clear operational ownership
- Easier live troubleshooting
- Digest history can be recorded on host

---

### Tradeoffs

- Slightly more mutable runtime state
- Requires procedural discipline
- Container definition exists outside systemd
- Less purely declarative than Model-A

---

### Best Fit

- Ops-driven production environments
- Security-sensitive systems
- Incident-response-heavy services
- Environments with human approval gates

---

## Why Both Models Are Supported

These models solve **different operational problems**.

| Concern | Model-A | Model-B |
|-------|--------|--------|
| Immutability | Excellent | Moderate |
| Upgrade safety | Moderate | Excellent |
| Rollback speed | Moderate | Excellent |
| CI/CD alignment | Excellent | Good |
| Human-driven ops | Limited | Excellent |
| Drift resistance | Excellent | Depends on discipline |

Attempting to force one model to solve both sets of concerns leads to brittle systems.

Supporting both allows:
- Model-A for CI-managed or image-based hosts
- Model-B for live-operated production systems

---

## Critical Rule (Applies to Both Models)

**Pick one model per service. Never mix them.**

Specifically:
- Model-A **must not** use `podman create`
- Model-B **must not** use `podman run` or `systemd --new`

Mixing ownership causes:
- split-brain state
- confusing failures
- unsafe upgrades

---

## Recommended Usage Pattern

For most environments:

- **Production (human-operated)** → Model-B
- **Golden images / CI-only nodes** → Model-A

Both models are first-class and supported.

---

## Summary

- Model-A favors **immutability and declarative control**
- Model-B favors **operational safety and clarity**
- Neither model is universally better
- The correct choice depends on **how the host is managed**

This document exists to ensure the choice is **explicit and intentional**.
