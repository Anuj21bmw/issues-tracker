#!/usr/bin/env python3
import sys
import os
sys.path.append('/app')

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import User, UserRole, Issue, IssueSeverity, IssueStatus, Base
from app.core.auth import get_password_hash

def create_demo_users():
    print("🔧 Setting up database and demo users...")
    
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Check if admin user already exists
        existing_admin = db.query(User).filter(User.email == "admin@example.com").first()
        if existing_admin:
            print("✅ Demo users already exist, skipping creation")
            return
        
        # Create demo users
        demo_users_data = [
            {
                "email": "admin@example.com",
                "password": "admin123",
                "full_name": "Admin User",
                "role": UserRole.ADMIN
            },
            {
                "email": "maintainer@example.com", 
                "password": "maintainer123",
                "full_name": "Maintainer User",
                "role": UserRole.MAINTAINER
            },
            {
                "email": "reporter@example.com",
                "password": "reporter123", 
                "full_name": "Reporter User",
                "role": UserRole.REPORTER
            }
        ]
        
        created_users = []
        
        for user_data in demo_users_data:
            user = User(
                email=user_data["email"],
                hashed_password=get_password_hash(user_data["password"]),
                full_name=user_data["full_name"],
                role=user_data["role"],
                is_active=True
            )
            
            db.add(user)
            db.flush()  # Flush to get the ID
            created_users.append(user)
        
        db.commit()
        
        # Create demo issues
        demo_issues = [
            {
                "title": "🐛 Login Page Not Loading",
                "description": "Users report that the login page is not loading properly on mobile devices. This appears to be a CSS rendering issue affecting iOS Safari specifically.",
                "severity": IssueSeverity.HIGH,
                "status": IssueStatus.OPEN,
                "tags": "bug,mobile,ui",
                "reporter_id": created_users[2].id  # Reporter
            },
            {
                "title": "⚡ Database Performance Issues",
                "description": "Queries are running slowly during peak hours (2-4 PM). Need to optimize database performance and add proper indexing.",
                "severity": IssueSeverity.CRITICAL,
                "status": IssueStatus.TRIAGED,
                "tags": "performance,database,optimization",
                "reporter_id": created_users[2].id,
                "assignee_id": created_users[1].id  # Maintainer
            },
            {
                "title": "🌙 Add Dark Mode Toggle",
                "description": "Users have requested a dark mode option for better accessibility and reduced eye strain during night usage.",
                "severity": IssueSeverity.LOW,
                "status": IssueStatus.IN_PROGRESS,
                "tags": "enhancement,ui,accessibility",
                "reporter_id": created_users[2].id,
                "assignee_id": created_users[1].id
            },
            {
                "title": "📧 Email Notifications Bug",
                "description": "Users are not receiving email notifications for status updates. SMTP configuration appears to be working but notifications are not being sent.",
                "severity": IssueSeverity.MEDIUM,
                "status": IssueStatus.DONE,
                "tags": "bug,notifications,email",
                "reporter_id": created_users[2].id,
                "assignee_id": created_users[1].id
            },
            {
                "title": "🔐 Two-Factor Authentication",
                "description": "Implement two-factor authentication for enhanced security. Should support both SMS and authenticator apps.",
                "severity": IssueSeverity.MEDIUM,
                "status": IssueStatus.OPEN,
                "tags": "security,enhancement,auth",
                "reporter_id": created_users[0].id  # Admin
            }
        ]
        
        for issue_data in demo_issues:
            issue = Issue(**issue_data)
            db.add(issue)
        
        db.commit()
        
        print("✅ Demo users and issues created successfully!")
        print("\n📋 Demo Accounts:")
        for user_data in demo_users_data:
            print(f"  {user_data['role'].value}: {user_data['email']} / {user_data['password']}")
        
        print(f"\n🎫 Created {len(demo_issues)} sample issues")
        print("🚀 Application is ready to use!")
        
    except Exception as e:
        print(f"❌ Error creating demo data: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_demo_users()
