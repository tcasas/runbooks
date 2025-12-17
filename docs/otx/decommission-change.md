# Decommission Change Requests

This runbook summarizes the three-phase process for decommissioning in SM9. Each phase builds on the previous change record, so keep the parent record accurate and carry updates forward.

- Parent change: tracking decommissioning and gathering approvals.
- Shutdown change: executing shutdown activities.
- Eliminate change: physically removing the device.

## Parent Change Record (Decom CR)
1. Log into SM9 and navigate to **Change > Open New Change > Decommission Change**.
2. Complete all required fields; assign the change to **Ops-Service Mgt_Release Mgt** with an assignee of **Bhavya Uday Shankar / Ravali Kantareddy / Lalitha Sathish**.
3. In **Technical Plans and Concurrences**, provide implementation, verification, and reversion plans (numbered steps or attachment).
4. Set **Expert Review of this CR?** to **Y, SHAKIRABANU (SHAKIRABANUY)**.
5. In **Decommission Q&A**, provide the purpose, decommission owner (**Bhavya Uday Shankar / Ravali Kantareddy / Lalitha Sathish**), key participants (including SM9 queue details), and evidence of inactivity. Attach the inactivity report.
6. Save the record. Approvals are required from the initiator’s Director/M1/M2 and a Release Manager. Once approved, the record moves to **Evaluation & Change Closure** and an automated RFA is assigned to monitoring to disable the host.

## Shutdown Change Record
1. After the parent is approved, open it, select **More > Copy record** to create the shutdown CR.
2. Update fields:
   - **Category:** Shutdown.
   - **Assignment Group & Assignee**, **Planned Start/End Date**.
   - **Technical Plans** for shutdown.
   - **Expert Review:** assign the technical lead for your group.
3. Save. Approvals by Release Management and Change Coordinator move it to **Evaluation & Change Closure**.

## Eliminate Change Record
1. Create 14 days after the shutdown CR is completed by copying the shutdown record.
2. Relate both the parent and shutdown records to the eliminate CR.
3. Update fields:
   - **Category:** Eliminate.
   - **Assignment Group & Assignee**, **Planned Start/End Date**, **Expert Reviewer**.
4. Attach the required **Decommission Hardware Information** spreadsheet (link available within the eliminate CR).
5. Save. Release Management and Change Coordinator approvals move the record to **Evaluation & Closure**, after which the assignee completes the work. Automated RFAs will be issued to the appropriate operations teams once closed.

## Contacts and Help
- **Release Management:** opentext_release_management@opentext.com
- **Business Process Analysts:** Shakirabanu Y (shakirabanuy@opentext.com), Bhavya Uday Shankar (bhavyaudayu@opentext.com)
- Reference: Release Mgt. Decommission Procedure.pptx
