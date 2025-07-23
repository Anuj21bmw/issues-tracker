# backend/app/ai/assignment_engine.py
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy import func, and_
from app.ai.base import AIBaseService
from app.models import Issue, User, UserRole, IssueStatus, IssueSeverity

logger = logging.getLogger(__name__)

class SmartAssignmentEngine(AIBaseService):
    """AI-powered intelligent issue assignment system"""
    
    def __init__(self):
        super().__init__()
        self.expertise_weights = {
            'frontend': ['react', 'vue', 'angular', 'javascript', 'css', 'html', 'ui'],
            'backend': ['api', 'server', 'database', 'python', 'java', 'node'],
            'mobile': ['ios', 'android', 'react native', 'flutter', 'mobile'],
            'devops': ['docker', 'kubernetes', 'aws', 'deploy', 'ci/cd'],
            'security': ['security', 'auth', 'vulnerability', 'breach'],
            'performance': ['performance', 'optimization', 'slow', 'memory'],
            'database': ['sql', 'mysql', 'postgresql', 'mongodb', 'query']
        }
    
    async def suggest_assignee(self, issue_data: Dict) -> Dict[str, Any]:
        """Suggest the best assignee for an issue"""
        try:
            db = self.get_db()
            
            # Get available maintainers and admins
            available_users = db.query(User).filter(
                and_(
                    User.role.in_([UserRole.MAINTAINER, UserRole.ADMIN]),
                    User.is_active == True
                )
            ).all()
        except Exception as e:
            logger.error(f"Error while suggesting assignee: {e}")
            return {
                'suggested_assignee': None,
                'reason': 'An error occurred while processing the request',
                'confidence': 0.0,
                'alternatives': []
            }
            
            if not available_users:
                return {
                    'suggested_assignee': None,
                    'reason': 'No available maintainers or admins found',
                    'confidence': 0.0,
                    'alternatives': []
                }
            
            # Calculate assignment scores for each user
            scored_users = []
            for user in available_users:
                score_details = await self._calculate_assignment_score(user, issue_data)
                scored_users.append({
                    'user': {
                        'id': user.id,
                        'name': user.full_name,
                        'email': user.email,
                        'role': user.role.value
                    },
                    'score': score_details['total_score'],
                    'score_breakdown': score_details,
                    'current_workload': self._get_user_workload(user.id),
                    'availability_status': self._assess_availability(user.id)
                })
            
            # Sort by score
            scored_users.sort(key=lambda x: x['score'], reverse=True)
            
            if not scored_users:
                return {
                    'suggested_assignee': None,
                    'reason': 'Unable to calculate assignment scores',
                    'confidence': 0.0,
                    'alternatives': []
                }
            
            best_candidate = scored_users[0] if scored_users else None
            
            return {
                'suggested_assignee': best_candidate['user'] if best_candidate else None,
                'reason': 'Best candidate selected based on score' if best_candidate else 'No suitable candidate found',
                'confidence': best_candidate['score'] if best_candidate else 0.0,
                'alternatives': scored_users[1:] if len(scored_users) > 1 else []
            }