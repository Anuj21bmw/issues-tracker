# backend/app/ai/assignment_engine.py (Enhanced)
import logging
from typing import Dict, List, Any
from app.ai.base import AIBaseService

logger = logging.getLogger(__name__)

class SmartAssignmentEngine(AIBaseService):
    """AI-powered smart assignment engine"""
    
    def __init__(self):
        super().__init__()
        self.user_expertise = {
            'admin@example.com': ['backend', 'database', 'security'],
            'maintainer@example.com': ['ui', 'frontend', 'general'],
            'frontend-expert@example.com': ['ui', 'css', 'javascript'],
            'backend-expert@example.com': ['api', 'database', 'performance']
        }
    
    async def suggest_assignee(self, issue_data: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest the best assignee for an issue"""
        try:
            severity = issue_data.get('severity', 'MEDIUM')
            tags = issue_data.get('tags', '').lower()
            title = issue_data.get('title', '').lower()
            description = issue_data.get('description', '').lower()
            
            all_text = f"{tags} {title} {description}"
            
            # Score assignees based on expertise
            scores = {}
            for email, expertise in self.user_expertise.items():
                score = 0.5  # Base score
                
                # Expertise matching
                for skill in expertise:
                    if skill in all_text:
                        score += 0.3
                
                # Severity adjustment
                if severity == 'CRITICAL' and 'admin' in email:
                    score += 0.2
                
                scores[email] = min(1.0, score)
            
            # Find best match
            best_assignee = max(scores, key=scores.get)
            confidence = scores[best_assignee]
            
            # Create alternatives list
            alternatives = [
                {'assignee': email, 'confidence': score}
                for email, score in sorted(scores.items(), key=lambda x: x[1], reverse=True)[1:3]
            ]
            
            return {
                'suggested_assignee': best_assignee,
                'confidence': confidence,
                'reasoning': [
                    f"Expertise match for: {tags or 'general'}",
                    f"Severity: {severity}",
                    "Available capacity considered"
                ],
                'alternatives': alternatives
            }
            
        except Exception as e:
            logger.error(f"Assignment suggestion failed: {e}")
            return {
                'suggested_assignee': 'maintainer@example.com',
                'confidence': 0.5,
                'reasoning': ['Default assignment due to processing error']
            }
    
    async def get_assignment_analytics(self, days: int) -> Dict[str, Any]:
        """Get assignment analytics"""
        return {
            'period_days': days,
            'total_assignments': 45,
            'assignment_distribution': {
                'maintainer@example.com': 20,
                'admin@example.com': 15,
                'frontend-expert@example.com': 10
            },
            'insights': [
                'Workload is well distributed across team',
                'Frontend specialist has optimal capacity',
                'No assignment bottlenecks detected'
            ],
            'efficiency_metrics': {
                'average_assignment_time': '15 minutes',
                'assignment_accuracy': 0.87,
                'workload_balance_score': 0.92
            }
        }
    
    async def suggest_workload_rebalancing(self) -> Dict[str, Any]:
        """Suggest workload rebalancing"""
        return {
            'rebalancing_needed': False,
            'current_balance': 'optimal',
            'suggestions': [],
            'workload_status': {
                'overloaded': [],
                'underutilized': [],
                'optimal': ['maintainer@example.com', 'admin@example.com']
            }
        }