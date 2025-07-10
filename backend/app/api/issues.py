from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
import os
import uuid
from datetime import datetime

from app.database import get_db
from app.models import Issue, User, UserRole, IssueStatus, IssueSeverity
from app.schemas import IssueResponse, IssueUpdate, IssueListResponse
from app.core.auth import get_current_active_user, require_roles
from app.api.websocket import manager

router = APIRouter()

UPLOAD_DIR = "uploads"
ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".gif", ".doc", ".docx", ".txt"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def save_upload_file(upload_file: UploadFile) -> tuple[str, str]:
    if not upload_file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    file_ext = os.path.splitext(upload_file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    with open(file_path, "wb") as buffer:
        content = upload_file.file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large")
        buffer.write(content)
    
    return file_path, upload_file.filename

@router.post("/", response_model=IssueResponse)
async def create_issue(
    title: str = Form(...),
    description: str = Form(...),
    severity: IssueSeverity = Form(IssueSeverity.LOW),
    tags: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    file_path = None
    file_name = None
    
    if file and file.filename:
        file_path, file_name = save_upload_file(file)
    
    db_issue = Issue(
        title=title,
        description=description,
        severity=severity,
        tags=tags,
        file_path=file_path,
        file_name=file_name,
        reporter_id=current_user.id
    )
    
    db.add(db_issue)
    db.commit()
    db.refresh(db_issue)
    
    # Send WebSocket notification
    await manager.broadcast({
        "type": "issue_created",
        "data": {
            "id": db_issue.id,
            "title": db_issue.title,
            "reporter": current_user.full_name,
            "severity": db_issue.severity.value,
            "created_at": db_issue.created_at.isoformat()
        }
    })
    
    return db_issue

@router.get("/", response_model=IssueListResponse)
def read_issues(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100),
    status: Optional[IssueStatus] = None,
    severity: Optional[IssueSeverity] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    query = db.query(Issue)
    
    # Role-based filtering
    if current_user.role == UserRole.REPORTER:
        query = query.filter(Issue.reporter_id == current_user.id)
    
    # Apply filters
    if status:
        query = query.filter(Issue.status == status)
    if severity:
        query = query.filter(Issue.severity == severity)
    if search:
        query = query.filter(
            or_(
                Issue.title.ilike(f"%{search}%"),
                Issue.description.ilike(f"%{search}%")
            )
        )
    
    total = query.count()
    issues = query.order_by(Issue.created_at.desc()).offset(skip).limit(limit).all()
    
    return IssueListResponse(
        items=issues,
        total=total,
        page=skip // limit + 1,
        per_page=limit,
        total_pages=(total + limit - 1) // limit
    )

@router.get("/{issue_id}", response_model=IssueResponse)
def read_issue(
    issue_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    if (current_user.role == UserRole.REPORTER and 
        issue.reporter_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return issue

@router.put("/{issue_id}", response_model=IssueResponse)
async def update_issue(
    issue_id: int,
    issue_update: IssueUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    can_edit = (
        current_user.role in [UserRole.ADMIN, UserRole.MAINTAINER] or
        (current_user.role == UserRole.REPORTER and issue.reporter_id == current_user.id)
    )
    
    if not can_edit:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Reporters can only edit title, description, and severity
    if current_user.role == UserRole.REPORTER:
        allowed_fields = {"title", "description", "severity", "tags"}
        update_data = {k: v for k, v in issue_update.dict(exclude_unset=True).items() 
                      if k in allowed_fields}
    else:
        update_data = issue_update.dict(exclude_unset=True)
    
    old_status = issue.status
    
    for field, value in update_data.items():
        setattr(issue, field, value)
    
    db.commit()
    db.refresh(issue)
    
    # Send WebSocket notification if status changed
    if old_status != issue.status:
        await manager.broadcast({
            "type": "issue_status_changed",
            "data": {
                "id": issue.id,
                "title": issue.title,
                "old_status": old_status.value,
                "new_status": issue.status.value,
                "updated_by": current_user.full_name,
                "updated_at": datetime.utcnow().isoformat()
            }
        })
    
    return issue

@router.delete("/{issue_id}")
def delete_issue(
    issue_id: int,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.MAINTAINER)),
    db: Session = Depends(get_db)
):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    if issue.file_path and os.path.exists(issue.file_path):
        os.remove(issue.file_path)
    
    db.delete(issue)
    db.commit()
    
    return {"message": "Issue deleted successfully"}
