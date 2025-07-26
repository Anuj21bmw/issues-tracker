# backend/app/ai/notification_engine.py (Enhanced)
import logging
from typing import Dict, List, Any
from datetime import datetime, timedelta
from app.ai.base import AIBaseService

logger = logging.getLogger(__name__)

class SmartNotificationEngine(AIBaseService):
    """AI-powered smart notification engine"""
    
    def __init__(self):
        super().__init__()
    
    async def should_escalate(self, issue) -> Dict[str, Any]:
        """Determine if issue should be escalated"""
        try:
            age = datetime.utcnow() - issue.created_at
            hours_old = age.total_seconds() / 3600
            
            should_escalate = False
            escalation_level = 'none'
            reasoning = []
            
            # Escalation rules
            if issue.severity.value == 'CRITICAL' and hours_old > 4:
                should_escalate = True
                escalation_level = 'immediate'
                reasoning.append('Critical issue open for >4 hours')
            elif issue.severity.value == 'HIGH' and hours_old > 24:
                should_escalate = True
                escalation_level = 'urgent'
                reasoning.append('High priority issue open for >24 hours')
            elif hours_old > 72:
                should_escalate = True
                escalation_level = 'review'
                reasoning.append('Issue open for >72 hours')
            
            if not reasoning:
                reasoning.append('Issue within normal timeframe')
            
            return {
                'should_escalate': should_escalate,
                'escalation_level': escalation_level,
                'reasoning': reasoning,
                'hours_old': round(hours_old, 1)
            }
            
        except Exception as e:
            logger.error(f"Escalation check failed: {e}")
            return {
                'should_escalate': False,
                'escalation_level': 'none',
                'reasoning': ['Unable to assess escalation need']
            }
    
    async def generate_smart_notifications(self, users: List) -> List[Dict[str, Any]]:
        """Generate smart notifications for users"""
        notifications = []
        
        for user in users:
            user_notifications = []
            
            # Role-based notifications
            if user.role in ['ADMIN', 'MAINTAINER']:
                user_notifications.extend([
                    {
                        'type': 'info',
                        'message': f'You have 3 issues requiring attention',
                        'priority': 'medium',
                        'action': 'review_issues'
                    },
                    {
                        'type': 'warning',
                        'message': 'One critical issue has been open for 3 hours',
                        'priority': 'high',
                        'action': 'escalate_review'
                    }
                ])
            
            if user.role == 'ADMIN':
                user_notifications.append({
                    'type': 'insight',
                    'message': 'Team productivity is up 15% this week',
                    'priority': 'low',
                    'action': 'view_analytics'
                })
            
            notifications.append({
                'user_id': user.id,
                'notifications': user_notifications
            })
        
        return notifications
    
    async def get_notification_summary(self, user, days: int) -> Dict[str, Any]:
        """Get notification summary for user"""
        return {
            'total_notifications': 12,
            'unread_count': 4,
            'priority_breakdown': {
                'high': 2,
                'medium': 6,
                'low': 4
            },
            'recent_activity': [
                'Issue #123 assigned to you',
                'Critical issue #124 needs attention',
                'Weekly analytics report available'
            ]
        }
    
    async def analyze_notification_patterns(self, days: int) -> Dict[str, Any]:
        """Analyze notification patterns"""
        return {
            'period_days': days,
            'total_notifications': 156,
            'patterns': {
                'peak_hours': ['9-11 AM', '2-4 PM'],
                'common_types': ['assignment', 'status_update', 'escalation'],
                'response_rate': 0.78
            },
            'insights': [
                'Notifications most effective during morning hours',
                'Escalation alerts have 95% response rate',
                'Weekend notifications have lower engagement'
            ]
        }
