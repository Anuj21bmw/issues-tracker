# backend/app/ai/classifier.py
import re
import logging
from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy import func
from app.ai.base import AIBaseService
from app.models import Issue, IssueSeverity, User

logger = logging.getLogger(__name__)

class IssueClassifier(AIBaseService):
    """AI-powered issue classification and analysis"""
    
    def __init__(self):
        super().__init__()
        self.severity_patterns = {
            'CRITICAL': [
                r'\b(crash|crashes|crashing|down|outage|offline|dead|fatal|emergency)\b',
                r'\b(production|live|prod)\s+(down|broken|fail)',
                r'\b(system|server|database|db)\s+(down|crash|fail)',
                r'\b(urgent|asap|immediately|critical|emergency)\b'
            ],
            'HIGH': [
                r'\b(error|exception|broken|fail|bug|issue)\b',
                r'\b(not working|doesn\'t work|can\'t|cannot)\b',
                r'\b(major|serious|important|significant)\b',
                r'\b(security|vulnerability|breach)\b'
            ],
            'MEDIUM': [
                r'\b(slow|performance|lag|delay|timeout)\b',
                r'\b(improvement|enhance|optimize)\b',
                r'\b(ui|interface|design|layout)\b',
                r'\b(minor|small|little)\b'
            ],
            'LOW': [
                r'\b(suggestion|idea|request|feature)\b',
                r'\b(nice to have|would be good|consider)\b',
                r'\b(cosmetic|style|appearance)\b',
                r'\b(documentation|docs|help|guide)\b'
            ]
        }
        
        self.tech_tags = {
            'frontend': ['react', 'vue', 'angular', 'javascript', 'js', 'css', 'html', 'ui', 'interface'],
            'backend': ['api', 'server', 'database', 'db', 'sql', 'python', 'java', 'node'],
            'mobile': ['ios', 'android', 'mobile', 'app', 'react native', 'flutter'],
            'performance': ['slow', 'lag', 'memory', 'cpu', 'performance', 'optimization'],
            'security': ['security', 'auth', 'login', 'password', 'vulnerability', 'breach'],
            'bug': ['error', 'exception', 'crash', 'bug', 'broken', 'fail'],
            'feature': ['feature', 'enhancement', 'improvement', 'request', 'suggestion'],
            'documentation': ['docs', 'documentation', 'help', 'guide', 'readme']
        }
    
    async def classify_issue(self, title: str, description: str) -> Dict:
        """Main classification method that analyzes an issue"""
        cache_key = f"classify:{hash(title + description)}"
        cached = self.get_cached_result(cache_key)
        if cached:
            return cached
        
        text = f"{title} {description}".lower()
        
        # Classify severity
        severity = self._classify_severity(text)
        
        # Suggest tags
        tags = self._suggest_tags(text)
        
        # Predict resolution time
        estimated_time = self._predict_resolution_time(severity, tags)
        
        # Find similar issues
        similar_issues = await self._find_similar_issues(title, description)
        
        # Get AI insights
        ai_insights = await self._get_ai_insights(title, description, severity)
        
        result = {
            'suggested_severity': severity,
            'suggested_tags': tags,
            'estimated_resolution_hours': estimated_time,
            'similar_issues': similar_issues,
            'ai_insights': ai_insights,
            'confidence_score': self._calculate_confidence(text, severity, tags),
            'analysis_timestamp': datetime.utcnow().isoformat()
        }
        
        # Cache result for 1 hour
        self.cache_result(cache_key, result, 3600)
        return result
    
    def _classify_severity(self, text: str) -> str:
        """Classify issue severity based on patterns and keywords"""
        scores = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        
        for severity, patterns in self.severity_patterns.items():
            for pattern in patterns:
                matches = len(re.findall(pattern, text, re.IGNORECASE))
                scores[severity] += matches
        
        # Find the severity with highest score
        max_score = max(scores.values())
        if max_score == 0:
            return 'MEDIUM'  # Default severity
        
        return max(scores, key=scores.get)
    
    def _suggest_tags(self, text: str) -> List[str]:
        """Suggest relevant tags based on content analysis"""
        suggested = []
        
        for tag, keywords in self.tech_tags.items():
            for keyword in keywords:
                if keyword in text:
                    suggested.append(tag)
                    break
        
        # Add custom extracted keywords
        keywords = self.extract_keywords(text)
        for keyword in keywords[:3]:  # Limit to top 3 extracted keywords
            if len(keyword) > 3 and keyword not in suggested:
                suggested.append(keyword)
        
        return list(set(suggested))[:8]  # Limit to 8 tags max
    
    def _predict_resolution_time(self, severity: str, tags: List[str]) -> int:
        """Predict resolution time based on historical data and complexity"""
        base_hours = {
            'CRITICAL': 4,
            'HIGH': 24,
            'MEDIUM': 72,
            'LOW': 168
        }
        
        estimated = base_hours.get(severity, 72)
        
        # Adjust based on tags
        complexity_modifiers = {
            'backend': 1.3,
            'database': 1.5,
            'security': 1.4,
            'performance': 1.2,
            'frontend': 1.0,
            'documentation': 0.5
        }
        
        modifier = 1.0
        for tag in tags:
            if tag in complexity_modifiers:
                modifier *= complexity_modifiers[tag]
        
        return int(estimated * modifier)
    
    async def _find_similar_issues(self, title: str, description: str, limit: int = 5) -> List[Dict]:
        """Find similar resolved issues for reference"""
        try:
            db = self.get_db()
            
            # Get resolved issues
            resolved_issues = db.query(Issue).filter(
                Issue.status == 'DONE'
            ).order_by(Issue.updated_at.desc()).limit(50).all()
            
            similar = []
            query_text = f"{title} {description}"
            
            for issue in resolved_issues:
                issue_text = f"{issue.title} {issue.description}"
                similarity = self.calculate_text_similarity(query_text, issue_text)
                
                if similarity > 0.3:  # Minimum similarity threshold
                    similar.append({
                        'id': issue.id,
                        'title': issue.title,
                        'similarity_score': round(similarity, 2),
                        'resolution_time_hours': self._calculate_resolution_time(issue),
                        'tags': issue.tags
                    })
            
            # Sort by similarity and return top matches
            similar.sort(key=lambda x: x['similarity_score'], reverse=True)
            return similar[:limit]
            
        except Exception as e:
            logger.error(f"Similar issues search failed: {e}")
            return []
        finally:
            db.close()
    
    async def _get_ai_insights(self, title: str, description: str, severity: str) -> Dict:
        """Get AI-powered insights about the issue"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are an expert software engineering assistant. Analyze issues and provide helpful insights, troubleshooting steps, and recommendations."
                },
                {
                    "role": "user",
                    "content": f"""
                    Analyze this issue:
                    Title: {title}
                    Description: {description}
                    Classified Severity: {severity}
                    
                    Provide:
                    1. Key insights about this issue
                    2. 3-5 troubleshooting steps
                    3. Potential root causes
                    4. Prevention recommendations
                    
                    Keep response concise and actionable.
                    """
                }
            ]
            
            ai_response = await self.call_openai_chat(messages, max_tokens=400)
            
            return {
                'analysis': ai_response,
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"AI insights generation failed: {e}")
            return {
                'analysis': 'AI analysis temporarily unavailable.',
                'generated_at': datetime.utcnow().isoformat()
            }
    
    def _calculate_confidence(self, text: str, severity: str, tags: List[str]) -> float:
        """Calculate confidence score for the classification"""
        confidence = 0.5  # Base confidence
        
        # Increase confidence based on pattern matches
        patterns = self.severity_patterns.get(severity, [])
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                confidence += 0.1
        
        # Increase confidence based on tag matches
        confidence += min(len(tags) * 0.05, 0.3)
        
        # Cap at 0.95
        return min(confidence, 0.95)
    
    def _calculate_resolution_time(self, issue: Issue) -> Optional[int]:
        """Calculate actual resolution time for an issue"""
        if issue.updated_at and issue.created_at:
            delta = issue.updated_at - issue.created_at
            return int(delta.total_seconds() / 3600)  # Convert to hours
        return None

    async def batch_classify_issues(self, issues: List[Dict]) -> List[Dict]:
        """Classify multiple issues in batch for better performance"""
        results = []
        for issue in issues:
            try:
                classification = await self.classify_issue(
                    issue.get('title', ''),
                    issue.get('description', '')
                )
                results.append({
                    'issue_id': issue.get('id'),
                    'classification': classification
                })
            except Exception as e:
                logger.error(f"Batch classification failed for issue {issue.get('id')}: {e}")
                results.append({
                    'issue_id': issue.get('id'),
                    'classification': {'error': str(e)}
                })
        return results