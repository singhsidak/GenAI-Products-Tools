# US-005: Credit Bureau Integration & Analysis

| Field          | Value                                                                 |
|----------------|-----------------------------------------------------------------------|
| **Story ID**   | US-005                                                                |
| **Module**     | B — Customer Onboarding                                               |
| **Priority**   | Critical                                                              |
| **PRD Ref**    | FR 2.2                                                                |
| **Created**    | 2026-02-19                                                            |

---

## Actors

| Actor               | Role                                                                 |
|----------------------|----------------------------------------------------------------------|
| **Credit Manager**   | Initiates bureau pull and reviews parsed report                       |
| **System (E-LOS)**   | Calls bureau APIs, parses XML/JSON, and populates structured fields  |
| **Operations Admin** | Configures bureau preferences and consent rules                      |
| **CIBIL / Experian / Highmark** | External credit bureaus providing credit reports          |

---

## System Name

**E-LOS** (Enterprise Loan Origination System)

---

## Brief Description

As a **Credit Manager**, I want the system to pull the applicant's credit report from CIBIL, Experian, or Highmark and auto-parse the response to extract key metrics (Score, Enquiry Count, Total EMI) so that I can make informed credit decisions without manually reading raw bureau data.

---

## Business Goal

- Automate bureau data extraction, eliminating manual parsing of XML/JSON reports.
- Ensure consistent credit decision inputs across all assessors.
- Enable real-time creditworthiness assessment at the point of onboarding.

---

## Acceptance Criteria

| #  | Criterion                                                                                                    | Status |
|----|--------------------------------------------------------------------------------------------------------------|--------|
| 1  | System integrates with at least **CIBIL** and one secondary bureau (Experian or Highmark).                    | ☐      |
| 2  | Bureau pull is triggered via a "Pull Bureau" button on the applicant's profile, requiring applicant consent flag. | ☐      |
| 3  | System sends applicant details (Name, DOB, PAN, Address) to the bureau API.                                  | ☐      |
| 4  | Raw bureau response (XML or JSON) is stored in the document store for audit/reference.                       | ☐      |
| 5  | Parser extracts: **Credit Score**, **Count of Enquiries (last 3 months)**, **Total Current EMI**.            | ☐      |
| 6  | Parsed fields are displayed on a structured "Bureau Summary" card on the applicant's profile.                | ☐      |
| 7  | If bureau API returns an error or timeout, system retries 3 times → then shows a graceful error with a "Retry" button. | ☐      |
| 8  | System supports **multi-bureau pull** — Credit Manager can pull from multiple bureaus for the same applicant. | ☐      |
| 9  | If multiple reports exist, system displays a side-by-side comparison view.                                   | ☐      |
| 10 | Bureau pull events are audit-logged with timestamp, bureau name, and response status.                        | ☐      |
| 11 | PII data in bureau requests/responses is encrypted in transit (TLS 1.3) and at rest (AES-256).               | ☐      |

---

## Use Cases

### UC-005.1 — Standard CIBIL Pull
1. Credit Manager opens applicant profile → clicks "Pull Bureau" → selects "CIBIL."
2. System verifies consent flag → sends request to CIBIL API.
3. CIBIL returns XML response.
4. Parser extracts: Score = 745, Enquiries (3M) = 2, Total EMI = ₹35,000.
5. Bureau Summary card is populated. Raw XML is stored in DMS.

### UC-005.2 — Multi-Bureau Pull
1. Credit Manager pulls CIBIL (score = 745) and Experian (score = 738).
2. System displays both reports side by side.
3. Credit Manager uses the higher/lower score per company policy.

### UC-005.3 — Bureau API Failure
1. Credit Manager triggers CIBIL pull.
2. CIBIL API returns HTTP 503.
3. System retries 3 times → all fail.
4. "CIBIL service unavailable" message shown with a "Retry Later" button.
5. No partial data saved; raw error response logged for debugging.

### UC-005.4 — Missing Applicant in Bureau
1. Bureau returns a "No Hit" / "No Match" response.
2. System displays: "No bureau record found for this applicant."
3. Credit Manager can proceed with NTC (New to Credit) workflow.

---

## Manual Testing Instructions

| Step | Action                                                                                          | Expected Result                                                        |
|------|-------------------------------------------------------------------------------------------------|------------------------------------------------------------------------|
| 1    | Pull CIBIL for a test applicant (sandbox credentials).                                          | Bureau Summary card shows Score, Enquiries, Total EMI.                 |
| 2    | Pull Experian for the same applicant.                                                           | Second report appears; side-by-side comparison available.              |
| 3    | Simulate CIBIL timeout (mock).                                                                  | Retry 3 times → error message → "Retry" button shown.                 |
| 4    | Pull bureau for an applicant without consent flag set.                                          | System blocks the pull; error: "Applicant consent required."           |
| 5    | Pull bureau for non-existent PAN.                                                               | "No bureau record found" message.                                      |
| 6    | Check DMS for raw XML/JSON of the bureau response.                                              | File exists with correct bureau name and timestamp in metadata.        |
| 7    | Check Audit Log for bureau pull events.                                                         | Entry with bureau name, status (success/fail), and timestamp.          |

---

## Note for Automation Testing

> **Future Automation Scope:**
> - **Parser Unit Tests**: Feed known XML/JSON samples from each bureau → assert extracted fields match expected values.
> - **Edge Case Parsing**: Test with malformed XML, missing nodes, empty score fields.
> - **Retry Logic**: Simulate intermittent 503s and validate retry count and backoff.
> - **Consent Gate**: API-level test to assert bureau pull is blocked without consent flag.
> - **Security**: Verify PII masking in logs; validate TLS 1.3 in API calls.
> - **Performance**: Bureau pull + parse should complete in < 5 seconds end-to-end.

---

## Assumptions

1. Bureau sandbox credentials are available for CIBIL and at least one secondary bureau.
2. The raw XML/JSON is stored as a document in DMS (see US-012), not inline in the database.
3. Only one bureau pull per bureau per application is allowed per 24 hours (to avoid unnecessary hits).
4. Consent is captured digitally (checkbox or e-sign) and timestamped.

---

## Open Questions / Response Section

> **For Product Owner / Stakeholder to fill:**

| #  | Question                                                                                             | Response |
|----|------------------------------------------------------------------------------------------------------|----------|
| 1  | Which bureaus are in scope for V1 — CIBIL + Experian, or all three (CIBIL + Experian + Highmark)?     |          |
| 2  | Should the system auto-select the primary bureau or let the Credit Manager choose each time?          |          |
| 3  | Is there a daily/monthly limit on bureau pulls per application (e.g., max 2 per bureau per case)?     |          |
| 4  | For NTC (No bureau history) applicants, should the system route them to a specific assessment path?    |          |
