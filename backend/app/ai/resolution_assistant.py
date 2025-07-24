# backend/app/ai/resolution_assistant.py
import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_
from app.ai.base import AIBaseService
from app.models import Issue, User, IssueStatus, IssueSeverity

logger = logging.getLogger(__name__)

class ResolutionAssistant(AIBaseService):
    """AI-powered resolution guidance and automation assistant"""
    
    def __init__(self):
        super().__init__()
        
        # Solution patterns for common issues
        self.solution_patterns = {
            'authentication': {
                'keywords': ['login', 'auth', 'password', 'token', 'session'],
                'common_solutions': [
                    'Check token expiration and refresh logic',
                    'Verify authentication headers are properly set',
                    'Clear browser cache and cookies',
                    'Check for CORS configuration issues'
                ]
            },
            'database': {
                'keywords': ['database', 'sql', 'query', 'connection', 'timeout'],
                'common_solutions': [
                    'Check database connection pool settings',
                    'Optimize slow-running queries with EXPLAIN',
                    'Verify database indexes are properly configured',
                    'Check for deadlocks in concurrent operations'
                ]
            },
            'ui_layout': {
                'keywords': ['layout', 'responsive', 'mobile', 'css', 'display'],
                'common_solutions': [
                    'Check CSS media queries for responsive design',
                    'Verify flexbox or grid configurations',
                    'Test on different screen sizes and browsers',
                    'Check for conflicting CSS styles'
                ]
            },
            'performance': {
                'keywords': ['slow', 'performance', 'loading', 'lag', 'timeout'],
                'common_solutions': [
                    'Profile application performance with DevTools',
                    'Optimize database queries and add indexes',
                    'Implement caching for frequently accessed data',
                    'Compress and optimize static assets'
                ]
            },
            'api': {
                'keywords': ['api', 'endpoint', 'request', 'response', '500', '404'],
                'common_solutions': [
                    'Check API endpoint URL and HTTP method',
                    'Verify request payload format and validation',
                    'Check server logs for detailed error messages',
                    'Test API endpoints with tools like Postman'
                ]
            }
        }
    
    async def suggest_resolution_steps(self, issue: Issue) -> Dict[str, Any]:
        """Suggest resolution steps for an issue"""
        try:
            issue_text = f"{issue.title} {issue.description}".lower()
            
            # Find matching solution patterns
            matching_patterns = []
            for pattern_name, pattern_data in self.solution_patterns.items():
                matches = sum(1 for keyword in pattern_data['keywords'] if keyword in issue_text)
                if matches > 0:
                    matching_patterns.append({
                        'pattern': pattern_name,
                        'matches': matches,
                        'solutions': pattern_data['common_solutions']
                    })
            
            # Sort by relevance
            matching_patterns.sort(key=lambda x: x['matches'], reverse=True)
            
            # Get similar resolved issues
            similar_issues = await self._find_similar_resolved_issues(issue)
            
            # Generate AI-powered suggestions
            ai_suggestions = await self._generate_ai_suggestions(issue, matching_patterns)
            
            # Estimate resolution complexity
            complexity_analysis = self._analyze_resolution_complexity(issue, matching_patterns)
            
            return {
                'issue_id': issue.id,
                'suggested_steps': self._compile_resolution_steps(matching_patterns, similar_issues),
                'similar_resolved_issues': similar_issues,
                'ai_insights': ai_suggestions,
                'complexity_analysis': complexity_analysis,
                'estimated_effort': self._estimate_resolution_effort(issue, complexity_analysis),
                'recommended_resources': self._recommend_resources(matching_patterns),
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error suggesting resolution steps for issue {issue.id}: {e}")
            return {
                'issue_id': issue.id,
                'error': 'Failed to generate resolution suggestions',
                'suggested_steps': ['Review issue details and consult team lead'],
                'generated_at': datetime.utcnow().isoformat()
            }
    
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
            ).order_by(Issue.updated_at.desc()).limit(50).all()
            
            similar_issues = []
            issue_text = f"{issue.title} {issue.description}".lower()
            
            for resolved_issue in resolved_issues:
                resolved_text = f"{resolved_issue.title} {resolved_issue.description}".lower()
                similarity_score = self._calculate_text_similarity(issue_text, resolved_text)
                
                if similarity_score > 0.3:  # Minimum similarity threshold
                    resolution_time = None
                    if resolved_issue.updated_at and resolved_issue.created_at:
                        resolution_time = (resolved_issue.updated_at - resolved_issue.created_at).total_seconds() / 3600
                    
                    similar_issues.append({
                        'id': resolved_issue.id,
                        'title': resolved_issue.title,
                        'similarity_score': round(similarity_score, 2),
                        'resolution_time_hours': round(resolution_time, 1) if resolution_time else None,
                        'severity': resolved_issue.severity.value,
                        'assignee': resolved_issue.assignee.full_name if resolved_issue.assignee else None,
                        'tags': resolved_issue.tags
                    })
            
            # Sort by similarity and return top matches
            similar_issues.sort(key=lambda x: x['similarity_score'], reverse=True)
            return similar_issues[:limit]
            
        except Exception as e:
            logger.error(f"Error finding similar issues: {e}")
            return []
        finally:
            db.close()
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity score"""
        try:
            # Simple word-based similarity
            words1 = set(text1.split())
            words2 = set(text2.split())
            
            if not words1 or not words2:
                return 0.0
            
            intersection = words1.intersection(words2)
            union = words1.union(words2)
            
            return len(intersection) / len(union)
            
        except Exception:
            return 0.0
    
    async def _generate_ai_suggestions(self, issue: Issue, patterns: List[Dict]) -> Dict[str, Any]:
        """Generate AI-powered resolution suggestions"""
        try:
            # Prepare context for AI
            context = f"""
            Issue: {issue.title}
            Description: {issue.description}
            Severity: {issue.severity.value}
            """
            
            if patterns:
                context += f"\nDetected patterns: {', '.join([p['pattern'] for p in patterns[:2]])}"
            
            messages = [
                {
                    "role": "system",
                    "content": "You are a software engineering expert. Provide concise, actionable resolution steps for the given issue."
                },
                {
                    "role": "user",
                    "content": f"Analyze this issue and provide 3-5 specific resolution steps:\n{context}"
                }
            ]
            
            ai_response = await self.call_openai_chat(messages, max_tokens=300)
            
            return {
                'ai_generated_steps': ai_response,
                'confidence': 0.8 if patterns else 0.6,
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating AI suggestions: {e}")
            return {
                'ai_generated_steps': 'AI suggestions temporarily unavailable. Please follow standard troubleshooting procedures.',
                'confidence': 0.0,
                'generated_at': datetime.utcnow().isoformat()
            }
    
    def _analyze_resolution_complexity(self, issue: Issue, patterns: List[Dict]) -> Dict[str, Any]:
        """Analyze the complexity of resolving the issue"""
        complexity_factors = []
        complexity_score = 1.0  # Base complexity
        
        # Severity impact
        if issue.severity == IssueSeverity.CRITICAL:
            complexity_score += 1.5
            complexity_factors.append("Critical severity increases urgency and complexity")
        elif issue.severity == IssueSeverity.HIGH:
            complexity_score += 1.0
            complexity_factors.append("High severity requires thorough testing")
        
        # Pattern-based complexity
        if any(p['pattern'] in ['database', 'performance'] for p in patterns):
            complexity_score += 1.2
            complexity_factors.append("Database/performance issues require careful analysis")
        
        if any(p['pattern'] in ['authentication', 'api'] for p in patterns):
            complexity_score += 0.8
            complexity_factors.append("Authentication/API issues need security consideration")
        
        # Description complexity
        description_length = len(issue.description) if issue.description else 0
        if description_length > 500:
            complexity_score += 0.5
            complexity_factors.append("Detailed description suggests complex issue")
        elif description_length < 50:
            complexity_score += 0.3
            complexity_factors.append("Brief description may require clarification")
        
        # Determine complexity level
        if complexity_score >= 3.0:
            complexity_level = "High"
        elif complexity_score >= 2.0:
            complexity_level = "Medium"
        else:
            complexity_level = "Low"
        
        return {
            'complexity_level': complexity_level,
            'complexity_score': round(complexity_score, 1),
            'factors': complexity_factors,
            'estimated_skill_level': self._get_required_skill_level(complexity_score)
        }
    
    def _get_required_skill_level(self, complexity_score: float) -> str:
        """Determine required skill level based on complexity"""
        if complexity_score >= 3.5:
            return "Senior/Expert"
        elif complexity_score >= 2.5:
            return "Intermediate to Senior"
        elif complexity_score >= 1.5:
            return "Intermediate"
        else:
            return "Junior to Intermediate"
    
    def _compile_resolution_steps(self, patterns: List[Dict], similar_issues: List[Dict]) -> List[str]:
        """Compile comprehensive resolution steps"""
        steps = []
        
        # Add pattern-based steps
        if patterns:
            primary_pattern = patterns[0]
            steps.extend(primary_pattern['solutions'][:3])
        
        # Add steps from similar issues
        if similar_issues:
            steps.append(f"Review similar issue #{similar_issues[0]['id']} which was resolved successfully")
        
        # Add general troubleshooting steps
        general_steps = [
            "Reproduce the issue in a controlled environment",
            "Check recent code changes that might be related",
            "Review system logs for error messages or patterns",
            "Test the fix thoroughly before deploying to production"
        ]
        
        # Add general steps if we don't have enough specific ones
        while len(steps) < 6:
            for step in general_steps:
                if step not in steps:
                    steps.append(step)
                    break
            else:
                break
        
        return steps[:8]  # Limit to 8 steps
    
    def _estimate_resolution_effort(self, issue: Issue, complexity_analysis: Dict) -> Dict[str, Any]:
        """Estimate resolution effort"""
        base_hours = {
            IssueSeverity.CRITICAL: 4,
            IssueSeverity.HIGH: 8,
            IssueSeverity.MEDIUM: 16,
            IssueSeverity.LOW: 32
        }
        
        estimated_hours = base_hours.get(issue.severity, 16)
        complexity_multiplier = complexity_analysis['complexity_score']
        
        final_estimate = estimated_hours * complexity_multiplier
        
        return {
            'estimated_hours': round(final_estimate, 1),
            'estimated_days': round(final_estimate / 8, 1),
            'confidence_level': "Medium" if complexity_analysis['complexity_level'] == "Medium" else "Low",
            'factors_considered': [
                f"Severity: {issue.severity.value}",
                f"Complexity: {complexity_analysis['complexity_level']}",
                "Historical similar issues"
            ]
        }
    
    def _recommend_resources(self, patterns: List[Dict]) -> List[Dict[str, str]]:
        """Recommend helpful resources based on issue patterns"""
        resource_map = {
            'authentication': [
                {'title': 'JWT Authentication Best Practices', 'type': 'documentation'},
                {'title': 'OAuth 2.0 Security Guide', 'type': 'guide'}
            ],
            'database': [
                {'title': 'Database Query Optimization', 'type': 'tutorial'},
                {'title': 'SQL Performance Tuning', 'type': 'documentation'}
            ],
            'ui_layout': [
                {'title': 'CSS Grid and Flexbox Guide', 'type': 'tutorial'},
                {'title': 'Responsive Design Patterns', 'type': 'examples'}
            ],
            'performance': [
                {'title': 'Web Performance Optimization', 'type': 'guide'},
                {'title': 'Browser DevTools Performance Tab', 'type': 'tool'}
            ],
            'api': [
                {'title': 'REST API Design Best Practices', 'type': 'guide'},
                {'title': 'API Testing with Postman', 'type': 'tool'}
            ]
        }
        
        recommended = []
        for pattern in patterns[:2]:  # Top 2 patterns
            pattern_resources = resource_map.get(pattern['pattern'], [])
            recommended.extend(pattern_resources)
        
        # Remove duplicates and limit
        seen = set()
        unique_resources = []
        for resource in recommended:
            resource_key = resource['title']
            if resource_key not in seen:
                seen.add(resource_key)
                unique_resources.append(resource)
        
        return unique_resources[:5]
    
    async def track_resolution_progress(self, issue_id: int) -> Dict[str, Any]:
        """Track and analyze resolution progress"""
        try:
            db = self.get_db()
            
            issue = db.query(Issue).filter(Issue.id == issue_id).first()
            if not issue:
                return {'error': 'Issue not found'}
            
            # Calculate time metrics
            current_time = datetime.utcnow()
            age_hours = (current_time - issue.created_at).total_seconds() / 3600
            
            # Get expected resolution time
            expected_hours = self._get_expected_resolution_time(issue.severity)
            
            # Calculate progress indicators
            time_progress = min((age_hours / expected_hours) * 100, 100)
            is_overdue = age_hours > expected_hours
            
            # Status progress mapping
            status_progress = {
                IssueStatus.OPEN: 10,
                IssueStatus.TRIAGED: 25,
                IssueStatus.IN_PROGRESS: 60,
                IssueStatus.DONE: 100
            }
            
            current_progress = status_progress.get(issue.status, 0)
            
            # Generate progress insights
            insights = []
            if is_overdue:
                insights.append(f"⚠️ Issue is overdue by {age_hours - expected_hours:.1f} hours")
            
            if current_progress < time_progress:
                insights.append("📈 Issue may need additional attention or resources")
            elif current_progress > time_progress + 20:
                insights.append("🚀 Excellent progress - ahead of schedule")
            
            # Suggest next actions
            next_actions = self._suggest_next_actions(issue, age_hours, expected_hours)
            
            return {
                'issue_id': issue_id,
                'current_status': issue.status.value,
                'age_hours': round(age_hours, 1),
                'expected_resolution_hours': expected_hours,
                'time_progress_percent': round(time_progress, 1),
                'status_progress_percent': current_progress,
                'is_overdue': is_overdue,
                'insights': insights,
                'next_actions': next_actions,
                'urgency_level': self._calculate_urgency_level(issue, age_hours, expected_hours)
            }
            
        except Exception as e:
            logger.error(f"Error tracking resolution progress: {e}")
            return {'error': 'Failed to track resolution progress'}
        finally:
            db.close()
    
    def _get_expected_resolution_time(self, severity: IssueSeverity) -> float:
        """Get expected resolution time in hours based on severity"""
        expected_times = {
            IssueSeverity.CRITICAL: 8,    # 8 hours
            IssueSeverity.HIGH: 48,       # 2 days
            IssueSeverity.MEDIUM: 168,    # 1 week
            IssueSeverity.LOW: 336        # 2 weeks
        }
        return expected_times.get(severity, 168)
    
    def _suggest_next_actions(self, issue: Issue, age_hours: float, expected_hours: float) -> List[str]:
        """Suggest next actions based on issue progress"""
        actions = []
        
        # Status-based actions
        if issue.status == IssueStatus.OPEN:
            actions.append("🎯 Triage and assign issue to appropriate team member")
            if age_hours > 24:
                actions.append("⚡ Issue has been open for over 24 hours - prioritize assignment")
        
        elif issue.status == IssueStatus.TRIAGED:
            actions.append("🚀 Move to IN_PROGRESS and begin active work")
            if age_hours > expected_hours * 0.3:
                actions.append("📋 Review complexity and consider breaking into smaller tasks")
        
        elif issue.status == IssueStatus.IN_PROGRESS:
            if age_hours > expected_hours * 0.8:
                actions.append("🔍 Review progress and identify any blockers")
                actions.append("👥 Consider pair programming or consultation")
            else:
                actions.append("✅ Continue current work - progress looks good")
        
        # Severity-based actions
        if issue.severity == IssueSeverity.CRITICAL and age_hours > 4:
            actions.append("🚨 Critical issue escalation - notify management")
        
        # Time-based actions
        if age_hours > expected_hours:
            actions.append("📞 Schedule status update meeting with stakeholders")
            actions.append("🔄 Re-evaluate scope and complexity estimates")
        
        return actions[:4]  # Limit to 4 actions
    
    def _calculate_urgency_level(self, issue: Issue, age_hours: float, expected_hours: float) -> str:
        """Calculate current urgency level"""
        urgency_ratio = age_hours / expected_hours
        
        if issue.severity == IssueSeverity.CRITICAL:
            if urgency_ratio > 1.0:
                return "URGENT"
            elif urgency_ratio > 0.5:
                return "HIGH"
            else:
                return "MEDIUM"
        
        elif issue.severity == IssueSeverity.HIGH:
            if urgency_ratio > 1.2:
                return "URGENT"
            elif urgency_ratio > 0.8:
                return "HIGH"
            else:
                return "MEDIUM"
        
        else:
            if urgency_ratio > 1.5:
                return "HIGH"
            elif urgency_ratio > 1.0:
                return "MEDIUM"
            else:
                return "LOW"
    
    async def generate_resolution_report(self, issue_id: int) -> Dict[str, Any]:
        """Generate comprehensive resolution report for completed issue"""
        try:
            db = self.get_db()
            
            issue = db.query(Issue).filter(Issue.id == issue_id).first()
            if not issue:
                return {'error': 'Issue not found'}
            
            if issue.status != IssueStatus.DONE:
                return {'error': 'Issue is not yet resolved'}
            
            # Calculate resolution metrics
            resolution_time = None
            if issue.updated_at and issue.created_at:
                resolution_time = (issue.updated_at - issue.created_at).total_seconds() / 3600
            
            expected_time = self._get_expected_resolution_time(issue.severity)
            met_sla = resolution_time <= expected_time if resolution_time else False
            
            # Analyze resolution patterns
            resolution_analysis = await self._analyze_resolution_patterns(issue)
            
            # Generate lessons learned
            lessons_learned = self._generate_lessons_learned(issue, resolution_time, expected_time)
            
            return {
                'issue_id': issue_id,
                'title': issue.title,
                'severity': issue.severity.value,
                'resolution_time_hours': round(resolution_time, 1) if resolution_time else None,
                'expected_time_hours': expected_time,
                'met_sla': met_sla,
                'assignee': issue.assignee.full_name if issue.assignee else None,
                'reporter': issue.reporter.full_name if issue.reporter else None,
                'created_at': issue.created_at.isoformat(),
                'resolved_at': issue.updated_at.isoformat() if issue.updated_at else None,
                'resolution_analysis': resolution_analysis,
                'lessons_learned': lessons_learned,
                'performance_score': self._calculate_resolution_performance_score(
                    resolution_time, expected_time, issue.severity
                ),
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating resolution report: {e}")
            return {'error': 'Failed to generate resolution report'}
        finally:
            db.close()
    
    async def _analyze_resolution_patterns(self, issue: Issue) -> Dict[str, Any]:
        """Analyze patterns in how the issue was resolved"""
        try:
            # Find similar resolved issues
            similar_issues = await self._find_similar_resolved_issues(issue, limit=10)
            
            if not similar_issues:
                return {
                    'pattern_analysis': 'No similar issues found for pattern analysis',
                    'comparative_performance': 'N/A'
                }
            
            # Calculate comparative metrics
            resolution_times = [si['resolution_time_hours'] for si in similar_issues 
                              if si['resolution_time_hours']]
            
            if resolution_times:
                avg_similar_time = sum(resolution_times) / len(resolution_times)
                current_time = (issue.updated_at - issue.created_at).total_seconds() / 3600 if issue.updated_at else 0
                
                performance_comparison = "faster" if current_time < avg_similar_time else "slower"
                time_difference = abs(current_time - avg_similar_time)
                
                return {
                    'similar_issues_count': len(similar_issues),
                    'average_resolution_time': round(avg_similar_time, 1),
                    'performance_comparison': f"{time_difference:.1f} hours {performance_comparison} than similar issues",
                    'pattern_insights': [
                        f"Found {len(similar_issues)} similar resolved issues",
                        f"Average resolution time for similar issues: {avg_similar_time:.1f} hours",
                        f"This issue was resolved {performance_comparison} than average"
                    ]
                }
            
            return {
                'similar_issues_count': len(similar_issues),
                'pattern_insights': ['Similar issues found but resolution time data incomplete']
            }
            
        except Exception as e:
            logger.error(f"Error analyzing resolution patterns: {e}")
            return {'pattern_analysis': 'Pattern analysis failed'}
    
    def _generate_lessons_learned(self, issue: Issue, resolution_time: float, 
                                 expected_time: float) -> List[str]:
        """Generate lessons learned from issue resolution"""
        lessons = []
        
        # Time-based lessons
        if resolution_time and resolution_time < expected_time * 0.5:
            lessons.append("✨ Excellent resolution speed - consider documenting approach for future reference")
        elif resolution_time and resolution_time > expected_time * 1.5:
            lessons.append("⏱️ Resolution took longer than expected - review for process improvements")
        
        # Severity-based lessons
        if issue.severity == IssueSeverity.CRITICAL:
            lessons.append("🚨 Critical issue resolved - ensure post-mortem is conducted")
        
        # Pattern-based lessons
        issue_text = f"{issue.title} {issue.description}".lower()
        if any(keyword in issue_text for keyword in ['authentication', 'login', 'auth']):
            lessons.append("🔐 Authentication issue - review security protocols and documentation")
        
        if any(keyword in issue_text for keyword in ['performance', 'slow', 'timeout']):
            lessons.append("⚡ Performance issue - consider adding monitoring and alerts")
        
        # General lessons
        if issue.assignee:
            lessons.append(f"👤 Successfully resolved by {issue.assignee.full_name} - expertise noted")
        
        if not lessons:
            lessons.append("📝 Standard resolution completed - maintain current processes")
        
        return lessons[:4]  # Limit to 4 lessons
    
    def _calculate_resolution_performance_score(self, resolution_time: float, 
                                              expected_time: float, severity: IssueSeverity) -> Dict[str, Any]:
        """Calculate performance score for resolution"""
        if not resolution_time:
            return {
                'score': 'N/A',
                'grade': 'N/A',
                'explanation': 'Resolution time data not available'
            }
        
        # Calculate time ratio
        time_ratio = resolution_time / expected_time
        
        # Base score calculation
        if time_ratio <= 0.5:
            score = 100
            grade = 'A+'
        elif time_ratio <= 0.75:
            score = 90
            grade = 'A'
        elif time_ratio <= 1.0:
            score = 80
            grade = 'B+'
        elif time_ratio <= 1.25:
            score = 70
            grade = 'B'
        elif time_ratio <= 1.5:
            score = 60
            grade = 'C'
        else:
            score = 50
            grade = 'D'
        
        # Adjust for severity
        if severity == IssueSeverity.CRITICAL and time_ratio <= 1.0:
            score += 5  # Bonus for meeting critical deadlines
        elif severity == IssueSeverity.LOW and time_ratio > 1.5:
            score -= 5  # Small penalty for low priority delays
        
        score = max(0, min(100, score))  # Clamp between 0-100
        
        return {
            'score': score,
            'grade': grade,
            'time_ratio': round(time_ratio, 2),
            'explanation': f"Resolved in {resolution_time:.1f}h vs expected {expected_time:.1f}h ({time_ratio:.1f}x expected time)"
        }