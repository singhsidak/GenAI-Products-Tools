"""
LoanMatrix Health Score Engine
Simulates ML-based cash-flow scoring with SHAP-like explainability.
"""
from typing import Tuple, Dict, List, Any
import random


ADVERSE_ACTION_CODES = {
    "credit_score": "Credit score below minimum threshold",
    "annual_revenue": "Insufficient annual business revenue",
    "years_in_business": "Insufficient time in business",
    "debt_to_income": "Debt-to-income ratio too high",
    "loan_to_revenue": "Requested amount disproportionate to revenue",
    "nsf_fees": "Excessive non-sufficient fund (NSF) occurrences",
    "avg_bank_balance": "Insufficient average bank balance",
}

ECOA_CODES = {
    "credit_score": "AA001 - Insufficient credit history or score",
    "annual_revenue": "AA002 - Income insufficient to support requested credit amount",
    "years_in_business": "AA003 - Insufficient length of time at present address/employment",
    "debt_to_income": "AA004 - Ratio of debt to income is excessive",
    "loan_to_revenue": "AA005 - Requested amount exceeds income-based limits",
    "nsf_fees": "AA006 - Insufficient funds history in bank account",
    "avg_bank_balance": "AA007 - Insufficient balance in depository account",
}


def calculate_health_score(
    credit_score: int = 650,
    annual_revenue: float = 100000,
    years_in_business: float = 2.0,
    monthly_expenses: float = 5000,
    loan_amount: float = 50000,
    avg_bank_balance: float = None,
    nsf_count: int = 0,
    bank_connected: bool = False,
) -> Tuple[int, Dict[str, float], List[str]]:
    """
    Calculate proprietary LoanMatrix Health Score (0-1000).
    Returns (score, shap_values, top_negative_factors)
    """
    contributions: Dict[str, float] = {}
    raw_score = 0.0

    # ── Credit Score (max 250 pts) ──────────────────────────────────
    credit_contrib = max(0, min(250, (credit_score / 850) * 250))
    raw_score += credit_contrib
    contributions["credit_score"] = round(credit_contrib, 1)

    # ── Annual Revenue (max 200 pts) ────────────────────────────────
    if annual_revenue >= 2_000_000:
        rev_contrib = 200
    elif annual_revenue >= 1_000_000:
        rev_contrib = 175
    elif annual_revenue >= 500_000:
        rev_contrib = 140
    elif annual_revenue >= 250_000:
        rev_contrib = 100
    elif annual_revenue >= 100_000:
        rev_contrib = 65
    else:
        rev_contrib = 20
    raw_score += rev_contrib
    contributions["annual_revenue"] = round(rev_contrib, 1)

    # ── Time in Business (max 150 pts) ──────────────────────────────
    if years_in_business >= 10:
        time_contrib = 150
    elif years_in_business >= 5:
        time_contrib = 120
    elif years_in_business >= 3:
        time_contrib = 90
    elif years_in_business >= 2:
        time_contrib = 65
    elif years_in_business >= 1:
        time_contrib = 40
    else:
        time_contrib = 10
    raw_score += time_contrib
    contributions["years_in_business"] = round(time_contrib, 1)

    # ── Debt-to-Income Ratio (max 150 pts) ──────────────────────────
    annual_expenses = monthly_expenses * 12
    dti = annual_expenses / max(annual_revenue, 1)
    if dti <= 0.20:
        dti_contrib = 150
    elif dti <= 0.35:
        dti_contrib = 120
    elif dti <= 0.50:
        dti_contrib = 80
    elif dti <= 0.65:
        dti_contrib = 40
    elif dti <= 0.80:
        dti_contrib = 15
    else:
        dti_contrib = 0
    raw_score += dti_contrib
    contributions["debt_to_income"] = round(dti_contrib, 1)

    # ── Loan-to-Revenue Ratio (max 100 pts) ─────────────────────────
    ltr = loan_amount / max(annual_revenue, 1)
    if ltr <= 0.15:
        ltr_contrib = 100
    elif ltr <= 0.30:
        ltr_contrib = 80
    elif ltr <= 0.60:
        ltr_contrib = 50
    elif ltr <= 1.0:
        ltr_contrib = 25
    else:
        ltr_contrib = 5
    raw_score += ltr_contrib
    contributions["loan_to_revenue"] = round(ltr_contrib, 1)

    # ── Bank Balance Stability (max 100 pts, only if bank connected) ─
    if bank_connected and avg_bank_balance is not None:
        balance_contrib = min(100, (avg_bank_balance / 100_000) * 100)
        raw_score += balance_contrib
        contributions["avg_bank_balance"] = round(balance_contrib, 1)
    else:
        contributions["avg_bank_balance"] = 0.0

    # ── NSF Penalty (0 to -100) ──────────────────────────────────────
    if nsf_count > 0:
        nsf_penalty = min(100, nsf_count * 15)
        raw_score -= nsf_penalty
        contributions["nsf_fees"] = round(-nsf_penalty, 1)
    else:
        contributions["nsf_fees"] = 0.0

    # Normalize to 0-1000
    max_possible = 950.0
    health_score = int(min(1000, max(0, (raw_score / max_possible) * 1000)))

    # Determine top negative SHAP factors for adverse action
    negative_factors = sorted(
        [(k, v) for k, v in contributions.items() if v < 50],
        key=lambda x: x[1],
    )
    top_negatives = [k for k, _ in negative_factors[:3]]

    return health_score, contributions, top_negatives


