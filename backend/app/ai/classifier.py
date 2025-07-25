# backend/app/ai/classifier.py - Complete AI Issue Classifier
import logging
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from app.ai.base import AIBaseService
from app.models import Issue, IssueSeverity

logger = logging.getLogger(__name__)

class IssueClassifier(AIBaseService):
    """AI-powered issue classification system"""
    
    def __init__(self):
        super().__init__()
        
        # Severity classification patterns
        self.severity_patterns = {
            'CRITICAL': [
                'crash', 'down', 'broken', 'fails', 'error 500', 'production', 
                'urgent', 'critical', 'blocker', 'cannot', 'unable', 'dead',
                'outage', 'security breach', 'data loss', 'corruption'
            ],
            'HIGH': [
                'bug', 'issue', 'problem', 'incorrect', 'wrong', 'missing',
                'slow', 'performance', 'timeout', 'error', 'exception',
                'important', 'high priority', 'blocker'
            ],
            'MEDIUM': [
                'improvement', 'enhance', 'optimize', 'update', 'modify',
                'feature request', 'suggestion', 'nice to have'
            ],
            'LOW': [
                'typo', 'spelling', 'cosmetic', 'minor', 'cleanup',
                'documentation', 'comment', 'formatting'
            ]
        }
        
        # Category classification patterns
        self.category_patterns = {
            'bug': ['bug', 'error', 'issue', 'problem', 'broken', 'fail', 'crash'],
            'feature': ['feature', 'enhancement', 'new', 'add', 'implement'],
            'performance': ['slow', 'performance', 'optimize', 'speed', 'memory'],
            'ui': ['ui', 'interface', 'design', 'layout', 'css', 'styling'],
            'security': ['security', 'vulnerability', 'auth', 'permission', 'access'],
            'documentation': ['docs', 'documentation', 'readme', 'guide', 'manual'],
            'test': ['test', 'testing', 'qa', 'verification', 'validation']
        }
        
        # Technology classification patterns
        self.tech_patterns = {
            'frontend': ['react', 'vue', 'angular', 'javascript', 'css', 'html', 'ui', 'svelte'],
            'backend': ['api', 'server', 'database', 'python', 'node', 'fastapi', 'django'],
            'mobile': ['ios', 'android', 'mobile', 'app', 'flutter', 'react native'],
            'devops': ['docker', 'kubernetes', 'deployment', 'ci/cd', 'pipeline'],
            'database': ['sql', 'mysql', 'postgresql', 'mongodb', 'query', 'schema']
        }
    
    async def classify_issue(self, title: str, description: str) -> Dict[str, Any]:
        """Classify an issue's severity, category, and suggested tags"""
        try:
            combined_text = f"{title} {description}".lower()
            
            # Get AI-powered classification
            ai_classification = await self._get_ai_classification(title, description)
            
            # Get rule-based classification as fallback
            rule_classification = self._get_rule_based_classification(combined_text)
            
            # Combine AI and rule-based results
            final_classification = self._combine_classifications(ai_classification, rule_classification)
            
            # Extract additional insights
            final_classification.update({
                'confidence': self._calculate_confidence(combined_text, final_classification),
                'suggested_tags': self._suggest_tags(combined_text),
                'estimated_complexity': self._estimate_complexity(combined_text),
                'classification_timestamp': datetime.utcnow().isoformat()
            })
            
            self.log_ai_operation('classify_issue', True, {
                'severity': final_classification['severity'],
                'category': final_classification['category']
            })
            
            return final_classification
            
        except Exception as e:
            logger.error(f"Issue classification failed: {e}")
            self.log_ai_operation('classify_issue', False, {'error': str(e)})
            
            # Return safe fallback classification
            return {
                'severity': 'MEDIUM',
                'category': 'general',
                'technology': 'unknown',
                'confidence': 0.3,
                'suggested_tags': ['needs-review'],
                'estimated_complexity': 'medium',
                'classification_timestamp': datetime.utcnow().isoformat()
            }
    
    async def _get_ai_classification(self, title: str, description: str) -> Dict[str, str]:
        """Get AI-powered classification using language model"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": """You are an expert issue classifier. Analyze the issue and respond with ONLY a JSON object containing:
{
  "severity": "LOW|MEDIUM|HIGH|CRITICAL",
  "category": "bug|feature|performance|ui|security|documentation|test|other",
  "technology": "frontend|backend|mobile|devops|database|general"
}

Classification criteria:
- CRITICAL: System down, data loss, security breach, production outage
- HIGH: Major functionality broken, significant user impact
- MEDIUM: Minor bugs, feature requests, improvements  
- LOW: Cosmetic issues, typos, minor cleanup

