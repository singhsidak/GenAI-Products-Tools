# US-020: Reporting & Analytics Dashboard

| Field          | Value                                                                 |
|----------------|-----------------------------------------------------------------------|
| **Story ID**   | US-020                                                                |
| **Module**     | Cross-Cutting — Reporting & Analytics                                 |
| **Priority**   | High                                                                  |
| **PRD Ref**    | Section 4 — Reporting & Analytics Requirements                        |
| **Created**    | 2026-02-19                                                            |

---

## Actors

| Actor               | Role                                                                 |
|----------------------|----------------------------------------------------------------------|
| **Business Head**    | Views funnel and conversion reports for strategic decisions           |
| **Operations Manager**| Monitors TAT and productivity reports for operational efficiency     |
| **Credit Manager**   | Reviews rejection analysis for policy refinement                     |
| **System (E-LOS)**   | Aggregates data and generates real-time and scheduled reports        |

---

## System Name

**E-LOS** (Enterprise Loan Origination System)

---

## Brief Description

As a **Business Head**, I want access to a comprehensive Reporting & Analytics Dashboard covering TAT, Funnel Conversion, Productivity, and Rejection Analysis so that I can make data-driven decisions on operational efficiency and business growth.

---

## Business Goal

- Enable data-driven decision-making at all management levels.
- Identify bottlenecks in the loan lifecycle (TAT analysis).
- Measure team productivity and conversion efficiency.
- Understand rejection trends for product/policy refinement.

---

## Acceptance Criteria

| #  | Criterion                                                                                                    | Status |
|----|--------------------------------------------------------------------------------------------------------------|--------|
| **TAT Report** | | |
| 1  | Shows average time spent in each stage (Draft, Logged In, Underwriting, etc.).                               | ☐      |
| 2  | Highlights cases exceeding SLA (e.g., "In Underwriting > 3 days") in red.                                    | ☐      |
| 3  | Filterable by: Product, Branch, Date Range, Stage.                                                           | ☐      |
| **Funnel Report** | | |
| 4  | Shows conversion funnel: Leads → Logins → Sanctions → Disbursements with count + %.                         | ☐      |
| 5  | Visual funnel chart with drill-down to individual stage.                                                     | ☐      |
| 6  | Filterable by: Product, Source Channel, Date Range.                                                          | ☐      |
| **Productivity Report** | | |
| 7  | Shows number of cases processed per user per day/week/month.                                                 | ☐      |
| 8  | Sortable by user, team, and region.                                                                          | ☐      |
| 9  | Includes breakdown by action (cases reviewed, approved, rejected).                                           | ☐      |
| **Rejection Analysis** | | |
| 10 | Shows top reasons for rejection (e.g., "Low CIBIL" 35%, "Low Income" 25%, "Age" 15%).                       | ☐      |
| 11 | Visualised as a **pie chart / bar chart** with filterable dimensions.                                        | ☐      |
| 12 | Drill-down to list of rejected applications per reason.                                                      | ☐      |
| **General** | | |
| 13 | All reports support **CSV/Excel export**.                                                                    | ☐      |
| 14 | Reports refresh in **near real-time** (data lag < 5 minutes).                                                | ☐      |
| 15 | Reports are accessible only to authorized roles (per RBAC).                                                  | ☐      |

---

## Use Cases

### UC-020.1 — TAT Monitoring
1. Operations Manager opens TAT Report.
2. Filters by Product = "Home Loan", last 30 days.
3. Sees avg. Underwriting time = 4.2 days (exceeding 3-day SLA) highlighted in red.
4. Drills down to see the 15 cases stuck in Underwriting.

### UC-020.2 — Funnel Analysis
1. Business Head opens Funnel Report.
2. Sees: 1,000 Leads → 650 Logins (65%) → 400 Sanctions (62%) → 350 Disbursements (88%).
3. Identifies Login-to-Sanction conversion as the bottleneck.

### UC-020.3 — Productivity Review
1. Sales Manager opens Productivity Report.
2. Sees Officer A processed 15 cases/day, Officer B processed 5 cases/day.
3. Initiates workload rebalancing.

### UC-020.4 — Rejection Trend Analysis
1. Credit Head opens Rejection Analysis.
2. Sees "Low CIBIL" is the #1 reason (40% of rejections).
3. Considers adjusting lead sourcing criteria to improve quality.

---

## Manual Testing Instructions

| Step | Action                                                                                          | Expected Result                                                        |
|------|-------------------------------------------------------------------------------------------------|------------------------------------------------------------------------|
| 1    | Create 50 test applications across various stages. Open TAT Report.                             | Accurate time calculations per stage.                                  |
| 2    | Open Funnel Report → verify counts at each stage match actual data.                              | Counts and percentages are accurate.                                   |
| 3    | Open Productivity Report → verify user-wise case count matches actions taken.                    | Numbers match.                                                         |
| 4    | Reject 20 applications with various reasons. Open Rejection Analysis.                            | Pie chart shows correct distribution.                                  |
| 5    | Export each report to CSV.                                                                      | CSV downloaded with all visible data.                                  |
| 6    | Apply filters (Product, Date Range, Branch).                                                    | Report data updates correctly.                                         |
| 7    | Log in as Sales User → attempt to access reports.                                               | Blocked per RBAC (if not authorized).                                  |

---

## Note for Automation Testing

> **Future Automation Scope:**
> - **Data Accuracy Tests**: Seed N records → assert report aggregates match DB queries.
> - **Filter Tests**: Apply each filter combination → verify results.
> - **Export Tests**: Download CSV → programmatically validate column count and key values.
> - **Performance Tests**: Generate reports on 100K+ records → assert render time < 5 seconds.
> - **Refresh Tests**: Insert new data → verify report updates within 5 minutes.

---

## Assumptions

1. Reports are built on a read-replica or materialized views (not real-time transactional DB queries).
2. Charting library: Chart.js, Recharts, or similar frontend library.
3. Initial dashboard layout is fixed; custom report builder is out of scope for V1.

---

## Open Questions / Response Section

> **For Product Owner / Stakeholder to fill:**

| #  | Question                                                                                             | Response |
|----|------------------------------------------------------------------------------------------------------|----------|
| 1  | Should reports support **scheduled email delivery** (e.g., daily TAT report to Operations Head)?      |          |
| 2  | Are there additional KPIs/reports beyond the 4 listed (TAT, Funnel, Productivity, Rejection)?        |          |
| 3  | Should we support a **custom report builder** for ad-hoc queries in V1?                               |          |
| 4  | What is the required data refresh frequency — real-time, 5-minute, or daily batch?                   |          |
