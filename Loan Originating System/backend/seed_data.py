"""
Seed script — populates the database with demo applications for testing.
Run: python3 seed_data.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from database import engine, SessionLocal, Base
import models
from services.scoring import calculate_health_score, generate_offers

Base.metadata.create_all(bind=engine)

DEMO_APPS = [
    dict(applicant_name="Sarah Johnson", applicant_email="sarah@brightbakery.com",
         business_name="Bright Bakery LLC", business_type="llc", ein="45-1234567",
         years_in_business=4, industry="Restaurant / Food Service", state="CA",
         annual_revenue=420000, monthly_expenses=15000, credit_score=738,
         loan_amount=75000, loan_purpose="Equipment Purchase",
         bank_connected=True, avg_bank_balance=32000, nsf_count=0, monthly_deposits_avg=35000),
    dict(applicant_name="Marcus Webb", applicant_email="marcus@webbtech.io",
         business_name="Webb Tech Solutions", business_type="corporation", ein="55-9876543",
         years_in_business=7, industry="Technology", state="TX",
         annual_revenue=1_200_000, monthly_expenses=45000, credit_score=790,
         loan_amount=250000, loan_purpose="Business Expansion",
         bank_connected=True, avg_bank_balance=95000, nsf_count=0, monthly_deposits_avg=102000),
    dict(applicant_name="Priya Patel", applicant_email="priya@spicemarket.com",
         business_name="Spice Market", business_type="sole_proprietor",
         years_in_business=1.5, industry="Retail", state="NY",
         annual_revenue=88000, monthly_expenses=6500, credit_score=645,
         loan_amount=30000, loan_purpose="Working Capital",
         bank_connected=True, avg_bank_balance=5500, nsf_count=3, monthly_deposits_avg=7200),
    dict(applicant_name="James Carter", applicant_email="james@carterconst.com",
         business_name="Carter Construction", business_type="llc", ein="67-2345678",
         years_in_business=9, industry="Construction", state="FL",
         annual_revenue=2_500_000, monthly_expenses=85000, credit_score=755,
         loan_amount=400000, loan_purpose="Equipment Purchase",
         bank_connected=True, avg_bank_balance=180000, nsf_count=1, monthly_deposits_avg=215000),
    dict(applicant_name="Emily Torres", applicant_email="emily@etdesign.co",
         business_name="ET Design Studio", business_type="sole_proprietor",
         years_in_business=0.8, industry="Professional Services", state="WA",
         annual_revenue=65000, monthly_expenses=4200, credit_score=598,
         loan_amount=20000, loan_purpose="Marketing",
         bank_connected=False, avg_bank_balance=None, nsf_count=5, monthly_deposits_avg=None),
]

def seed():
    db = SessionLocal()
    # Ensure threshold exists
    if db.query(models.ThresholdConfig).count() == 0:
        db.add(models.ThresholdConfig())
        db.commit()

    threshold = db.query(models.ThresholdConfig).first()

    for data in DEMO_APPS:
        app = models.Application(**data)
        db.add(app)
        db.flush()

        score, shap_values, top_neg = calculate_health_score(
            credit_score=data.get("credit_score", 650),
            annual_revenue=data.get("annual_revenue", 0),
            years_in_business=data.get("years_in_business", 0),
            monthly_expenses=data.get("monthly_expenses", 0),
            loan_amount=data.get("loan_amount", 0),
            avg_bank_balance=data.get("avg_bank_balance"),
            nsf_count=data.get("nsf_count", 0),
            bank_connected=data.get("bank_connected", False),
        )

        app.health_score = score
        if score >= threshold.auto_approve_min:
            app.status = "auto_approved"
            decision_type = "auto_approve"
            reasons = ["Strong credit profile", "Adequate revenue-to-debt ratio"]
        elif score <= threshold.auto_decline_max:
            app.status = "auto_declined"
            decision_type = "auto_decline"
            reasons = [f"Health Score ({score}) below threshold"]
        else:
            app.status = "referred"
            decision_type = "referred"
            reasons = ["Manual review required", f"Health Score: {score}"]

        decision = models.Decision(
            application_id=app.id,
            decision_type=decision_type,
            reasons=reasons,
            shap_values=shap_values,
            decided_by="ai",
        )
        db.add(decision)

        if decision_type == "auto_approve":
            for offer_data in generate_offers(score, data["loan_amount"], data["annual_revenue"]):
                db.add(models.Offer(application_id=app.id, **offer_data))

        db.add(models.AuditLog(
            application_id=app.id,
            event_type="APPLICATION_SEEDED",
            details={"score": score, "decision": decision_type}
        ))

    db.commit()
    db.close()
    print(f"✓ Seeded {len(DEMO_APPS)} demo applications.")
    print("  Run 'uvicorn main:app --reload' to start the backend.")

if __name__ == "__main__":
    seed()
