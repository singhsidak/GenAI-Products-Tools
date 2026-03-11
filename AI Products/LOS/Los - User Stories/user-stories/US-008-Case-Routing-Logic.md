# US-008: Case Routing Logic

| Field          | Value                                                                 |
|----------------|-----------------------------------------------------------------------|
| **Story ID**   | US-008                                                                |
| **Module**     | C — Business Rule Engine (BRE)                                        |
| **Priority**   | High                                                                  |
| **PRD Ref**    | FR 3.3                                                                |
| **Created**    | 2026-02-19                                                            |

---

## Actors

| Actor                   | Role                                                              |
|--------------------------|------------------------------------------------------------------|
| **System (E-LOS)**       | Evaluates routing rules and assigns cases to appropriate queues  |
| **Senior Credit Manager**| Receives high-value cases (> ₹50L)                              |
| **Junior Credit Manager**| Receives small-ticket cases (< ₹5L)                             |
| **Credit Manager**       | Receives cases in the mid-range                                  |
| **Credit Admin**         | Configures routing rules and threshold amounts                   |

---

## System Name

**E-LOS** (Enterprise Loan Origination System)

---

## Brief Description

As the **E-LOS system**, I want to automatically route loan applications to the appropriate Credit Manager tier based on configurable rules (e.g., loan amount thresholds) so that cases are handled by officers with the right authority level.

---

## Business Goal

- Ensure proper **segregation of authority** — high-value decisions are made by senior staff.
- Reduce manual case assignment by Credit Admin.
- Align routing with the organisation's **Delegation of Authority (DOA)** matrix.

---

## Acceptance Criteria

| #  | Criterion                                                                                                    | Status |
|----|--------------------------------------------------------------------------------------------------------------|--------|
| 1  | Admin can configure routing rules based on application attributes (Loan Amount, Product, Risk Score, etc.).   | ☐      |
| 2  | PRD rule implemented: Loan Amount **> ₹50L** → route to "Senior Credit Manager" queue.                       | ☐      |
| 3  | PRD rule implemented: Loan Amount **< ₹5L** → route to "Junior Credit Manager" queue.                        | ☐      |
| 4  | Mid-range amounts (₹5L – ₹50L) → route to "Credit Manager" queue.                                           | ☐      |
| 5  | Routing rules integrate with the BRE — they use the same rule engine and admin UI.                           | ☐      |
| 6  | When a case is routed, it appears in the target officer's **My Cases** queue.                                | ☐      |
| 7  | Officers receive an **in-app notification** when a new case lands in their queue.                            | ☐      |
| 8  | If no routing rule matches, case is placed in a **default/unassigned queue** with an alert to Credit Admin.  | ☐      |
| 9  | Credit Admin can manually **override routing** with audit trail.                                             | ☐      |
| 10 | Routing decision is logged: matched rule, target queue, and timestamp.                                       | ☐      |

---

## Use Cases

### UC-008.1 — High-Value Routing
1. Application submitted with Loan Amount = ₹75,00,000.
2. BRE evaluates routing rules → matches "Amount > ₹50L → Senior Credit Manager."
3. Case appears in Senior Credit Manager queue.

### UC-008.2 — Small-Ticket Routing
1. Application with Loan Amount = ₹3,00,000.
2. Matches "Amount < ₹5L → Junior Credit Manager."
3. Case routed to Junior Credit Manager queue.

### UC-008.3 — No Rule Match (Fallback)
1. Application with an unusual attribute combination that no rule covers.
2. Case placed in "Unassigned" queue.
3. Credit Admin receives alert; manually assigns.

### UC-008.4 — Manual Override
1. Credit Admin sees a case in the Junior queue but knows it requires senior review (complex collateral).
2. Manually re-routes to Senior Credit Manager with reason: "Complex collateral structure."

---

## Manual Testing Instructions

| Step | Action                                                                                          | Expected Result                                                        |
|------|-------------------------------------------------------------------------------------------------|------------------------------------------------------------------------|
| 1    | Submit application with Loan Amount = ₹80L.                                                     | Case appears in Senior Credit Manager queue.                           |
| 2    | Submit application with Loan Amount = ₹3L.                                                      | Case appears in Junior Credit Manager queue.                           |
| 3    | Submit application with Loan Amount = ₹25L.                                                     | Case appears in Credit Manager queue.                                  |
| 4    | Change routing threshold from ₹50L to ₹40L. Submit application with ₹45L.                       | Case now routes to Senior queue (new threshold applied).               |
| 5    | Submit application that matches no rule.                                                         | Case in Unassigned queue; admin alerted.                               |
| 6    | Manually re-route a case, providing a reason.                                                   | Case moves; Audit Log records override.                                |

---

## Note for Automation Testing

> **Future Automation Scope:**
> - **Boundary Tests**: Amounts at exact thresholds (₹5,00,000 and ₹50,00,000) → validate correct queue.
> - **Rule Priority Tests**: Overlapping rules → assert correct precedence.
> - **Load Tests**: Route 1,000 cases simultaneously and verify correct queue assignment.
> - **Notification Tests**: Assert notification delivery on routing.

---

## Assumptions

1. Routing rules are a subset of BRE rules — they share the same engine and UI.
2. "Senior/Junior Credit Manager" are role-based queues, not specific individuals.
3. Amount thresholds are configurable and can vary by product type.

---

## Open Questions / Response Section

> **For Product Owner / Stakeholder to fill:**

| #  | Question                                                                                             | Response |
|----|------------------------------------------------------------------------------------------------------|----------|
| 1  | Should routing also consider **product type** (e.g., Home Loan vs. Personal Loan have different thresholds)? |          |
| 2  | What happens at exact boundary amounts — does ₹50,00,000 go to Senior or Mid-tier?                   |          |
| 3  | Should multiple routing criteria be combined (e.g., Amount > ₹50L **AND** Risk Score < 50)?           |          |
