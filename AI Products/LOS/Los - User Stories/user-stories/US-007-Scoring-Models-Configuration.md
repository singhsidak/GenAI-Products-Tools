# US-007: Scoring Models Configuration

| Field          | Value                                                                 |
|----------------|-----------------------------------------------------------------------|
| **Story ID**   | US-007                                                                |
| **Module**     | C — Business Rule Engine (BRE)                                        |
| **Priority**   | High                                                                  |
| **PRD Ref**    | FR 3.2                                                                |
| **Created**    | 2026-02-19                                                            |

---

## Actors

| Actor               | Role                                                                 |
|----------------------|----------------------------------------------------------------------|
| **Credit Admin**     | Creates and configures scoring models with weighted parameters       |
| **Credit Manager**   | Views scoring outcomes on applications                               |
| **System (E-LOS)**   | Computes weighted scores against application data                    |

---

## System Name

**E-LOS** (Enterprise Loan Origination System)

---

## Brief Description

As a **Credit Admin**, I want to define scoring models that assign weighted scores to applicant parameters (e.g., Age = 10 points, Employment Stability = 20 points) so that each application receives a quantitative risk score to support credit decisions.

---

## Business Goal

- Standardise credit risk assessment across all assessors via objective scoring.
- Enable rapid policy tuning by adjusting weights without code changes.
- Support multiple scoring models per product type.

---

## Acceptance Criteria

| #  | Criterion                                                                                                    | Status |
|----|--------------------------------------------------------------------------------------------------------------|--------|
| 1  | Admin can create a **Scoring Model** with a name, description, and product applicability.                    | ☐      |
| 2  | Each model contains multiple **parameters** — each with: Parameter Name, Weight, Value Range → Score mapping. | ☐      |
| 3  | Example config: Age 25-35 → 10 pts, Age 36-50 → 8 pts, Age 51-60 → 5 pts, Age > 60 → 0 pts.                | ☐      |
| 4  | System auto-calculates the **total weighted score** for an application when triggered.                       | ☐      |
| 5  | Score breakdown is visible on the application (which parameters contributed how many points).                 | ☐      |
| 6  | Models can be versioned — editing creates a new version; old version is retained.                            | ☐      |
| 7  | Models can be set to `ACTIVE` or `INACTIVE` per product.                                                    | ☐      |
| 8  | Scoring output can be used as an input to BRE rules (e.g., `IF TotalScore < 40 THEN Auto-Reject`).          | ☐      |
| 9  | Admin can **simulate** a model against sample data before activating.                                       | ☐      |
| 10 | Score computation completes in < 100ms per application.                                                     | ☐      |

---

## Use Cases

### UC-007.1 — Create a Scoring Model
1. Credit Admin navigates to **BRE → Scoring Models → Create**.
2. Defines model "PL Risk Score v1" for product "Personal Loan."
3. Adds parameters: Age (weight 10), Bureau Score (weight 30), Employment Type (weight 20), Income Stability (weight 15), Existing Obligations (weight 25).
4. For each parameter, defines value-range-to-score mapping.
5. Saves and sets to `ACTIVE`.

### UC-007.2 — Score an Application
1. Application reaches the BRE evaluation stage.
2. System applies "PL Risk Score v1" → calculates: Age=8 + Bureau=25 + Employment=18 + Income=12 + Obligations=20 = **83/100**.
3. Score appears on the application profile with breakdown.

### UC-007.3 — Simulate Model
1. Admin clicks "Simulate" → enters test data.
2. System returns the score breakdown without affecting any real application.

---

## Manual Testing Instructions

| Step | Action                                                                                          | Expected Result                                                        |
|------|-------------------------------------------------------------------------------------------------|------------------------------------------------------------------------|
| 1    | Create a scoring model with 3 parameters and defined ranges.                                    | Model saved and visible in model list.                                 |
| 2    | Submit an application matching the model's product.                                              | Total score calculated; breakdown visible on application.              |
| 3    | Change a parameter weight → verify new version created.                                          | Version history shows V1 and V2 with different weights.                |
| 4    | Simulate model with edge-case data (values at boundary of ranges).                               | Correct scores for boundary values.                                    |
| 5    | Create a BRE rule: `IF TotalScore < 40 THEN Auto-Reject`. Submit an application scoring 35.     | Application auto-rejected.                                             |

---

## Note for Automation Testing

> **Future Automation Scope:**
> - **Parameterized Tests**: Matrix of all value-range combinations → assert correct point assignment.
> - **Boundary Tests**: Values exactly at range boundaries (e.g., Age = 35.0 vs 35.01).
> - **Integration Tests**: Score flows into BRE rule evaluation correctly.
> - **Performance**: Score 1,000 applications in batch within 2 seconds.

---

## Assumptions

1. Maximum of 20 parameters per scoring model.
2. All parameter weights are positive integers; total possible score = sum of max points per parameter.
3. Scoring models are product-specific (e.g., separate models for PL and HL).

---

## Open Questions / Response Section

> **For Product Owner / Stakeholder to fill:**

| #  | Question                                                                                             | Response |
|----|------------------------------------------------------------------------------------------------------|----------|
| 1  | Should scoring models support **decimal weights** or only integers?                                   |          |
| 2  | Can one application have **multiple scoring models** applied (e.g., Risk Score + Income Score)?       |          |
| 3  | Should there be a **minimum cutoff score** defined at the model level (auto-reject threshold)?        |          |
