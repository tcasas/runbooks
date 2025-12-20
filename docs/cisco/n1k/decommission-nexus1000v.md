[Runbooks Index](../../index.md) / [Cisco](../index.md) / [Nexus 1000V](index.md)

# Cisco Nexus 1000V Decommission Runbook

## Preparation
- Identify all hosts with Nexus 1000V DVS/VSM/VEM.
- Back up the current VSM configuration and record port-group assignments, uplinks, VLANs, and VM connectivity.
- Schedule a maintenance window and ensure access to both vCenter and the VSM CLI.

## Step 1: Migrate VM/VMkernel Networking
1. Move all virtual machines and VMkernel adapters off the Nexus 1000V DVS.
2. In the vCenter Web Client, navigate to **Networking → Distributed Switch (Nexus1000V) → Migrate Virtual Machine Networking**.
3. For each VM/VMkernel adapter, migrate to a standard vSwitch or VMware DVS.
4. Verify no VM or VMkernel adapter remains on Nexus 1000V port-groups.

## Step 2: Remove ESXi Hosts from Nexus 1000V DVS
1. Once no VMs or VMkernels remain, open vCenter and go to **Networking → Nexus1000V → Hosts**.
2. For each host, right-click and select **Remove from Distributed Virtual Switch**.
3. Confirm all hosts are detached from the DVS.

## Step 3: Remove the DVS via VSM CLI
1. SSH to the VSM and remove the DVS configuration:
   ```
   ssh admin@<vsm-ip>
   show svs connections
   conf t
   svs connection <connection-name>
   no vmware dvs
   exit
   no connect
   exit
   ```
2. Confirm the Nexus 1000V DVS object disappears from vCenter.

## Step 4: Unregister the vCenter Extension
1. Access the vCenter Managed Object Browser (MOB) at `https://<vcenter>/mob/?moid=ExtensionManager`.
2. Locate the Cisco Nexus 1000V extension key (for example, `Cisco_Nexus_1000V_xxx`).
3. Click **UnregisterExtension**, paste the extension key, and invoke the method.
4. Log out and back into vCenter to verify the plugin is removed.

## Step 5: Remove VEM Modules from ESXi Hosts
1. For each ESXi host, check for VEM modules and remove them:
   ```
   esxcli software vib list | grep cisco-vem
   vem status
   esxcli software vib remove -n cisco-vem-vXXX
   ```
2. For older versions, use:
   ```
   vem-remove -d
   ```
3. Reboot the host if required:
   ```
   reboot
   ```
4. Verify removal with `esxcli software vib list | grep cisco-vem` and repeat for all hosts.

## Step 6: Delete VSM Virtual Machines
1. In vCenter, locate the VSM VM(s) (primary and standby if present).
2. Power off each VSM VM.
3. Right-click the VM and select **Delete from Disk**.
4. Ensure all configuration files and snapshots are removed.

## Step 7: Cleanup and Validation
- Verify no Nexus 1000V port-groups or uplinks remain.
- Confirm physical switches show no Nexus 1000V VLANs or LAGs.
- Ensure all ESXi hosts have valid connectivity via standard vSwitches or VMware DVS.
- Confirm vCenter displays no Nexus 1000V objects.
- Check for residual logs or errors in vCenter or ESXi.
- Update documentation and inventory.

## Optional Recovery (Orphaned DVS)
- If the VSM was deleted before DVS removal:
  - Reinstall a temporary VSM using the same extension key.
  - Issue `no vmware dvs` from the VSM CLI to clean up the orphaned DVS.
- Avoid manual database edits unless absolutely necessary.

## Final Checklist
- [ ] VM/VMkernel traffic migrated off Nexus 1000V
- [ ] All hosts removed from the DVS
- [ ] DVS removed via VSM CLI
- [ ] vCenter extension unregistered
- [ ] VEM modules removed from hosts
- [ ] VSM VMs deleted
- [ ] Validation and cleanup complete
- [ ] Documentation updated
