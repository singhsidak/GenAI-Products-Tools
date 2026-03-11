# US-013: Document Deferral Tracking (OTC / PDD)

| Field          | Value                                                                 |
|----------------|-----------------------------------------------------------------------|
| **Story ID**   | US-013                                                                |
| **Module**     | E — Document Management System (DMS)                                  |
| **Priority**   | High                                                                  |
| **PRD Ref**    | FR 5.2                                                                |
| **Created**    | 2026-02-19                                                            |

---

## Actors

| Actor               | Role                                                                 |
|----------------------|----------------------------------------------------------------------|
| **Operations User**  | Marks documents as OTC or PDD; tracks deferral status                |
| **Credit Manager**   | Approves deferral requests                                            |
| **Sales Officer**    | Uploads deferred documents when obtained from the applicant           |
| **System (E-LOS)**   | Enforces OTC blocks and PDD tracking with reminders                  |

---

## System Name

**E-LOS** (Enterprise Loan Origination System)

---

## Brief Description

As an **Operations User**, I want to mark required documents as **OTC** (Over the Counter — mandatory before disbursal) or **PDD** (Post Disbursal Document — can be collected after disbursal) so that loan disbursement is blocked for missing OTC documents while allowing conditional disbursal for PDD items.

---

## Business Goal

- Prevent disbursement of loans with missing critical documents (OTC).
- Enable conditional disbursement when non-critical documents are pending (PDD).
- Provide automated tracking and reminders for PDD collection.

---

## Acceptance Criteria

| #  | Criterion                                                                                                    | Status |
|----|--------------------------------------------------------------------------------------------------------------|--------|
| 1  | Each required document in the checklist can be tagged as **OTC** or **PDD** by the Operations User.           | ☐      |
| 2  | OTC documents **block disbursement** — system prevents moving to "Disbursed" if any OTC doc is missing.      | ☐      |
| 3  | PDD documents **do not block** disbursement but are tracked with a due date.                                 | ☐      |
| 4  | PDD items show a deadline (configurable per document type, e.g., 90 days post-disbursal).                    | ☐      |
| 5  | System sends **automated reminders** (email/notification) as PDD deadline approaches (e.g., 30, 15, 7 days before). | ☐      |
| 6  | When a deferred document is uploaded, its status changes from "Pending" to "Received."                       | ☐      |
| 7  | A **Deferral Dashboard** lists all applications with pending OTC and PDD documents.                          | ☐      |
| 8  | Credit Manager approval is required to classify a document as PDD (it's not free for Ops to defer anything). | ☐      |
| 9  | Deferral status changes are audit-logged.                                                                    | ☐      |

---

## Use Cases

### UC-013.1 — OTC Blocking Disbursement
1. Application approved; moving to "Disbursement Pending."
2. Operations checks document checklist → "Property Title Deed" is OTC and missing.
3. System blocks disbursement: "Cannot disburse — OTC document missing: Property Title Deed."
4. Sales Officer uploads the title deed → OTC fulfilled → disbursement unblocked.

### UC-013.2 — PDD Allowed Disbursement
1. All OTC documents are uploaded.
2. "RC Transfer" document is marked PDD with deadline = 90 days post-disbursal.
3. Disbursement proceeds.
4. At Day 60, system sends reminder to Sales Officer: "RC Transfer due in 30 days."
5. At Day 91, PDD is overdue → escalated to Operations Manager.

### UC-013.3 — PDD Approval Flow
1. Operations User requests to mark "Insurance Policy" as PDD.
2. Request goes to Credit Manager for approval.
3. Credit Manager approves → document tagged as PDD with deadline.

---

## Manual Testing Instructions

| Step | Action                                                                                          | Expected Result                                                        |
|------|-------------------------------------------------------------------------------------------------|------------------------------------------------------------------------|
| 1    | Mark a required document as OTC. Attempt disbursement without uploading it.                      | Disbursement blocked with error message.                               |
| 2    | Upload the OTC document. Re-attempt disbursement.                                               | Disbursement proceeds.                                                 |
| 3    | Mark a document as PDD with 90-day deadline. Disburse the loan.                                  | Loan disbursed; PDD item appears in deferral tracker with due date.    |
| 4    | Fast-forward time (or adjust deadline) to trigger reminder.                                      | Reminder notification sent.                                            |
| 5    | Upload the PDD document.                                                                        | Status changes to "Received"; item cleared from dashboard.             |
| 6    | Check Audit Log for deferral events.                                                            | All status changes logged.                                             |

---

## Note for Automation Testing

> **Future Automation Scope:**
> - **OTC Gate Tests**: API-level attempt to disburse with missing OTC → assert blocked.
> - **PDD Timer Tests**: Mock time to trigger reminder at correct intervals.
> - **Approval Flow Tests**: Assert PDD request requires Credit Manager approval.
> - **Dashboard Tests**: Assert correct count and details of pending OTC/PDD items.

---

## Assumptions

1. Document checklist (which docs are required) is product-specific and pre-configured.
2. PDD deadlines are configurable per document type (not per application).
3. Overdue PDD items trigger escalation but do not retroactively block the existing disbursal.

---

## Open Questions / Response Section

> **For Product Owner / Stakeholder to fill:**

| #  | Question                                                                                             | Response |
|----|------------------------------------------------------------------------------------------------------|----------|
| 1  | What is the default PDD deadline per document type (e.g., 30, 60, 90 days)?                           |          |
| 2  | Should overdue PDDs trigger a **financial penalty** or just an operational alert?                      |          |
| 3  | Can a PDD deadline be **extended** — and by whom?                                                     |          |
| 4  | Who can mark a document as OTC vs. PDD — only Ops, or also the Credit Manager?                        |          |
