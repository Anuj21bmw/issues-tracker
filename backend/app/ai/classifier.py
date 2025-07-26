# backend/app/ai/classifier.py
import logging
from typing import Dict, Any, List
from app.ai.base import AIBaseService

logger = logging.getLogger(__name__)

class IssueClassifier(AIBaseService):
    """AI-powered issue classifier"""
    
    def __init__(self):
        super().__init__()
        self.categories = {
            'bug': ['error', 'crash', 'broken', 'not working', 'fails', 'exception'],
            'feature': ['enhancement', 'new', 'add', 'feature', 'improve'],
            'ui': ['interface', 'design', 'layout', 'visual', 'display'],
            'performance': ['slow', 'timeout', 'lag', 'performance', 'speed'],
            'security': ['security', 'vulnerability', 'authentication', 'authorization']
        }
    
    async def classify_issue(self, title: str, description: str) -> Dict[str, Any]:
        """Classify an issue based on title and description"""
        try:
            text = f"{title} {description}".lower()
            
            # Determine severity
            severity = 'LOW'
            if any(word in text for word in ['critical', 'urgent', 'crash', 'down', 'broken']):
                severity = 'CRITICAL'
            elif any(word in text for word in ['important', 'high', 'major', 'serious']):
                severity = 'HIGH'
            elif any(word in text for word in ['medium', 'moderate', 'normal']):
                severity = 'MEDIUM'
            
            # Suggest tags
            suggested_tags = []
            for category, keywords in self.categories.items():
                if any(keyword in text for keyword in keywords):
                    suggested_tags.append(category)
            
            # Default tags if none found
            if not suggested_tags:
                suggested_tags = ['general']
            
            # Confidence score
            confidence = 0.8 if suggested_tags else 0.5
            
            return {
                'suggested_severity': severity,
                'suggested_tags': suggested_tags,
                'confidence': confidence,
                'reasoning': f"Classified based on keywords: {', '.join(suggested_tags)}"
            }
            
        except Exception as e:
            logger.error(f"Classification failed: {e}")
            return {
                'suggested_severity': 'MEDIUM',
                'suggested_tags': ['general'],
                'confidence': 0.3,
                'reasoning': 'Default classification due to processing error'
            }
    
    async def batch_classify_issues(self, issues_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Classify multiple issues in batch"""
        results = []
        for issue in issues_data:
            classification = await self.classify_issue(
                issue.get('title', ''),
                issue.get('description', '')
            )
            results.append({
                'issue_id': issue.get('id'),
                'classification': classification
            })
        return results