Respond with ONLY the JSON object, no additional text."""
                },
                {
                    "role": "user", 
                    "content": f"Title: {title}\nDescription: {description}"
                }
            ]
            
            ai_response = await self.call_openai_chat(messages, max_tokens=100, temperature=0.3)
            
            # Try to parse JSON response
            import json
            try:
                return json.loads(ai_response)
            except json.JSONDecodeError:
                # Fallback parsing
                return self._parse_ai_response_fallback(ai_response)
                
        except Exception as e:
            logger.error(f"AI classification failed: {e}")
            return {}
    
    def _parse_ai_response_fallback(self, response: str) -> Dict[str, str]:
        """Parse AI response when JSON parsing fails"""
        result = {}
        response_lower = response.lower()
        
        # Extract severity
        for severity in ['critical', 'high', 'medium', 'low']:
            if severity in response_lower:
                result['severity'] = severity.upper()
                break
        
        # Extract category
        for category in ['bug', 'feature', 'performance', 'ui', 'security', 'documentation', 'test']:
            if category in response_lower:
                result['category'] = category
                break
        
        # Extract technology
        for tech in ['frontend', 'backend', 'mobile', 'devops', 'database']:
            if tech in response_lower:
                result['technology'] = tech
                break
        
        return result
    
    def _get_rule_based_classification(self, text: str) -> Dict[str, str]:
        """Get classification using pattern matching rules"""
        classification = {}
        
        # Classify severity
        severity_scores = {}
        for severity, patterns in self.severity_patterns.items():
            score = sum(1 for pattern in patterns if pattern in text)
            if score > 0:
                severity_scores[severity] = score
        
        if severity_scores:
            classification['severity'] = max(severity_scores, key=severity_scores.get)
        else:
            classification['severity'] = 'MEDIUM'
        
        # Classify category
        category_scores = {}
        for category, patterns in self.category_patterns.items():
            score = sum(1 for pattern in patterns if pattern in text)
            if score > 0:
                category_scores[category] = score
        
        if category_scores:
            classification['category'] = max(category_scores, key=category_scores.get)
        else:
            classification['category'] = 'general'
        
        # Classify technology
        tech_scores = {}
        for tech, patterns in self.tech_patterns.items():
            score = sum(1 for pattern in patterns if pattern in text)
            if score > 0:
                tech_scores[tech] = score
        
        if tech_scores:
            classification['technology'] = max(tech_scores, key=tech_scores.get)
        else:
            classification['technology'] = 'general'
        
        return classification
    
    def _combine_classifications(self, ai_result: Dict, rule_result: Dict) -> Dict[str, str]:
        """Combine AI and rule-based classifications"""
        combined = {}
        
        # Prefer AI results, fallback to rules
        combined['severity'] = ai_result.get('severity', rule_result.get('severity', 'MEDIUM'))
        combined['category'] = ai_result.get('category', rule_result.get('category', 'general'))
        combined['technology'] = ai_result.get('technology', rule_result.get('technology', 'general'))
        
        return combined
    
    def _calculate_confidence(self, text: str, classification: Dict) -> float:
        """Calculate confidence score for classification"""
        confidence = 0.5  # Base confidence
        
        # Increase confidence based on pattern matches
        severity = classification.get('severity', '').upper()
        if severity in self.severity_patterns:
            patterns = self.severity_patterns[severity]
            matches = sum(1 for pattern in patterns if pattern in text)
            confidence += min(0.3, matches * 0.1)
        
        # Increase confidence for clear technical terms
        tech_terms = ['api', 'database', 'frontend', 'backend', 'server', 'client']
        tech_matches = sum(1 for term in tech_terms if term in text)
        confidence += min(0.2, tech_matches * 0.05)
        
        return min(0.95, confidence)
    
    def _suggest_tags(self, text: str) -> List[str]:
        """Suggest relevant tags based on content analysis"""
        tags = []
        
        # Technology tags
        for tech, patterns in self.tech_patterns.items():
            if any(pattern in text for pattern in patterns):
                tags.append(tech)
        
        # Severity indicator tags
        if any(word in text for word in ['urgent', 'critical', 'blocker']):
            tags.append('urgent')
        
        if any(word in text for word in ['security', 'vulnerability', 'breach']):
            tags.append('security')
        
        if any(word in text for word in ['performance', 'slow', 'timeout']):
            tags.append('performance')
        
        if any(word in text for word in ['ui', 'interface', 'design']):
            tags.append('ui')
        
        # Environment tags
        if any(word in text for word in ['production', 'prod', 'live']):
            tags.append('production')
        
        if any(word in text for word in ['test', 'testing', 'qa']):
            tags.append('testing')
        
        return list(set(tags))[:5]  # Limit to 5 unique tags
    
    def _estimate_complexity(self, text: str) -> str:
        """Estimate implementation complexity"""
        complexity_indicators = {
            'high': [
                'architecture', 'redesign', 'refactor', 'migrate', 'complex',
                'multiple systems', 'integration', 'large change'
            ],
            'medium': [
                'new feature', 'enhancement', 'modify', 'update', 'improve'
            ],
            'low': [
                'typo', 'text change', 'color', 'styling', 'minor', 'simple'
            ]
        }
        
        for complexity, indicators in complexity_indicators.items():
            if any(indicator in text for indicator in indicators):
                return complexity
        
        return 'medium'  # Default complexity
    
    async def batch_classify_issues(self, issues_data: List[Dict]) -> List[Dict]:
        """Classify multiple issues in batch"""
        async def classify_single(issue_data):
            return await self.classify_issue(
                issue_data.get('title', ''),
                issue_data.get('description', '')
            )
        
        results = await self.batch_process(issues_data, classify_single, batch_size=5)
        
        # Add batch metadata
        return [{
            'issue_id': issues_data[i].get('id') if i < len(issues_data) else None,
            'classification': result
        } for i, result in enumerate(results)]
    
    async def update_classification_learning(self, issue_id: int, actual_resolution: Dict):
        """Update classification learning based on actual resolution data"""
        try:
            # This could be enhanced to improve classification accuracy over time
            # For now, just log the learning data
            learning_data = {
                'issue_id': issue_id,
                'actual_resolution': actual_resolution,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Classification learning data: {learning_data}")
            
        except Exception as e:
            logger.error(f"Classification learning update failed: {e}")
    
    def get_classification_stats(self) -> Dict[str, Any]:
        """Get classification statistics and performance metrics"""
        return {
            'service_status': 'active',
            'pattern_categories': len(self.category_patterns),
            'technology_patterns': len(self.tech_patterns),
            'severity_levels': len(self.severity_patterns),
            'last_updated': datetime.utcnow().isoformat()
        }