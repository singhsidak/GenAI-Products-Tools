# US-010: Financial Ratio Auto-Calculation

| Field          | Value                                                                 |
|----------------|-----------------------------------------------------------------------|
| **Story ID**   | US-010                                                                |
| **Module**     | D — Underwriting & Assessment                                         |
| **Priority**   | High                                                                  |
| **PRD Ref**    | FR 4.2                                                                |
| **Created**    | 2026-02-19                                                            |

---

## Actors

| Actor               | Role                                                                 |
|----------------------|----------------------------------------------------------------------|
| **Credit Manager**   | Reviews computed ratios; may override input values                    |
| **System (E-LOS)**   | Auto-computes FOIR, LTV, DSCR from available application data       |

---

## System Name

**E-LOS** (Enterprise Loan Origination System)

---

## Brief Description

As the **E-LOS system**, I want to automatically calculate key financial ratios — **FOIR** (Fixed Obligation to Income Ratio), **LTV** (Loan to Value), and **DSCR** (Debt Service Coverage Ratio) — using application and spreading data so that Credit Managers have instant, consistent underwriting metrics.

---

## Business Goal

- Eliminate manual ratio calculations and associated errors.
- Ensure consistent ratio definitions across all assessors.
- Enable real-time ratio updates as input data changes.

---

## Acceptance Criteria

| #  | Criterion                                                                                                    | Status |
|----|--------------------------------------------------------------------------------------------------------------|--------|
| 1  | **FOIR** = (Existing EMI + Proposed EMI) / Net Monthly Income. Displayed as percentage.                       | ☐      |
| 2  | **LTV** = Proposed Loan Amount / Property Value. Displayed as percentage.                                    | ☐      |
| 3  | **DSCR** = Net Operating Income / Total Debt Service. Displayed as ratio (e.g., 1.5x).                      | ☐      |
| 4  | Ratios are **auto-calculated** whenever relevant input fields are updated.                                   | ☐      |
| 5  | Ratios are displayed on a dedicated "Ratio Summary" panel on the application detail screen.                  | ☐      |
| 6  | If an input is missing (e.g., Property Value not yet entered), the ratio shows "N/A — missing input."        | ☐      |
| 7  | Ratios feed into BRE rules (e.g., `IF FOIR > 60% THEN Trigger Deviation`).                                  | ☐      |
| 8  | Credit Manager can see the **input breakdown** behind each ratio (click to expand).                          | ☐      |
| 9  | Ratio computation handles edge cases: division by zero → "N/A"; negative values → flagged in red.           | ☐      |
| 10 | All ratio computations are deterministic and produce identical results for identical inputs.                  | ☐      |

---

## Use Cases

### UC-010.1 — FOIR Calculation
1. Application has: Existing EMI = ₹15,000, Proposed EMI = ₹25,000, Net Monthly Income = ₹80,000.
2. System calculates: FOIR = (15,000 + 25,000) / 80,000 = **50%**.
3. Credit Manager sees FOIR = 50% on the Ratio Summary panel.

### UC-010.2 — LTV Calculation
1. Proposed Loan = ₹40,00,000, Property Value = ₹60,00,000.
2. LTV = 40,00,000 / 60,00,000 = **66.67%**.

### UC-010.3 — DSCR Calculation
1. Net Operating Income = ₹12,00,000/year, Total Debt Service = ₹8,00,000/year.
2. DSCR = 12,00,000 / 8,00,000 = **1.50x**.

### UC-010.4 — Missing Input
1. Property Value is not yet entered.
2. LTV shows "N/A — Property Value missing" instead of an error.

---

## Manual Testing Instructions

| Step | Action                                                                                          | Expected Result                                                        |
|------|-------------------------------------------------------------------------------------------------|------------------------------------------------------------------------|
| 1    | Enter all FOIR inputs on an application.                                                        | FOIR auto-calculates and displays correctly.                           |
| 2    | Change Proposed EMI → verify FOIR updates in real time.                                          | FOIR recalculates instantly.                                           |
| 3    | Enter LTV inputs; leave Property Value blank.                                                   | LTV shows "N/A — Property Value missing."                              |
| 4    | Enter Net Monthly Income = 0.                                                                   | FOIR shows "N/A" (division by zero handled).                           |
| 5    | Create BRE rule: `IF FOIR > 60% THEN Trigger Deviation`. Submit case with FOIR = 65%.           | Deviation triggered.                                                   |
| 6    | Click the ratio to expand breakdown.                                                            | Input values (Existing EMI, Proposed EMI, Income) shown.               |

---

## Note for Automation Testing

> **Future Automation Scope:**
> - **Formula Unit Tests**: Parameterized tests for FOIR, LTV, DSCR with 30+ value combinations including edge cases.
> - **Edge Cases**: Zero income, zero property value, negative NOI, very large numbers.
> - **Real-Time Update Tests**: Update an input via API → assert ratio recalculates within 100ms.
> - **BRE Integration Tests**: Assert ratios correctly trigger/don't trigger BRE rules at boundary values.

---

## Assumptions

1. "Existing EMI" is sourced from the Bureau report (Total Current EMI) — see US-005.
2. "Proposed EMI" is derived from loan amount, tenor, and interest rate (calculated by E-LOS).
3. LTV is only applicable for secured products (Home Loan, LAP); hidden for unsecured products.
4. DSCR is only applicable for business loan / self-employed applicants.

---

## Open Questions / Response Section

> **For Product Owner / Stakeholder to fill:**

| #  | Question                                                                                             | Response |
|----|------------------------------------------------------------------------------------------------------|----------|
| 1  | What is the acceptable **FOIR threshold** per product (e.g., PL max 50%, HL max 60%)?                 |          |
| 2  | What is the maximum acceptable **LTV** per product (e.g., HL max 80%, LAP max 65%)?                   |          |
| 3  | Should ratios be calculated based on **gross** or **net** income?                                     |          |
| 4  | Are there additional ratios beyond FOIR/LTV/DSCR needed in V1?                                        |          |
