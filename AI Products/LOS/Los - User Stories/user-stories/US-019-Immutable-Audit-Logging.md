# US-019: Immutable Audit Logging

| Field          | Value                                                                 |
|----------------|-----------------------------------------------------------------------|
| **Story ID**   | US-019                                                                |
| **Module**     | Cross-Cutting — Security & Compliance                                 |
| **Priority**   | Critical                                                              |
| **PRD Ref**    | Section 2 — Non-Functional Requirements (Audit Logging)               |
| **Created**    | 2026-02-19                                                            |

---

## Actors

| Actor               | Role                                                                 |
|----------------------|----------------------------------------------------------------------|
| **System (E-LOS)**   | Captures and writes immutable audit entries for every data mutation   |
| **Compliance Officer**| Queries and reviews audit logs for regulatory inspections            |
| **IT Admin**         | Manages log retention, storage, and access policies                  |

---

## System Name

**E-LOS** (Enterprise Loan Origination System)

---

## Brief Description

As a **Compliance Officer**, I want the system to maintain an immutable log of every data change (who changed what field, when, from what value to what value, and from which IP) so that we have a complete regulatory-grade audit trail.

---

## Business Goal

- Meet regulatory audit requirements (RBI, internal audit).
- Enable forensic investigation of data tampering or fraud.
- Provide a full history of every application's data lifecycle.

---

## Acceptance Criteria

| #  | Criterion                                                                                                    | Status |
|----|--------------------------------------------------------------------------------------------------------------|--------|
| 1  | Every create, update, and delete operation across all entities writes an audit log entry.                     | ☐      |
| 2  | Each entry contains: **Timestamp**, **User ID**, **User Role**, **IP Address**, **Entity** (table/field), **Old Value**, **New Value**, **Action Type** (CREATE/UPDATE/DELETE). | ☐      |
| 3  | Audit logs are **immutable** — no user (including Super Admin) can edit or delete them.                       | ☐      |
| 4  | Logs are stored in a separate, append-only data store (not the main application database).                   | ☐      |
| 5  | Compliance Officer can **search** audit logs by: User, Entity, Date Range, Application ID.                   | ☐      |
| 6  | Audit log query results are exportable to **CSV/Excel**.                                                     | ☐      |
| 7  | Log retention period is configurable (default: 7 years per regulatory requirement).                          | ☐      |
| 8  | Audit log writes do **not** block the primary transaction (async write with guaranteed delivery).             | ☐      |
| 9  | Sensitive fields (PAN, Aadhaar) are **masked** in audit logs (e.g., `XXXXX1234F`).                           | ☐      |
| 10 | System logs **failed access attempts** (403 events) as well.                                                 | ☐      |

---

## Use Cases

### UC-019.1 — Track Field Change
1. Credit Manager changes the interest rate from 10.5% to 11.0% on Application #5678.
2. Audit log entry: `{timestamp: ..., userId: CM01, ip: 192.168.1.10, entity: Application#5678.interestRate, oldValue: 10.5, newValue: 11.0, action: UPDATE}`.
3. Compliance Officer can search by Application #5678 and see the change.

### UC-019.2 — Investigation
1. Compliance suspects data tampering on an application.
2. Searches audit log by Application ID → sees all changes in chronological order.
3. Identifies who changed a critical field and when.

### UC-019.3 — Export for Audit
1. RBI auditor requests 6 months of audit data for all rejected applications.
2. Compliance Officer filters by status = REJECTED, date range = last 6 months.
3. Exports to Excel → shares with auditor.

---

## Manual Testing Instructions

| Step | Action                                                                                          | Expected Result                                                        |
|------|-------------------------------------------------------------------------------------------------|------------------------------------------------------------------------|
| 1    | Edit any field on an application (e.g., change loan amount).                                     | Audit log entry created with old and new values.                       |
| 2    | Attempt to delete an audit log entry via DB.                                                     | Blocked (append-only table or external store).                         |
| 3    | Search audit logs by Application ID.                                                            | All changes for that application returned.                             |
| 4    | Search by date range and export to CSV.                                                          | CSV downloaded with correct data.                                      |
| 5    | Verify PAN is masked in audit log entry.                                                         | Shows `XXXXX1234F` not full PAN.                                       |
| 6    | Trigger a 403 access denial. Check audit log.                                                    | Entry for failed access attempt present.                               |

---

## Note for Automation Testing

> **Future Automation Scope:**
> - **Completeness Tests**: Perform CRUD operations on every entity → assert audit entry exists for each.
> - **Immutability Tests**: Attempt UPDATE/DELETE on audit table → assert failure at DB level.
> - **Masking Tests**: Assert PII fields are masked in logs.
> - **Performance Tests**: 10,000 concurrent operations → verify audit logging doesn't degrade primary transaction performance.
> - **Retention Tests**: Assert log rotation/archival after configured period.

---

## Assumptions

1. Audit logs use a separate store (e.g., MongoDB, Elasticsearch, or append-only Postgres partition).
2. The async write uses a message queue (e.g., Kafka) to guarantee delivery.
3. "Immutable" means no UPDATE/DELETE SQL permissions on the audit tables, even for DBAs.

---

## Open Questions / Response Section

> **For Product Owner / Stakeholder to fill:**

| #  | Question                                                                                             | Response |
|----|------------------------------------------------------------------------------------------------------|----------|
| 1  | What is the log retention period — 7 years (regulatory standard) or different?                        |          |
| 2  | Should audit logs be encrypted at rest separately from the main DB?                                   |          |
| 3  | Do we need **real-time audit dashboards** (e.g., Kibana) or just search/export?                       |          |
| 4  | Should audit logs capture **read access** (view events) or only write operations?                     |          |
