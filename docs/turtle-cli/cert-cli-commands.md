[Runbooks Index](../index.md) / [Turtle CLI](index.md)

# Turtle CLI certificate commands

Use these commands inside the Turtle CLI REPL to work with certificates. Each verb delegates to the certificate command set defined in the Turtle CLI parser and executes through the Macro runner.

## Create

```
create cert COMMON_NAME DEVICE [-cssl-prof PROFILE] [-project_id PROJECT] [--no-prompt] [--no-install] [-org ORG] [-city CITY] [-state STATE] [-country COUNTRY]
```
- `COMMON_NAME`: one or more comma-delimited common names.
- `DEVICE`: one or more comma-delimited device names.

## Delete

```
delete pending COMMON_NAME
```
- Remove pending certificate requests for the given common name.

## Disable

```
disable auto-renew COMMON_NAME
```
```
disable cert-decom COMMON_NAME
```
- Turn off auto-renew or cert-decommissioning for one or more comma-delimited common names.

## Email

```
email cert-expr [RECIPIENTS] [--expr1 | --expr5 | --expr15 | --expr30 | --expr60]
```
- Email expiration summaries to optional comma-delimited recipients and filter by the provided expiration window.

```
email cert-monitor NAME SENTINELS [RECIPIENTS] [--expr1] [--expr5]
```
- Monitor sensitive certificates by tenant `NAME`, matching `SENTINELS` in the common name. Flags scope to the next 24 hours (`--expr1`) or 5 days (`--expr5`).

```
email cert-weekly [RECIPIENTS]
```
- Send the weekly completion report to optional comma-delimited recipients.

## Enable

```
enable auto-renew COMMON_NAME
```
```
enable cert-decom COMMON_NAME
```
- Re-enable auto-renew or cert-decommissioning for comma-delimited common names.

## Export

```
export csr CN TO
export cert CN TO
export chain CN TO
export p12 CN TO
```
- Export the CSR, certificate, chain, or PKCS#12 keystore for common name `CN` to comma-delimited recipients `TO`.

## Install

```
install pending [COMMON_NAME] [--cid CID] [--expr1] [--expr5] [--expr15] [--expr30] [--expr60] [--crt-file FILE] [--no-prompt] [--serial SERIAL]
```
- Install pending items optionally filtered by common name, CID, expiration window flags, certificate file names, or serial numbers.

## List

```
list auto-renew COMMON_NAME
```
- Show auto-renew status for the comma-delimited common names.

```
list cert [COMMON_NAME] [--cid CID] [--crt-file FILE] [--expr] [--expr1] [--expr5] [--expr15] [--expr30] [--expr60] [--expired-90] [--local-dir PATH] [--serial SERIAL]
```
- List certificates for optional common names, filtering by CID, certificate files, expiration windows, recent expiry, local directory, or serial numbers.

```
list cert-chain [COMMON_NAME]
```
- If `COMMON_NAME` ends with `.crt`, `.chain`, or `.bak`, the command loads the local file as a chain; otherwise it queries devices for the certificate chain.

```
list cert-device COMMON_NAME
```
- List certificates by device for the comma-delimited common names.

```
list certfile COMMON_NAME
```
- List PEM files for the comma-delimited common names using the certificate host device.

```
list complete [COMMON_NAME] [--cid CID] [--crt-file FILE] [--expr1] [--expr5] [--expr15] [--expr30] [--expr60] [--serial SERIAL]
```
- Show completed certificate requests with optional filters.

```
list device [DEVICE]
```
- List devices (comma-delimited) through the OTX device command.

```
list domain DOMAIN
```
- List domains for the provided comma-delimited names.

```
list pending [COMMON_NAME] [--cid CID] [--crt-file FILE] [--expr1] [--expr5] [--expr15] [--expr30] [--expr60] [--serial SERIAL]
```
- List pending certificate requests with optional filters.

## Renew

```
renew auto-renew [--expr1] [--expr5] [--expr15] [--expr30] [--expr60]
```
- Renew auto-renew entries filtered by the selected expiration window.

```
renew cert [COMMON_NAME] [--cid CID] [--expr1] [--expr5] [--expr15] [--expr30] [--expr60] [--crt-file FILE] [--no-install] [--no-prompt] [--serial SERIAL]
```
- Renew certificates with optional filters, skipping install or prompting when requested.

## Revert

```
revert cert COMMON_NAME
```
- Revert certificates for the comma-delimited common names.

## Update

```
update device [--addr ADDR] [--dtype TYPE] [--fqdn FQDN] [--org ORG] [--proxy PROXY] [--pwd PASSWORD] [--state STATE] [--user USER]
```
- Update device metadata fields for the certificate host.

```
update cert-note COMMON_NAME NOTE
```
- Attach or change the note for the certificate common name.

```
update pending COMMON_NAME [--crt-pem] [--chain-pem] [--key-pem] [--aaa-removed]
```
- Refresh pending certificate artifacts or flag AAA removal from the chain.

```
update stat-calendar
```
- Update calendar statistics for certificates.
