from celery import Celery
from celery.schedules import crontab
from sqlalchemy.orm import Session
from datetime import date
import structlog

from app.core.config import settings
from app.database import SessionLocal
from app.models import Issue, IssueStatus, DailyStats

logger = structlog.get_logger()

celery_app = Celery(
    "worker",
    broker=settings.redis_url,
    backend=settings.redis_url
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "aggregate-daily-stats": {
            "task": "app.worker.aggregate_daily_stats",
            "schedule": crontab(minute="*/30"),  # Every 30 minutes
        },
    },
)

@celery_app.task
def aggregate_daily_stats():
    """Aggregate issue counts by status into daily_stats table"""
    db = SessionLocal()
    try:
        today = date.today()
        
        logger.info("Starting daily stats aggregation", date=today.isoformat())
        
        # Count issues by status
        open_count = db.query(Issue).filter(Issue.status == IssueStatus.OPEN).count()
        triaged_count = db.query(Issue).filter(Issue.status == IssueStatus.TRIAGED).count()
        in_progress_count = db.query(Issue).filter(Issue.status == IssueStatus.IN_PROGRESS).count()
        done_count = db.query(Issue).filter(Issue.status == IssueStatus.DONE).count()
        
        # Check if stats for today already exist
        existing_stats = db.query(DailyStats).filter(DailyStats.date == today).first()
        
        if existing_stats:
            existing_stats.open_count = open_count
            existing_stats.triaged_count = triaged_count
            existing_stats.in_progress_count = in_progress_count
            existing_stats.done_count = done_count
        else:
            new_stats = DailyStats(
                date=today,
                open_count=open_count,
                triaged_count=triaged_count,
                in_progress_count=in_progress_count,
                done_count=done_count
            )
            db.add(new_stats)
        
        db.commit()
        
        logger.info(
            "Daily stats aggregation completed",
            date=today.isoformat(),
            open_count=open_count,
            triaged_count=triaged_count,
            in_progress_count=in_progress_count,
            done_count=done_count
        )
        
        return {
            "date": today.isoformat(),
            "open_count": open_count,
            "triaged_count": triaged_count,
            "in_progress_count": in_progress_count,
            "done_count": done_count
        }
        
    except Exception as e:
        logger.error("Error in daily stats aggregation", error=str(e))
        db.rollback()
        raise
    finally:
        db.close()

@celery_app.task
def process_file_upload(file_path: str, issue_id: int):
    """Process uploaded files"""
    logger.info("Processing file upload", file_path=file_path, issue_id=issue_id)
    return {"status": "processed", "file_path": file_path, "issue_id": issue_id}
