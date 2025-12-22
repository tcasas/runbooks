[Runbooks Index](../index.md) / [Turtle CLI](index.md)

# Turtle CLI F5 commands

Use these commands inside the Turtle CLI REPL to work with F5 Local Traffic Manager (LTM) devices, REST files, and supporting system metadata. Commands are grouped by their verb. Optional arguments appear in square brackets.

## Delete

```
delete sys crypto cert [NAME]
delete sys crypto key [NAME]
delete certs [-confirm]
delete profile client-ssl [NAME]
delete rest file [NAME]
```
- Remove system certificates or keys, optionally targeting a single `NAME`.
- `delete certs` drops certificate records from the database. Add `-confirm` to delete all records without specifying devices.
- `delete profile client-ssl` removes one or more comma-delimited client SSL profiles from LTM.
- `delete rest file` removes REST-uploaded files by optional comma-delimited name.

## Download

```
download cert FILENAME
download key FILENAME
```
- Pull certificate or key files by filename from the REST download location.

## Import

```
import certs [RECIPIENTS]
```
- Import certificates and optionally email comma-delimited `RECIPIENTS` after completion.

## Install

```
install cert FILENAME
install key FILENAME
```
- Install certificate or key files that already exist under `/var/config/rest/downloads/`.

## List

```
list backup [--oneline]
list device [DEVICE]
list oneline [NAME] [--addr ADDRESS]
list rest-files
list virtual-summary [NAME] [-ivip] [-evip] [--partition PARTITION]
```
- `list backup` shows available UCS backups; add `--oneline` for condensed output.
- `list device` lists OTX devices; accepts optional comma-delimited names.
- `list oneline` returns virtual server summaries, optionally filtered by name or address.
- `list rest-files` enumerates REST-uploaded files.
- `list virtual-summary` shows virtual server summaries, scoped to internal (`-ivip`), external (`-evip`), or a specific partition.

### LTM monitors

```
list ltm monitor http [NAME] [--partition PARTITION]
list ltm monitor https [NAME] [--partition PARTITION]
list ltm monitor icmp [NAME] [--partition PARTITION]
list ltm monitor tcp [NAME] [--partition PARTITION]
list ltm monitor udp [NAME] [--partition PARTITION]
```
- Display monitor definitions by protocol with optional name and partition filters.

### LTM nodes, pools, rules, and SNAT

```
list ltm node [NAME] [--partition PARTITION]
list ltm pool [NAME] [--partition PARTITION]
list ltm pool-member [NAME] [--partition PARTITION]
list ltm rule [NAME]
list ltm snat [NAME]
```
- Inspect node, pool, pool member, iRule, or SNAT objects. Provide `NAME` as a comma-delimited list when applicable.

### LTM profiles

```
list ltm profile client-ssl [NAME] [--partition PARTITION]
list ltm profile http [NAME] [--partition PARTITION]
list ltm profile server-ssl [NAME] [--partition PARTITION]
list ltm profile tcp [NAME] [--partition PARTITION]
list ltm profile udp [NAME] [--partition PARTITION]
```
- Show profile configuration for the specified type. Partition defaults to `Common` when omitted.

### LTM persistence profiles

```
list ltm persist cookie [NAME] [--partition PARTITION]
list ltm persist dest-addr [NAME] [--partition PARTITION]
list ltm persist source-addr [NAME] [--partition PARTITION]
list ltm persist ssl [NAME] [--partition PARTITION]
list ltm persist universal [NAME] [--partition PARTITION]
```
- Review persistence profile settings by method with optional name and partition filters.

### LTM virtual servers

```
list ltm virtual NAME [--verbose] [--oneline] [--partition PARTITION]
```
- Retrieve virtual server details. Use `--oneline` for condensed output or `--verbose` for expanded statistics.

### Network objects

```
list net interface [NAME]
list net route [NAME] [--partition PARTITION]
list net self [NAME] [--partition PARTITION]
list net trunk [NAME]
list net vlan [NAME]
```
- Show interface, route, self-IP, trunk, or VLAN definitions with optional filters.

### System configuration

```
list sys crypto cert [NAME]
list sys crypto key [NAME]
list sys dns
list sys failover
list sys global-settings
list sys license
list sys management-ip [NAME]
list sys management-route [NAME]
list sys ntp
list sys smtp-server
list sys snmp [NAME]
list sys syslog [NAME]
```
- Inspect certificate and key stores, DNS, failover status, global settings, license info, management IPs/routes, NTP, SMTP servers, SNMP, and syslog configuration. Many commands accept optional names to narrow the results.

## Save

```
save config
```
- Save the current LTM configuration.

## Show

```
show cm sync-status
show sys license
```
- Display device cluster sync status or the system license summary.

## Test

```
test device
```
- Run the OTX device test for the currently loaded device list.

## Update

```
update backup [--oneline]
update device [--addr ADDR] [--dtype TYPE] [--fqdn FQDN] [--org ORG] [--proxy PROXY] [--pwd PASSWORD] [--state STATE] [--user USER]
update profile client-ssl NAME [--cert CERT] [--chain CHAIN] [--key KEY]
update version
```
- `update backup` triggers a UCS backup or a condensed one-line backup with `--oneline`.
- `update device` edits device metadata fields.
- `update profile client-ssl` swaps the certificate, chain, or key for the given profile.
- `update version` refreshes the LTM version metadata.

## Upload

```
upload cert [FILENAME]
upload chain [FILENAME]
upload key [FILENAME]
upload rest file [FILENAME]
upload cert-key NAME CERT KEY [--chain CHAIN]
```
- Upload certificate, chain, key, or arbitrary REST files. Each accepts comma-delimited filenames when multiple files are provided.
- `upload cert-key` performs a combined workflow: upload certificate/key (and optional chain), install the uploaded components, and update the referenced client SSL profile.
