"""Dashboard routes: analytics, notifications."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user, require_admin
from ..models import Run, Notification, NotificationPreference, ComplianceReport, User
from ..schemas import (
    AnalyticsSummary,
    NotificationOut,
    NotificationPrefOut,
    NotificationPrefUpdate,
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/analytics", response_model=AnalyticsSummary)
def get_analytics(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    runs = db.query(Run).all()
    total = len(runs)
    completed = sum(1 for r in runs if r.status == "completed")
    failed = sum(1 for r in runs if r.status == "failed")
    total_cost = sum(r.total_cost_usd or 0 for r in runs)
    total_tokens = sum(r.total_tokens_used or 0 for r in runs)

    by_status: dict[str, int] = {}
    for r in runs:
        by_status[r.status] = by_status.get(r.status, 0) + 1

    durations = [r.duration_minutes for r in runs if r.duration_minutes]
    avg_dur = round(sum(durations) / len(durations), 1) if durations else None

    # Compliance pass rate
    reports = db.query(ComplianceReport).all()
    if reports:
        passed = sum(1 for r in reports if r.overall_status == "pass")
        compliance_rate = round(passed / len(reports) * 100, 1)
    else:
        compliance_rate = None

    return AnalyticsSummary(
        period="all_time",
        total_runs=total,
        completed_runs=completed,
        failed_runs=failed,
        total_cost_usd=round(total_cost, 4),
        avg_cost_per_run_usd=round(total_cost / total, 4) if total else 0,
        total_tokens=total_tokens,
        total_tokens_used=total_tokens,
        runs_by_status=by_status,
        avg_completion_minutes=avg_dur,
        compliance_pass_rate=compliance_rate,
    )


# ── Notifications ─────────────────────────────────────────────────────────────

@router.get("/notifications", response_model=list[NotificationOut])
def list_notifications(
    unread_only: bool = False,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    q = db.query(Notification).filter(Notification.user_id == user.id)
    if unread_only:
        q = q.filter(Notification.is_read.is_(False))
    notifs = q.order_by(Notification.created_at.desc()).limit(100).all()
    return [NotificationOut.model_validate(n) for n in notifs]


@router.post("/notifications/{notification_id}/read")
def mark_read(
    notification_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    n = db.query(Notification).filter(
        Notification.id == notification_id, Notification.user_id == user.id
    ).first()
    if not n:
        raise HTTPException(status_code=404, detail="Notification not found")
    n.is_read = True
    db.commit()
    return {"message": "Marked as read"}


@router.post("/notifications/read-all")
def mark_all_read(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    db.query(Notification).filter(
        Notification.user_id == user.id, Notification.is_read.is_(False)
    ).update({"is_read": True})
    db.commit()
    return {"message": "All notifications marked as read"}


@router.get("/notifications/preferences", response_model=list[NotificationPrefOut])
def get_preferences(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    prefs = db.query(NotificationPreference).filter(
        NotificationPreference.user_id == user.id
    ).all()

    # Return defaults if none set
    if not prefs:
        defaults = [
            "pipeline_completed", "pipeline_failed",
            "compliance_review_required", "section_complete",
        ]
        return [NotificationPrefOut(event_type=et, is_enabled=True) for et in defaults]

    return [NotificationPrefOut(event_type=p.event_type, is_enabled=p.is_enabled) for p in prefs]


@router.put("/notifications/preferences")
def update_preference(
    body: NotificationPrefUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    pref = db.query(NotificationPreference).filter(
        NotificationPreference.user_id == user.id,
        NotificationPreference.event_type == body.event_type,
    ).first()

    if pref:
        pref.is_enabled = body.is_enabled
    else:
        pref = NotificationPreference(
            user_id=user.id,
            event_type=body.event_type,
            is_enabled=body.is_enabled,
        )
        db.add(pref)
    db.commit()
    return {"message": "Preference updated"}
