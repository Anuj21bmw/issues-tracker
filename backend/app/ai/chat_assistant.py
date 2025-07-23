# backend/app/ai/chat_assistant.py
import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_
from app.ai.base import AIBaseService
from app.models import Issue, User, IssueStatus, IssueSeverity

logger = logging.getLogger(__name__)

class ChatAssistant(AIBaseService):
    """AI-powered chat assistant for issue management"""
    
    def __init__(self):
        super().__init__()
        self.conversation_context = {}
        
        self.quick_actions = {
            'show_open_issues': self._get_open_issues,
            'show_my_issues': self._get_user_issues,
            'show_critical_issues': self._get_critical_issues,
            'show_recent_issues': self._get_recent_issues,
            'show_team_stats': self._get_team_stats,
            'show_overdue_issues': self._get_overdue_issues
        }
        
        self.intent_patterns = {
            'issue_search': ['show', 'find', 'search', 'get', 'list'],
            'statistics': ['stats', 'statistics', 'metrics', 'report', 'summary'],
            'help': ['help', 'how', 'what', 'explain', 'guide'],
            'assignment': ['assign', 'who should', 'recommend', 'suggest'],
            'prediction': ['predict', 'estimate', 'forecast', 'when'],
            'analysis': ['analyze', 'insights', 'trends', 'patterns']
        }
    
    async def process_message(self, message: str, user: User, conversation_id: str = None) -> Dict:
        """Process user message and generate appropriate response"""
        try:
            # Store conversation context
            if conversation_id:
                self._update_conversation_context(conversation_id, message, user)
            
            # Detect intent
            intent = self._detect_intent(message)
            
            # Check for quick actions first
            quick_response = await self._check_quick_actions(message, user)
            if quick_response:
                return quick_response
            
            # Handle different intents
            if intent == 'issue_search':
                return await self._handle_issue_search(message, user)
            elif intent == 'statistics':
                return await self._handle_statistics_request(message, user)
            elif intent == 'assignment':
                return await self._handle_assignment_request(message, user)
            elif intent == 'prediction':
                return await self._handle_prediction_request(message, user)
            elif intent == 'analysis':
                return await self._handle_analysis_request(message, user)
            elif intent == 'help':
                return self._handle_help_request(message, user)
            else:
                # Fall back to AI chat for complex queries
                return await self._handle_ai_chat(message, user, conversation_id)
        
        except Exception as e:
            logger.error(f"Chat processing failed: {e}")
            return {
                'message': "I'm sorry, I encountered an error processing your request. Please try again.",
                'type': 'error',
                'suggestions': ['Try rephrasing your question', 'Contact support if the issue persists']
            }
    
    def _detect_intent(self, message: str) -> str:
        """Detect user intent from message"""
        message_lower = message.lower()
        
        for intent, patterns in self.intent_patterns.items():
            if any(pattern in message_lower for pattern in patterns):
                return intent
        
        return 'general'
    
    async def _check_quick_actions(self, message: str, user: User) -> Optional[Dict]:
        """Check if message matches any quick actions"""
        message_lower = message.lower()
        
        if any(phrase in message_lower for phrase in ['open issues', 'show open', 'list open']):
            return await self._get_open_issues(user)
        elif any(phrase in message_lower for phrase in ['my issues', 'show my', 'list my']):
            return await self._get_user_issues(user)
        elif any(phrase in message_lower for phrase in ['critical issues', 'show critical', 'urgent']):
            return await self._get_critical_issues(user)
        elif any(phrase in message_lower for phrase in ['recent issues', 'latest issues', 'new issues']):
            return await self._get_recent_issues(user)
        elif any(phrase in message_lower for phrase in ['team stats', 'statistics', 'metrics']):
            return await self._get_team_stats(user)
        elif any(phrase in message_lower for phrase in ['overdue', 'delayed', 'stuck']):
            return await self._get_overdue_issues(user)
        
        return None
    
    async def _get_open_issues(self, user: User) -> Dict:
        """Get open issues for the user"""
        try:
            db = self.get_db()
            
            if user.role == 'REPORTER':
                issues = db.query(Issue).filter(
                    and_(Issue.reporter_id == user.id, Issue.status == IssueStatus.OPEN)
                ).limit(10).all()
            else:
                issues = db.query(Issue).filter(Issue.status == IssueStatus.OPEN).limit(10).all()
            
            if not issues:
                return {
                    'message': "🎉 Great news! There are no open issues right now.",
                    'type': 'success',
                    'data': []
                }
            
            issue_list = []
            for issue in issues:
                issue_list.append({
                    'id': issue.id,
                    'title': issue.title,
                    'severity': issue.severity.value,
                    'created_at': issue.created_at.strftime('%Y-%m-%d %H:%M'),
                    'reporter': issue.reporter.full_name
                })
            
            return {
                'message': f"Found {len(issues)} open issues:",
                'type': 'data',
                'data': issue_list,
                'suggestions': [
                    'Show critical issues',
                    'Show my assigned issues',
                    'Create new issue'
                ]
            }
        
        except Exception as e:
            logger.error(f"Get open issues failed: {e}")
            return {'message': 'Failed to retrieve open issues.', 'type': 'error'}
        finally:
            db.close()
    
    async def _get_user_issues(self, user: User) -> Dict:
        """Get issues assigned to or reported by the user"""
        try:
            db = self.get_db()
            
            # Get issues where user is reporter or assignee
            issues = db.query(Issue).filter(
                or_(
                    Issue.reporter_id == user.id,
                    Issue.assignee_id == user.id
                )
            ).filter(Issue.status != IssueStatus.DONE).limit(15).all()
            
            if not issues:
                return {
                    'message': "You don't have any active issues right now.",
                    'type': 'info',
                    'suggestions': ['Create new issue', 'View all issues', 'Show team stats']
                }
            
            reported = [i for i in issues if i.reporter_id == user.id]
            assigned = [i for i in issues if i.assignee_id == user.id]
            
            message = f"Your active issues:\n"
            if reported:
                message += f"📝 Reported: {len(reported)} issues\n"
            if assigned:
                message += f"👨‍💼 Assigned: {len(assigned)} issues"
            
            issue_list = []
            for issue in issues[:10]:  # Limit display
                issue_list.append({
                    'id': issue.id,
                    'title': issue.title,
                    'severity': issue.severity.value,
                    'status': issue.status.value,
                    'role': 'Reporter' if issue.reporter_id == user.id else 'Assignee'
                })
            
            return {
                'message': message,
                'type': 'data',
                'data': issue_list,
                'suggestions': ['Show high priority', 'Show overdue issues']
            }
        
        except Exception as e:
            logger.error(f"Get user issues failed: {e}")
            return {'message': 'Failed to retrieve your issues.', 'type': 'error'}
        finally:
            db.close()
    
    async def _get_critical_issues(self, user: User) -> Dict:
        """Get critical and high priority issues"""
        try:
            db = self.get_db()
            
            issues = db.query(Issue).filter(
                and_(
                    Issue.severity.in_([IssueSeverity.CRITICAL, IssueSeverity.HIGH]),
                    Issue.status != IssueStatus.DONE
                )
            ).order_by(Issue.created_at.desc()).limit(10).all()
            
            if not issues:
                return {
                    'message': "🎉 No critical or high priority issues found!",
                    'type': 'success'
                }
            
            critical = [i for i in issues if i.severity == IssueSeverity.CRITICAL]
            high = [i for i in issues if i.severity == IssueSeverity.HIGH]
            
            message = f"⚠️ Priority Issues Found:\n"
            if critical:
                message += f"🔴 Critical: {len(critical)} issues\n"
            if high:
                message += f"🟠 High: {len(high)} issues"
            
            issue_list = []
            for issue in issues:
                issue_list.append({
                    'id': issue.id,
                    'title': issue.title,
                    'severity': issue.severity.value,
                    'status': issue.status.value,
                    'age_hours': int((datetime.utcnow() - issue.created_at).total_seconds() / 3600),
                    'assignee': issue.assignee.full_name if issue.assignee else 'Unassigned'
                })
            
            return {
                'message': message,
                'type': 'warning',
                'data': issue_list,
                'suggestions': ['Assign critical issues', 'Show team workload']
            }
        
        except Exception as e:
            logger.error(f"Get critical issues failed: {e}")
            return {'message': 'Failed to retrieve critical issues.', 'type': 'error'}
        finally:
            db.close()
    
    async def _get_team_stats(self, user: User) -> Dict:
        """Get team statistics and metrics"""
        try:
            if user.role == 'REPORTER':
                return {
                    'message': 'Team statistics are available for Maintainers and Admins only.',
                    'type': 'info'
                }
            
            db = self.get_db()
            
            # Basic counts
            total_issues = db.query(Issue).count()
            open_issues = db.query(Issue).filter(Issue.status == IssueStatus.OPEN).count()
            in_progress = db.query(Issue).filter(Issue.status == IssueStatus.IN_PROGRESS).count()
            done_issues = db.query(Issue).filter(Issue.status == IssueStatus.DONE).count()
            
            # Recent activity (last 7 days)
            week_ago = datetime.utcnow() - timedelta(days=7)
            recent_issues = db.query(Issue).filter(Issue.created_at >= week_ago).count()
            
            # Team workload
            team_workload = db.query(
                User.full_name,
                func.count(Issue.id).label('assigned_count')
            ).join(Issue, Issue.assignee_id == User.id)\
             .filter(Issue.status != IssueStatus.DONE)\
             .group_by(User.full_name)\
             .all()
            
            stats_message = f"""📊 Team Statistics:
            
Total Issues: {total_issues}
📝 Open: {open_issues}
🚀 In Progress: {in_progress}  
✅ Completed: {done_issues}
📈 New This Week: {recent_issues}

Active Workload:"""
            
            workload_data = []
            for name, count in team_workload:
                stats_message += f"\n👤 {name}: {count} issues"
                workload_data.append({'name': name, 'active_issues': count})
            
            return {
                'message': stats_message,
                'type': 'data',
                'data': {
                    'total': total_issues,
                    'open': open_issues,
                    'in_progress': in_progress,
                    'done': done_issues,
                    'recent': recent_issues,
                    'workload': workload_data
                },
                'suggestions': ['Show overdue issues', 'Team performance analysis', 'Workload balancing']
            }
        
        except Exception as e:
            logger.error(f"Get team stats failed: {e}")
            return {'message': 'Failed to retrieve team statistics.', 'type': 'error'}
        finally:
            db.close()
    
    async def _handle_ai_chat(self, message: str, user: User, conversation_id: str = None) -> Dict:
        """Handle complex queries with AI chat"""
        try:
            # Get conversation context
            context = self._get_conversation_context(conversation_id) if conversation_id else []
            
            # Build system message with user context
            system_message = f"""You are an intelligent assistant for an issue tracking system. 
            User: {user.full_name} ({user.role})
            
            You can help with:
            - Finding and filtering issues
            - Providing statistics and insights
            - Suggesting assignments and priorities
            - Explaining system features
            - Troubleshooting guidance
            
            Be helpful, concise, and actionable. If you need specific data, suggest they use commands like 'show my issues' or 'team stats'."""
            
            messages = [{"role": "system", "content": system_message}]
            
            # Add conversation history
            for ctx_msg in context[-5:]:  # Last 5 messages for context
                messages.append(ctx_msg)
            
            messages.append({"role": "user", "content": message})
            
            ai_response = await self.call_openai_chat(messages, max_tokens=300)
            
            return {
                'message': ai_response,
                'type': 'ai_response',
                'suggestions': self._generate_context_suggestions(message, user)
            }
        
        except Exception as e:
            logger.error(f"AI chat failed: {e}")
            return {
                'message': "I'm having trouble processing your request right now. Try asking for specific information like 'show my issues' or 'team stats'.",
                'type': 'error',
                'suggestions': ['Show my issues', 'Show open issues', 'Team stats']
            }
    
    def _generate_context_suggestions(self, message: str, user: User) -> List[str]:
        """Generate contextual suggestions based on user message and role"""
        base_suggestions = ['Show my issues', 'Show open issues', 'Help']
        
        if user.role in ['ADMIN', 'MAINTAINER']:
            base_suggestions.extend(['Team stats', 'Critical issues', 'Overdue issues'])
        
        message_lower = message.lower()
        if 'assign' in message_lower:
            base_suggestions.append('Show unassigned issues')
        elif 'critical' in message_lower or 'urgent' in message_lower:
            base_suggestions.append('Show critical issues')
        elif 'performance' in message_lower or 'stats' in message_lower:
            base_suggestions.append('Team performance')
        
        return base_suggestions[:5]  # Limit to 5 suggestions
    
    def _update_conversation_context(self, conversation_id: str, message: str, user: User):
        """Update conversation context for better AI responses"""
        if conversation_id not in self.conversation_context:
            self.conversation_context[conversation_id] = []
        
        self.conversation_context[conversation_id].append({
            'role': 'user',
            'content': message,
            'timestamp': datetime.utcnow(),
            'user_id': user.id
        })
        
        # Keep only last 10 messages per conversation
        if len(self.conversation_context[conversation_id]) > 10:
            self.conversation_context[conversation_id] = self.conversation_context[conversation_id][-10:]
    
    def _get_conversation_context(self, conversation_id: str) -> List[Dict]:
        """Get conversation context for AI chat"""
        return self.conversation_context.get(conversation_id, [])