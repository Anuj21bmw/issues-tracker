# backend/app/ai/classifier.py (Simplified)
import logging
from typing import Dict, List, Any
from app.ai.base import AIBaseService

logger = logging.getLogger(__name__)

class IssueClassifier(AIBaseService):
    """AI-powered issue classification service"""
    
    def __init__(self):
        super().__init__()
        self.severity_keywords = {
            'CRITICAL': ['crash', 'down', 'broken', 'error', 'fatal', 'urgent'],
            'HIGH': ['bug', 'issue', 'problem', 'fail', 'not working'],
            'MEDIUM': ['improve', 'enhance', 'slow', 'performance'],
            'LOW': ['cosmetic', 'minor', 'typo', 'suggestion']
        }
    
    async def classify_issue(self, title: str, description: str) -> Dict[str, Any]:
        """Classify issue and suggest severity/tags"""
        try:
            text = f"{title} {description}".lower()
            
            # Simple keyword-based classification
            severity_scores = {}
            for severity, keywords in self.severity_keywords.items():
                score = sum(1 for keyword in keywords if keyword in text)
                severity_scores[severity] = score
            
            suggested_severity = max(severity_scores, key=severity_scores.get)
            if severity_scores[suggested_severity] == 0:
                suggested_severity = 'MEDIUM'
            
            confidence = min(severity_scores[suggested_severity] / 3.0, 1.0)
            
            return {
                'suggested_severity': suggested_severity,
                'confidence': confidence,
                'suggested_tags': ['general'],
                'reasoning': f"Based on keyword analysis"
            }
            
        except Exception as e:
            logger.error(f"Classification failed: {e}")
            return {
                'suggested_severity': 'MEDIUM',
                'confidence': 0.5,
                'suggested_tags': [],
                'reasoning': 'Default classification'
            }
    
    async def batch_classify_issues(self, issues_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Batch classify multiple issues"""
        results = []
        for issue_data in issues_data:
            classification = await self.classify_issue(
                issue_data.get('title', ''),
                issue_data.get('description', '')
            )
            results.append({
                'issue_id': issue_data.get('id'),
                'classification': classification
            })
        return results