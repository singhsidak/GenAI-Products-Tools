# US-001: Multi-Channel Lead Ingestion

| Field          | Value                                                                 |
|----------------|-----------------------------------------------------------------------|
| **Story ID**   | US-001                                                                |
| **Module**     | A — Lead & Sourcing                                                   |
| **Priority**   | High                                                                  |
| **PRD Ref**    | FR 1.1                                                                |
| **Created**    | 2026-02-19                                                            |

---

## Actors

| Actor               | Role                                                                 |
|----------------------|----------------------------------------------------------------------|
| **Applicant**        | End-user submitting a loan lead via website or mobile form            |
| **Aggregator**       | External partner (e.g., Paisabazaar) sending leads via API            |
| **Sales Officer**    | Internal user manually entering walk-in or telephonic leads           |
| **System (E-LOS)**   | Enterprise Loan Origination System — ingests, validates & persists leads |

---

## System Name

**E-LOS** (Enterprise Loan Origination System)

---

## Brief Description

As a **Sales Officer / Aggregator / Applicant**, I want to submit loan leads through multiple channels (website forms, aggregator APIs, and manual entry) so that all leads are captured in a single system regardless of the source channel.

---

## Business Goal

- Ensure **zero lead leakage** — every lead, irrespective of channel, lands in E-LOS.
- Reduce manual data entry errors by accepting structured JSON from digital channels.
- Enable real-time lead tracking from the moment of ingestion.

---

## Acceptance Criteria

| #  | Criterion                                                                                                    | Status |
|----|--------------------------------------------------------------------------------------------------------------|--------|
| 1  | System exposes a REST API endpoint (`POST /api/v1/leads`) that accepts a JSON payload.                        | ☐      |
| 2  | The JSON schema enforces mandatory fields: Full Name, Mobile Number, Loan Product, Loan Amount Requested.     | ☐      |
| 3  | Validation errors return HTTP 400 with field-level error messages.                                            | ☐      |
| 4  | Successfully ingested leads are assigned a unique **Lead ID** and status `DRAFT`.                             | ☐      |
| 5  | The API supports a `source` field with enum values: `WEBSITE`, `AGGREGATOR`, `MANUAL`.                        | ☐      |
| 6  | Website form submissions hit the same API endpoint via the frontend.                                          | ☐      |
| 7  | Manual entry by Sales Officers uses an admin-facing form that posts to the same endpoint.                     | ☐      |
| 8  | API response time for lead ingestion is **< 200ms** (P95).                                                    | ☐      |
| 9  | Every ingestion event writes an immutable entry to the Audit Log (timestamp, source, IP, payload hash).       | ☐      |
| 10 | Aggregator API calls are authenticated via API Key / OAuth2 token.                                            | ☐      |

---

## Use Cases

### UC-001.1 — Website Lead Submission
1. Applicant fills a loan enquiry form on the company website.
2. Frontend serialises form data into JSON and calls `POST /api/v1/leads` with `source: WEBSITE`.
3. System validates the payload → persists → returns Lead ID.
4. Applicant sees a confirmation message with Lead ID.

### UC-001.2 — Aggregator Lead Push
1. Aggregator system sends a batch or single-lead JSON to `POST /api/v1/leads` with `source: AGGREGATOR` and an API key header.
2. System validates credentials → validates payload → persists → returns Lead ID.
3. On failure, system returns structured error and does **not** create a partial record.

### UC-001.3 — Manual Lead Entry
1. Sales Officer logs into E-LOS admin panel.
2. Navigates to **Leads → Create New Lead**.
3. Fills the lead form and submits.
4. System creates a lead with `source: MANUAL` and assigns status `DRAFT`.

---

## Manual Testing Instructions

| Step | Action                                                                                          | Expected Result                                                       |
|------|-------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------|
| 1    | Open Postman / API client; send a valid JSON payload to `POST /api/v1/leads` with source `WEBSITE`. | HTTP 201 with `leadId` in response body.                              |
| 2    | Send the same payload without the `mobile` field.                                                | HTTP 400 with error: `"mobile is required"`.                          |
| 3    | Send a payload with `source: AGGREGATOR` but **no API key** header.                              | HTTP 401 Unauthorized.                                                |
| 4    | Send a valid aggregator payload with a valid API key.                                            | HTTP 201 with `leadId`.                                               |
| 5    | Log in as Sales Officer → navigate to Create Lead form → fill and submit.                       | Lead appears in the lead list with status `DRAFT` and source `MANUAL`.|
| 6    | Query the Audit Log table for the newly created Lead ID.                                        | Audit entry exists with correct timestamp, source, and IP.            |
| 7    | Measure API response time for 50 sequential calls.                                               | P95 response time < 200ms.                                            |

---

## Note for Automation Testing

> **Future Automation Scope:**
> - **API Contract Tests**: Validate JSON schema for all three source types using a contract-testing framework (e.g., Pact or Spring Cloud Contract).
> - **Load Tests**: Use k6/JMeter to simulate 5,000 concurrent lead submissions and assert < 200ms P95.
> - **Security Tests**: Automate aggregator authentication edge cases (expired token, invalid key, replay attack).
> - **E2E UI Tests**: Selenium/Cypress script for the manual lead form — fill, submit, verify in lead list.
> - **Audit Log Assertion**: After each API call, programmatically query audit table and assert presence + correctness.

---

## Assumptions

1. JSON is the only accepted content type; XML or form-encoded payloads are out of scope for V1.
2. Aggregators will be pre-registered and issued API keys via an admin process (not self-service).
3. Lead ingestion does **not** trigger deduplication immediately — that is handled separately (see US-002).

---

## Open Questions / Response Section

> **For Product Owner / Stakeholder to fill:**

| #  | Question                                                                                             | Response |
|----|------------------------------------------------------------------------------------------------------|----------|
| 1  | Should the system support **batch ingestion** (array of leads in a single API call) for aggregators?  |          |
| 2  | What is the maximum payload size allowed per request?                                                |          |
| 3  | Do we need a **webhook / callback URL** for aggregators to receive lead status updates?               |          |
| 4  | Should the manual entry form support **save as draft** before final submission?                       |          |