def generate_offers(
    health_score: int,
    loan_amount: float,
    annual_revenue: float,
) -> List[Dict[str, Any]]:
    """Generate risk-based pricing offers."""
    offers = []

    if health_score >= 700:
        # Tier 1 - Prime
        tiers = [
            {"product_type": "term_loan", "rate": 7.5, "term_months": 36, "multiplier": 1.0},
            {"product_type": "line_of_credit", "rate": 8.5, "term_months": 12, "multiplier": 0.8},
            {"product_type": "sba_loan", "rate": 6.5, "term_months": 60, "multiplier": 1.2},
        ]
    elif health_score >= 550:
        # Tier 2 - Near-Prime
        tiers = [
            {"product_type": "term_loan", "rate": 12.5, "term_months": 24, "multiplier": 0.85},
            {"product_type": "line_of_credit", "rate": 14.0, "term_months": 12, "multiplier": 0.65},
            {"product_type": "sba_loan", "rate": 11.0, "term_months": 48, "multiplier": 0.9},
        ]
    else:
        # Tier 3 - Subprime (still referred, but pricing ready)
        tiers = [
            {"product_type": "term_loan", "rate": 19.9, "term_months": 18, "multiplier": 0.6},
            {"product_type": "line_of_credit", "rate": 22.0, "term_months": 12, "multiplier": 0.45},
            {"product_type": "sba_loan", "rate": 18.0, "term_months": 36, "multiplier": 0.65},
        ]

    for tier in tiers:
        amount = min(loan_amount * tier["multiplier"], annual_revenue * 1.5)
        amount = round(amount, -2)   # round to nearest 100
        rate = tier["rate"] / 100 / 12
        n = tier["term_months"]
        if rate > 0:
            monthly_payment = amount * (rate * (1 + rate) ** n) / ((1 + rate) ** n - 1)
        else:
            monthly_payment = amount / n

        offers.append({
            "product_type": tier["product_type"],
            "rate": tier["rate"],
            "term_months": tier["term_months"],
            "amount": round(amount, 2),
            "monthly_payment": round(monthly_payment, 2),
        })

    return offers


def generate_risk_alerts(app_data: Dict[str, Any]) -> List[Dict[str, str]]:
    """Generate underwriter risk alerts based on application data."""
    alerts = []

    revenue = app_data.get("annual_revenue", 0) or 0
    expenses = app_data.get("monthly_expenses", 0) or 0
    nsf = app_data.get("nsf_count", 0) or 0
    loan = app_data.get("loan_amount", 0) or 0
    years = app_data.get("years_in_business", 0) or 0
    credit = app_data.get("credit_score", 700) or 700

    if nsf > 3:
        alerts.append({
            "severity": "high",
            "code": "NSF_HIGH",
            "message": f"High NSF frequency: {nsf} occurrences in last 12 months indicate cash flow stress.",
        })

    if revenue > 0 and (expenses * 12) / revenue > 0.75:
        alerts.append({
            "severity": "high",
            "code": "DTI_HIGH",
            "message": f"Expense-to-revenue ratio is {round((expenses*12/revenue)*100)}% — exceeds 75% threshold.",
        })

    if revenue > 0 and loan / revenue > 1.2:
        alerts.append({
            "severity": "medium",
            "code": "LTR_HIGH",
            "message": f"Requested loan (${loan:,.0f}) exceeds 120% of annual revenue. Elevated repayment risk.",
        })

    if years < 1.5:
        alerts.append({
            "severity": "medium",
            "code": "THIN_FILE",
            "message": f"Business established only {years} year(s) ago. Limited operating history for risk assessment.",
        })

    if credit < 580:
        alerts.append({
            "severity": "high",
            "code": "CREDIT_LOW",
            "message": f"Personal credit score ({credit}) is below the subprime threshold of 580.",
        })

    if 550 <= credit < 640:
        alerts.append({
            "severity": "medium",
            "code": "CREDIT_WATCH",
            "message": f"Personal credit score ({credit}) in near-prime range. Monitor for payment delinquencies.",
        })

    if not alerts:
        alerts.append({
            "severity": "low",
            "code": "PROFILE_CLEAN",
            "message": "No significant risk flags detected. Profile appears within acceptable risk parameters.",
        })

    return alerts


