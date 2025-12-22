[Runbooks Index](../index.md) / [Turtle CLI](index.md)

# Turtle CLI GCP commands

Use these commands inside the Turtle CLI REPL to manage GCP resources through the GCP command set. Arguments that accept multiple values expect comma-delimited input.

## Assign

```
assign lb-admin PROJECT_ID
```
- Assign load balancer admin access for the comma-delimited project IDs.

## Create

```
create projects PROJECT_ID
```
- Create one or more projects identified by comma-delimited project IDs.

## Delete

```
delete certs
```
- Remove certificate records associated with the currently loaded devices.

## Import

```
import certs [RECIPIENTS] [--region REGION]
```
- Import certificates using optional comma-delimited recipients and an optional comma-delimited region list. When `--region` is provided, certificates are imported regionally; otherwise, the global import runs.

```
import project FILENAME
```
- Import a GCP project from the service account file at `FILENAME`.

## List

```
list device [DEVICE]
```
- List one or more devices (comma-delimited) through the OTX device command.

```
list projects
```
- List available projects.

```
list xpn-resources PROJECT_ID
```
- List cross-project networking resources for the comma-delimited project IDs.

## Update

```
update device [--addr ADDR] [--dtype TYPE] [--fqdn FQDN] [--org ORG] [--proxy PROXY] [--pwd PASSWORD] [--state STATE] [--user USER]
```
- Update device metadata fields for the certificate host device. The command operates on the devices configured for the current session.
