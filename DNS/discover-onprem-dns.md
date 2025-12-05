
# Discover On-Prem Name Servers (DNS) Runbook

## 1️⃣ Check Local System Configuration

**Linux – see DNS servers in use**
```bash
cat /etc/resolv.conf
```
> nameserver <IP>

```bash
systemd-resolve --status
```
> DNS Servers: <IP-1>, <IP-2>

```bash
nmcli dev show | grep DNS
```
> DNS: <IP>

**Windows**
```powershell
Get-DnsClientServerAddress
```
> ServerAddresses: {<IP>}

```powershell
ipconfig /all | findstr "DNS Servers"
```
> DNS Servers . . . . . . . . . . . : <IP>

## 2️⃣ Query Internal Domain NS Records

> Replace `corp.local` with your internal domain

```bash
dig corp.local NS
```
> ;; ANSWER SECTION:  
> corp.local. 3600 IN NS <ns1.corp.local.>

```bash
nslookup -type=ns corp.local
```
> ns1.corp.local  
> ns2.corp.local

## 3️⃣ Discover AD-Backed DNS (if applicable)

**Show Domain Controllers and DNS service role**
```powershell
Get-ADDomainController -Filter * | Select-Object HostName,IPv4Address
```
> hostname.domain | 10.x.x.x

**Check which servers have DNS role installed**
```powershell
Get-WindowsFeature DNS
```
> Installed: True

## 4️⃣ Scan Subnets for Port 53

**Network scan for DNS servers**
```bash
nmap -sU -p 53 10.0.0.0/24
```
> 10.0.0.10 53/udp open domain

**Attempt version discovery**
```bash
nmap -sV -p 53 10.0.0.0/24
```
> ISC BIND / Microsoft DNS version info

## 5️⃣ Check DHCP Distributed DNS Servers

**Linux DHCP config**
```bash
grep domain-name-servers /etc/dhcp/dhcpd.conf
```
> option domain-name-servers <IP1>,<IP2>;

**Windows DHCP GUI**
> Scope Options → **006 DNS Servers** & **015 DNS Domain Name**

## 6️⃣ Check Network Core Devices

**Cisco**
```bash
show run | include name-server
```
> ip name-server <IP>

**F5 BIG-IP**
```bash
tmsh list sys dns
```
> name-servers { <IP1> <IP2> }

**Palo Alto**
```bash
show dns-proxy dns-summary
```

> Check firewall logs for DNS traffic patterns if needed

## 7️⃣ Validate DNS Server Role

**Test for authoritative response**
```bash
dig @<server-ip> corp.local SOA +norecurse
```
> flags: aa;  # authoritative

**Test recursion**
```bash
dig @<server-ip> google.com
```
> ;; ANSWER SECTION:  # recursive resolver OK

## 8️⃣ Document Findings

**Recommended table format**
```
Server       | Role          | Zone        | Recursive | Comments
-------------|---------------|-------------|-----------|---------
10.0.0.10    | Primary DNS   | corp.local  | Yes       | AD DC1
10.0.0.11    | Secondary DNS | corp.local  | Yes       | AD DC2
```
