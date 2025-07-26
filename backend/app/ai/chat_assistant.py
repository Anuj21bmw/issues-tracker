# backend/app/ai/chat_assistant.py (Simplified)
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from app.ai.base import AIBaseService
from app.models import Issue, User, IssueStatus, IssueSeverity

logger = logging.getLogger(__name__)

class ChatAssistant(AIBaseService):
    """AI-powered chat assistant for issue management queries"""
    
    def __init__(self):
        super().__init__()
        self.conversation_memory = {}
        logger.info("ChatAssistant initialized successfully")
    
    async def process_message(
        self, 
        message: str, 
        user: User, 
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process user message and return AI response"""
        try:
            # Normalize message
            message = message.lower().strip()
            
            # Simple response generation
            if any(word in message for word in ['help', 'what can you do']):
                return {
                    "message": "I can help you with issue management tasks like counting issues, showing recent issues, and providing statistics.",
                    "type": "info",
                    "suggestions": [
                        "How many issues do we have?",
                        "Show recent issues",
                        "What are my issues?"
                    ]
                }
            
            elif any(word in message for word in ['count', 'how many', 'number of']):
                return await self._get_issue_count(user)
            
            elif any(word in message for word in ['recent', 'latest']):
                return await self._get_recent_issues(user)
            
            else:
                return {
                    "message": "I can help you with various issue management tasks. Try asking 'How many issues do we have?' or 'Show recent issues'.",
                    "type": "info",
                    "suggestions": [
                        "How many issues do we have?",
                        "Show recent issues",
                        "Help"
                    ]
                }
            
        except Exception as e:
            logger.error(f"Chat processing failed: {e}")
            return {
                "message": "I'm having trouble processing your request. Please try again.",
                "type": "error",
                "suggestions": ["Try rephrasing your question"]
            }
    
    async def _get_issue_count(self, user: User) -> Dict[str, Any]:
        """Get total issue count"""
        try:
            db = self.get_db()
            
            if user.role == 'REPORTER':
                total = db.query(Issue).filter(Issue.reporter_id == user.id).count()
                message = f"You have {total} issues."
            else:
                total = db.query(Issue).count()
                message = f"There are {total} total issues in the system."
            
            db.close()
            
            return {
                "message": message,
                "type": "info",
                "data": {"total_issues": total}
            }
            
        except Exception as e:
            logger.error(f"Get issue count failed: {e}")
            return {
                "message": "Unable to retrieve issue count at the moment.",
                "type": "error"
            }
    
    async def _get_recent_issues(self, user: User, limit: int = 5) -> Dict[str, Any]:
        """Get recent issues"""
        try:
            db = self.get_db()
            
            query = db.query(Issue).order_by(Issue.created_at.desc())
            
            if user.role == 'REPORTER':
                query = query.filter(Issue.reporter_id == user.id)
            
            recent_issues = query.limit(limit).all()
            db.close()
            
            if not recent_issues:
                return {
                    "message": "No recent issues found.",
                    "type": "info"
                }
            
            issues_text = []
            for issue in recent_issues:
                status_emoji = "🔴" if issue.status == IssueStatus.OPEN else "✅"
                issues_text.append(f"{status_emoji} #{issue.id}: {issue.title}")
            
            message = f"Here are the {len(recent_issues)} most recent issues:\n" + "\n".join(issues_text)
            
            return {
                "message": message,
                "type": "info",
                "data": {
                    "issues": [
                        {
                            "id": issue.id,
                            "title": issue.title,
                            "status": issue.status.value,
                            "created_at": issue.created_at.isoformat()
                        }
                        for issue in recent_issues
                    ]
                }
            }
            
        except Exception as e:
            logger.error(f"Get recent issues failed: {e}")
            return {
                "message": "Unable to retrieve recent issues at the moment.",
                "type": "error"
            }