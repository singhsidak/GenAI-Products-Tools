# US-017: Workflow State Machine

| Field          | Value                                                                 |
|----------------|-----------------------------------------------------------------------|
| **Story ID**   | US-017                                                                |
| **Module**     | Cross-Cutting — Workflow Engine                                       |
| **Priority**   | Critical                                                              |
| **PRD Ref**    | Section 3 — Workflow States                                           |
| **Created**    | 2026-02-19                                                            |

---

## Actors

| Actor               | Role                                                                 |
|----------------------|----------------------------------------------------------------------|
| **Sales Officer**    | Moves cases from Draft to Logged In                                  |
| **Credit Manager**   | Transitions cases through Underwriting to Approved/Rejected          |
| **Operations User**  | Manages Disbursement Pending → Disbursed                             |
| **System (E-LOS)**   | Enforces valid state transitions and prevents illegal moves          |
| **Workflow Admin**   | Configures state machine rules and mandatory checks per transition   |

---

## System Name

**E-LOS** (Enterprise Loan Origination System)

---

## Brief Description

As the **E-LOS system**, I want to enforce a strict state machine governing application lifecycle transitions (Draft → Logged In → Underwriting → Approved → Disbursed, with Query Raised & Rejected/Cancelled as side-paths) so that no application can skip a stage or move to an invalid state.

---

## Business Goal

- Ensure **process integrity** — every application follows a governed lifecycle.
- Enable real-time status tracking and TAT measurement.
- Prevent unauthorized or premature state transitions.

---

## Acceptance Criteria

| #  | Criterion                                                                                                    | Status |
|----|--------------------------------------------------------------------------------------------------------------|--------|
| 1  | System enforces the following valid states: `DRAFT`, `LOGGED_IN`, `QUERY_RAISED`, `UNDERWRITING`, `APPROVED`, `DISBURSEMENT_PENDING`, `DISBURSED`, `REJECTED`, `CANCELLED`. | ☐      |
| 2  | Only the following transitions are allowed (see state diagram below).                                        | ☐      |
| 3  | Each transition validates **pre-conditions** (e.g., all mandatory docs uploaded before `LOGGED_IN`).         | ☐      |
| 4  | Invalid transition attempts return a clear error: "Cannot move from {current} to {target}."                  | ☐      |
| 5  | `REJECTED` and `CANCELLED` are **terminal states** — no further transitions allowed.                        | ☐      |
| 6  | Every state transition is **audit-logged** (old state, new state, user, timestamp, reason).                  | ☐      |
| 7  | Current state is prominently displayed on the application header/status bar.                                 | ☐      |
| 8  | State transition timestamps enable **TAT calculation** per stage.                                            | ☐      |
| 9  | Only authorized roles can execute specific transitions (e.g., only Credit Manager can approve).              | ☐      |

---

## State Transition Rules

```
DRAFT → LOGGED_IN (Sales submits with mandatory data)
LOGGED_IN → UNDERWRITING (Auto/Manual after BRE check passes)
LOGGED_IN → QUERY_RAISED (Credit Manager sends back for info)
QUERY_RAISED → LOGGED_IN (Sales re-submits with updates)
UNDERWRITING → APPROVED (Credit Manager approves)
UNDERWRITING → QUERY_RAISED (Credit Manager requests more info)
UNDERWRITING → REJECTED (Credit Manager rejects)
APPROVED → DISBURSEMENT_PENDING (Ops begins disbursement prep)
DISBURSEMENT_PENDING → DISBURSED (Ops completes disbursement)
Any non-terminal state → CANCELLED (Authorized user cancels)
```

---

## Use Cases

### UC-017.1 — Happy Path
1. Lead enters as `DRAFT`.
2. Sales uploads KYC/docs → submits → moves to `LOGGED_IN`.
3. BRE evaluates → routes to Credit → `UNDERWRITING`.
4. Credit Manager approves → `APPROVED`.
5. Ops verifies docs → `DISBURSEMENT_PENDING`.
6. Money sent → `DISBURSED`.

### UC-017.2 — Query Raised Loop
1. Application in `UNDERWRITING`.
2. Credit Manager needs more info → `QUERY_RAISED`.
3. Sales adds the info → re-submits → `LOGGED_IN` → `UNDERWRITING`.

### UC-017.3 — Invalid Transition Blocked
1. Application in `DRAFT`.
2. User attempts to move directly to `APPROVED`.
3. System blocks: "Cannot move from DRAFT to APPROVED."

### UC-017.4 — Cancellation
1. Application in `LOGGED_IN`.
2. Authorized user clicks "Cancel" with reason: "Customer withdrew."
3. Application moves to `CANCELLED` (terminal).

---

## Manual Testing Instructions

| Step | Action                                                                                          | Expected Result                                                        |
|------|-------------------------------------------------------------------------------------------------|------------------------------------------------------------------------|
| 1    | Walk through the full happy path (DRAFT → DISBURSED).                                           | All transitions succeed with proper pre-condition checks.              |
| 2    | Attempt DRAFT → APPROVED directly.                                                              | Blocked with error.                                                    |
| 3    | Create, then reject an application.                                                              | Status = REJECTED (terminal). No further transitions allowed.          |
| 4    | Cancel a LOGGED_IN application.                                                                 | Status = CANCELLED (terminal).                                         |
| 5    | Query raised → re-submit loop.                                                                  | Transitions work correctly; audit log shows the loop.                  |
| 6    | Check TAT: measure timestamp between LOGGED_IN and UNDERWRITING.                                | Timestamp difference calculated and accurate.                          |
| 7    | Non-Credit user attempts to approve.                                                            | Blocked: "Insufficient permissions."                                   |

---

## Note for Automation Testing

> **Future Automation Scope:**
> - **Transition Matrix Tests**: Test all N×N state combinations → assert valid ones pass and invalid ones fail.
> - **Pre-Condition Tests**: Assert each transition validates its prerequisites.
> - **Role-Authorization Tests**: Assert only authorized roles can execute each transition.
> - **Concurrency Tests**: Two users attempt conflicting transitions simultaneously.
> - **TAT Accuracy**: Assert timestamps are captured with sub-second precision.

---

## Assumptions

1. The workflow engine (Camunda/JBPM) will enforce state transitions at an engine level (not just UI validation).
2. Pre-conditions per transition will be defined during detailed design (e.g., what's mandatory for DRAFT → LOGGED_IN).
3. `QUERY_RAISED` re-submits go back to `LOGGED_IN` (not directly to `UNDERWRITING`).

---

## Open Questions / Response Section

> **For Product Owner / Stakeholder to fill:**

| #  | Question                                                                                             | Response |
|----|------------------------------------------------------------------------------------------------------|----------|
| 1  | Can a `REJECTED` application be **reopened** (e.g., a reconsideration flow)?                          |          |
| 2  | Should `CANCELLED` require senior approval or can any user cancel?                                   |          |
| 3  | Is there a **timeout/SLA** on states (e.g., auto-escalate if in UNDERWRITING > 3 days)?               |          |
| 4  | Should there be a `SANCTIONED` state between `APPROVED` and `DISBURSEMENT_PENDING`?                   |          |
