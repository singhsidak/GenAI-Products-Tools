# US-012: Intelligent Document Upload

| Field          | Value                                                                 |
|----------------|-----------------------------------------------------------------------|
| **Story ID**   | US-012                                                                |
| **Module**     | E — Document Management System (DMS)                                  |
| **Priority**   | High                                                                  |
| **PRD Ref**    | FR 5.1                                                                |
| **Created**    | 2026-02-19                                                            |

---

## Actors

| Actor               | Role                                                                 |
|----------------------|----------------------------------------------------------------------|
| **Sales Officer**    | Uploads applicant documents during onboarding                         |
| **Credit Manager**   | Reviews uploaded documents during underwriting                        |
| **Operations User**  | Manages and verifies document completeness before disbursement        |
| **System (E-LOS)**   | Stores documents with metadata, enforces tagging rules               |

---

## System Name

**E-LOS** (Enterprise Loan Origination System)

---

## Brief Description

As a **Sales Officer**, I want to upload applicant documents via a drag-and-drop interface with mandatory meta-tagging (Document Type and Sub-Type) so that all documents are properly classified, searchable, and audit-ready in the system.

---

## Business Goal

- Eliminate unclassified document uploads that cause downstream delays.
- Enable instant document retrieval by type/sub-type during underwriting.
- Maintain regulatory-compliant document storage.

---

## Acceptance Criteria

| #  | Criterion                                                                                                    | Status |
|----|--------------------------------------------------------------------------------------------------------------|--------|
| 1  | System provides a **drag-and-drop upload zone** on the application document tab.                              | ☐      |
| 2  | Multiple files can be uploaded simultaneously (batch upload).                                                 | ☐      |
| 3  | Before upload completes, user must select: **Document Type** (e.g., "Income Proof") and **Sub-Type** (e.g., "ITR 2023"). | ☐      |
| 4  | Document Type and Sub-Type are selected from a **pre-configured dropdown** (not free-text).                  | ☐      |
| 5  | Upload is blocked if meta-tags are not provided.                                                             | ☐      |
| 6  | Supported file formats: PDF, JPG, JPEG, PNG (max file size: 10MB per file).                                  | ☐      |
| 7  | Uploaded documents are stored with: File hash, Upload timestamp, Uploader ID, Document Type, Sub-Type.       | ☐      |
| 8  | Documents are viewable inline (PDF viewer / image viewer) and downloadable.                                  | ☐      |
| 9  | Document list shows all uploaded files with type, sub-type, uploader, and upload date.                       | ☐      |
| 10 | Documents are encrypted at rest (AES-256).                                                                   | ☐      |
| 11 | Upload events are audit-logged.                                                                              | ☐      |

---

## Use Cases

### UC-012.1 — Standard Upload
1. Sales Officer opens application → Document tab → drag-and-drop zone.
2. Drags a PDF file into the zone.
3. System prompts for Document Type → selects "Income Proof" → Sub-Type → selects "ITR 2023."
4. File uploads → appears in the document list with a green checkmark.

### UC-012.2 — Batch Upload
1. Sales Officer drags 5 files at once.
2. System prompts for tags for each file individually (or allows selecting a common type).
3. All 5 files upload successfully.

### UC-012.3 — Upload Blocked (No Tags)
1. User tries to upload without selecting Document Type.
2. System shows: "Document Type is mandatory. Please classify the document."
3. Upload does not proceed.

### UC-012.4 — Invalid File Type
1. User tries to upload a `.docx` file.
2. System shows: "Unsupported file format. Allowed: PDF, JPG, JPEG, PNG."

---

## Manual Testing Instructions

| Step | Action                                                                                          | Expected Result                                                        |
|------|-------------------------------------------------------------------------------------------------|------------------------------------------------------------------------|
| 1    | Drag-and-drop a PDF with proper tags.                                                           | File uploads; appears in list with correct metadata.                   |
| 2    | Try uploading without selecting Document Type.                                                   | Upload blocked; error message shown.                                   |
| 3    | Upload 5 files at once.                                                                         | All upload successfully with individual tags.                          |
| 4    | Upload a `.docx` file.                                                                          | Rejected with "Unsupported format" error.                              |
| 5    | Upload a file > 10MB.                                                                           | Rejected with "File too large" error.                                  |
| 6    | Click on an uploaded PDF to view inline.                                                        | PDF renders in embedded viewer.                                        |
| 7    | Check database for encryption of stored file.                                                    | File content encrypted at rest.                                        |

---

## Note for Automation Testing

> **Future Automation Scope:**
> - **File Format Validation**: Upload each supported and unsupported format → assert accept/reject.
> - **File Size Boundary Tests**: Files at 9.9MB, 10MB, 10.1MB → assert boundary behavior.
> - **Metadata Enforcement**: API-level upload without tags → assert 400 error.
> - **E2E UI Tests**: Cypress tests for drag-and-drop, tag selection, and list verification.
> - **Security**: Verify files are encrypted in storage layer.

---

## Assumptions

1. Document Type and Sub-Type master list is pre-configured by Operations Admin.
2. No virus/malware scanning in V1 (can be added later).
3. Cloud object storage (S3/GCS) or local filesystem with encryption — TBD during tech design.

---

## Open Questions / Response Section

> **For Product Owner / Stakeholder to fill:**

| #  | Question                                                                                             | Response |
|----|------------------------------------------------------------------------------------------------------|----------|
| 1  | Should we support **document versioning** (re-upload a newer version of the same document type)?     |          |
| 2  | What is the max file size per document — 10MB or higher?                                             |          |
| 3  | Should the system support **auto-classification** via AI/ML in V1 (detect doc type from content)?    |          |
| 4  | Are there any document types that are **product-specific** (e.g., RC Book only for Vehicle Loans)?    |          |
