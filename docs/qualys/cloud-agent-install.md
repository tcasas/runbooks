# Qualys Cloud Agent Installation Runbook

This runbook describes how to transfer and install the Qualys Cloud Agent with proxy support and sudo configuration.

## Prerequisites
- Root privileges on the target host.
- Customer ID and Activation ID for the appropriate environment.
- Access to the Qualys Cloud Agent installation package (`QualysCloudAgent.rpm`).
- Network access to the Qualys platform (`https://qagpublic.qg1.apps.qualys.com/CloudAgent/`) and any required proxy.

## Activation details
- Customer ID: `9c0e25eb-bee2-5af6-e040-10ac13043f6a`
- Activation ID (Network): `6fc8bfb9-1869-4456-be16-f8dfc76bbd85`

## Download the Cloud Agent
- Retrieve the installer from the internal download page: https://intranet.opentext.com/intranet/llisapi.dll?func=ll&objId=178461660&objAction=browse
- Save the RPM as `QualysCloudAgent.rpm` on your workstation.

## Transfer the installer to the target host
Choose one of the following methods.

### Option 1: SSH port forwarding via jump host
1. Forward a local port (example uses 2057) to the target host through the jump host:
   ```bash
   ssh -L 2057:10.138.194.78:22 tcasas@150.105.166.78
   ```
2. Copy the installer through the forwarded port:
   ```bash
   scp -P 2057 ./QualysCloudAgent.rpm root@localhost:/root/
   ```
3. SSH to the target through the forwarded port to verify the file:
   ```bash
   ssh -p 2057 root@127.0.0.1
   ls -l /root/QualysCloudAgent.rpm
   ```

### Option 2: ProxyJump with scp
Copy the installer directly through the jump host in one command:
```bash
scp -o ProxyJump=tcasas@150.105.166.78 ./QualysCloudAgent.rpm root@10.138.194.78:/root/
```

## Install and configure the agent
1. Install the RPM:
   ```bash
   sudo rpm -ivh QualysCloudAgent.rpm
   ```
2. Register the agent:
   ```bash
   sudo /usr/local/qualys/cloud-agent/bin/qualys-cloud-agent.sh \
     ActivationId=6fc8bfb9-1869-4456-be16-f8dfc76bbd85 \
     CustomerId=9c0e25eb-bee2-5af6-e040-10ac13043f6a \
     ServerUri=https://qagpublic.qg1.apps.qualys.com/CloudAgent/ \
     LogLevel=4
   ```
3. (Optional) Configure the agent service account:
   ```bash
   /usr/local/qualys/cloud-agent/bin/qualys-cloud-agent.sh User="username" UseSudo=1
   ```

## Configure proxy (if required)
1. Create `/etc/sysconfig/qualys-cloud-agent` with proxy settings:
   ```bash
   sudo tee /etc/sysconfig/qualys-cloud-agent >/dev/null <<'CFG'
   qualys_https_proxy=http://f5exp-proxy.all.gxsonline.net:3128/
   CFG
   ```
   - For proxy failover, specify multiple entries separated by semicolons, e.g. `https://<host1>:<port1>;https://<host2>:<port2>`.
2. Secure the proxy file:
   ```bash
   sudo chown root:root /etc/sysconfig/qualys-cloud-agent
   sudo chmod 600 /etc/sysconfig/qualys-cloud-agent
   ```
3. Restart the agent after proxy updates:
   ```bash
   sudo service qualys-cloud-agent restart
   sudo service qualys-cloud-agent status
   ```

## Sudo configuration for non-root agent user
- Add the agent user (e.g., `agentuser`) to sudoers without a password prompt:
  ```bash
  echo '%agentuser ALL=(ALL) NOPASSWD: ALL' | sudo tee -a /etc/sudoers.d/qualys-agent
  ```
- Ensure `secure_path` includes Qualys paths if commands are not in `PATH`.

## Logging and troubleshooting
- Set log level (0 fatal, 1 error, 2 warning, 3 info, 4 debug, 5 trace):
  ```bash
  /usr/local/qualys/cloud-agent/bin/qualys-cloud-agent.sh LogLevel=4
  ```
- View logs:
  ```bash
  sudo tail -f /var/log/qualys/qualys-cloud-agent.log
  ```

## Agent options reference
Use the built-in script to set optional parameters such as process priority, scan randomization, and EDR limits:
```bash
/usr/local/qualys/cloud-agent/bin/qualys-cloud-agent.sh
```
Key options include:
- `InstallDirPermission=0755`
- `LogDestType=<syslog|file>` and `LogFileDir=<dir>`
- `LogCompression=0|1`
- `UseSudo=0|1`, `User=<scanuser>`, `Group=<scangroup>`, `SudoCommand=<cmd>`
- `CmdMaxTimeOut=<seconds>`
- `ProcessPriority=-20..19`
- `HostIdSearchDir=<dir>`
- `ProviderName=AWS|AZURE|GCP|IBM|ALIBABA|ORACLE|NONE`
- `UseAuditDispatcher=0|1`
- `QualysProxyOrder=sequential|random`
- `ProxyFailOpen=0|1`
- `CmdStdOutSize=<KB>`
- `MaxRandomScanIntervalVM=<0-86400>` and `MaxRandomScanIntervalPC=<0-86400>`
- `ScanDelayVM=<0-86400>` and `ScanDelayPC=<0-86400>`
- `EDRCPULimit=<2-100>` and `EDRMemoryLimit=<2-100>`
- `AuditBacklogLimit=<>=320>` (default 8192)

## Self-service portal reminders
- Qualys self-service portal: http://go/scanner
- Add `svc_VAScanner` to ISE to bypass 2FA and to sudoers:
  ```
  IDLDAP\\svc_VAScannerALL=(ALL)NOPASSWD: ALL
  ```
- Use the portal to initiate scans after agent deployment.
