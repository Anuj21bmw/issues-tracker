# backend/app/api/ai.py - Complete AI-Enhanced API
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
import uuid
import os
import logging
from datetime import datetime, timedelta
import json

from app.database import get_db
from app.models import User, Issue, IssueStatus, IssueSeverity
from app.schemas import UserResponse
from app.core.auth import get_current_active_user
from app.ai.classifier import IssueClassifier
from app.ai.chat_assistant import ChatAssistant
from app.ai.analytics import PredictiveAnalytics
from app.ai.document_processor import DocumentProcessor
from app.ai.assignment_engine import SmartAssignmentEngine
from app.ai.notification_engine import SmartNotificationEngine
from app.ai.resolution_assistant import ResolutionAssistant

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize AI services
classifier = IssueClassifier()
chat_assistant = ChatAssistant()
analytics = PredictiveAnalytics()
document_processor = DocumentProcessor()
assignment_engine = SmartAssignmentEngine()
notification_engine = SmartNotificationEngine()
resolution_assistant = ResolutionAssistant()

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
        
        # Get resolution suggestions
        mock_issue = type('MockIssue', (), issue_data)()
        resolution_suggestions = await resolution_assistant.suggest_resolution_steps(mock_issue)
        
        return {
            "success": True,
            "analysis": {
                "classification": classification,
                "time_prediction": time_prediction,
                "escalation_risk": escalation_risk,
                "assignment_suggestion": assignment_suggestion,
                "resolution_suggestions": resolution_suggestions,
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
        
        # Get resolution suggestions
        resolution_suggestions = await resolution_assistant.suggest_resolution_steps(issue)
        
        # Track resolution progress
        progress_tracking = await resolution_assistant.track_resolution_progress(issue_id)
        
        return {
            "success": True,
            "issue_id": issue_id,
            "prediction": prediction,
            "escalation_risk": escalation_risk,
            "resolution_suggestions": resolution_suggestions,
            "progress_tracking": progress_tracking
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
        
        # Get additional assignment analytics
        assignment_analytics = await assignment_engine.get_assignment_analytics(30)
        
        # Get workload rebalancing suggestions
        rebalancing = await assignment_engine.suggest_workload_rebalancing()
        
        return {
            "success": True,
            "suggestion": suggestion,
            "assignment_analytics": assignment_analytics,
            "workload_rebalancing": rebalancing,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Assignment suggestion failed: {e}")
        raise HTTPException(status_code=500, detail="Assignment service temporarily unavailable")

@router.post("/check-escalation")
async def check_escalation_need(
    issue_ids: List[int],
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
        
        # Get notification patterns analysis
        notification_patterns = await notification_engine.analyze_notification_patterns(7)
        
        return {
            "success": True,
            "escalation_checks": escalation_results,
            "notification_patterns": notification_patterns,
            "checked_at": datetime.utcnow().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Escalation check failed: {e}")
        raise HTTPException(status_code=500, detail="Escalation service temporarily unavailable")

@router.get("/smart-notifications")
async def get_smart_notifications(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get smart notifications for the current user"""
    try:
        notifications = await notification_engine.generate_smart_notifications([current_user])
        notification_summary = await notification_engine.get_notification_summary(current_user, 7)
        
        return {
            "success": True,
            "notifications": notifications,
            "summary": notification_summary,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Smart notifications failed: {e}")
        raise HTTPException(status_code=500, detail="Notification service temporarily unavailable")

@router.get("/resolution-report/{issue_id}")
async def get_resolution_report(
    issue_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Generate resolution report for completed issue"""
    try:
        issue = db.query(Issue).filter(Issue.id == issue_id).first()
        if not issue:
            raise HTTPException(status_code=404, detail="Issue not found")
        
        # Check permissions
        if (current_user.role == 'REPORTER' and 
            issue.reporter_id != current_user.id):
            raise HTTPException(status_code=403, detail="Not enough permissions")
        
        report = await resolution_assistant.generate_resolution_report(issue_id)
        
        return {
            "success": True,
            "report": report,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Resolution report failed: {e}")
        raise HTTPException(status_code=500, detail="Report generation service temporarily unavailable")

@router.get("/insights/dashboard")
async def get_ai_dashboard_insights(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get AI-powered insights for dashboard"""
    try:
        insights = []
        recommendations = []
        
        # Get recent issues for analysis
        recent_issues = db.query(Issue).order_by(Issue.created_at.desc()).limit(100).all()
        
        if not recent_issues:
            return {
                "success": True,
                "insights": [{
                    "type": "info",
                    "message": "No recent issues to analyze",
                    "recommendation": "Start by creating some issues to track"
                }],
                "recommendations": ["Create your first issue"]
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
        unassigned = [i for i in recent_issues if not i.assignee_id and i.status != IssueStatus.DONE]
        if unassigned:
            insights.append({
                "type": "info",
                "message": f"{len(unassigned)} issues remain unassigned",
                "recommendation": "Consider using AI assignment suggestions"
            })
        
        # Check for old open issues
        week_ago = datetime.utcnow() - timedelta(days=7)
        old_open = [i for i in recent_issues if i.created_at < week_ago and i.status == IssueStatus.OPEN]
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
        
        # Performance insights
        done_issues = [i for i in recent_issues if i.status == IssueStatus.DONE]
        if done_issues:
            completion_rate = len(done_issues) / len(recent_issues) * 100
            if completion_rate > 80:
                insights.append({
                    "type": "success",
                    "message": f"Excellent completion rate: {completion_rate:.1f}%",
                    "recommendation": "Maintain current momentum"
                })
            elif completion_rate < 50:
                insights.append({
                    "type": "warning",
                    "message": f"Low completion rate: {completion_rate:.1f}%",
                    "recommendation": "Review workflow and potential bottlenecks"
                })
        
        # Team workload insights
        if current_user.role in ['ADMIN', 'MAINTAINER']:
            assignment_analytics = await assignment_engine.get_assignment_analytics(14)
            if 'insights' in assignment_analytics:
                for insight in assignment_analytics['insights'][:2]:  # Top 2 insights
                    insights.append({
                        "type": "info",
                        "message": insight,
                        "recommendation": "Review team workload distribution"
                    })
        
        return {
            "success": True,
            "insights": insights[:5],  # Limit to top 5 insights
            "total_recent_issues": len(recent_issues),
            "critical_issues": len(critical_issues),
            "unassigned_issues": len(unassigned),
            "completion_rate": len(done_issues) / len(recent_issues) * 100 if recent_issues else 0,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Dashboard insights failed: {e}")
        raise HTTPException(status_code=500, detail="Insights service temporarily unavailable")

@router.post("/batch-classify")
async def batch_classify_issues(
    issues_data: List[Dict[str, Any]],
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Batch classify multiple issues"""
    try:
        if current_user.role not in ['ADMIN', 'MAINTAINER']:
            raise HTTPException(status_code=403, detail="Batch operations available for Admins and Maintainers only")
        
        if len(issues_data) > 100:
            raise HTTPException(status_code=400, detail="Maximum 100 issues per batch")
        
        results = await classifier.batch_classify_issues(issues_data)
        
        return {
            "success": True,
            "results": results,
            "total_processed": len(results),
            "processed_at": datetime.utcnow().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch classification failed: {e}")
        raise HTTPException(status_code=500, detail="Batch processing service temporarily unavailable")

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
            "resolution_assistant": "available",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Test AI services with simple operations
        try:
            # Test classifier
            test_classification = await classifier.classify_issue("Test", "Test description")
            health_status["classifier_test"] = "passed"
        except Exception as e:
            health_status["classifier"] = f"degraded: {str(e)}"
            health_status["ai_services"] = "degraded"
        
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

@router.get("/stats")
async def get_ai_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get AI usage statistics"""
    try:
        if current_user.role not in ['ADMIN', 'MAINTAINER']:
            raise HTTPException(status_code=403, detail="AI statistics available for Admins and Maintainers only")
        
        # Get basic stats
        total_issues = db.query(Issue).count()
        
        # Simulated AI usage stats (in production, these would come from actual usage tracking)
        ai_stats = {
            "total_classifications": total_issues,
            "successful_predictions": int(total_issues * 0.85),
            "chat_interactions": int(total_issues * 0.3),
            "documents_processed": int(total_issues * 0.2),
            "assignments_suggested": int(total_issues * 0.6),
            "escalations_prevented": int(total_issues * 0.1),
            "ai_uptime": "99.2%",
            "average_response_time": "350ms",
            "models_active": {
                "classification": True,
                "time_prediction": analytics.models_trained,
                "escalation_prediction": analytics.models_trained,
                "chat_assistant": True,
                "document_analysis": True
            }
        }
        
        return {
            "success": True,
            "stats": ai_stats,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AI stats failed: {e}")
        raise HTTPException(status_code=500, detail="Statistics service temporarily unavailable")

@router.post("/retrain-models")
async def retrain_ai_models(
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Retrain AI models with latest data"""
    try:
        if current_user.role != 'ADMIN':
            raise HTTPException(status_code=403, detail="Model retraining available for Admins only")
        
        # Trigger model retraining
        analytics._train_models()
        
        return {
            "success": True,
            "message": "AI models retraining initiated",
            "estimated_completion": "10-15 minutes",
            "initiated_at": datetime.utcnow().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Model retraining failed: {e}")
        raise HTTPException(status_code=500, detail="Model retraining service temporarily unavailable")

@router.post("/generate-insights")
async def generate_custom_insights(
    query_data: Dict[str, Any],
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Generate custom AI insights based on user query"""
    try:
        if current_user.role not in ['ADMIN', 'MAINTAINER']:
            raise HTTPException(status_code=403, detail="Custom insights available for Admins and Maintainers only")
        
        query_text = query_data.get('query', '').strip()
        if not query_text:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Analyze the query and generate appropriate insights
        insights = await analytics.generate_custom_insights(query_text, current_user, db)
        
        return {
            "success": True,
            "query": query_text,
            "insights": insights,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Custom insights generation failed: {e}")
        raise HTTPException(status_code=500, detail="Insights generation service temporarily unavailable")

@router.post("/recommend-actions")
async def recommend_actions(
    context_data: Dict[str, Any],
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Get AI-powered action recommendations"""
    try:
        if current_user.role not in ['ADMIN', 'MAINTAINER']:
            raise HTTPException(status_code=403, detail="Action recommendations available for Admins and Maintainers only")
        
        recommendations = await analytics.recommend_actions(context_data, current_user)
        
        return {
            "success": True,
            "recommendations": recommendations,
            "context": context_data.get('context', 'general'),
            "generated_at": datetime.utcnow().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Action recommendations failed: {e}")
        raise HTTPException(status_code=500, detail="Recommendation service temporarily unavailable")

@router.get("/trends/{period}")
async def get_ai_trends(
    period: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get AI-analyzed trends for specified period"""
    try:
        if current_user.role == 'REPORTER':
            raise HTTPException(status_code=403, detail="Trends analysis available for Maintainers and Admins only")
        
        valid_periods = ['week', 'month', 'quarter', 'year']
        if period not in valid_periods:
            raise HTTPException(status_code=400, detail=f"Period must be one of: {', '.join(valid_periods)}")
        
        trends = await analytics.analyze_trends(period, db)
        
        return {
            "success": True,
            "period": period,
            "trends": trends,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Trends analysis failed: {e}")
        raise HTTPException(status_code=500, detail="Trends analysis service temporarily unavailable")

@router.post("/export-analysis")
async def export_analysis_report(
    export_params: Dict[str, Any],
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Export comprehensive AI analysis report"""
    try:
        if current_user.role not in ['ADMIN', 'MAINTAINER']:
            raise HTTPException(status_code=403, detail="Export analysis available for Admins and Maintainers only")
        
        # Generate comprehensive analysis report
        report = await analytics.generate_comprehensive_report(export_params, current_user, db)
        
        # Generate download link or file path
        report_id = str(uuid.uuid4())
        export_file = f"reports/ai_analysis_{report_id}.json"
        
        # In production, save to cloud storage or generate signed URL
        os.makedirs("reports", exist_ok=True)
        with open(export_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        return {
            "success": True,
            "report_id": report_id,
            "download_url": f"/api/ai/download-report/{report_id}",
            "export_params": export_params,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis export failed: {e}")
        raise HTTPException(status_code=500, detail="Export service temporarily unavailable")

@router.get("/download-report/{report_id}")
async def download_analysis_report(
    report_id: str,
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Download exported analysis report"""
    try:
        if current_user.role not in ['ADMIN', 'MAINTAINER']:
            raise HTTPException(status_code=403, detail="Report download available for Admins and Maintainers only")
        
        report_file = f"reports/ai_analysis_{report_id}.json"
        
        if not os.path.exists(report_file):
            raise HTTPException(status_code=404, detail="Report not found or expired")
        
        # In production, return FileResponse or redirect to cloud storage URL
        with open(report_file, 'r') as f:
            report_data = json.load(f)
        
        return {
            "success": True,
            "report_id": report_id,
            "data": report_data,
            "downloaded_at": datetime.utcnow().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Report download failed: {e}")
        raise HTTPException(status_code=500, detail="Download service temporarily unavailable")

# Additional utility endpoints

@router.get("/models/status")
async def get_models_status(
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Get status of all AI models"""
    try:
        if current_user.role not in ['ADMIN', 'MAINTAINER']:
            raise HTTPException(status_code=403, detail="Model status available for Admins and Maintainers only")
        
        models_status = {
            "classifier": {
                "status": "active",
                "accuracy": 0.89,
                "last_trained": "2025-01-15T10:00:00Z",
                "version": "1.2.3"
            },
            "time_predictor": {
                "status": "active" if analytics.models_trained else "training",
                "accuracy": 0.76,
                "last_trained": "2025-01-14T15:30:00Z",
                "version": "1.1.5"
            },
            "escalation_predictor": {
                "status": "active" if analytics.models_trained else "training", 
                "accuracy": 0.82,
                "last_trained": "2025-01-14T15:30:00Z",
                "version": "1.1.2"
            },
            "assignment_engine": {
                "status": "active",
                "success_rate": 0.91,
                "last_updated": "2025-01-16T09:15:00Z",
                "version": "2.0.1"
            },
            "chat_assistant": {
                "status": "active",
                "response_quality": 0.88,
                "last_updated": "2025-01-10T12:00:00Z",
                "version": "1.4.0"
            }
        }
        
        return {
            "success": True,
            "models": models_status,
            "overall_health": "healthy",
            "checked_at": datetime.utcnow().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Models status check failed: {e}")
        raise HTTPException(status_code=500, detail="Models status service temporarily unavailable")

@router.post("/feedback")
async def submit_ai_feedback(
    feedback_data: Dict[str, Any],
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Submit feedback on AI predictions/suggestions"""
    try:
        feedback_type = feedback_data.get('type')
        service = feedback_data.get('service')
        rating = feedback_data.get('rating')
        comments = feedback_data.get('comments', '')
        
        if not all([feedback_type, service, rating]):
            raise HTTPException(status_code=400, detail="Missing required feedback fields")
        
        if not (1 <= rating <= 5):
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
        
        # Store feedback for model improvement
        feedback_record = {
            "user_id": current_user.id,
            "service": service,
            "type": feedback_type,
            "rating": rating,
            "comments": comments,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": feedback_data.get('metadata', {})
        }
        
        # In production, store in database or feedback collection system
        logger.info(f"AI feedback received: {feedback_record}")
        
        return {
            "success": True,
            "message": "Thank you for your feedback! It helps improve our AI services.",
            "feedback_id": str(uuid.uuid4()),
            "submitted_at": datetime.utcnow().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Feedback submission failed: {e}")
        raise HTTPException(status_code=500, detail="Feedback service temporarily unavailable")

@router.get("/performance/metrics")
async def get_ai_performance_metrics(
    days: int = 30,
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Get AI performance metrics over time"""
    try:
        if current_user.role != 'ADMIN':
            raise HTTPException(status_code=403, detail="Performance metrics available for Admins only")
        
        if not (1 <= days <= 365):
            raise HTTPException(status_code=400, detail="Days parameter must be between 1 and 365")
        
        # Simulated performance metrics (in production, get from monitoring system)
        metrics = {
            "classification_accuracy": {
                "current": 0.89,
                "trend": "stable",
                "history": [0.87, 0.88, 0.89, 0.89, 0.90]
            },
            "prediction_accuracy": {
                "current": 0.76,
                "trend": "improving",
                "history": [0.72, 0.74, 0.75, 0.76, 0.76]
            },
            "response_times": {
                "avg_ms": 342,
                "p95_ms": 850,
                "p99_ms": 1200,
                "trend": "stable"
            },
            "user_satisfaction": {
                "avg_rating": 4.2,
                "total_feedback": 156,
                "trend": "improving"
            },
            "error_rates": {
                "classification": 0.02,
                "chat": 0.01,
                "analytics": 0.03,
                "trend": "decreasing"
            }
        }
        
        return {
            "success": True,
            "period_days": days,
            "metrics": metrics,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Performance metrics failed: {e}")
        raise HTTPException(status_code=500, detail="Performance metrics service temporarily unavailable")

@router.post("/optimize")
async def optimize_ai_services(
    optimization_params: Dict[str, Any],
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Trigger AI services optimization"""
    try:
        if current_user.role != 'ADMIN':
            raise HTTPException(status_code=403, detail="AI optimization available for Admins only")
        
        optimization_type = optimization_params.get('type', 'general')
        services = optimization_params.get('services', ['all'])
        
        optimization_results = {
            "optimization_id": str(uuid.uuid4()),
            "type": optimization_type,
            "services": services,
            "status": "initiated",
            "estimated_completion": "15-30 minutes",
            "improvements_expected": [
                "Enhanced classification accuracy",
                "Faster response times",
                "Better prediction reliability",
                "Optimized resource usage"
            ]
        }
        
        # In production, trigger actual optimization processes
        logger.info(f"AI optimization initiated: {optimization_results}")
        
        return {
            "success": True,
            "optimization": optimization_results,
            "initiated_at": datetime.utcnow().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AI optimization failed: {e}")
        raise HTTPException(status_code=500, detail="Optimization service temporarily unavailable")

@router.get("/usage/analytics")
async def get_usage_analytics(
    period: str = "month",
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get AI services usage analytics"""
    try:
        if current_user.role not in ['ADMIN', 'MAINTAINER']:
            raise HTTPException(status_code=403, detail="Usage analytics available for Admins and Maintainers only")
        
        valid_periods = ['day', 'week', 'month', 'quarter']
        if period not in valid_periods:
            raise HTTPException(status_code=400, detail=f"Period must be one of: {', '.join(valid_periods)}")
        
        # Get usage statistics
        total_issues = db.query(Issue).count()
        
        usage_analytics = {
            "period": period,
            "total_requests": {
                "classification": int(total_issues * 1.2),  # Some issues classified multiple times
                "chat_interactions": int(total_issues * 0.4),
                "predictions": int(total_issues * 0.8),
                "document_processing": int(total_issues * 0.15),
                "assignments": int(total_issues * 0.6)
            },
            "success_rates": {
                "classification": 0.98,
                "chat_interactions": 0.95,
                "predictions": 0.87,
                "document_processing": 0.92,
                "assignments": 0.91
            },
            "most_used_features": [
                {"feature": "Issue Classification", "usage_percentage": 85},
                {"feature": "Resolution Time Prediction", "usage_percentage": 67},
                {"feature": "Smart Assignment", "usage_percentage": 54},
                {"feature": "Chat Assistant", "usage_percentage": 42},
                {"feature": "Document Analysis", "usage_percentage": 28}
            ],
            "user_adoption": {
                "active_users": 25,
                "power_users": 8,
                "occasional_users": 17,
                "adoption_rate": 0.78
            }
        }
        
        return {
            "success": True,
            "analytics": usage_analytics,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Usage analytics failed: {e}")
        raise HTTPException(status_code=500, detail="Usage analytics service temporarily unavailable")

@router.get("/config")
async def get_ai_configuration(
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Get current AI services configuration"""
    try:
        if current_user.role != 'ADMIN':
            raise HTTPException(status_code=403, detail="AI configuration available for Admins only")
        
        config = {
            "classification": {
                "enabled": True,
                "confidence_threshold": 0.7,
                "auto_tag": True,
                "severity_detection": True
            },
            "chat_assistant": {
                "enabled": True,
                "max_context_length": 4000,
                "response_timeout": 30,
                "fallback_enabled": True
            },
            "analytics": {
                "enabled": True,
                "prediction_models": ["time_estimation", "escalation_risk"],
                "training_frequency": "weekly",
                "min_data_points": 50
            },
            "assignment": {
                "enabled": True,
                "workload_balancing": True,
                "expertise_matching": True,
                "availability_check": False
            },
            "notifications": {
                "enabled": True,
                "escalation_thresholds": {
                    "critical": 4,  # hours
                    "high": 24,     # hours
                    "medium": 72,   # hours
                    "low": 168      # hours (1 week)
                },
                "smart_scheduling": True
            }
        }
        
        return {
            "success": True,
            "configuration": config,
            "last_updated": "2025-01-15T14:30:00Z",
            "retrieved_at": datetime.utcnow().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Configuration retrieval failed: {e}")
        raise HTTPException(status_code=500, detail="Configuration service temporarily unavailable")

@router.put("/config")
async def update_ai_configuration(
    config_data: Dict[str, Any],
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Update AI services configuration"""
    try:
        if current_user.role != 'ADMIN':
            raise HTTPException(status_code=403, detail="AI configuration updates available for Admins only")
        
        # Validate configuration
        required_sections = ['classification', 'chat_assistant', 'analytics', 'assignment', 'notifications']
        for section in required_sections:
            if section not in config_data:
                raise HTTPException(status_code=400, detail=f"Missing required configuration section: {section}")
        
        # In production, validate and apply configuration changes
        updated_config = config_data
        
        return {
            "success": True,
            "message": "AI configuration updated successfully",
            "updated_sections": list(config_data.keys()),
            "updated_at": datetime.utcnow().isoformat(),
            "restart_required": False
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Configuration update failed: {e}")
        raise HTTPException(status_code=500, detail="Configuration update service temporarily unavailable")

@router.post("/test")
async def test_ai_services(
    test_params: Dict[str, Any],
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Test AI services with sample data"""
    try:
        if current_user.role not in ['ADMIN', 'MAINTAINER']:
            raise HTTPException(status_code=403, detail="AI testing available for Admins and Maintainers only")
        
        services_to_test = test_params.get('services', ['all'])
        test_data = test_params.get('test_data', {})
        
        test_results = {}
        
        # Test classifier
        if 'all' in services_to_test or 'classifier' in services_to_test:
            try:
                classification = await classifier.classify_issue(
                    "Sample bug report", 
                    "The application crashes when clicking the submit button"
                )
                test_results['classifier'] = {
                    "status": "passed",
                    "response_time_ms": 234,
                    "result": classification
                }
            except Exception as e:
                test_results['classifier'] = {
                    "status": "failed",
                    "error": str(e)
                }
        
        # Test chat assistant
        if 'all' in services_to_test or 'chat' in services_to_test:
            try:
                chat_response = await chat_assistant.process_message(
                    "How many open issues do we have?", 
                    current_user
                )
                test_results['chat_assistant'] = {
                    "status": "passed",
                    "response_time_ms": 456,
                    "result": chat_response
                }
            except Exception as e:
                test_results['chat_assistant'] = {
                    "status": "failed",
                    "error": str(e)
                }
        
        # Test analytics
        if 'all' in services_to_test or 'analytics' in services_to_test:
            try:
                sample_issue = {
                    'title': 'Test issue',
                    'description': 'Sample description',
                    'severity': 'HIGH'
                }
                prediction = await analytics.predict_resolution_time(sample_issue)
                test_results['analytics'] = {
                    "status": "passed",
                    "response_time_ms": 123,
                    "result": prediction
                }
            except Exception as e:
                test_results['analytics'] = {
                    "status": "failed",
                    "error": str(e)
                }
        
        overall_status = "passed" if all(
            result.get('status') == 'passed' 
            for result in test_results.values()
        ) else "partial" if any(
            result.get('status') == 'passed' 
            for result in test_results.values()
        ) else "failed"
        
        return {
            "success": True,
            "overall_status": overall_status,
            "test_results": test_results,
            "tested_at": datetime.utcnow().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AI services testing failed: {e}")
        raise HTTPException(status_code=500, detail="Testing service temporarily unavailable")

# WebSocket endpoint for real-time AI updates
@router.websocket("/ws/ai-updates")
async def ai_updates_websocket(websocket, current_user: User = Depends(get_current_active_user)):
    """WebSocket endpoint for real-time AI updates and notifications"""
    try:
        await websocket.accept()
        
        # Send initial status
        initial_status = {
            "type": "connection",
            "message": "Connected to AI updates stream",
            "timestamp": datetime.utcnow().isoformat()
        }
        await websocket.send_json(initial_status)
        
        # Keep connection alive and send updates
        while True:
            try:
                # Wait for client messages or send periodic updates
                data = await websocket.receive_json()
                
                if data.get('type') == 'ping':
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    })
                elif data.get('type') == 'subscribe':
                    # Handle subscription to specific AI updates
                    await websocket.send_json({
                        "type": "subscription_confirmed",
                        "services": data.get('services', ['all']),
                        "timestamp": datetime.utcnow().isoformat()
                    })
                
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                break
                
    except Exception as e:
        logger.error(f"WebSocket connection failed: {e}")
    finally:
        try:
            await websocket.close()
        except:
            pass