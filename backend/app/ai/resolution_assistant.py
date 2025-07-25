# backend/app/ai/resolution_assistant.py - Complete AI Resolution Assistant
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import func, and_
from app.ai.base import AIBaseService
from app.models import Issue, User, IssueStatus, IssueSeverity

logger = logging.getLogger(__name__)

class ResolutionAssistant(AIBaseService):
    """AI-powered resolution assistance and guidance system"""
    
    def __init__(self):
        super().__init__()
        
        # Knowledge base of common solutions
        self.solution_templates = {
            'frontend': {
                'ui_bugs': [
                    "Check CSS styles and responsive design",
                    "Verify browser compatibility", 
                    "Test with different screen sizes",
                    "Review JavaScript console for errors"
                ],
                'performance': [
                    "Optimize images and assets",
                    "Minimize JavaScript bundles",
                    "Implement lazy loading",
                    "Review network requests"
                ]
            },
            'backend': {
                'api_errors': [
                    "Check server logs for error details",
                    "Verify database connections",
                    "Review API endpoint configuration",
                    "Test with API client tools"
                ],
                'performance': [
                    "Optimize database queries",
                    "Review caching strategy",
                    "Check server resource usage",
                    "Profile slow endpoints"
                ]
            },
            'database': {
                'connection_issues': [
                    "Verify database server status",
                    "Check connection string configuration",
                    "Review network connectivity",
                    "Validate user permissions"
                ],
                'performance': [
                    "Analyze slow query logs",
                    "Review and optimize indexes",
                    "Check table statistics",
                    "Consider query optimization"
                ]
            }
        }
        
        # Common troubleshooting steps by issue type
        self.troubleshooting_steps = {
            'bug': [
                "Reproduce the issue consistently",
                "Check recent code changes",
                "Review error logs and stack traces",
                "Test in different environments",
                "Verify data integrity"
            ],
            'performance': [
                "Measure current performance metrics",
                "Identify bottlenecks using profiling",
                "Review system resource usage",
                "Test with realistic data volumes",
                "Compare against performance benchmarks"
            ],
            'security': [
                "Assess the security impact",
                "Review access controls and permissions",
                "Check for data exposure",
                "Update security configurations",
                "Document the vulnerability"
            ]
        }
    
    async def suggest_resolution_steps(self, issue: Issue) -> Dict[str, Any]:
        """Generate AI-powered resolution suggestions for an issue"""
        try:
            # Get AI-powered suggestions
            ai_suggestions = await self._get_ai_resolution_suggestions(issue)
            
            # Get template-based suggestions
            template_suggestions = self._get_template_suggestions(issue)
            
            # Get similar issue analysis
            similar_issues = await self._find_similar_resolved_issues(issue)
            
            # Combine all suggestions
            resolution_plan = {
                'immediate_steps': ai_suggestions.get('immediate_steps', template_suggestions['immediate']),
                'investigation_steps': ai_suggestions.get('investigation_steps', template_suggestions['investigation']),
                'resolution_options': ai_suggestions.get('resolution_options', []),
                'preventive_measures': ai_suggestions.get('preventive_measures', []),
                'similar_issues': similar_issues,
                'estimated_effort': self._estimate_resolution_effort(issue),
                'risk_assessment': self._assess_resolution_risk(issue),
                'resources_needed': self._identify_required_resources(issue),
                'generated_at': datetime.utcnow().isoformat()
            }
            
            self.log_ai_operation('suggest_resolution_steps', True, {
                'issue_id': issue.id,
                'suggestions_count': len(resolution_plan['immediate_steps'])
            })
            
            return resolution_plan
            
        except Exception as e:
            logger.error(f"Resolution suggestion failed for issue {issue.id}: {e}")
            self.log_ai_operation('suggest_resolution_steps', False, {'error': str(e)})
            
            # Return basic fallback suggestions
            return {
                'immediate_steps': ["Review issue details", "Assign to appropriate team member"],
                'investigation_steps': ["Gather more information", "Reproduce the issue"],
                'resolution_options': [],
                'preventive_measures': [],
                'similar_issues': [],
                'estimated_effort': 'unknown',
                'risk_assessment': 'medium',
                'resources_needed': [],
                'generated_at': datetime.utcnow().isoformat()
            }
    
    async def _get_ai_resolution_suggestions(self, issue: Issue) -> Dict[str, List[str]]:
        """Get AI-powered resolution suggestions"""
        try:
            issue_context = f"""
Title: {issue.title}
Description: {issue.description}
Severity: {issue.severity}
Tags: {', '.join([tag.name for tag in issue.tags]) if issue.tags else 'None'}
Status: {issue.status}
"""
            
            messages = [
                {
                    "role": "system",
                    "content": """You are an expert technical troubleshooter. Analyze the issue and provide structured resolution guidance.

Respond with a JSON object containing:
{
  "immediate_steps": ["step1", "step2", "step3"],
  "investigation_steps": ["investigate1", "investigate2"],
  "resolution_options": ["option1", "option2"],
  "preventive_measures": ["prevent1", "prevent2"]
}

Keep steps concise and actionable. Focus on the most likely causes and solutions."""
                },
                {
                    "role": "user",
                    "content": f"Provide resolution guidance for this issue:\n{issue_context}"
                }
            ]
            
            ai_response = await self.call_openai_chat(messages, max_tokens=400, temperature=0.5)
            
            import json
            try:
                return json.loads(ai_response)
            except json.JSONDecodeError:
                return self._parse_resolution_response(ai_response)
                
        except Exception as e:
            logger.error(f"AI resolution suggestions failed: {e}")
            return {}
    
    def _parse_resolution_response(self, response: str) -> Dict[str, List[str]]:
        """Parse AI response when JSON fails"""
        lines = response.split('\n')
        suggestions = {
            'immediate_steps': [],
            'investigation_steps': [],
            'resolution_options': [],
            'preventive_measures': []
        }
        
        current_section = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if 'immediate' in line.lower():
                current_section = 'immediate_steps'
            elif 'investigation' in line.lower():
                current_section = 'investigation_steps'
            elif 'resolution' in line.lower() or 'option' in line.lower():
                current_section = 'resolution_options'
            elif 'prevent' in line.lower():
                current_section = 'preventive_measures'
            elif line.startswith('-') or line.startswith('•') or line.startswith('*'):
                if current_section:
                    clean_line = line.lstrip('-•* ').strip()
                    if clean_line:
                        suggestions[current_section].append(clean_line)
        
        return suggestions
    
    def _get_template_suggestions(self, issue: Issue) -> Dict[str, List[str]]:
        """Get template-based suggestions based on issue categorization"""
        suggestions = {
            'immediate': ["Review issue details thoroughly", "Confirm issue reproduction steps"],
            'investigation': ["Check system logs", "Review recent changes"]
        }
        
        # Add category-specific suggestions
        issue_text = f"{issue.title} {issue.description}".lower()
        
        # Detect issue category and technology
        if any(term in issue_text for term in ['ui', 'interface', 'frontend', 'css', 'javascript']):
            suggestions['immediate'].extend(self.solution_templates['frontend']['ui_bugs'])
        elif any(term in issue_text for term in ['api', 'server', 'backend', 'endpoint']):
            suggestions['immediate'].extend(self.solution_templates['backend']['api_errors'])
        elif any(term in issue_text for term in ['database', 'sql', 'query', 'connection']):
            suggestions['immediate'].extend(self.solution_templates['database']['connection_issues'])
        
        # Add issue type specific steps
        if any(term in issue_text for term in ['slow', 'performance', 'timeout']):
            suggestions['investigation'].extend(["Profile performance bottlenecks", "Monitor resource usage"])
        elif any(term in issue_text for term in ['security', 'auth', 'permission']):
            suggestions['investigation'].extend(self.troubleshooting_steps['security'])
        else:
            suggestions['investigation'].extend(self.troubleshooting_steps['bug'])
        
        return suggestions
    
    async def _find_similar_resolved_issues(self, issue: Issue, limit: int = 5) -> List[Dict]:
        """Find similar resolved issues for reference"""
        try:
            db = self.get_db()
            
            # Get resolved issues
            resolved_issues = db.query(Issue).filter(
                and_(
                    Issue.status == IssueStatus.DONE,
                    Issue.id != issue.id
                )
            ).limit(100).all()  # Get more to analyze similarity
            
            similar_issues = []
            issue_keywords = set(self.extract_keywords(f"{issue.title} {issue.description}"))
            
            for resolved_issue in resolved_issues:
                resolved_keywords = set(self.extract_keywords(f"{resolved_issue.title} {resolved_issue.description}"))
                similarity = self.calculate_text_similarity(
                    f"{issue.title} {issue.description}",
                    f"{resolved_issue.title} {resolved_issue.description}"
                )
                
                if similarity > 0.3:  # Threshold for similarity
                    resolution_time = None
                    if resolved_issue.updated_at and resolved_issue.created_at:
                        resolution_time = self.get_business_hours_between(
                            resolved_issue.created_at, 
                            resolved_issue.updated_at
                        )
                    
                    similar_issues.append({
                        'id': resolved_issue.id,
                        'title': resolved_issue.title,
                        'similarity_score': round(similarity, 2),
                        'resolution_time_hours': resolution_time,
                        'assignee': resolved_issue.assignee.full_name if resolved_issue.assignee else None
                    })
            
            # Sort by similarity and return top matches
            similar_issues.sort(key=lambda x: x['similarity_score'], reverse=True)
            return similar_issues[:limit]
            
        except Exception as e:
            logger.error(f"Similar issues search failed: {e}")
            return []
        finally:
            db.close()
    
    def _estimate_resolution_effort(self, issue: Issue) -> str:
        """Estimate effort required to resolve the issue"""
        issue_text = f"{issue.title} {issue.description}".lower()
        
        # High effort indicators
        high_effort_terms = [
            'architecture', 'redesign', 'refactor', 'migration', 'complex',
            'multiple systems', 'integration', 'data migration'
        ]
        
        # Low effort indicators  
        low_effort_terms = [
            'typo', 'text', 'color', 'styling', 'minor', 'simple',
            'configuration', 'setting', 'parameter'
        ]
        
        if any(term in issue_text for term in high_effort_terms):
            return 'high'
        elif any(term in issue_text for term in low_effort_terms):
            return 'low'
        elif issue.severity in [IssueSeverity.CRITICAL, IssueSeverity.HIGH]:
            return 'medium-high'
        else:
            return 'medium'
    
    def _assess_resolution_risk(self, issue: Issue) -> str:
        """Assess risk level of resolving the issue"""
        issue_text = f"{issue.title} {issue.description}".lower()
        
        # High risk indicators
        high_risk_terms = [
            'production', 'live', 'customer data', 'security', 'payment',
            'database', 'migration', 'authentication', 'critical system'
        ]
        
        # Low risk indicators
        low_risk_terms = [
            'development', 'staging', 'test', 'documentation', 'cosmetic',
            'ui text', 'color', 'styling', 'non-functional'
        ]
        
        if any(term in issue_text for term in high_risk_terms):
            return 'high'
        elif any(term in issue_text for term in low_risk_terms):
            return 'low'
        else:
            return 'medium'
    
    def _identify_required_resources(self, issue: Issue) -> List[str]:
        """Identify resources needed to resolve the issue"""
        resources = []
        issue_text = f"{issue.title} {issue.description}".lower()
        
        # Technical expertise needed
        if any(term in issue_text for term in ['frontend', 'ui', 'react', 'javascript']):
            resources.append('Frontend Developer')
        if any(term in issue_text for term in ['backend', 'api', 'server', 'database']):
            resources.append('Backend Developer')
        if any(term in issue_text for term in ['devops', 'deployment', 'infrastructure']):
            resources.append('DevOps Engineer')
        if any(term in issue_text for term in ['security', 'vulnerability', 'breach']):
            resources.append('Security Expert')
        if any(term in issue_text for term in ['design', 'ux', 'user experience']):
            resources.append('UX Designer')
        
        # Additional resources
        if issue.severity == IssueSeverity.CRITICAL:
            resources.append('Senior Developer')
            resources.append('Team Lead Review')
        
        if any(term in issue_text for term in ['database', 'migration', 'data']):
            resources.append('Database Administrator')
        
        if any(term in issue_text for term in ['test', 'qa', 'quality']):
            resources.append('QA Engineer')
        
        return list(set(resources))  # Remove duplicates
    
    async def generate_resolution_report(self, issue_id: int) -> Dict[str, Any]:
        """Generate a comprehensive resolution report for a completed issue"""
        try:
            db = self.get_db()
            issue = db.query(Issue).filter(Issue.id == issue_id).first()
            
            if not issue:
                raise ValueError(f"Issue {issue_id} not found")
            
            if issue.status != IssueStatus.DONE:
                raise ValueError(f"Issue {issue_id} is not resolved yet")
            
            # Calculate resolution metrics
            resolution_time = None
            if issue.updated_at and issue.created_at:
                total_time = (issue.updated_at - issue.created_at).total_seconds() / 3600
                resolution_time = self.get_business_hours_between(issue.created_at, issue.updated_at)
            
            # Analyze resolution effectiveness
            report = {
                'issue_summary': {
                    'id': issue.id,
                    'title': issue.title,
                    'severity': issue.severity.value,
                    'category': 'general',  # Could be enhanced with classification
                    'created_at': issue.created_at.isoformat(),
                    'resolved_at': issue.updated_at.isoformat() if issue.updated_at else None
                },
                'resolution_metrics': {
                    'total_resolution_time_hours': total_time if resolution_time else None,
                    'business_hours_to_resolution': resolution_time,
                    'formatted_resolution_time': self.format_duration(resolution_time) if resolution_time else 'Unknown',
                    'assignee': issue.assignee.full_name if issue.assignee else 'Unassigned',
                    'reporter': issue.reporter.full_name if issue.reporter else 'Unknown'
                },
                'resolution_analysis': await self._analyze_resolution_quality(issue),
                'lessons_learned': await self._extract_lessons_learned(issue),
                'recommendations': self._generate_process_recommendations(issue),
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Resolution report generation failed: {e}")
            raise
        finally:
            db.close()
    
    async def _analyze_resolution_quality(self, issue: Issue) -> Dict[str, Any]:
        """Analyze the quality and effectiveness of the resolution"""
        analysis = {
            'resolution_speed': 'unknown',
            'process_efficiency': 'unknown',
            'quality_indicators': []
        }
        
        if issue.updated_at and issue.created_at:
            resolution_hours = self.get_business_hours_between(issue.created_at, issue.updated_at)
            
            # Analyze resolution speed based on severity
            speed_thresholds = {
                IssueSeverity.CRITICAL: 4,    # 4 business hours
                IssueSeverity.HIGH: 24,       # 1 business day
                IssueSeverity.MEDIUM: 72,     # 3 business days
                IssueSeverity.LOW: 168        # 1 business week
            }
            
            threshold = speed_thresholds.get(issue.severity, 72)
            
            if resolution_hours <= threshold * 0.5:
                analysis['resolution_speed'] = 'excellent'
            elif resolution_hours <= threshold:
                analysis['resolution_speed'] = 'good'
            elif resolution_hours <= threshold * 2:
                analysis['resolution_speed'] = 'acceptable'
            else:
                analysis['resolution_speed'] = 'slow'
            
            # Quality indicators
            if resolution_hours <= threshold:
                analysis['quality_indicators'].append('Resolved within SLA')
            
            if issue.assignee_id:
                analysis['quality_indicators'].append('Properly assigned')
            
            # Check if issue was escalated (simplified check)
            if issue.severity == IssueSeverity.CRITICAL and resolution_hours <= 8:
                analysis['quality_indicators'].append('Rapid critical issue response')
        
        return analysis
    
    async def _extract_lessons_learned(self, issue: Issue) -> List[str]:
        """Extract lessons learned from the issue resolution"""
        lessons = []
        
        # Analyze issue patterns for learning opportunities
        issue_text = f"{issue.title} {issue.description}".lower()
        
        if any(term in issue_text for term in ['production', 'outage', 'down']):
            lessons.append("Consider implementing better monitoring to detect similar issues earlier")
        
        if any(term in issue_text for term in ['test', 'testing', 'qa']):
            lessons.append("Review testing procedures to prevent similar issues")
        
        if issue.severity == IssueSeverity.CRITICAL:
            lessons.append("Critical issue - review incident response procedures")
        
        if any(term in issue_text for term in ['security', 'vulnerability']):
            lessons.append("Conduct security review of related systems")
        
        if any(term in issue_text for term in ['performance', 'slow']):
            lessons.append("Implement performance monitoring for early detection")
        
        # Add generic lessons based on resolution time
        if issue.updated_at and issue.created_at:
            resolution_hours = self.get_business_hours_between(issue.created_at, issue.updated_at)
            if resolution_hours > 72:  # More than 3 business days
                lessons.append("Consider breaking down complex issues into smaller tasks")
        
        return lessons[:5]  # Limit to top 5 lessons
    
    def _generate_process_recommendations(self, issue: Issue) -> List[str]:
        """Generate process improvement recommendations"""
        recommendations = []
        
        # Analyze assignment patterns
        if not issue.assignee_id:
            recommendations.append("Implement automatic assignment rules for faster issue allocation")
        
        # Analyze severity and response
        if issue.severity == IssueSeverity.CRITICAL:
            recommendations.append("Establish clear escalation procedures for critical issues")
        
        # Analyze documentation
        if len(issue.description) < 50:  # Short description
            recommendations.append("Encourage more detailed issue descriptions for faster resolution")
        
        # General recommendations
        recommendations.extend([
            "Consider implementing similar issue detection to leverage past solutions",
            "Establish knowledge base for common issue patterns",
            "Implement automated testing for regression prevention"
        ])
        
        return recommendations[:5]  # Limit recommendations
    
    async def get_resolution_suggestions_for_user(self, user: User, limit: int = 10) -> List[Dict]:
        """Get personalized resolution suggestions for a user's active issues"""
        try:
            db = self.get_db()
            
            # Get user's active issues
            active_issues = db.query(Issue).filter(
                and_(
                    Issue.assignee_id == user.id,
                    Issue.status.in_([IssueStatus.OPEN, IssueStatus.TRIAGED, IssueStatus.IN_PROGRESS])
                )
            ).limit(limit).all()
            
            suggestions = []
            for issue in active_issues:
                resolution_plan = await self.suggest_resolution_steps(issue)
                suggestions.append({
                    'issue_id': issue.id,
                    'issue_title': issue.title,
                    'next_steps': resolution_plan['immediate_steps'][:3],  # Top 3 steps
                    'estimated_effort': resolution_plan['estimated_effort'],
                    'risk_level': resolution_plan['risk_assessment']
                })
            
            return suggestions
            
        except Exception as e:
            logger.error(f"User resolution suggestions failed: {e}")
            return []
        finally:
            db.close()
    
    def get_resolution_stats(self) -> Dict[str, Any]:
        """Get resolution assistant statistics"""
        return {
            'service_status': 'active',
            'solution_templates': sum(len(solutions) for category in self.solution_templates.values() 
                                     for solutions in category.values()),
            'troubleshooting_categories': len(self.troubleshooting_steps),
            'last_updated': datetime.utcnow().isoformat()
        }