from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, ForeignKey, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from datetime import datetime

Base = declarative_base()

class UserRole(PyEnum):
    ADMIN = "ADMIN"
    MAINTAINER = "MAINTAINER"
    REPORTER = "REPORTER"

class IssueStatus(PyEnum):
    OPEN = "OPEN"
    TRIAGED = "TRIAGED"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"

class IssueSeverity(PyEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)  # Nullable for OAuth users
    full_name = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.REPORTER)
    google_id = Column(String, unique=True, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships - Fix the foreign_keys issue
    reported_issues = relationship("Issue", foreign_keys="Issue.reporter_id", back_populates="reporter")
    assigned_issues = relationship("Issue", foreign_keys="Issue.assignee_id", back_populates="assignee")

class Issue(Base):
    __tablename__ = "issues"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(Enum(IssueSeverity), default=IssueSeverity.LOW)
    status = Column(Enum(IssueStatus), default=IssueStatus.OPEN)
    file_path = Column(String, nullable=True)
    file_name = Column(String, nullable=True)
    tags = Column(String, nullable=True)  # JSON string of tags
    reporter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    reporter = relationship("User", foreign_keys=[reporter_id], back_populates="reported_issues")
    assignee = relationship("User", foreign_keys=[assignee_id], back_populates="assigned_issues")

class DailyStats(Base):
    __tablename__ = "daily_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, unique=True)
    open_count = Column(Integer, default=0)
    triaged_count = Column(Integer, default=0)
    in_progress_count = Column(Integer, default=0)
    done_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
