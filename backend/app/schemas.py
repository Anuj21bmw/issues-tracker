from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime, date
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "ADMIN"
    MAINTAINER = "MAINTAINER"
    REPORTER = "REPORTER"

class IssueStatus(str, Enum):
    OPEN = "OPEN"
    TRIAGED = "TRIAGED"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"

class IssueSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole = UserRole.REPORTER

class UserCreate(UserBase):
    password: Optional[str] = None
    google_id: Optional[str] = None

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Issue schemas
class IssueBase(BaseModel):
    title: str
    description: str
    severity: IssueSeverity = IssueSeverity.LOW
    tags: Optional[str] = None

class IssueCreate(IssueBase):
    pass

class IssueUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[IssueSeverity] = None
    status: Optional[IssueStatus] = None
    tags: Optional[str] = None
    assignee_id: Optional[int] = None

class IssueResponse(IssueBase):
    id: int
    status: IssueStatus
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    reporter_id: int
    assignee_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    reporter: UserResponse
    assignee: Optional[UserResponse] = None

    class Config:
        from_attributes = True

class IssueListResponse(BaseModel):
    items: List[IssueResponse]
    total: int
    page: int
    per_page: int
    total_pages: int

# Dashboard schemas
class DashboardStats(BaseModel):
    total_issues: int
    open_issues: int
    triaged_issues: int
    in_progress_issues: int
    done_issues: int
    issues_by_severity: dict
    recent_activity: List[IssueResponse]

class DailyStatsResponse(BaseModel):
    date: date
    open_count: int
    triaged_count: int
    in_progress_count: int
    done_count: int
    created_at: datetime

    class Config:
        from_attributes = True

# WebSocket schemas
class WebSocketMessage(BaseModel):
    type: str
    data: dict
