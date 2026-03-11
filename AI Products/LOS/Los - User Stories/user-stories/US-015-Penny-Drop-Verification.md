# US-015: Penny Drop Account Verification

| Field          | Value                                                                 |
|----------------|-----------------------------------------------------------------------|
| **Story ID**   | US-015                                                                |
| **Module**     | F — Disbursement                                                      |
| **Priority**   | Critical                                                              |
| **PRD Ref**    | FR 6.1                                                                |
| **Created**    | 2026-02-19                                                            |

---

## Actors

| Actor               | Role                                                                 |
|----------------------|----------------------------------------------------------------------|
| **Operations User**  | Initiates penny drop verification before disbursement                 |
| **System (E-LOS)**   | Calls bank API to deposit ₹1 and validate beneficiary details        |
| **Banking API**       | External bank partner providing IMPS/NEFT penny drop service         |

---

## System Name

**E-LOS** (Enterprise Loan Origination System)

---

## Brief Description

As an **Operations User**, I want to verify the applicant's bank account by performing a "Penny Drop" (depositing ₹1 via bank API) so that the beneficiary name, account number, and IFSC are validated before the full loan disbursement.

---

## Business Goal

- Prevent disbursement to incorrect or fraudulent bank accounts.
- Reduce failed NEFT/RTGS transactions and associated operational costs.
- Comply with beneficiary verification norms.

---

## Acceptance Criteria

| #  | Criterion                                                                                                    | Status |
|----|--------------------------------------------------------------------------------------------------------------|--------|
| 1  | System provides a "Verify Account" button on the disbursement screen.                                        | ☐      |
| 2  | On click, system sends ₹1 via IMPS/NEFT to the applicant's bank account using the bank API.                 | ☐      |
| 3  | API response returns: **Beneficiary Name** as registered with the bank.                                      | ☐      |
| 4  | System compares the returned beneficiary name with the applicant name (fuzzy match ≥ 80%).                   | ☐      |
| 5  | If match → displays "Account Verified ✓" with beneficiary name.                                             | ☐      |
| 6  | If mismatch → displays "Name Mismatch ⚠" with both names for manual review.                                | ☐      |
| 7  | If penny drop fails (invalid account/IFSC) → displays "Verification Failed" with error details.             | ☐      |
| 8  | Penny drop can be retried up to 3 times per account.                                                        | ☐      |
| 9  | Disbursement is **blocked** until penny drop verification passes (or is manually overridden with reason).    | ☐      |
| 10 | Penny drop result is audit-logged: UTR number, beneficiary name, match result, timestamp.                    | ☐      |

---

## Use Cases

### UC-015.1 — Successful Penny Drop
1. Operations User clicks "Verify Account."
2. System sends ₹1 to account 1234567890, IFSC HDFC0001234.
3. Bank API returns: "Rajesh Kumar" — matches applicant name → "Account Verified ✓."

### UC-015.2 — Name Mismatch
1. Penny drop returns beneficiary name = "R. Kumar" vs. applicant name = "Rajesh Kumar".
2. Fuzzy match = 75% (below 80%) → "Name Mismatch ⚠."
3. Operations reviews → confirms it's the same person → manually overrides.

### UC-015.3 — Failed Penny Drop
1. Penny drop to invalid IFSC code.
2. Bank API returns error: "Invalid IFSC."
3. Operations corrects IFSC and retries.

---

## Manual Testing Instructions

| Step | Action                                                                                          | Expected Result                                                        |
|------|-------------------------------------------------------------------------------------------------|------------------------------------------------------------------------|
| 1    | Initiate penny drop with valid sandbox account.                                                  | ₹1 deposited; beneficiary name returned; "Verified" shown.            |
| 2    | Initiate with mismatched beneficiary name.                                                       | "Name Mismatch" warning with both names displayed.                     |
| 3    | Initiate with invalid IFSC.                                                                     | "Verification Failed — Invalid IFSC."                                  |
| 4    | Try to disburse without passing penny drop.                                                      | Disbursement blocked.                                                  |
| 5    | Override a name mismatch with a reason.                                                          | Override recorded; disbursement unblocked.                             |
| 6    | Check Audit Log for penny drop events.                                                           | UTR, beneficiary name, result logged.                                  |

---

## Note for Automation Testing

> **Future Automation Scope:**
> - **Mock Bank API**: Simulate valid, invalid, mismatch, timeout responses.
> - **Gate Tests**: Assert disbursement is blocked without passing penny drop.
> - **Name Match Tests**: Parameterized tests for various name similarities at boundary thresholds.
> - **Retry Tests**: Assert max 3 retries and proper error after exhaustion.

---

## Assumptions

1. The ₹1 amount is **non-recoverable** (treated as a verification cost).
2. Bank API partner will be pre-integrated (e.g., RazorpayX, Cashfree).
3. Only one bank account is verified per disbursement (primary beneficiary).

---

## Open Questions / Response Section

> **For Product Owner / Stakeholder to fill:**

| #  | Question                                                                                             | Response |
|----|------------------------------------------------------------------------------------------------------|----------|
| 1  | Which bank API partner should we use (RazorpayX, Cashfree, BankOpen)?                                |          |
| 2  | Should penny drop support **multiple accounts** (e.g., builder + borrower for HL)?                    |          |
| 3  | Is Operations User allowed to skip penny drop with senior approval?                                  |          |
