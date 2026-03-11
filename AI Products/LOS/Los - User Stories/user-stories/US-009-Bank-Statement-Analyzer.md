# US-009: Bank Statement Analyzer & Financial Spreading

| Field          | Value                                                                 |
|----------------|-----------------------------------------------------------------------|
| **Story ID**   | US-009                                                                |
| **Module**     | D — Underwriting & Assessment                                         |
| **Priority**   | Critical                                                              |
| **PRD Ref**    | FR 4.1                                                                |
| **Created**    | 2026-02-19                                                            |

---

## Actors

| Actor               | Role                                                                 |
|----------------------|----------------------------------------------------------------------|
| **Credit Manager**   | Uploads bank statements, reviews extracted data, adjusts figures     |
| **System (E-LOS)**   | Parses PDFs, extracts transactions, computes financial metrics       |
| **Sales Officer**    | Collects and uploads bank statements from the applicant              |

---

## System Name

**E-LOS** (Enterprise Loan Origination System)

---

## Brief Description

As a **Credit Manager**, I want to upload an applicant's bank statement PDF and have the system auto-extract transactions to calculate Average Bank Balance (ABB), Total Credits, and Cheque Bounces; and also have an Excel-like input grid to manually adjust values from ITR/Balance Sheets, so that financial assessment is accurate, fast, and auditable.

---

## Business Goal

- Reduce financial analysis time from 2+ hours (manual) to minutes (automated).
- Minimise human error in computing financial metrics.
- Maintain manual override capability for complex cases (ITR adjustments).

---

## Acceptance Criteria

| #  | Criterion                                                                                                    | Status |
|----|--------------------------------------------------------------------------------------------------------------|--------|
| 1  | System provides a **drag-and-drop upload** zone for bank statement PDFs.                                     | ☐      |
| 2  | Uploaded PDF is processed via OCR/parser to extract transaction line items (Date, Description, Debit, Credit, Balance). | ☐      |
| 3  | System calculates: **Average Bank Balance (ABB)** = average of month-end balances.                            | ☐      |
| 4  | System calculates: **Total Credits** = sum of all credit entries.                                            | ☐      |
| 5  | System calculates: **Cheque Bounces** = count of transactions matching bounce patterns (e.g., "CHQ RTN", "INSUFFICIENT FUNDS"). | ☐      |
| 6  | Extracted data is displayed in a tabular view; Credit Manager can review and flag corrections.               | ☐      |
| 7  | An **Excel-like input grid** is provided for manual entry/adjustment of ITR and Balance Sheet figures.        | ☐      |
| 8  | Grid supports columns: Year, Gross Revenue, Net Profit, Depreciation, Tax Paid, etc.                        | ☐      |
| 9  | All manual adjustments are audit-logged (original value, new value, user, timestamp).                        | ☐      |
| 10 | Supported bank statement formats: Major Indian banks (SBI, HDFC, ICICI, Axis, etc.).                         | ☐      |

---

## Use Cases

### UC-009.1 — Automated Bank Statement Analysis
1. Credit Manager uploads a 6-month HDFC bank statement (PDF).
2. System parses the PDF → extracts 450 transactions.
3. Dashboard shows: ABB = ₹2,34,567 | Total Credits = ₹18,45,000 | Cheque Bounces = 2.
4. Credit Manager reviews the breakdown and proceeds.

### UC-009.2 — Manual ITR Spreading
1. Credit Manager opens the "Financial Spreading" grid.
2. Enters ITR data for FY 2023-24 and FY 2024-25: Gross Revenue, Cost of Goods, Operating Expenses, Net Profit.
3. System auto-calculates growth rate and net margin.
4. Manager adjusts Depreciation figure (adds back non-cash charges).

### UC-009.3 — Parse Failure Handling
1. Credit Manager uploads a scanned, low-quality PDF.
2. Parser fails to extract > 80% of transactions.
3. System shows: "Unable to parse this statement reliably. Please upload a digital/e-statement."
4. Manager can still enter data manually via the grid.

---

## Manual Testing Instructions

| Step | Action                                                                                          | Expected Result                                                        |
|------|-------------------------------------------------------------------------------------------------|------------------------------------------------------------------------|
| 1    | Upload a known test bank statement PDF (digital, HDFC).                                          | Transactions extracted; ABB, Credits, Bounces computed correctly.       |
| 2    | Upload a scanned/image-based PDF.                                                                | Graceful error or partial extraction with warning.                     |
| 3    | Open Financial Spreading grid → enter ITR values → save.                                         | Values persisted; grid reflects entries.                               |
| 4    | Edit a grid value → check Audit Log.                                                            | Original and new values logged with timestamp.                         |
| 5    | Upload statements from 3 different banks (SBI, ICICI, Axis).                                    | All parsed correctly with bank-specific format handling.               |

---

## Note for Automation Testing

> **Future Automation Scope:**
> - **Parser Accuracy Tests**: Feed 50 known bank statements → assert ABB, Credits, Bounces match pre-calculated expected values.
> - **Multi-Bank Tests**: Test parsers for top 10 Indian banks independently.
> - **Grid E2E Tests**: Cypress/Selenium tests for grid input, edit, save, and audit log verification.
> - **OCR Quality Tests**: Test with varying PDF quality levels (e.g., 300 DPI, 150 DPI, scanned).

---

## Assumptions

1. The bank statement parser will support **digital PDFs** from major Indian banks in V1; scanned/image PDFs are best-effort.
2. The parser may use a third-party service (e.g., Perfios, Finbox) or be built in-house.
3. The input grid is a web-based component (not an actual Excel embed).

---

## Open Questions / Response Section

> **For Product Owner / Stakeholder to fill:**

| #  | Question                                                                                             | Response |
|----|------------------------------------------------------------------------------------------------------|----------|
| 1  | Should we use a third-party bank statement analyzer (Perfios/Finbox) or build in-house?               |          |
| 2  | How many months of bank statements are required (3, 6, or 12)?                                       |          |
| 3  | Should the grid support **multiple applicants** (e.g., co-borrower financials)?                       |          |
| 4  | Is password-protected PDF upload a V1 requirement?                                                   |          |
