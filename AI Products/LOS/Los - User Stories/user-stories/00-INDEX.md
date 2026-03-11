# Enterprise LOS — User Stories Index

> **System Name:** E-LOS (Enterprise Loan Origination System)
> **PRD Version:** 1.0
> **Created:** 2026-02-19
> **Total Stories:** 20

---

## Story Structure (per file)

Each user story includes the following sections:
1. **Actors** — All personas involved
2. **System Name** — E-LOS
3. **Brief Description** — User story in standard format
4. **Business Goal** — Why this matters
5. **Acceptance Criteria** — Testable pass/fail conditions
6. **Use Cases** — Scenarios to implement
7. **Manual Testing Instructions** — Step-by-step QA guide
8. **Note for Automation Testing** — Future automation scope
9. **Assumptions** — Documented assumptions
10. **Open Questions / Response Section** — For stakeholder input

---

## Module A — Lead & Sourcing

| Story ID | Title | PRD Ref | Priority | File |
|----------|-------|---------|----------|------|
| US-001 | Multi-Channel Lead Ingestion | FR 1.1 | High | [US-001](./US-001-Multi-Channel-Lead-Ingestion.md) |
| US-002 | Lead Deduplication & Customer Linking | FR 1.2 | High | [US-002](./US-002-Lead-Deduplication-Customer-Linking.md) |
| US-003 | Lead Auto-Allocation Engine | FR 1.3 | High | [US-003](./US-003-Lead-Auto-Allocation-Engine.md) |

---

## Module B — Customer Onboarding

| Story ID | Title | PRD Ref | Priority | File |
|----------|-------|---------|----------|------|
| US-004 | KYC Integration & Verification | FR 2.1 | Critical | [US-004](./US-004-KYC-Integration-Verification.md) |
| US-005 | Credit Bureau Integration & Analysis | FR 2.2 | Critical | [US-005](./US-005-Credit-Bureau-Integration-Analysis.md) |

---

## Module C — Business Rule Engine (BRE)

| Story ID | Title | PRD Ref | Priority | File |
|----------|-------|---------|----------|------|
| US-006 | Configurable Rule Builder | FR 3.1 | Critical | [US-006](./US-006-Configurable-Rule-Builder.md) |
| US-007 | Scoring Models Configuration | FR 3.2 | High | [US-007](./US-007-Scoring-Models-Configuration.md) |
| US-008 | Case Routing Logic | FR 3.3 | High | [US-008](./US-008-Case-Routing-Logic.md) |

---

## Module D — Underwriting & Assessment

| Story ID | Title | PRD Ref | Priority | File |
|----------|-------|---------|----------|------|
| US-009 | Bank Statement Analyzer & Financial Spreading | FR 4.1 | Critical | [US-009](./US-009-Bank-Statement-Analyzer.md) |
| US-010 | Financial Ratio Auto-Calculation | FR 4.2 | High | [US-010](./US-010-Financial-Ratio-Calculation.md) |
| US-011 | Deviation Management Workflow | FR 4.3 | Critical | [US-011](./US-011-Deviation-Management-Workflow.md) |

---

## Module E — Document Management System (DMS)

| Story ID | Title | PRD Ref | Priority | File |
|----------|-------|---------|----------|------|
| US-012 | Intelligent Document Upload | FR 5.1 | High | [US-012](./US-012-Intelligent-Document-Upload.md) |
| US-013 | Document Deferral Tracking (OTC/PDD) | FR 5.2 | High | [US-013](./US-013-Document-Deferral-Tracking.md) |
| US-014 | Sanction Letter & Loan Agreement Generation | FR 5.3 | High | [US-014](./US-014-Document-Generation.md) |

---

## Module F — Disbursement

| Story ID | Title | PRD Ref | Priority | File |
|----------|-------|---------|----------|------|
| US-015 | Penny Drop Account Verification | FR 6.1 | Critical | [US-015](./US-015-Penny-Drop-Verification.md) |
| US-016 | LMS Handoff via REST API | FR 6.2 | Critical | [US-016](./US-016-LMS-Handoff.md) |

---

## Cross-Cutting Concerns

| Story ID | Title | PRD Ref | Priority | File |
|----------|-------|---------|----------|------|
| US-017 | Workflow State Machine | Section 3 | Critical | [US-017](./US-017-Workflow-State-Machine.md) |
| US-018 | Role-Based Access Control (RBAC) | Section 2 (Security) | Critical | [US-018](./US-018-RBAC.md) |
| US-019 | Immutable Audit Logging | Section 2 (Audit) | Critical | [US-019](./US-019-Immutable-Audit-Logging.md) |
| US-020 | Reporting & Analytics Dashboard | Section 4 | High | [US-020](./US-020-Reporting-Analytics-Dashboard.md) |

---

## Priority Summary

| Priority | Count | Stories |
|----------|-------|---------|
| Critical | 11 | US-004, 005, 006, 009, 011, 015, 016, 017, 018, 019 |
| High | 9 | US-001, 002, 003, 007, 008, 010, 012, 013, 014, 020 |

---

## Open Questions Across Stories

> Each story has its own "Open Questions / Response Section" at the bottom. Please review each story's questions and provide responses directly in the respective files. Key decisions that impact multiple stories:

1. **Third-party vendors**: AI Liveness (US-004), Bank API (US-015), Bureau partners (US-005), Bank Statement Parser (US-009)
2. **Authentication**: SSO/LDAP vs. native auth (US-018)
3. **Workflow**: Should `REJECTED` be re-openable? (US-017)
4. **Audit**: Log retention period and real-time dashboards (US-019)
5. **Reporting**: Scheduled reports and custom report builder scope (US-020)
