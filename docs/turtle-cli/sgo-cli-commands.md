[Runbooks Index](../index.md) / [Turtle CLI](index.md)

# Turtle CLI SGO commands

Use these commands inside the Turtle CLI REPL to work with SGO certificate operations. Each verb delegates to the SGO command set and executes through the Macro runner.

## Collect

```
collect pending SGO_ID
```
- Queue collection for one or more comma-delimited Sectigo order IDs.

## Import

```
import domains [RECIPIENTS]
```
- Import new domains and optionally email comma-delimited recipients with the results.

## List

```
list cert [COMMON_NAME] [--sgo-id SGO_ID] [--status STATUS]
```
- List certificates by optional comma-delimited common names, SGO IDs, or a status filter.

```
list cert-profiles ORG_ID
```
- List certificate profiles for one or more comma-delimited department IDs.

```
list device [DEVICE]
```
- List comma-delimited devices through the OTX device command.

```
list domain DOMAIN
```
- List domains for the provided comma-delimited domain names.

```
list domains
```
- List all OTX domains from the SGO host.

```
list validation DOMAIN
```
- List domain validation results for comma-delimited domain names.

```
list orgs
```
- List organizations available to SGO.

## Revoke

```
revoke cert [--sgo-id SGO_ID] [--serial SERIAL]
```
- Revoke certificates filtered by comma-delimited SGO IDs or serial numbers.

## Update

```
update device [--addr ADDR] [--dtype TYPE] [--fqdn FQDN] [--org ORG] [--proxy PROXY] [--pwd PASSWORD] [--state STATE] [--user USER]
```
- Update device metadata fields for the SGO host, setting address, type, FQDN, organization, proxy, password, state, or username as needed.
