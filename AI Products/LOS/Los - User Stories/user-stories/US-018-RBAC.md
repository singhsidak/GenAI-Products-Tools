# US-018: Role-Based Access Control (RBAC)

| Field          | Value                                                                 |
|----------------|-----------------------------------------------------------------------|
| **Story ID**   | US-018                                                                |
| **Module**     | Cross-Cutting — Security                                              |
| **Priority**   | Critical                                                              |
| **PRD Ref**    | Section 2 — Non-Functional Requirements (Security)                    |
| **Created**    | 2026-02-19                                                            |

---

## Actors

| Actor               | Role                                                                 |
|----------------------|----------------------------------------------------------------------|
| **Super Admin**      | Creates roles, assigns permissions, manages user-role mappings       |
| **Sales User**       | Has access to leads and onboarding; **restricted** from underwriting  |
| **Credit Manager**   | Has access to underwriting and assessment; not lead management        |
| **Operations User**  | Has access to disbursement and document management                   |
| **System (E-LOS)**   | Enforces access control at UI, API, and data levels                  |

---

## System Name

**E-LOS** (Enterprise Loan Origination System)

---

## Brief Description

As a **Super Admin**, I want to define roles and granular permissions so that each user sees only the screens, fields, and actions they are authorised for — specifically ensuring that "Sales" users **cannot** see "Underwriting" fields and vice versa.

---

## Business Goal

- Enforce **data segregation** — prevent unauthorized access to sensitive financial data.
- Comply with information security policy and regulatory requirements.
- Enable flexible role management as the organisation scales.

---

## Acceptance Criteria

| #  | Criterion                                                                                                    | Status |
|----|--------------------------------------------------------------------------------------------------------------|--------|
| 1  | Admin can create **Roles** (e.g., Sales Officer, Credit Manager, Operations, Admin).                          | ☐      |
| 2  | Each Role has a set of **Permissions** (View, Create, Edit, Delete) per module/screen/field.                 | ☐      |
| 3  | Permissions are enforced at **3 levels**: UI (hide/show), API (403 Forbidden), Data (row-level filtering).   | ☐      |
| 4  | A "Sales" user logging in **cannot see** the Underwriting tab, assessment fields, or credit ratios.          | ☐      |
| 5  | A "Credit Manager" logging in **cannot see** the Sales pipeline or lead allocation dashboard.                | ☐      |
| 6  | Admin can assign **multiple roles** to a single user.                                                        | ☐      |
| 7  | Role changes take effect on the **next login** (or within 5 minutes if using token-based auth).              | ☐      |
| 8  | All access denial events are audit-logged (user, attempted action, timestamp).                               | ☐      |
| 9  | Default roles are pre-seeded: Super Admin, Sales Officer, Sales Manager, Credit Manager, Senior CM, Operations, IT Admin. | ☐      |
| 10 | Password policy: minimum 8 characters, 1 uppercase, 1 number, 1 special character, expiry every 90 days.    | ☐      |

---

## Use Cases

### UC-018.1 — Sales User Restriction
1. Sales Officer logs in.
2. Navigation menu shows: Leads, My Cases, Documents → **no** Underwriting, BRE, or Ratios tabs.
3. If Sales user manually hits `/api/underwriting/123`, system returns HTTP 403.

### UC-018.2 — Credit Manager Restriction
1. Credit Manager logs in.
2. Sees: My Cases, Underwriting, BRE, Ratios → **no** Lead Pipeline or Allocation Dashboard.

### UC-018.3 — Admin Creates a New Role
1. Super Admin creates role "Regional Head" with permissions: View All + Approve High-Value.
2. Assigns the role to a user.
3. User logs in → sees screens per new role's permissions.

### UC-018.4 — Multi-Role User
1. User has both "Sales Officer" and "Credit Manager" roles.
2. User sees combined permissions: Leads + Underwriting.

---

## Manual Testing Instructions

| Step | Action                                                                                          | Expected Result                                                        |
|------|-------------------------------------------------------------------------------------------------|------------------------------------------------------------------------|
| 1    | Log in as Sales Officer.                                                                        | Underwriting tabs/fields not visible.                                  |
| 2    | As Sales, hit an Underwriting API endpoint directly.                                             | HTTP 403 Forbidden.                                                    |
| 3    | Log in as Credit Manager.                                                                       | No Lead Pipeline or Allocation visible.                                |
| 4    | Create a new role with specific permissions. Assign to user. Log in.                             | Permissions match exactly.                                             |
| 5    | Remove a permission from a role. Log out and back in.                                            | Removed permission no longer available.                                |
| 6    | Check Audit Log for access denial attempts.                                                     | Entry for each 403 attempt.                                            |

---

## Note for Automation Testing

> **Future Automation Scope:**
> - **Permission Matrix Tests**: For each role × endpoint combination, assert expected 200 or 403.
> - **UI Visibility Tests**: Selenium/Cypress tests asserting hidden/shown elements per role.
> - **Multi-Role Tests**: Assert combined permissions for users with multiple roles.
> - **Session Tests**: Assert role changes invalidate previous sessions.
> - **Penetration Tests**: Automated API fuzzing to find authorization bypass vulnerabilities.

---

## Assumptions

1. RBAC is implemented at both frontend (UI hiding) and backend (API enforcement) — UI-only hiding is NOT sufficient.
2. Authentication mechanism is JWT-based with role claims.
3. Row-level data filtering (e.g., Sales sees only their leads) is part of RBAC scope.

---

## Open Questions / Response Section

> **For Product Owner / Stakeholder to fill:**

| #  | Question                                                                                             | Response |
|----|------------------------------------------------------------------------------------------------------|----------|
| 1  | Should RBAC support **branch/region-level access** (e.g., Manager sees only their branch's cases)?    |          |
| 2  | Should we integrate with an existing **SSO/LDAP/Active Directory** or use E-LOS native auth?          |          |
| 3  | What is the session timeout duration (e.g., 30 min inactivity)?                                      |          |
| 4  | Should we support **IP whitelisting** for certain roles (e.g., Admin only from office network)?       |          |
