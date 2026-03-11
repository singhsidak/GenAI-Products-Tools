# US-006: Configurable Rule Builder (Expression Builder)

| Field          | Value                                                                 |
|----------------|-----------------------------------------------------------------------|
| **Story ID**   | US-006                                                                |
| **Module**     | C — Business Rule Engine (BRE)                                        |
| **Priority**   | Critical                                                              |
| **PRD Ref**    | FR 3.1                                                                |
| **Created**    | 2026-02-19                                                            |

---

## Actors

| Actor               | Role                                                                 |
|----------------------|----------------------------------------------------------------------|
| **Credit Admin**     | Creates and manages business rules without writing code              |
| **Credit Manager**   | Reviews rule outcomes on individual applications                      |
| **System (E-LOS)**   | Evaluates rules against application data in real time                |
| **IT Admin**         | Manages rule versioning, audit, and environment promotion            |

---

## System Name

**E-LOS** (Enterprise Loan Origination System)

---

## Brief Description

As a **Credit Admin**, I want to create, modify, and manage business rules using a no-code Expression Builder UI (e.g., `IF BureauScore < 650 AND Product == 'Personal Loan' THEN Status = 'Auto-Reject'`) so that underwriting policies can be changed without developer involvement.

---

## Business Goal

- Enable **business-driven policy changes** without code deployments.
- Reduce rule change turnaround from weeks (dev cycle) to minutes.
- Maintain a versioned audit trail of all rule changes for regulatory compliance.

---

## Acceptance Criteria

| #  | Criterion                                                                                                    | Status |
|----|--------------------------------------------------------------------------------------------------------------|--------|
| 1  | Admin UI provides a drag-and-drop / form-based **Expression Builder** for rule creation.                      | ☐      |
| 2  | Builder supports conditions using: Comparison (`<`, `>`, `==`, `!=`), Logical (`AND`, `OR`, `NOT`), `IN` list. | ☐      |
| 3  | Available fields/parameters are dynamically loaded from application data schema (e.g., BureauScore, Age, Product, LoanAmount). | ☐      |
| 4  | Actions supported: Set Status (`Auto-Reject`, `Auto-Approve`, `Send to Manual Review`), Set Flag, Trigger Deviation. | ☐      |
| 5  | Rules have a **priority/order** — rules execute top-down; first matching rule with "stop" flag terminates. | ☐      |
| 6  | Every rule must have a name, description, effective date, and expiry date.                                   | ☐      |
| 7  | Rules can be marked as `ACTIVE`, `INACTIVE`, or `DRAFT`.                                                     | ☐      |
| 8  | Rule changes create a **new version**; previous versions are retained and viewable.                          | ☐      |
| 9  | A **Test/Simulate** mode allows admin to input sample data and see rule outcomes without affecting live data. | ☐      |
| 10 | Rule change events are immutably logged (who, when, old version, new version).                               | ☐      |

---

## Use Cases

### UC-006.1 — Create a New Rule
1. Credit Admin opens **BRE → Rule Builder → Create New**.
2. Defines: `IF BureauScore < 650 AND Product == 'Personal Loan' THEN Status = 'Auto-Reject'`.
3. Sets priority = 1, effective date = today, status = `ACTIVE`.
4. Saves → rule appears in the active rule list.

### UC-006.2 — Simulate a Rule
1. Admin clicks "Simulate" on the new rule.
2. Enters test data: BureauScore = 620, Product = "Personal Loan."
3. System evaluates → result: "Auto-Reject." Admin validates correctness.

### UC-006.3 — Edit and Version a Rule
1. Admin modifies the threshold from 650 to 600.
2. System creates Version 2; Version 1 is retained with a "Superseded" flag.
3. Audit Log records: "Rule #12 updated by Admin X at timestamp."

### UC-006.4 — Deactivate a Rule
1. Admin sets a rule to `INACTIVE`.
2. Rule no longer evaluates against new applications.
3. Historical applications processed under this rule retain their original outcomes.

---

## Manual Testing Instructions

| Step | Action                                                                                          | Expected Result                                                        |
|------|-------------------------------------------------------------------------------------------------|------------------------------------------------------------------------|
| 1    | Create a rule: `IF Age > 65 THEN Status = 'Auto-Reject'`. Set to ACTIVE.                        | Rule appears in active list.                                           |
| 2    | Submit a test application with Age = 70.                                                        | Application auto-rejected by BRE.                                      |
| 3    | Submit a test application with Age = 40.                                                        | Rule does not trigger; application proceeds normally.                  |
| 4    | Use Simulate mode with Age = 70.                                                                | Simulation returns "Auto-Reject" without creating real data.           |
| 5    | Edit the rule to Age > 70 → verify a new version is created.                                    | Version history shows V1 (>65) and V2 (>70).                          |
| 6    | Deactivate the rule → submit application with Age = 75.                                         | Rule does not trigger; application proceeds.                           |
| 7    | Check Audit Log for rule creation, edit, and deactivation events.                               | All three events logged with user, timestamp, and change details.      |

---

## Note for Automation Testing

> **Future Automation Scope:**
> - **Rule Engine Unit Tests**: Parameterized tests with 50+ data combinations per rule to validate correct evaluation.
> - **Expression Parser Tests**: Validate complex nested expressions, e.g., `(A AND B) OR (C AND NOT D)`.
> - **Version Integrity**: After N edits, assert N+1 versions exist and original is intact.
> - **Performance**: Evaluate 100 rules against 1,000 applications in batch → assert < 500ms total.
> - **Regression**: Ensure rule deactivation doesn't affect historical decision records.

---

## Assumptions

1. The expression builder will use a GUI — not raw code/scripting.
2. The underlying rule engine will be Drools or easy-rules (per tech stack recommendation).
3. "Auto-Approve" rules still require final human sign-off at the Underwriting stage.
4. Rule simulation uses a sandboxed evaluation — no DB writes for simulated runs.

---

## Open Questions / Response Section

> **For Product Owner / Stakeholder to fill:**

| #  | Question                                                                                             | Response |
|----|------------------------------------------------------------------------------------------------------|----------|
| 1  | Should rules support **nested conditions** (e.g., `IF (A AND B) OR (C AND D)`) in V1?                |          |
| 2  | Is there an **approval workflow** for rule changes (e.g., maker-checker), or can the admin publish directly? |          |
| 3  | Should we support rule **import/export** (e.g., JSON/CSV) for bulk management?                        |          |
| 4  | What is the maximum number of active rules the system should support per product?                     |          |
