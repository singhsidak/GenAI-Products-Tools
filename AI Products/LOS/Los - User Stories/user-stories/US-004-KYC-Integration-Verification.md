# US-004: KYC Integration & Verification

| Field          | Value                                                                 |
|----------------|-----------------------------------------------------------------------|
| **Story ID**   | US-004                                                                |
| **Module**     | B — Customer Onboarding                                               |
| **Priority**   | Critical                                                              |
| **PRD Ref**    | FR 2.1                                                                |
| **Created**    | 2026-02-19                                                            |

---

## Actors

| Actor               | Role                                                                 |
|----------------------|----------------------------------------------------------------------|
| **Sales Officer**    | Initiates KYC verification during onboarding                         |
| **Applicant**        | Provides PAN, Aadhaar, and selfie for verification                   |
| **System (E-LOS)**   | Orchestrates API calls to NSDL/UIDAI and AI liveness service         |
| **NSDL/UIDAI API**   | External government service providing PAN/Aadhaar verification       |
| **AI Liveness Service** | Third-party or in-house service for face-match and liveness check |

---

## System Name

**E-LOS** (Enterprise Loan Origination System)

---

## Brief Description

As a **Sales Officer**, I want to verify the applicant's identity by entering their PAN (to auto-fetch Name, DOB, and seeding status from NSDL) and performing an AI-powered liveness check (selfie vs. ID photo) so that KYC compliance is met digitally without manual document verification.

---

## Business Goal

- Achieve **100% digital KYC** for eligible applicants, eliminating paper-based verification.
- Reduce onboarding time from days to minutes.
- Comply with RBI KYC norms and prevent identity fraud via liveness detection.

---

## Acceptance Criteria

| #  | Criterion                                                                                                    | Status |
|----|--------------------------------------------------------------------------------------------------------------|--------|
| 1  | System provides a PAN input field; on submission, calls the NSDL API to fetch Name, DOB, and seeding status.  | ☐      |
| 2  | Fetched PAN details are auto-populated into the applicant's profile (non-editable by UI user).               | ☐      |
| 3  | If PAN is linked to Aadhaar (seeded), system displays a green "Aadhaar Linked" badge.                        | ☐      |
| 4  | If NSDL API is unavailable, system retries up to 3 times with exponential backoff, then shows a graceful error. | ☐      |
| 5  | The liveness check module captures a live selfie from the applicant's device camera.                          | ☐      |
| 6  | System compares the selfie against the ID card photo (uploaded or from Aadhaar e-KYC) using AI face-match.   | ☐      |
| 7  | Face-match returns a confidence score; threshold for pass is ≥ 80% (configurable).                           | ☐      |
| 8  | Liveness detection rejects static photos, printed copies, and screen replays.                                | ☐      |
| 9  | KYC verification results (PAN status, liveness score, face-match score) are stored and audit-logged.          | ☐      |
| 10 | All API calls use **TLS 1.3**; PAN and Aadhaar data are encrypted at rest (AES-256).                         | ☐      |

---

## Use Cases

### UC-004.1 — PAN Verification
1. Sales Officer enters applicant's PAN on the onboarding screen.
2. System calls NSDL API → receives Name, DOB, seeding status.
3. Details are auto-filled; Sales Officer confirms correctness with the applicant.
4. If PAN is invalid, system displays "Invalid PAN — Not Found in NSDL."

### UC-004.2 — Liveness Check (Pass)
1. System prompts the applicant to capture a live selfie.
2. Applicant takes a selfie via the device camera.
3. AI service performs liveness detection (blink, head-turn prompt) → confirms live person.
4. Face-match compares selfie to Aadhaar/ID photo → confidence = 92% → **PASS**.
5. Green "KYC Verified" badge displayed.

### UC-004.3 — Liveness Check (Fail)
1. Applicant holds a printed photo in front of the camera.
2. AI liveness service detects no live movement → **FAIL**.
3. System logs the failure and displays: "Liveness check failed. Please try again with a live selfie."
4. After 3 failed attempts, case is flagged for **manual KYC review**.

### UC-004.4 — NSDL API Timeout
1. Sales Officer submits PAN.
2. NSDL API does not respond within 10 seconds.
3. System retries 3 times (2s, 4s, 8s backoff).
4. After all retries fail, system shows: "NSDL service unavailable. Please try again later."
5. Lead remains in `DRAFT` status; no partial KYC data saved.

---

## Manual Testing Instructions

| Step | Action                                                                                          | Expected Result                                                        |
|------|-------------------------------------------------------------------------------------------------|------------------------------------------------------------------------|
| 1    | Enter a valid PAN (test PAN from NSDL sandbox).                                                 | Name, DOB, seeding status auto-populated.                              |
| 2    | Enter an invalid PAN (e.g., `ZZZZZ9999Z`).                                                     | Error: "Invalid PAN — Not Found."                                      |
| 3    | Simulate NSDL API downtime (mock 500 response).                                                 | System retries 3 times → shows graceful error message.                 |
| 4    | Complete liveness check with a live selfie.                                                     | Face-match score displayed; "KYC Verified" badge shown.                |
| 5    | Attempt liveness with a printed photo.                                                          | Liveness check fails; "Try again" message shown.                       |
| 6    | Fail liveness 3 times.                                                                          | Case flagged for "Manual KYC Review."                                  |
| 7    | Verify PAN data is encrypted in the database (check raw column values).                         | Data is not human-readable (encrypted).                                |
| 8    | Check Audit Log for the KYC verification event.                                                 | Entry present with PAN hash, liveness score, and timestamp.            |

---

## Note for Automation Testing

> **Future Automation Scope:**
> - **Mock API Tests**: Use WireMock/MockServer to simulate NSDL responses (valid, invalid, timeout, 500).
> - **Liveness AI Tests**: Feed pre-recorded video clips (live face, photo, screen) and assert pass/fail outcomes.
> - **Encryption Verification**: Automated DB query to assert PAN/Aadhaar fields are encrypted at rest.
> - **Retry Logic Tests**: Simulate intermittent failures and validate retry count + backoff timing.
> - **Compliance Audit**: Automated scan of Audit Log entries for completeness after each KYC event.

---

## Assumptions

1. NSDL sandbox is available for development/testing; production credentials will be provisioned separately.
2. AI liveness service will be a third-party SDK (e.g., HyperVerge, IDfy) — specific vendor TBD.
3. Aadhaar e-KYC (UIDAI) integration is for optional photo fetch — not OTP-based Aadhaar auth in V1.
4. Face-match threshold of 80% is an initial default; will be fine-tuned based on pilot data.

---

## Open Questions / Response Section

> **For Product Owner / Stakeholder to fill:**

| #  | Question                                                                                             | Response |
|----|------------------------------------------------------------------------------------------------------|----------|
| 1  | Which AI liveness vendor should we integrate (HyperVerge, IDfy, or build in-house)?                   |          |
| 2  | Is Aadhaar OTP-based e-KYC in scope for V1, or only PAN verification?                                |          |
| 3  | What is the maximum number of liveness re-attempts before manual review (proposed: 3)?               |          |
| 4  | Should KYC verification be mandatory before moving to Credit Bureau pull, or can they run in parallel? |          |
