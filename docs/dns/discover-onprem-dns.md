[Runbooks Index](../index.md) / [DNS](index.md)

# Discover On-Prem Name Servers (DNS) Runbook

Follow these steps to identify all on-prem DNS servers and understand their roles.

## 1️⃣ Check Local System Configuration

- **Linux – current resolvers**
  - `/etc/resolv.conf`
    ```bash
    cat /etc/resolv.conf
    ```
    Expected line: `nameserver <IP>`
  - `systemd-resolved`
    ```bash
    systemd-resolve --status
    ```
    Look for: `DNS Servers: <IP-1>, <IP-2>`
  - NetworkManager
    ```bash
    nmcli dev show | grep DNS
    ```
    Look for: `DNS: <IP>`

- **Windows – current resolvers**
  - DNS client servers
    ```powershell
    Get-DnsClientServerAddress
    ```
    Output sample: `ServerAddresses: {<IP>}`
  - Network adapter DNS servers
    ```powershell
    ipconfig /all | findstr "DNS Servers"
    ```
    Output sample: `DNS Servers . . . : <IP>`

## 2️⃣ Query Internal Domain NS Records

Replace `corp.local` with your internal domain when running the commands.

- `dig`
  ```bash
  dig corp.local NS
  ```
  Example answer section: `corp.local. 3600 IN NS <ns1.corp.local.>`

- `nslookup`
  ```bash
  nslookup -type=ns corp.local
  ```
  Example output:
  - `ns1.corp.local`
  - `ns2.corp.local`

## 3️⃣ Discover AD-Backed DNS (if applicable)

- **Find domain controllers and their IPs**
  ```powershell
  Get-ADDomainController -Filter * | Select-Object HostName,IPv4Address
  ```
  Example: `hostname.domain | 10.x.x.x`

- **Check which servers have the DNS role installed**
  ```powershell
  Get-WindowsFeature DNS
  ```
  Expect `Installed: True` on DNS hosts.

## 4️⃣ Scan Subnets for Port 53

- **Network scan for DNS servers**
  ```bash
  nmap -sU -p 53 10.0.0.0/24
  ```
  Example result: `10.0.0.10 53/udp open domain`

- **Attempt version discovery**
  ```bash
  nmap -sV -p 53 10.0.0.0/24
  ```
  Potential output: `ISC BIND / Microsoft DNS version info`

## 5️⃣ Check DHCP-Distributed DNS Servers

- **Linux DHCP config**
  ```bash
  grep domain-name-servers /etc/dhcp/dhcpd.conf
  ```
  Example: `option domain-name-servers <IP1>,<IP2>;`

- **Windows DHCP GUI**
  - Review **Scope Options** → **006 DNS Servers** and **015 DNS Domain Name**.

## 6️⃣ Check Network Core Devices

- **Cisco**
  ```bash
  show run | include name-server
  ```
  Expect: `ip name-server <IP>`

- **F5 BIG-IP**
  ```bash
  tmsh list sys dns
  ```
  Expect: `name-servers { <IP1> <IP2> }`

- **Palo Alto**
  ```bash
  show dns-proxy dns-summary
  ```
  Also review firewall logs for DNS traffic patterns if needed.

## 7️⃣ Validate DNS Server Role

- **Test for authoritative response**
  ```bash
  dig @<server-ip> corp.local SOA +norecurse
  ```
  Indicator: `flags: aa;  # authoritative`

- **Test recursion**
  ```bash
  dig @<server-ip> google.com
  ```
  Indicator: `;; ANSWER SECTION:  # recursive resolver OK`

## 8️⃣ Document Findings

Use a table to capture results:

```
Server       | Role          | Zone        | Recursive | Comments
-------------|---------------|-------------|-----------|---------
10.0.0.10    | Primary DNS   | corp.local  | Yes       | AD DC1
10.0.0.11    | Secondary DNS | corp.local  | Yes       | AD DC2
```
