# US-002: Lead Deduplication & Customer Linking

| Field          | Value                                                                 |
|----------------|-----------------------------------------------------------------------|
| **Story ID**   | US-002                                                                |
| **Module**     | A — Lead & Sourcing                                                   |
| **Priority**   | High                                                                  |
| **PRD Ref**    | FR 1.2                                                                |
| **Created**    | 2026-02-19                                                            |

---

## Actors

| Actor               | Role                                                                 |
|----------------------|----------------------------------------------------------------------|
| **System (E-LOS)**   | Automatically runs deduplication checks on every incoming lead        |
| **Sales Officer**    | Reviews duplicate alerts and decides on merge/link actions            |
| **Operations Admin** | Configures deduplication thresholds and fuzzy-match sensitivity       |

---

## System Name

**E-LOS** (Enterprise Loan Origination System)

---

## Brief Description

As the **E-LOS system**, I want to automatically detect duplicate leads at the point of ingestion using PAN exact-match and Name + DOB fuzzy-match so that duplicate records are linked to the existing Customer ID instead of creating redundant entries.

---

## Business Goal

- Maintain a **single customer view** across all channels and products.
- Prevent duplicate processing effort and conflicting credit decisions.
- Ensure regulatory compliance by linking all applications to the correct KYC-verified identity.

---

## Acceptance Criteria

| #  | Criterion                                                                                                    | Status |
|----|--------------------------------------------------------------------------------------------------------------|--------|
| 1  | On lead creation, system checks the incoming **PAN** against existing records — exact match.                  | ☐      |
| 2  | If PAN is absent or no PAN match, system performs a **fuzzy match** on (Full Name + Date of Birth).           | ☐      |
| 3  | Fuzzy match uses a configurable similarity threshold (default ≥ 85% on name using Levenshtein/Jaro-Winkler). | ☐      |
| 4  | If a match is found → the lead is **linked** to the existing `CustomerID`.                                   | ☐      |
| 5  | If no match is found → a **new Customer record** is created and linked to the lead.                          | ☐      |
| 6  | Duplicate detection results are logged (match type, score, matched `CustomerID`).                            | ☐      |
| 7  | Sales Officer can view the duplicate alert on the lead detail screen showing matched customer details.        | ☐      |
| 8  | System allows Sales Officer to **override** the match (mark as "Not a Duplicate") with a mandatory reason.   | ☐      |
| 9  | Deduplication does not block lead creation — lead is always persisted; linking is additive.                   | ☐      |
| 10 | Operations Admin can adjust the fuzzy-match threshold from the Admin Settings panel.                         | ☐      |

---

## Use Cases

### UC-002.1 — Exact PAN Match
1. New lead arrives with PAN `ABCDE1234F`.
2. System queries Customer table → finds existing Customer #1023 with the same PAN.
3. Lead is linked to Customer #1023; a "Duplicate Detected — PAN Match" flag is set.
4. Sales Officer sees the linked customer's previous application history.

### UC-002.2 — Fuzzy Name + DOB Match
1. New lead arrives without PAN; Name = "Rajesh Kumar", DOB = 1990-04-15.
2. System queries → finds Customer #2045 with Name "Rajesh Kumaar", DOB = 1990-04-15 (similarity = 91%).
3. Lead is provisionally linked to Customer #2045 with flag "Fuzzy Match — Needs Review."
4. Sales Officer reviews and confirms or overrides.

### UC-002.3 — No Match Found
1. New lead arrives; PAN and Name + DOB do not match any existing records.
2. System creates a new Customer record and links the lead.
3. No duplicate alert is raised.

### UC-002.4 — Override False Positive
1. Sales Officer sees a fuzzy-match alert on a lead.
2. After reviewing details, determines it is a different person (e.g., same name but different city/father's name).
3. Clicks "Not a Duplicate" and enters reason: "Different individual — verified via Aadhaar."
4. System unlinks the lead from the matched customer and creates a new Customer record.

---

## Manual Testing Instructions

| Step | Action                                                                                          | Expected Result                                                        |
|------|-------------------------------------------------------------------------------------------------|------------------------------------------------------------------------|
| 1    | Create Customer #1 with PAN `XYZAB5678C`. Then submit a new lead with the same PAN.             | Lead is linked to Customer #1; "PAN Match" flag shown.                 |
| 2    | Submit a lead with Name = "Amit Sharma", DOB = 1985-06-10. Then submit another with Name = "Amith Sharma", DOB = 1985-06-10. | Second lead shows fuzzy-match alert linked to first customer.       |
| 3    | Set fuzzy threshold to 95% in Admin. Re-test step 2.                                            | No match found (similarity ~90% < 95%); new customer created.         |
| 4    | On a fuzzy-matched lead, click "Not a Duplicate" and enter reason.                              | Lead unlinked; new Customer created; override logged in Audit.         |
| 5    | Submit a lead with a unique PAN and unique Name + DOB combination.                              | New Customer created; no duplicate flag.                               |
| 6    | Check Audit Log for any deduplication event.                                                    | Entries present with match type, score, and resolution.                |

---

## Note for Automation Testing

> **Future Automation Scope:**
> - **Unit Tests**: Test the fuzzy-match algorithm with boundary cases (threshold = 84%, 85%, 86%) to validate configurable threshold.
> - **Integration Tests**: Submit leads via API and assert `CustomerID` linkage in the database.
> - **Data-Driven Tests**: CSV with 100+ name-DOB pairs and expected match/no-match outcomes.
> - **Regression**: Ensure deduplication never blocks lead creation (negative test — even if dedup service is down, lead must persist).
> - **Performance**: Dedup execution time must remain < 200ms even with 1M+ customer records (index check).

---

## Assumptions

1. PAN match always takes precedence over fuzzy match.
2. Mobile number alone is **not** a deduplication key (per PRD: Mobile, PAN, DOB are inputs, but logic uses PAN exact or Name + DOB fuzzy).
3. The fuzzy-match algorithm will be Jaro-Winkler (to be confirmed during tech design).
4. Deduplication runs synchronously during lead creation but does not block on failure (graceful degradation).

---

## Open Questions / Response Section

> **For Product Owner / Stakeholder to fill:**

| #  | Question                                                                                             | Response |
|----|------------------------------------------------------------------------------------------------------|----------|
| 1  | Should mobile number be added as an additional dedup key (exact match on mobile)?                     |          |
| 2  | When a duplicate is found, should the system **merge** lead data into the existing record or keep them as separate leads linked to the same customer? |          |
| 3  | What is the default fuzzy-match threshold — 85% or something else?                                   |          |
| 4  | Should dedup run again on lead update (e.g., PAN added later)?                                       |          |
