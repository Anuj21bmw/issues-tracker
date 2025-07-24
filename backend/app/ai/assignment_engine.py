# backend/app/ai/assignment_engine.py - Complete Implementation
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
            'frontend': ['react', 'vue', 'angular', 'javascript', 'css', 'html', 'ui', 'svelte'],
            'backend': ['api', 'server', 'database', 'python', 'java', 'node', 'fastapi'],
            'mobile': ['ios', 'android', 'react native', 'flutter', 'mobile', 'app'],
            'devops': ['docker', 'kubernetes', 'aws', 'deploy', 'ci/cd', 'pipeline'],
            'security': ['security', 'auth', 'vulnerability', 'breach', 'ssl', 'encryption'],
            'performance': ['performance', 'optimization', 'slow', 'memory', 'cpu', 'cache'],
            'database': ['sql', 'mysql', 'postgresql', 'mongodb', 'query', 'migration'],
            'ui_ux': ['design', 'layout', 'responsive', 'user experience', 'accessibility']
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
            
            # Sort by score (highest first)
            scored_users.sort(key=lambda x: x['score'], reverse=True)
            
            if not scored_users:
                return {
                    'suggested_assignee': None,
                    'reason': 'Unable to calculate assignment scores',
                    'confidence': 0.0,
                    'alternatives': []
                }
            
            best_candidate = scored_users[0]
            
            return {
                'suggested_assignee': best_candidate['user'],
                'reason': self._generate_assignment_reason(best_candidate),
                'confidence': min(best_candidate['score'] / 10.0, 1.0),  # Normalize to 0-1
                'alternatives': scored_users[1:4],  # Top 3 alternatives
                'score_breakdown': best_candidate['score_breakdown']
            }
            
        except Exception as e:
            logger.error(f"Error while suggesting assignee: {e}")
            return {
                'suggested_assignee': None,
                'reason': f'An error occurred: {str(e)}',
                'confidence': 0.0,
                'alternatives': []
            }
        finally:
            db.close()
    
    async def _calculate_assignment_score(self, user: User, issue_data: Dict) -> Dict:
        """Calculate comprehensive assignment score for a user"""
        try:
            db = self.get_db()
            
            # Initialize score components
            expertise_score = 0.0
            workload_score = 0.0
            performance_score = 0.0
            availability_score = 0.0
            
            # 1. Expertise Score (40% weight)
            expertise_score = self._calculate_expertise_score(user, issue_data)
            
            # 2. Workload Score (25% weight)
            workload_score = self._calculate_workload_score(user.id)
            
            # 3. Performance Score (25% weight)
            performance_score = self._calculate_performance_score(user.id)
            
            # 4. Availability Score (10% weight)
            availability_score = self._calculate_availability_score(user.id)
            
            # Calculate weighted total score
            total_score = (
                expertise_score * 0.4 +
                workload_score * 0.25 +
                performance_score * 0.25 +
                availability_score * 0.1
            )
            
            return {
                'total_score': total_score,
                'expertise_score': expertise_score,
                'workload_score': workload_score,
                'performance_score': performance_score,
                'availability_score': availability_score,
                'breakdown': {
                    'expertise': f'{expertise_score:.1f}/10',
                    'workload': f'{workload_score:.1f}/10',
                    'performance': f'{performance_score:.1f}/10',
                    'availability': f'{availability_score:.1f}/10'
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating assignment score for user {user.id}: {e}")
            return {
                'total_score': 0.0,
                'expertise_score': 0.0,
                'workload_score': 0.0,
                'performance_score': 0.0,
                'availability_score': 0.0,
                'breakdown': {}
            }
        finally:
            db.close()
    
    def _calculate_expertise_score(self, user: User, issue_data: Dict) -> float:
        """Calculate expertise match score based on issue content"""
        issue_text = f"{issue_data.get('title', '')} {issue_data.get('description', '')}".lower()
        
        max_score = 0.0
        user_expertise_areas = []
        
        # Check each expertise area
        for area, keywords in self.expertise_weights.items():
            area_score = 0.0
            matched_keywords = []
            
            for keyword in keywords:
                if keyword in issue_text:
                    # Weight by keyword importance and frequency
                    frequency = issue_text.count(keyword)
                    keyword_weight = len(keyword) / 10.0  # Longer keywords are more specific
                    area_score += frequency * keyword_weight
                    matched_keywords.append(keyword)
            
            if area_score > 0:
                user_expertise_areas.append({
                    'area': area,
                    'score': min(area_score, 10.0),
                    'keywords': matched_keywords
                })
                max_score = max(max_score, min(area_score, 10.0))
        
        # Get historical performance in similar areas
        historical_score = self._get_historical_expertise_score(user.id, user_expertise_areas)
        
        # Combine current match with historical performance
        final_score = (max_score * 0.7) + (historical_score * 0.3)
        
        return min(final_score, 10.0)
    
    def _get_historical_expertise_score(self, user_id: int, expertise_areas: List[Dict]) -> float:
        """Get historical performance score in similar issue types"""
        try:
            db = self.get_db()
            
            # Get resolved issues assigned to this user
            resolved_issues = db.query(Issue).filter(
                and_(
                    Issue.assignee_id == user_id,
                    Issue.status == IssueStatus.DONE
                )
            ).limit(50).all()  # Last 50 resolved issues
            
            if not resolved_issues:
                return 5.0  # Neutral score for new users
            
            # Calculate average resolution time and success rate
            total_resolution_time = 0
            successful_resolutions = 0
            
            for issue in resolved_issues:
                if issue.updated_at and issue.created_at:
                    resolution_time = (issue.updated_at - issue.created_at).total_seconds() / 3600
                    total_resolution_time += resolution_time
                    
                    # Consider it successful if resolved within expected time for severity
                    expected_time = self._get_expected_resolution_time(issue.severity)
                    if resolution_time <= expected_time:
                        successful_resolutions += 1
            
            success_rate = successful_resolutions / len(resolved_issues)
            avg_resolution_time = total_resolution_time / len(resolved_issues)
            
            # Convert to score (higher success rate and lower resolution time = higher score)
            historical_score = (success_rate * 5) + (max(0, 10 - (avg_resolution_time / 24)) * 0.5)
            
            return min(historical_score, 10.0)
            
        except Exception as e:
            logger.error(f"Error calculating historical expertise score: {e}")
            return 5.0
        finally:
            db.close()
    
    def _calculate_workload_score(self, user_id: int) -> float:
        """Calculate workload score (higher score = less workload)"""
        try:
            current_workload = self._get_user_workload(user_id)
            
            # Score based on current workload (inverse relationship)
            if current_workload == 0:
                return 10.0
            elif current_workload <= 3:
                return 8.0
            elif current_workload <= 6:
                return 6.0
            elif current_workload <= 10:
                return 4.0
            else:
                return 2.0
                
        except Exception as e:
            logger.error(f"Error calculating workload score: {e}")
            return 5.0
    
    def _get_user_workload(self, user_id: int) -> int:
        """Get current active issue count for user"""
        try:
            db = self.get_db()
            
            workload = db.query(Issue).filter(
                and_(
                    Issue.assignee_id == user_id,
                    Issue.status.in_([IssueStatus.OPEN, IssueStatus.TRIAGED, IssueStatus.IN_PROGRESS])
                )
            ).count()
            
            return workload
            
        except Exception as e:
            logger.error(f"Error getting user workload: {e}")
            return 0
        finally:
            db.close()
    
    def _calculate_performance_score(self, user_id: int) -> float:
        """Calculate performance score based on historical data"""
        try:
            db = self.get_db()
            
            # Get recent resolved issues (last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_issues = db.query(Issue).filter(
                and_(
                    Issue.assignee_id == user_id,
                    Issue.status == IssueStatus.DONE,
                    Issue.updated_at >= thirty_days_ago
                )
            ).all()
            
            if not recent_issues:
                return 5.0  # Neutral score for users with no recent activity
            
            # Calculate performance metrics
            total_resolution_time = 0
            on_time_resolutions = 0
            
            for issue in recent_issues:
                if issue.updated_at and issue.created_at:
                    resolution_time_hours = (issue.updated_at - issue.created_at).total_seconds() / 3600
                    total_resolution_time += resolution_time_hours
                    
                    # Check if resolved within expected timeframe
                    expected_hours = self._get_expected_resolution_time(issue.severity)
                    if resolution_time_hours <= expected_hours:
                        on_time_resolutions += 1
            
            # Calculate metrics
            on_time_rate = on_time_resolutions / len(recent_issues)
            avg_resolution_hours = total_resolution_time / len(recent_issues)
            
            # Convert to performance score
            performance_score = (on_time_rate * 6) + (max(0, 4 - (avg_resolution_hours / 24)))
            
            return min(performance_score, 10.0)
            
        except Exception as e:
            logger.error(f"Error calculating performance score: {e}")
            return 5.0
        finally:
            db.close()
    
    def _calculate_availability_score(self, user_id: int) -> float:
        """Calculate availability score based on recent activity"""
        try:
            db = self.get_db()
            
            # Check recent activity (last 7 days)
            week_ago = datetime.utcnow() - timedelta(days=7)
            recent_activity = db.query(Issue).filter(
                and_(
                    Issue.assignee_id == user_id,
                    Issue.updated_at >= week_ago
                )
            ).count()
            
            # Score based on recent activity
            if recent_activity >= 5:
                return 10.0  # Very active
            elif recent_activity >= 3:
                return 8.0   # Active
            elif recent_activity >= 1:
                return 6.0   # Somewhat active
            else:
                return 4.0   # Less active
                
        except Exception as e:
            logger.error(f"Error calculating availability score: {e}")
            return 5.0
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
    
    def _assess_availability(self, user_id: int) -> str:
        """Assess user availability status"""
        try:
            workload = self._get_user_workload(user_id)
            
            if workload == 0:
                return "Available"
            elif workload <= 3:
                return "Lightly loaded"
            elif workload <= 6:
                return "Moderately loaded"
            elif workload <= 10:
                return "Heavily loaded"
            else:
                return "Overloaded"
                
        except Exception as e:
            logger.error(f"Error assessing availability: {e}")
            return "Unknown"
    
    def _generate_assignment_reason(self, candidate: Dict) -> str:
        """Generate human-readable reason for assignment suggestion"""
        user = candidate['user']
        scores = candidate['score_breakdown']
        workload = candidate['current_workload']
        
        reasons = []
        
        # Expertise-based reasons
        if scores['expertise_score'] >= 7:
            reasons.append(f"Strong expertise match ({scores['expertise_score']:.1f}/10)")
        elif scores['expertise_score'] >= 5:
            reasons.append(f"Good expertise match ({scores['expertise_score']:.1f}/10)")
        
        # Workload-based reasons
        if workload == 0:
            reasons.append("Currently available")
        elif workload <= 3:
            reasons.append(f"Light workload ({workload} active issues)")
        elif workload <= 6:
            reasons.append(f"Moderate workload ({workload} active issues)")
        
        # Performance-based reasons
        if scores['performance_score'] >= 8:
            reasons.append("Excellent track record")
        elif scores['performance_score'] >= 6:
            reasons.append("Good performance history")
        
        if not reasons:
            reasons.append("Best available option based on overall scoring")
        
        return f"{user['name']} is recommended: {', '.join(reasons[:3])}"
    
    async def get_assignment_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get analytics on assignment patterns and effectiveness"""
        try:
            db = self.get_db()
            
            # Get assignments from the specified period
            start_date = datetime.utcnow() - timedelta(days=days)
            assignments = db.query(Issue).filter(
                and_(
                    Issue.assignee_id.isnot(None),
                    Issue.created_at >= start_date
                )
            ).all()
            
            if not assignments:
                return {
                    'total_assignments': 0,
                    'message': 'No assignments found for the specified period'
                }
            
            # Calculate analytics
            total_assignments = len(assignments)
            completed_assignments = len([i for i in assignments if i.status == IssueStatus.DONE])
            
            # Workload distribution
            workload_distribution = {}
            for issue in assignments:
                assignee_name = issue.assignee.full_name if issue.assignee else 'Unassigned'
                workload_distribution[assignee_name] = workload_distribution.get(assignee_name, 0) + 1
            
            # Average resolution times by severity
            resolution_times = {severity.value: [] for severity in IssueSeverity}
            for issue in assignments:
                if issue.status == IssueStatus.DONE and issue.updated_at and issue.created_at:
                    resolution_hours = (issue.updated_at - issue.created_at).total_seconds() / 3600
                    resolution_times[issue.severity.value].append(resolution_hours)
            
            avg_resolution_times = {}
            for severity, times in resolution_times.items():
                if times:
                    avg_resolution_times[severity] = sum(times) / len(times)
                else:
                    avg_resolution_times[severity] = 0
            
            # Success metrics
            on_time_completions = 0
            for issue in assignments:
                if issue.status == IssueStatus.DONE and issue.updated_at and issue.created_at:
                    resolution_hours = (issue.updated_at - issue.created_at).total_seconds() / 3600
                    expected_hours = self._get_expected_resolution_time(issue.severity)
                    if resolution_hours <= expected_hours:
                        on_time_completions += 1
            
            completion_rate = (completed_assignments / total_assignments) * 100 if total_assignments > 0 else 0
            on_time_rate = (on_time_completions / completed_assignments) * 100 if completed_assignments > 0 else 0
            
            return {
                'total_assignments': total_assignments,
                'completed_assignments': completed_assignments,
                'completion_rate': round(completion_rate, 1),
                'on_time_completion_rate': round(on_time_rate, 1),
                'workload_distribution': workload_distribution,
                'avg_resolution_times_hours': avg_resolution_times,
                'insights': self._generate_assignment_insights(
                    total_assignments, completion_rate, on_time_rate, workload_distribution
                ),
                'period_days': days
            }
            
        except Exception as e:
            logger.error(f"Error generating assignment analytics: {e}")
            return {
                'error': 'Failed to generate assignment analytics',
                'details': str(e)
            }
        finally:
            db.close()
    
    def _generate_assignment_insights(self, total: int, completion_rate: float, 
                                    on_time_rate: float, workload_dist: Dict) -> List[str]:
        """Generate insights from assignment analytics"""
        insights = []
        
        # Volume insights
        if total > 100:
            insights.append(f"High assignment volume: {total} assignments in the period")
        elif total < 20:
            insights.append(f"Low assignment volume: {total} assignments in the period")
        
        # Performance insights
        if completion_rate >= 90:
            insights.append(f"Excellent completion rate: {completion_rate}%")
        elif completion_rate < 70:
            insights.append(f"Low completion rate: {completion_rate}% - consider workload review")
        
        if on_time_rate >= 80:
            insights.append(f"Good on-time delivery: {on_time_rate}%")
        elif on_time_rate < 60:
            insights.append(f"On-time delivery needs improvement: {on_time_rate}%")
        
        # Workload distribution insights
        if workload_dist:
            max_workload = max(workload_dist.values())
            min_workload = min(workload_dist.values())
            if max_workload > min_workload * 2:
                insights.append("Uneven workload distribution detected - consider rebalancing")
        
        return insights[:5]  # Return top 5 insights
    
    async def suggest_workload_rebalancing(self) -> Dict[str, Any]:
        """Suggest workload rebalancing opportunities"""
        try:
            db = self.get_db()
            
            # Get all maintainers and admins with their current workloads
            users = db.query(User).filter(
                and_(
                    User.role.in_([UserRole.MAINTAINER, UserRole.ADMIN]),
                    User.is_active == True
                )
            ).all()
            
            user_workloads = []
            for user in users:
                workload = self._get_user_workload(user.id)
                user_workloads.append({
                    'user_id': user.id,
                    'name': user.full_name,
                    'current_workload': workload,
                    'capacity_status': self._assess_availability(user.id)
                })
            
            # Sort by workload
            user_workloads.sort(key=lambda x: x['current_workload'], reverse=True)
            
            # Identify rebalancing opportunities
            if len(user_workloads) < 2:
                return {
                    'rebalancing_needed': False,
                    'message': 'Not enough team members for workload analysis'
                }
            
            heaviest_loaded = user_workloads[0]
            lightest_loaded = user_workloads[-1]
            
            workload_difference = heaviest_loaded['current_workload'] - lightest_loaded['current_workload']
            
            rebalancing_needed = workload_difference >= 4  # Significant difference threshold
            
            suggestions = []
            if rebalancing_needed:
                # Get reassignable issues from overloaded users
                overloaded_users = [u for u in user_workloads if u['current_workload'] > 8]
                underloaded_users = [u for u in user_workloads if u['current_workload'] < 4]
                
                for overloaded in overloaded_users:
                    for underloaded in underloaded_users:
                        if overloaded['current_workload'] - underloaded['current_workload'] >= 3:
                            suggestions.append({
                                'from_user': overloaded['name'],
                                'to_user': underloaded['name'],
                                'recommended_transfers': min(2, overloaded['current_workload'] // 2),
                                'reason': f"Balance workload between {overloaded['current_workload']} and {underloaded['current_workload']} issues"
                            })
            
            return {
                'rebalancing_needed': rebalancing_needed,
                'workload_distribution': user_workloads,
                'max_workload_difference': workload_difference,
                'suggestions': suggestions[:3],  # Top 3 suggestions
                'insights': [
                    f"Workload range: {lightest_loaded['current_workload']}-{heaviest_loaded['current_workload']} issues",
                    f"Average workload: {sum(u['current_workload'] for u in user_workloads) / len(user_workloads):.1f} issues"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error suggesting workload rebalancing: {e}")
            return {
                'rebalancing_needed': False,
                'error': 'Failed to analyze workload distribution',
                'details': str(e)
            }
        finally:
            db.close()