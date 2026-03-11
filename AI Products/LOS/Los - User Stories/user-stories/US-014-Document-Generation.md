# US-014: Sanction Letter & Loan Agreement Generation

| Field          | Value                                                                 |
|----------------|-----------------------------------------------------------------------|
| **Story ID**   | US-014                                                                |
| **Module**     | E — Document Management System (DMS)                                  |
| **Priority**   | High                                                                  |
| **PRD Ref**    | FR 5.3                                                                |
| **Created**    | 2026-02-19                                                            |

---

## Actors

| Actor               | Role                                                                 |
|----------------------|----------------------------------------------------------------------|
| **Operations User**  | Triggers document generation and reviews output                       |
| **Credit Manager**   | Approves the sanction letter before it is shared with the applicant   |
| **Applicant**        | Receives the sanction letter / loan agreement                        |
| **System (E-LOS)**   | Merges customer data into templates and generates PDF/HTML documents  |

---

## System Name

**E-LOS** (Enterprise Loan Origination System)

---

## Brief Description

As an **Operations User**, I want the system to auto-generate a **Sanction Letter** and **Loan Agreement** by merging applicant data (name, loan amount, tenure, interest rate, etc.) into pre-configured HTML/PDF templates so that offer and agreement documents are generated instantly, accurately, and consistently.

---

## Business Goal

- Eliminate manual document drafting — reduce from 1+ hours to seconds.
- Ensure zero data-entry errors in legal documents.
- Standardise document format and language across all branches.

---

## Acceptance Criteria

| #  | Criterion                                                                                                    | Status |
|----|--------------------------------------------------------------------------------------------------------------|--------|
| 1  | System supports **HTML templates** with merge fields (e.g., `{{customerName}}`, `{{loanAmount}}`).           | ☐      |
| 2  | Templates for "Sanction Letter" and "Loan Agreement" are pre-configured.                                     | ☐      |
| 3  | On clicking "Generate," system pulls application data → merges into template → produces PDF.                 | ☐      |
| 4  | Generated PDF is stored in DMS with Document Type = "Generated Document" and Sub-Type = "Sanction Letter."   | ☐      |
| 5  | Generated documents contain: Customer Name, Loan Amount, Interest Rate, Tenor, EMI, Repayment Schedule, Terms. | ☐      |
| 6  | PDF opens correctly in standard readers and prints cleanly on A4 paper.                                      | ☐      |
| 7  | Data accuracy: all merge fields reflect the **latest approved** application data.                             | ☐      |
| 8  | Credit Manager can **preview** the document before final generation.                                          | ☐      |
| 9  | Template management: Admin can add/edit templates (HTML editor with merge field insertion).                   | ☐      |
| 10 | Document generation is audit-logged (who generated, when, which template version).                           | ☐      |

---

## Use Cases

### UC-014.1 — Generate Sanction Letter
1. Application status = "Approved/Sanctioned."
2. Operations User opens application → clicks "Generate Sanction Letter."
3. System merges data into template → generates PDF preview.
4. User reviews → clicks "Finalise."
5. PDF stored in DMS and available for download/email.

### UC-014.2 — Generate Loan Agreement
1. After sanction, Operations generates the Loan Agreement.
2. Merge includes: Customer details, Co-borrower details, Property details, Repayment schedule.
3. Multi-page document generated as PDF.

### UC-014.3 — Data Mismatch Prevention
1. User generates sanction letter.
2. Before finalising, notices interest rate was updated after approval.
3. System uses the **sanctioned/approved** interest rate (point-in-time data), not the latest override.

---

## Manual Testing Instructions

| Step | Action                                                                                          | Expected Result                                                        |
|------|-------------------------------------------------------------------------------------------------|------------------------------------------------------------------------|
| 1    | Approve an application → generate Sanction Letter.                                               | PDF generated; all data fields correctly populated.                    |
| 2    | Open the PDF in Adobe Reader and Chrome PDF viewer.                                              | PDF renders correctly in both.                                         |
| 3    | Print the PDF on A4.                                                                            | Clean print; no cut-off text or formatting issues.                     |
| 4    | Generate Loan Agreement.                                                                         | Multi-page PDF with repayment schedule.                                |
| 5    | Verify data accuracy: compare PDF fields to application data on screen.                          | 100% match.                                                            |
| 6    | Edit an HTML template (Admin) → re-generate.                                                     | New generation uses updated template.                                  |
| 7    | Check DMS for generated document entry.                                                          | Document stored with correct type and metadata.                        |

---

## Note for Automation Testing

> **Future Automation Scope:**
> - **PDF Parsing Tests**: Generate PDF → programmatically extract text → assert all merge fields are correctly populated.
> - **Template Regression**: After template edit, verify all merge fields still resolve.
> - **Multi-Format Tests**: Open generated PDFs in various viewers/devices to assert rendering.
> - **Data Integrity**: Compare generated document data to DB values via API.
> - **Volume Tests**: Generate 500 documents in batch to test performance.

---

## Assumptions

1. PDF generation library: wkhtmltopdf, iText, or similar (TBD in tech design).
2. Templates are versioned — each generation records the template version used.
3. Only approved/sanctioned data is merged — not draft or unverified data.

---

## Open Questions / Response Section

> **For Product Owner / Stakeholder to fill:**

| #  | Question                                                                                             | Response |
|----|------------------------------------------------------------------------------------------------------|----------|
| 1  | Are there additional document types beyond Sanction Letter and Loan Agreement to be generated in V1? |          |
| 2  | Should generated documents support **digital signatures** (e-sign)?                                  |          |
| 3  | Should the system support **multi-language** templates (English + vernacular)?                        |          |
| 4  | Who has permission to edit templates — Admin only, or also Credit Managers?                           |          |