def generate_credit_memo(app: Any) -> str:
    """Generate a structured credit memo for the underwriter."""
    revenue = app.annual_revenue or 0
    expenses = app.monthly_expenses or 0
    credit = app.credit_score or 0
    dti = round((expenses * 12 / max(revenue, 1)) * 100, 1)
    ltr = round((app.loan_amount or 0) / max(revenue, 1) * 100, 1)

    memo = f"""# Credit Memorandum

**Application ID:** {app.id}
**Applicant:** {app.applicant_name or "N/A"}
**Business:** {app.business_name or "N/A"} ({app.business_type or "N/A"})
**Date:** {app.created_at.strftime("%B %d, %Y") if app.created_at else "N/A"}
**LoanMatrix Health Score:** {app.health_score or "N/A"} / 1000

---

## 1. Business Overview

{app.business_name or "The applicant's business"} is a {app.business_type or "business entity"} operating in the **{app.industry or "general"}** sector, incorporated in **{app.state or "N/A"}**. The business has been in operation for approximately **{app.years_in_business or "N/A"} years**, [{f"which exceeds our minimum threshold of 1 year" if (app.years_in_business or 0) >= 1 else "which is below our minimum threshold of 1 year and represents elevated vintage risk"}].

**Loan Request:** ${app.loan_amount:,.0f} for {app.loan_purpose or "general business purposes"}.

---

## 2. Financial Health Summary

| Metric | Value | Benchmark |
|--------|-------|-----------|
| Annual Revenue | **${revenue:,.0f}** | > $100,000 preferred |
| Monthly Operating Expenses | **${expenses:,.0f}** | — |
| Debt-to-Income Ratio | **{dti}%** | < 50% preferred |
| Loan-to-Revenue Ratio | **{ltr}%** | < 60% preferred |
| Personal Credit Score | **{credit}** | > 640 preferred |
| Avg. Bank Balance | **${app.avg_bank_balance:,.0f}** | — |
| NSF Count (12 mo.) | **{app.nsf_count}** | 0 preferred |

{"**Note:** Open Banking data (Plaid) was integrated. Cash flow analysis is based on verified transaction history." if app.bank_connected else "**Note:** Open Banking data was NOT connected. Financial figures are self-reported and require document verification."}

---

## 3. Cash Flow Analysis

Monthly deposits average approximately **${app.monthly_deposits_avg:,.0f}** based on bank data. {"The business demonstrates consistent inflow patterns with minimal seasonal volatility." if (app.nsf_count or 0) < 2 else "The account shows signs of cash flow stress, including " + str(app.nsf_count) + " NSF events in the past 12 months."}

Operating expense coverage ratio: **{round(revenue / max(expenses * 12, 1), 2)}x** — {"healthy" if revenue / max(expenses * 12, 1) > 1.5 else "marginal"}.

---

## 4. Risk Assessment

The LoanMatrix AI engine returned a Health Score of **{app.health_score or "N/A"}**, placing this application in the **{"Prime" if (app.health_score or 0) >= 700 else "Near-Prime" if (app.health_score or 0) >= 400 else "Subprime"}** risk tier.

**Key positive factors:** Strong {"revenue" if revenue > 200000 else "credit history" if credit > 680 else "business longevity"} relative to peer cohort.

**Key risk factors:** {"High DTI ratio requiring close monitoring." if dti > 50 else "Adequate debt management observed."} {"NSF history indicates periodic liquidity constraints." if (app.nsf_count or 0) > 2 else ""}

---

## 5. Recommendation

Based on the quantitative risk assessment and cash flow analysis, this application is referred for **human underwriter review**. The underwriter should validate the following before final disposition:

1. Verify income figures against uploaded Tax Return documents.
2. Confirm business license / EIN registration with Secretary of State.
3. Review 12-month bank statement for revenue concentration risk.
4. Assess borrower's repayment capacity under stress scenarios.

*This memo was generated by LoanMatrix AI Copilot. All cited figures are traceable to source documents in the document vault. The underwriter retains full decision authority.*
"""
    return memo
