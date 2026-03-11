# US-003: Lead Auto-Allocation Engine

| Field          | Value                                                                 |
|----------------|-----------------------------------------------------------------------|
| **Story ID**   | US-003                                                                |
| **Module**     | A — Lead & Sourcing                                                   |
| **Priority**   | High                                                                  |
| **PRD Ref**    | FR 1.3                                                                |
| **Created**    | 2026-02-19                                                            |

---

## Actors

| Actor               | Role                                                                 |
|----------------------|----------------------------------------------------------------------|
| **System (E-LOS)**   | Executes allocation logic on each new lead                           |
| **Sales Officer**    | Receives allocated leads in their work queue                          |
| **Sales Manager**    | Views allocation reports; can manually re-assign leads               |
| **Operations Admin** | Configures Pincode-to-Officer mapping and allocation strategy        |

---

## System Name

**E-LOS** (Enterprise Loan Origination System)

---

## Brief Description

As a **Sales Manager**, I want incoming leads to be automatically assigned to Sales Officers based on Pincode mapping (location-based) or Round Robin logic so that leads are distributed fairly and serviced quickly without manual intervention.

---

## Business Goal

- Eliminate manual lead assignment bottleneck.
- Ensure **geographic proximity** for on-ground leads (field sales efficiency).
- Guarantee **fair workload distribution** via round-robin when geography is not a factor.
- Reduce lead response time (first contact within SLA).

---

## Acceptance Criteria

| #  | Criterion                                                                                                    | Status |
|----|--------------------------------------------------------------------------------------------------------------|--------|
| 1  | Admin can create/edit a **Pincode ↔ Sales Officer** mapping table.                                           | ☐      |
| 2  | When a lead is created with a serviceable pincode, it is auto-assigned to the mapped Sales Officer.           | ☐      |
| 3  | If no pincode mapping exists or the mapped officer is inactive, system falls back to **Round Robin**.          | ☐      |
| 4  | Round Robin distributes leads equally among all active Sales Officers in the same region/team.                | ☐      |
| 5  | Round Robin state is persisted (survives server restarts).                                                    | ☐      |
| 6  | Allocated lead appears in the Sales Officer's **My Leads** dashboard immediately.                            | ☐      |
| 7  | A push notification / in-app alert is sent to the assigned officer on allocation.                            | ☐      |
| 8  | Sales Manager can **manually re-assign** a lead to another officer with a mandatory reason.                  | ☐      |
| 9  | Re-assignment is logged in the Audit Trail, capturing old and new assignee.                                  | ☐      |
| 10 | Allocation logic executes within **< 200ms** of lead creation.                                               | ☐      |

---

## Use Cases

### UC-003.1 — Pincode-Based Allocation
1. A lead arrives with Pincode `110001`.
2. System looks up Pincode mapping → finds Sales Officer "Rahul Mehta."
3. Lead is assigned to Rahul; he sees it in his queue with a "New" badge.

### UC-003.2 — Round Robin Fallback
1. A lead arrives with Pincode `999999` (unmapped).
2. System checks Round Robin pointer → next officer in rotation is "Priya Gupta."
3. Lead is assigned to Priya; pointer advances to the next officer.

### UC-003.3 — Manual Re-Assignment
1. Sales Manager views a lead assigned to Officer A (who is on leave).
2. Clicks "Re-Assign" → selects Officer B → enters reason: "Officer A on medical leave."
3. Lead moves to Officer B's queue; Audit Log records the change.

### UC-003.4 — Inactive Officer Handling
1. A lead's pincode maps to Officer C, who has status = `INACTIVE`.
2. System skips Officer C → falls back to Round Robin among active officers.

---

## Manual Testing Instructions

| Step | Action                                                                                          | Expected Result                                                        |
|------|-------------------------------------------------------------------------------------------------|------------------------------------------------------------------------|
| 1    | Set up Pincode mapping: `110001 → Officer A`. Create a lead with Pincode `110001`.              | Lead assigned to Officer A.                                            |
| 2    | Create a lead with an unmapped Pincode (`999999`).                                              | Lead assigned via Round Robin to the next officer in rotation.         |
| 3    | Create 5 leads with unmapped pincodes in sequence.                                              | Leads distributed evenly across active officers in order.              |
| 4    | Mark Officer A as `INACTIVE`. Create a lead with Pincode `110001`.                              | Lead NOT assigned to Officer A; falls back to Round Robin.             |
| 5    | Log in as Sales Manager → re-assign a lead from Officer B to Officer C with a reason.           | Lead moves to Officer C's queue; Audit Log entry created.             |
| 6    | Restart the application server. Create another unmapped lead.                                   | Round Robin continues from the correct pointer (not reset).            |

---

## Note for Automation Testing

> **Future Automation Scope:**
> - **Round Robin Fairness Test**: Create N leads (N = 3 × number of officers) and assert even distribution (±1).
> - **Failover Test**: Deactivate all officers in a region → assert lead is flagged as "Unassigned" with an alert to the Sales Manager.
> - **Concurrency Test**: Submit 100 leads simultaneously and verify no two leads skip the same Round Robin slot (no race condition).
> - **API Tests**: Assert `assignedOfficerId` in lead response after creation.
> - **Notification Tests**: Mock notification service to verify push is triggered on allocation.

---

## Assumptions

1. Pincode mapping is managed at the **team/region** level, not globally.
2. "Round Robin" means strict sequential rotation (not weighted).
3. The allocation runs **synchronously** as part of lead creation — not as a deferred background job.
4. Notification delivery mechanism (push/SMS/email) will be decided during tech design.

---

## Open Questions / Response Section

> **For Product Owner / Stakeholder to fill:**

| #  | Question                                                                                             | Response |
|----|------------------------------------------------------------------------------------------------------|----------|
| 1  | Should allocation support a **weighted Round Robin** (e.g., senior officers get 2x leads)?            |          |
| 2  | What happens if **all officers** in a region are inactive — should it escalate to the Manager?        |          |
| 3  | Is there a **daily cap** on leads per officer?                                                       |          |
| 4  | Should the system support **product-based** allocation (e.g., Home Loan officers vs. PL officers)?    |          |
