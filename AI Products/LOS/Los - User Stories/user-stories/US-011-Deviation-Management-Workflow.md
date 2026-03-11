# US-011: Deviation Management Workflow

| Field          | Value                                                                 |
|----------------|-----------------------------------------------------------------------|
| **Story ID**   | US-011                                                                |
| **Module**     | D — Underwriting & Assessment                                         |
| **Priority**   | Critical                                                              |
| **PRD Ref**    | FR 4.3                                                                |
| **Created**    | 2026-02-19                                                            |

---

## Actors

| Actor                    | Role                                                              |
|---------------------------|------------------------------------------------------------------|
| **Credit Manager**        | Encounters a deviation; selects justification and submits        |
| **Deviation Approver**    | Senior authority who approves/rejects deviations per DOA matrix  |
| **Credit Admin**          | Configures DOA matrix and deviation codes                         |
| **System (E-LOS)**        | Detects rule failures, triggers deviations, routes for approval  |

---

## System Name

**E-LOS** (Enterprise Loan Origination System)

---

## Brief Description

As a **Credit Manager**, when a business rule fails (e.g., applicant Age > 60), I want the system to trigger a formal "Deviation" requiring me to select a justification code, after which the system routes the deviation to the appropriate authority defined in the DOA (Delegation of Authority) matrix, so that exceptions are properly governed and audited.

---

## Business Goal

- Ensure **controlled exception handling** — no rule breach passes without senior approval.
- Maintain regulatory compliance via documented deviation justifications.
- Provide full audit trail of every deviation decision.

---

## Acceptance Criteria

| #  | Criterion                                                                                                    | Status |
|----|--------------------------------------------------------------------------------------------------------------|--------|
| 1  | When a BRE rule fails, system auto-creates a **Deviation** record linked to the application.                 | ☐      |
| 2  | Deviation record shows: Rule Name, Failed Condition, Actual Value vs. Allowed Value.                         | ☐      |
| 3  | Credit Manager must select a **Justification Code** from a pre-configured list (e.g., "Strong Collateral", "High Net Worth"). | ☐      |
| 4  | Credit Manager can add **free-text comments** supporting the justification.                                  | ☐      |
| 5  | System looks up the **DOA matrix** to determine the approval authority based on: Deviation Type + Amount slab. | ☐      |
| 6  | Deviation is routed to the identified approver's queue.                                                      | ☐      |
| 7  | Approver can **Approve**, **Reject**, or **Escalate** the deviation.                                         | ☐      |
| 8  | On approval → application proceeds. On rejection → application is sent back/rejected.                        | ☐      |
| 9  | Multiple deviations on the same application are tracked independently.                                       | ☐      |
| 10 | All deviation actions (create, justify, approve, reject, escalate) are immutably audit-logged.                | ☐      |
| 11 | DOA matrix is configurable by Credit Admin (Deviation Type × Amount Slab → Required Authority Level).        | ☐      |

---

## Use Cases

### UC-011.1 — Standard Deviation Flow
1. Application has Applicant Age = 63; BRE rule requires Age ≤ 60.
2. System triggers Deviation: "Age exceeds maximum (63 > 60)."
3. Credit Manager selects justification: "High Net Worth Individual" + comment: "Net worth ₹5Cr+."
4. DOA matrix: Age deviations for Loan Amount ₹20L → requires "Senior Credit Manager."
5. Deviation routed to Senior CM queue.
6. Senior CM reviews → Approves → Application proceeds.

### UC-011.2 — Deviation Rejected
1. Deviation raised for FOIR = 72% (max 60%).
2. Junior CM justifies: "Stable employment."
3. Senior CM reviews → Rejects: "FOIR too high; no compensating factors."
4. Application returns to Credit Manager for re-evaluation.

### UC-011.3 — Multiple Deviations
1. Application has Age = 63 (Deviation #1) and FOIR = 65% (Deviation #2).
2. Both tracked independently with separate justifications and approvals.
3. Application proceeds only when **all** deviations are approved.

### UC-011.4 — Escalation
1. DOA matrix allows Senior CM to approve up to certain limits.
2. Senior CM receives a deviation beyond their authority → clicks "Escalate."
3. System routes to the next authority level (e.g., Regional Head).

---

## Manual Testing Instructions

| Step | Action                                                                                          | Expected Result                                                        |
|------|-------------------------------------------------------------------------------------------------|------------------------------------------------------------------------|
| 1    | Submit application with Age = 63 (rule: max 60).                                                | Deviation auto-created; visible on application.                        |
| 2    | As Credit Manager, select justification code and submit.                                         | Deviation routed to approver per DOA matrix.                           |
| 3    | As Approver, approve the deviation.                                                              | Application status unblocked and proceeds.                             |
| 4    | Repeat with rejection.                                                                           | Application sent back; status reflects rejection.                      |
| 5    | Create application with 2 failed rules.                                                          | 2 separate deviations; application waits for both to be resolved.      |
| 6    | As Approver, escalate a deviation.                                                               | Deviation moves to the next authority level.                           |
| 7    | Check Audit Log.                                                                                 | All events logged: create, justify, route, approve/reject/escalate.    |

---

## Note for Automation Testing

> **Future Automation Scope:**
> - **E2E Deviation Flow**: API tests simulating full deviation lifecycle (trigger → justify → route → approve).
> - **DOA Matrix Tests**: Validate routing for all combinations of Deviation Type × Amount Slab.
> - **Multi-Deviation Tests**: Assert application blocked until all deviations resolved.
> - **Audit Completeness**: Assert every deviation action produces an audit entry.
> - **Authorization Tests**: Verify only DOA-authorised users can approve/reject deviations.

---

## Assumptions

1. Deviation codes are pre-configured by Credit Admin (not free-form).
2. DOA matrix is a 2D lookup: Deviation Category × Amount Slab → Required Authority Level.
3. An application with unresolved deviations **cannot** move to the Approved/Sanctioned state.
4. Escalation goes to the next level in the DOA hierarchy (not ad-hoc).

---

## Open Questions / Response Section

> **For Product Owner / Stakeholder to fill:**

| #  | Question                                                                                             | Response |
|----|------------------------------------------------------------------------------------------------------|----------|
| 1  | What are the deviation categories to be pre-configured for V1 (Age, FOIR, LTV, Income, Others)?       |          |
| 2  | How many levels of escalation should the DOA matrix support?                                         |          |
| 3  | Should deviation approval have an **SLA/timer** (e.g., auto-escalate if not acted on in 24 hours)?    |          |
| 4  | Can the Credit Manager **withdraw** a deviation before it's acted upon?                               |          |
