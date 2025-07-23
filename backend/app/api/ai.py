# backend/app/api/ai.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import uuid
import os
import logging
from datetime import datetime

from app.database import get_db
from app.models import User, Issue
from app.schemas import UserResponse
from app.core.auth import get_current_active_user
from app.ai.classifier import IssueClassifier
from app.ai.chat_assistant import ChatAssistant
from app.ai.analytics import PredictiveAnalytics
from app.ai.document_processor import DocumentProcessor
from app.ai.assignment_engine import SmartAssignmentEngine
from app.ai.notification_engine import SmartNotificationEngine

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize AI services
classifier = IssueClassifier()
chat_assistant = ChatAssistant()
analytics = PredictiveAnalytics()
document_processor = DocumentProcessor()
assignment_engine = SmartAssignmentEngine()
notification_engine = SmartNotificationEngine()

@router.post("/classify-issue")
async def classify_issue(
    title: str = Form(...),
    description: str = Form(...),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Classify an issue using AI"""
    try:
        classification = await classifier.classify_issue(title, description)
        return {
            "success": True,
            "classification": classification
        }
    except Exception as e:
        logger.error(f"Issue classification failed: {e}")
        raise HTTPException(status_code=500, detail="Classification service temporarily unavailable")

@router.post("/analyze-issue")
async def analyze_issue(
    issue_data: Dict[str, Any],
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Comprehensive AI analysis of an issue"""
    try:
        # Get classification
        classification = await classifier.classify_issue(
            issue_data.get('title', ''),
            issue_data.get('description', '')
        )
        
        # Get time prediction
        time_prediction = await analytics.predict_resolution_time(issue_data)
        
        # Get escalation risk
        escalation_risk = await analytics.predict_escalation_risk(issue_data)
        
        # Get assignment suggestion
        assignment_suggestion = await assignment_engine.suggest_assignee(issue_data)
        
        return {
            "success": True,
            "analysis": {
                "classification": classification,
                "time_prediction": time_prediction,
                "escalation_risk": escalation_risk,
                "assignment_suggestion": assignment_suggestion,
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Issue analysis failed: {e}")
        raise HTTPException(status_code=500, detail="Analysis service temporarily unavailable")

@router.post("/chat")
async def ai_chat(
    message_data: Dict[str, str],
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """AI chat assistant for user queries"""
    try:
        message = message_data.get('message', '').strip()
        conversation_id = message_data.get('conversation_id')
        
        if not message:
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        response = await chat_assistant.process_message(message, current_user, conversation_id)
        
        return {
            "success": True,
            "response": response,
            "conversation_id": conversation_id or str(uuid.uuid4())
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AI chat failed: {e}")
        return {
            "success": False,
            "response": {
                "message": "I'm having trouble processing your request right now. Please try again.",
                "type": "error",
                "suggestions": ["Try rephrasing your question", "Contact support"]
            }
        }

@router.post("/process-document")
async def process_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Process uploaded document with AI analysis"""
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Save uploaded file temporarily
        temp_dir = "temp_uploads"
        os.makedirs(temp_dir, exist_ok=True)
        
        temp_filename = f"{uuid.uuid4()}_{file.filename}"
        temp_filepath = os.path.join(temp_dir, temp_filename)
        
        with open(temp_filepath, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        try:
            # Process document
            analysis = await document_processor.process_document(temp_filepath, file.filename)
            
            return {
                "success": True,
                "filename": file.filename,
                "analysis": analysis,
                "processed_at": datetime.utcnow().isoformat()
            }
        finally:
            # Clean up temp file
            if os.path.exists(temp_filepath):
                os.remove(temp_filepath)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document processing failed: {e}")
        raise HTTPException(status_code=500, detail="Document processing service temporarily unavailable")

@router.get("/predict-resolution/{issue_id}")
async def predict_issue_resolution(
    issue_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Predict resolution time for a specific issue"""
    try:
        issue = db.query(Issue).filter(Issue.id == issue_id).first()
        if not issue:
            raise HTTPException(status_code=404, detail="Issue not found")
        
        # Check permissions
        if (current_user.role == 'REPORTER' and 
            issue.reporter_id != current_user.id):
            raise HTTPException(status_code=403, detail="Not enough permissions")
        
        issue_data = {
            'title': issue.title,
            'description': issue.description,
            'severity': issue.severity.value,
            'tags': issue.tags,
            'file_path': issue.file_path,
            'reporter_experience': db.query(Issue).filter(Issue.reporter_id == issue.reporter_id).count()
        }
        
        prediction = await analytics.predict_resolution_time(issue_data)
        escalation_risk = await analytics.predict_escalation_risk(issue_data)
        
        return {
            "success": True,
            "issue_id": issue_id,
            "prediction": prediction,
            "escalation_risk": escalation_risk
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Resolution prediction failed: {e}")
        raise HTTPException(status_code=500, detail="Prediction service temporarily unavailable")

@router.get("/team-analytics")
async def get_team_analytics(
    days: int = 30,
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Get AI-powered team analytics"""
    try:
        if current_user.role == 'REPORTER':
            raise HTTPException(status_code=403, detail="Analytics available for Maintainers and Admins only")
        
        if not (7 <= days <= 365):
            raise HTTPException(status_code=400, detail="Days parameter must be between 7 and 365")
        
        team_trends = await analytics.analyze_team_trends(days)
        
        return {
            "success": True,
            "analytics": team_trends,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Team analytics failed: {e}")
        raise HTTPException(status_code=500, detail="Analytics service temporarily unavailable")

@router.post("/suggest-assignment")
async def suggest_assignment(
    issue_data: Dict[str, Any],
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get AI suggestion for issue assignment"""
    try:
        if current_user.role not in ['ADMIN', 'MAINTAINER']:
            raise HTTPException(status_code=403, detail="Assignment suggestions available for Admins and Maintainers only")
        
        suggestion = await assignment_engine.suggest_assignee(issue_data)
        
        return {
            "success": True,
            "suggestion": suggestion,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Assignment suggestion failed: {e}")
        raise HTTPException(status_code=500, detail="Assignment service temporarily unavailable")

@router.post("/check-escalation")
async def check_escalation_need(
    issue_ids: list[int],
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Check which issues need escalation"""
    try:
        if current_user.role not in ['ADMIN', 'MAINTAINER']:
            raise HTTPException(status_code=403, detail="Escalation checks available for Admins and Maintainers only")
        
        escalation_results = []
        
        for issue_id in issue_ids[:50]:  # Limit to 50 issues
            issue = db.query(Issue).filter(Issue.id == issue_id).first()
            if issue:
                escalation_check = await notification_engine.should_escalate(issue)
                escalation_results.append({
                    "issue_id": issue_id,
                    "title": issue.title,
                    "escalation_needed": escalation_check
                })
        
        return {
            "success": True,
            "escalation_checks": escalation_results,
            "checked_at": datetime.utcnow().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Escalation check failed: {e}")
        raise HTTPException(status_code=500, detail="Escalation service temporarily unavailable")

@router.get("/insights/dashboard")
async def get_ai_dashboard_insights(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get AI-powered insights for dashboard"""
    try:
        insights = []
        
        # Get recent issues for analysis
        recent_issues = db.query(Issue).order_by(Issue.created_at.desc()).limit(100).all()
        
        if not recent_issues:
            return {
                "success": True,
                "insights": ["No recent issues to analyze"],
                "recommendations": ["Start by creating some issues to track"]
            }
        
        # Analyze patterns and generate insights
        critical_issues = [i for i in recent_issues if i.severity.value == 'CRITICAL']
        if len(critical_issues) > len(recent_issues) * 0.15:  # More than 15% critical
            insights.append({
                "type": "warning",
                "message": f"High critical issue ratio: {len(critical_issues)} out of {len(recent_issues)} recent issues",
                "recommendation": "Review critical issue triage process"
            })
        
        # Check for unassigned issues
        unassigned = [i for i in recent_issues if not i.assignee_id and i.status != 'DONE']
        if unassigned:
            insights.append({
                "type": "info",
                "message": f"{len(unassigned)} issues remain unassigned",
                "recommendation": "Consider using AI assignment suggestions"
            })
        
        # Check for old open issues
        from datetime import timedelta
        week_ago = datetime.utcnow() - timedelta(days=7)
        old_open = [i for i in recent_issues if i.created_at < week_ago and i.status == 'OPEN']
        if old_open:
            insights.append({
                "type": "warning",
                "message": f"{len(old_open)} issues have been open for over a week",
                "recommendation": "Review and triage older open issues"
            })
        
        # Generate AI predictions if we have enough data
        if current_user.role in ['ADMIN', 'MAINTAINER'] and len(recent_issues) >= 10:
            team_trends = await analytics.analyze_team_trends(14)  # 2 weeks
            if 'predictions' in team_trends:
                insights.append({
                    "type": "prediction",
                    "message": "Based on recent trends, issue volume may increase next week",
                    "recommendation": "Prepare team capacity for increased workload"
                })
        
        return {
            "success": True,
            "insights": insights[:5],  # Limit to top 5 insights
            "total_recent_issues": len(recent_issues),
            "critical_issues": len(critical_issues),
            "unassigned_issues": len(unassigned),
            "generated_at": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Dashboard insights failed: {e}")
        raise HTTPException(status_code=500, detail="Insights service temporarily unavailable")

@router.get("/health")
async def ai_health_check() -> Dict[str, Any]:
    """Check AI services health status"""
    try:
        health_status = {
            "ai_services": "healthy",
            "classifier": "available",
            "chat_assistant": "available", 
            "analytics": "available" if analytics.models_trained else "training",
            "document_processor": "available",
            "assignment_engine": "available",
            "notification_engine": "available",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return {
            "success": True,
            "health": health_status
        }
    except Exception as e:
        logger.error(f"AI health check failed: {e}")
        return {
            "success": False,
            "health": {
                "ai_services": "degraded",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        }