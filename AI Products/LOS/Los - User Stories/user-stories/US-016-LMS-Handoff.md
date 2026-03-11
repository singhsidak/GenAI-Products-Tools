# US-016: LMS Handoff via REST API

| Field          | Value                                                                 |
|----------------|-----------------------------------------------------------------------|
| **Story ID**   | US-016                                                                |
| **Module**     | F — Disbursement                                                      |
| **Priority**   | Critical                                                              |
| **PRD Ref**    | FR 6.2                                                                |
| **Created**    | 2026-02-19                                                            |

---

## Actors

| Actor               | Role                                                                 |
|----------------------|----------------------------------------------------------------------|
| **System (E-LOS)**   | Constructs the handoff payload and pushes to LMS                     |
| **LMS (Loan Management System)** | External system that receives disbursed loan data for servicing |
| **Operations User**  | Triggers final disbursement; monitors handoff status                  |
| **IT Admin**         | Configures LMS API endpoint and credentials                          |

---

## System Name

**E-LOS** (Enterprise Loan Origination System)

---

## Brief Description

As the **E-LOS system**, on final loan approval and disbursement, I want to construct a JSON payload containing all loan details (Customer Details, Interest Rate, Tenor, Repayment Schedule, Bank Details) and push it to the LMS via REST API so that the loan transitions seamlessly from origination to servicing.

---

## Business Goal

- Ensure automated, error-free data transfer from LOS to LMS.
- Eliminate manual data re-entry in the servicing system.
- Enable real-time loan activation in LMS post-disbursement.

---

## Acceptance Criteria

| #  | Criterion                                                                                                    | Status |
|----|--------------------------------------------------------------------------------------------------------------|--------|
| 1  | On final approval + disbursement, system auto-constructs a **JSON payload** with all required fields.        | ☐      |
| 2  | Payload includes: Customer Details (Name, PAN, Address, Contact), Loan Product, Loan Amount, Interest Rate, Tenor, EMI, Repayment Schedule, Disbursement Date, Bank Details. | ☐      |
| 3  | Payload is sent via **HTTP POST** to the configured LMS API endpoint.                                        | ☐      |
| 4  | On success (HTTP 200/201), LOS marks the case as **"Disbursed — LMS Synced"**.                               | ☐      |
| 5  | On failure (4xx/5xx/timeout), system retries up to 3 times with exponential backoff.                         | ☐      |
| 6  | After all retries fail, case is flagged as **"LMS Sync Failed"** with an alert to IT Admin.                  | ☐      |
| 7  | Operations User can view the handoff status and manually trigger a **retry** from the UI.                    | ☐      |
| 8  | The raw request/response payload is stored in the audit log for debugging.                                   | ☐      |
| 9  | LMS API endpoint and credentials are configurable via Admin settings (not hardcoded).                        | ☐      |
| 10 | Data in transit is encrypted (TLS 1.3); payload does not include raw Aadhaar numbers.                        | ☐      |

---

## Use Cases

### UC-016.1 — Successful Handoff
1. Loan fully approved and disbursed.
2. System constructs JSON payload → sends to LMS API.
3. LMS responds HTTP 201 → LOS marks case as "Disbursed — LMS Synced."
4. Loan appears in LMS for servicing.

### UC-016.2 — Handoff Failure + Retry
1. LMS API returns HTTP 503 (service down).
2. System retries 3 times (2s, 4s, 8s).
3. All retries fail → case flagged "LMS Sync Failed."
4. IT Admin is alerted; Operations can retry manually after LMS is back up.

### UC-016.3 — Manual Retry
1. Operations User sees "LMS Sync Failed" on a case.
2. Clicks "Retry LMS Sync" → system re-sends the payload.
3. This time LMS responds 201 → status updated to "Disbursed — LMS Synced."

---

## Manual Testing Instructions

| Step | Action                                                                                          | Expected Result                                                        |
|------|-------------------------------------------------------------------------------------------------|------------------------------------------------------------------------|
| 1    | Disburse a loan (happy path).                                                                   | LMS handoff triggers; case marked "LMS Synced."                        |
| 2    | Verify the JSON payload sent to LMS contains all required fields.                               | All fields present and correctly populated.                            |
| 3    | Simulate LMS downtime (mock 503).                                                               | 3 retries → "LMS Sync Failed" status → alert sent.                    |
| 4    | Manually retry sync after LMS is back.                                                          | Sync succeeds; status updated.                                         |
| 5    | Check audit log for raw request/response payloads.                                               | Both payloads stored with timestamps.                                  |
| 6    | Verify no Aadhaar number in the payload.                                                         | Aadhaar field absent or masked.                                        |

---

## Note for Automation Testing

> **Future Automation Scope:**
> - **Contract Tests**: Validate JSON payload schema against LMS API contract (Pact/Spring Cloud Contract).
> - **Retry Logic Tests**: Mock various failure scenarios (503, timeout, 400) → assert retry behavior.
> - **Data Completeness**: Compare payload fields to DB records → assert 100% accuracy.
> - **Idempotency Tests**: Send the same payload twice → assert LMS does not create duplicate records.
> - **Security**: Assert TLS 1.3 in API calls; assert no raw Aadhaar in payload.

---

## Assumptions

1. LMS API contract is defined and agreed upon before E-LOS implementation.
2. LMS handoff is a one-way push — E-LOS does not poll LMS for status.
3. Handoff happens immediately after disbursement (synchronous trigger, async execution).
4. A unique `losReferenceId` is included in the payload for cross-system traceability.

---

## Open Questions / Response Section

> **For Product Owner / Stakeholder to fill:**

| #  | Question                                                                                             | Response |
|----|------------------------------------------------------------------------------------------------------|----------|
| 1  | What is the exact JSON schema expected by the LMS API?                                               |          |
| 2  | Does LMS return a `lmsLoanId` in the response that E-LOS should store?                               |          |
| 3  | Should E-LOS also push **amendment data** (e.g., interest rate changes post-disbursement)?            |          |
| 4  | What is the SLA for LMS to acknowledge the handoff (timeout threshold)?                              |          |
