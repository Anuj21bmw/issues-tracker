from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from app.database import get_db
from app.models import Issue, IssueStatus, IssueSeverity, DailyStats, User, UserRole
from app.schemas import DashboardStats, DailyStatsResponse
from app.core.auth import get_current_active_user, require_roles

router = APIRouter()

@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.MAINTAINER)),
    db: Session = Depends(get_db)
):
    # Total counts by status
    total_issues = db.query(Issue).count()
    open_issues = db.query(Issue).filter(Issue.status == IssueStatus.OPEN).count()
    triaged_issues = db.query(Issue).filter(Issue.status == IssueStatus.TRIAGED).count()
    in_progress_issues = db.query(Issue).filter(Issue.status == IssueStatus.IN_PROGRESS).count()
    done_issues = db.query(Issue).filter(Issue.status == IssueStatus.DONE).count()
    
    # Issues by severity
    severity_counts = db.query(
        Issue.severity,
        func.count(Issue.id).label('count')
    ).filter(
        Issue.status != IssueStatus.DONE
    ).group_by(Issue.severity).all()
    
    issues_by_severity = {}
    for severity in IssueSeverity:
        issues_by_severity[severity.value] = 0
    
    for severity, count in severity_counts:
        issues_by_severity[severity.value] = count
    
    # Recent activity (last 10 issues)
    recent_activity = db.query(Issue).order_by(Issue.updated_at.desc()).limit(10).all()
    
    return DashboardStats(
        total_issues=total_issues,
        open_issues=open_issues,
        triaged_issues=triaged_issues,
        in_progress_issues=in_progress_issues,
        done_issues=done_issues,
        issues_by_severity=issues_by_severity,
        recent_activity=recent_activity
    )

@router.get("/daily-stats", response_model=List[DailyStatsResponse])
def get_daily_stats(
    days: int = 30,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.MAINTAINER)),
    db: Session = Depends(get_db)
):
    stats = db.query(DailyStats).order_by(DailyStats.date.desc()).limit(days).all()
    return stats
