# backend/app/ai/assignment_engine.py - Complete Implementation with Missing Methods
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
                User.role.in_([UserRole.ADMIN, UserRole.MAINTAINER])
            ).all()
            
            if not available_users:
                return {
                    'recommended_assignee': None,
                    'reason': 'No available maintainers or admins found',
                    'suggestions': [],
                    'confidence': 0.0
                }
            
            # Analyze issue content for expertise matching
            issue_text = f"{issue_data.get('title', '')} {issue_data.get('description', '')}".lower()
            required_expertise = self._identify_required_expertise(issue_text)
            
            # Score each potential assignee
            assignee_scores = []
            for user in available_users:
                score_data = await self._calculate_assignee_score(user, issue_data, required_expertise)
                assignee_scores.append(score_data)
            
            # Sort by score and get best match
            assignee_scores.sort(key=lambda x: x['total_score'], reverse=True)
            
            if assignee_scores:
                best_match = assignee_scores[0]
                
                return {
                    'recommended_assignee': {
                        'id': best_match['user_id'],
                        'name': best_match['user_name'],
                        'role': best_match['user_role']
                    },
                    'reason': best_match['reason'],
                    'confidence': best_match['confidence'],
                    'all_suggestions': assignee_scores[:3],  # Top 3 suggestions
                    'analysis_timestamp': datetime.utcnow().isoformat()
                }
            else:
                return {
                    'recommended_assignee': None,
                    'reason': 'No suitable assignee found based on current criteria',
                    'suggestions': [],
                    'confidence': 0.0
                }
                
        except Exception as e:
            logger.error(f"Assignee suggestion failed: {e}")
            return {
                'recommended_assignee': None,
                'reason': f'Assignment suggestion failed: {str(e)}',
                'suggestions': [],
                'confidence': 0.0,
                'error': True
            }
        finally:
            db.close()
    
    def _identify_required_expertise(self, issue_text: str) -> List[str]:
        """Identify required expertise areas from issue text"""
        required_areas = []
        
        for area, keywords in self.expertise_weights.items():
            if any(keyword in issue_text for keyword in keywords):
                required_areas.append(area)
        
        return required_areas
    
    async def _calculate_assignee_score(self, user: User, issue_data: Dict, required_expertise: List[str]) -> Dict[str, Any]:
        """Calculate assignment score for a user"""
        try:
            db = self.get_db()
            
            # Base scores
            expertise_score = await self._calculate_expertise_score(user, required_expertise)
            workload_score = await self._calculate_workload_score(user)
            availability_score = await self._calculate_availability_score(user)
            priority_score = self._calculate_priority_score(issue_data, user)
            
            # Weight the scores
            total_score = (
                expertise_score * 0.4 +      # 40% expertise
                workload_score * 0.3 +       # 30% workload
                availability_score * 0.2 +   # 20% availability
                priority_score * 0.1         # 10% priority handling
            )
            
            # Calculate confidence based on score distribution
            confidence = min(0.95, total_score / 10.0)
            
            # Generate reason for recommendation
            reason = self._generate_assignment_reason(
                user, expertise_score, workload_score, required_expertise
            )
            
            return {
                'user_id': user.id,
                'user_name': user.full_name,
                'user_role': user.role.value,
                'total_score': round(total_score, 2),
                'expertise_score': round(expertise_score, 2),
                'workload_score': round(workload_score, 2),
                'availability_score': round(availability_score, 2),
                'priority_score': round(priority_score, 2),
                'confidence': round(confidence, 2),
                'reason': reason
            }
            
        except Exception as e:
            logger.error(f"Assignee score calculation failed for user {user.id}: {e}")
            return {
                'user_id': user.id,
                'user_name': user.full_name,
                'user_role': user.role.value,
                'total_score': 0.0,
                'confidence': 0.0,
                'reason': 'Score calculation failed'
            }
    
    async def _calculate_expertise_score(self, user: User, required_expertise: List[str]) -> float:
        """Calculate expertise score based on user's past issue resolutions"""
        try:
            db = self.get_db()
            
            # Get user's resolved issues for expertise analysis
            resolved_issues = db.query(Issue).filter(
                and_(
                    Issue.assignee_id == user.id,
                    Issue.status == IssueStatus.DONE
                )
            ).limit(100).all()  # Last 100 resolved issues
            
            if not resolved_issues:
                return 3.0  # Default score for new users
            
            expertise_matches = 0
            total_expertise_score = 0
            
            for expertise_area in required_expertise:
                area_keywords = self.expertise_weights.get(expertise_area, [])
                
                # Count how many resolved issues involved this expertise area
                area_matches = 0
                for issue in resolved_issues:
                    issue_text = f"{issue.title} {issue.description}".lower()
                    if any(keyword in issue_text for keyword in area_keywords):
                        area_matches += 1
                
                if area_matches > 0:
                    expertise_matches += 1
                    # Score based on experience level in this area
                    area_score = min(10.0, (area_matches / len(resolved_issues)) * 20)
                    total_expertise_score += area_score
            
            if not required_expertise:
                # If no specific expertise required, give average score
                return 6.0
            
            # Average expertise score across required areas
            final_score = total_expertise_score / len(required_expertise) if required_expertise else 5.0
            
            # Bonus for having experience in multiple required areas
            if expertise_matches > 1:
                final_score += 1.0
            
            return min(10.0, final_score)
            
        except Exception as e:
            logger.error(f"Expertise score calculation failed: {e}")
            return 5.0  # Default score on error
    
    async def _calculate_workload_score(self, user: User) -> float:
        """Calculate workload score (higher score = less loaded)"""
        try:
            db = self.get_db()
            
            # Count current active issues
            active_issues = db.query(Issue).filter(
                and_(
                    Issue.assignee_id == user.id,
                    Issue.status.in_([IssueStatus.OPEN, IssueStatus.TRIAGED, IssueStatus.IN_PROGRESS])
                )
            ).count()
            
            # Score based on workload (inverse relationship)
            # 0 issues = 10 points, 5 issues = 5 points, 10+ issues = 1 point
            if active_issues == 0:
                return 10.0
            elif active_issues <= 3:
                return 8.0
            elif active_issues <= 5:
                return 6.0
            elif active_issues <= 8:
                return 4.0
            elif active_issues <= 10:
                return 2.0
            else:
                return 1.0
                
        except Exception as e:
            logger.error(f"Workload score calculation failed: {e}")
            return 5.0
    
    async def _calculate_availability_score(self, user: User) -> float:
        """Calculate availability score based on recent activity"""
        try:
            db = self.get_db()
            
            # Check recent activity (last 7 days)
            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            
            recent_activity = db.query(Issue).filter(
                and_(
                    Issue.assignee_id == user.id,
                    Issue.updated_at >= seven_days_ago
                )
            ).count()
            
            # Higher recent activity suggests availability
            if recent_activity >= 5:
                return 10.0
            elif recent_activity >= 3:
                return 8.0
            elif recent_activity >= 1:
                return 6.0
            else:
                return 4.0  # Lower score for inactive users
                
        except Exception as e:
            logger.error(f"Availability score calculation failed: {e}")
            return 7.0
    
    def _calculate_priority_score(self, issue_data: Dict, user: User) -> float:
        """Calculate priority handling score"""
        severity = issue_data.get('severity', 'MEDIUM')
        
        # Admin users get higher priority for critical issues
        if user.role == UserRole.ADMIN:
            if severity == 'CRITICAL':
                return 10.0
            elif severity == 'HIGH':
                return 8.0
            else:
                return 6.0
        elif user.role == UserRole.MAINTAINER:
            if severity in ['CRITICAL', 'HIGH']:
                return 8.0
            else:
                return 7.0
        else:
            return 5.0
    
    def _generate_assignment_reason(self, user: User, expertise_score: float, workload_score: float, required_expertise: List[str]) -> str:
        """Generate human-readable reason for assignment recommendation"""
        reasons = []
        
        if expertise_score >= 8.0:
            if required_expertise:
                reasons.append(f"Strong expertise in {', '.join(required_expertise[:2])}")
            else:
                reasons.append("Excellent overall technical experience")
        elif expertise_score >= 6.0:
            reasons.append("Good technical match for this issue type")
        
        if workload_score >= 8.0:
            reasons.append("currently has light workload")
        elif workload_score >= 6.0:
            reasons.append("manageable current workload")
        elif workload_score < 4.0:
            reasons.append("high current workload but may be best technical fit")
        
        if user.role == UserRole.ADMIN:
            reasons.append("admin privileges for complex issues")
        
        if not reasons:
            reasons.append("balanced technical skills and availability")
        
        return f"{user.full_name} recommended due to " + " and ".join(reasons)
    
    async def get_assignment_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get assignment analytics and insights"""
        try:
            db = self.get_db()
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Get issues from the period
            issues = db.query(Issue).filter(Issue.created_at >= cutoff_date).all()
            
            if not issues:
                return {'message': 'No issues in the specified period'}
            
            # Assignment statistics
            assigned_count = sum(1 for i in issues if i.assignee_id)
            unassigned_count = len(issues) - assigned_count
            assignment_rate = (assigned_count / len(issues)) * 100 if issues else 0
            
            # Assignee workload distribution
            assignee_workload = {}
            for issue in issues:
                if issue.assignee:
                    name = issue.assignee.full_name
                    if name not in assignee_workload:
                        assignee_workload[name] = {'total': 0, 'by_severity': {}}
                    
                    assignee_workload[name]['total'] += 1
                    severity = issue.severity.value
                    assignee_workload[name]['by_severity'][severity] = assignee_workload[name]['by_severity'].get(severity, 0) + 1
            
            # Resolution time by assignee
            assignee_performance = {}
            for issue in issues:
                if issue.assignee and issue.status == IssueStatus.DONE and issue.updated_at:
                    name = issue.assignee.full_name
                    if name not in assignee_performance:
                        assignee_performance[name] = {'total_hours': 0, 'count': 0}
                    
                    resolution_hours = self.get_business_hours_between(issue.created_at, issue.updated_at)
                    assignee_performance[name]['total_hours'] += resolution_hours
                    assignee_performance[name]['count'] += 1
            
            # Calculate averages
            for name, perf in assignee_performance.items():
                if perf['count'] > 0:
                    perf['avg_resolution_hours'] = round(perf['total_hours'] / perf['count'], 1)
            
            # Generate insights
            insights = []
            
            if assignment_rate < 70:
                insights.append(f"Low assignment rate ({assignment_rate:.1f}%) - consider implementing auto-assignment")
            
            if assignee_workload:
                max_workload = max(data['total'] for data in assignee_workload.values())
                min_workload = min(data['total'] for data in assignee_workload.values())
                
                if max_workload > min_workload * 2:
                    insights.append("Significant workload imbalance detected across team members")
            
            # Identify top performers
            if assignee_performance:
                sorted_performers = sorted(
                    assignee_performance.items(),
                    key=lambda x: x[1].get('avg_resolution_hours', float('inf'))
                )
                if sorted_performers and sorted_performers[0][1]['count'] >= 3:
                    insights.append(f"{sorted_performers[0][0]} shows excellent resolution times")
            
            return {
                'period_days': days,
                'total_issues': len(issues),
                'assignment_rate': round(assignment_rate, 1),
                'assigned_issues': assigned_count,
                'unassigned_issues': unassigned_count,
                'assignee_workload': assignee_workload,
                'assignee_performance': assignee_performance,
                'insights': insights,
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Assignment analytics failed: {e}")
            return {'error': str(e)}
        finally:
            db.close()
    
    async def suggest_workload_rebalancing(self) -> Dict[str, Any]:
        """Suggest workload rebalancing across team members"""
        try:
            db = self.get_db()
            
            # Get all maintainers and admins with their current workload
            users = db.query(User).filter(
                User.role.in_([UserRole.ADMIN, UserRole.MAINTAINER])
            ).all()
            
            if not users:
                return {'message': 'No maintainers or admins found'}
            
            # Calculate current workloads
            user_workloads = []
            for user in users:
                active_issues = db.query(Issue).filter(
                    and_(
                        Issue.assignee_id == user.id,
                        Issue.status != IssueStatus.DONE
                    )
                ).count()
                
                user_workloads.append({
                    'user_id': user.id,
                    'user_name': user.full_name,
                    'role': user.role.value,
                    'active_issues': active_issues
                })
            
            # Sort by workload
            user_workloads.sort(key=lambda x: x['active_issues'])
            
            # Identify rebalancing opportunities
            suggestions = []
            total_issues = sum(u['active_issues'] for u in user_workloads)
            avg_workload = total_issues / len(user_workloads) if user_workloads else 0
            
            overloaded_users = [u for u in user_workloads if u['active_issues'] > avg_workload * 1.3]
            underloaded_users = [u for u in user_workloads if u['active_issues'] < avg_workload * 0.7]
            
            for overloaded in overloaded_users:
                for underloaded in underloaded_users:
                    if overloaded['active_issues'] > underloaded['active_issues'] + 2:
                        excess = overloaded['active_issues'] - int(avg_workload)
                        transfer_count = min(excess // 2, 3)  # Transfer at most 3 issues
                        
                        if transfer_count > 0:
                            suggestions.append({
                                'from_user': overloaded['user_name'],
                                'to_user': underloaded['user_name'],
                                'suggested_transfer_count': transfer_count,
                                'reason': f"Reduce {overloaded['user_name']}'s workload from {overloaded['active_issues']} to {overloaded['active_issues'] - transfer_count}",
                                'priority': 'high' if excess > 5 else 'medium'
                            })
            
            # Calculate balance score
            if user_workloads and len(user_workloads) > 1:
                workload_variance = sum((u['active_issues'] - avg_workload) ** 2 for u in user_workloads) / len(user_workloads)
                balance_score = max(0, 100 - (workload_variance * 10))  # Simple balance scoring
            else:
                balance_score = 100
            
            return {
                'current_balance_score': round(balance_score, 1),
                'average_workload': round(avg_workload, 1),
                'user_workloads': user_workloads,
                'rebalancing_suggestions': suggestions[:5],  # Top 5 suggestions
                'analysis_summary': {
                    'total_active_issues': total_issues,
                    'team_size': len(user_workloads),
                    'overloaded_users': len(overloaded_users),
                    'underloaded_users': len(underloaded_users)
                },
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Workload rebalancing analysis failed: {e}")
            return {'error': str(e)}
        finally:
            db.close()
    
    async def get_user_assignment_recommendations(self, user: User) -> Dict[str, Any]:
        """Get assignment recommendations for a specific user"""
        try:
            db = self.get_db()
            
            # Get user's current workload
            current_issues = db.query(Issue).filter(
                and_(
                    Issue.assignee_id == user.id,
                    Issue.status != IssueStatus.DONE
                )
            ).count()
            
            # Get user's expertise areas based on resolved issues
            resolved_issues = db.query(Issue).filter(
                and_(
                    Issue.assignee_id == user.id,
                    Issue.status == IssueStatus.DONE
                )
            ).limit(50).all()
            
            expertise_analysis = self._analyze_user_expertise(resolved_issues)
            workload_status = self._assess_workload_status(current_issues, user.role)
            
            # Get unassigned issues that match user's expertise
            unassigned_issues = db.query(Issue).filter(
                and_(
                    Issue.assignee_id.is_(None),
                    Issue.status != IssueStatus.DONE
                )
            ).all()
            
            matching_issues = []
            for issue in unassigned_issues[:10]:  # Check top 10 unassigned
                issue_text = f"{issue.title} {issue.description}".lower()
                match_score = 0
                
                for expertise_area, score in expertise_analysis.items():
                    if score > 0.3:  # User has good expertise in this area
                        keywords = self.expertise_weights.get(expertise_area, [])
                        if any(keyword in issue_text for keyword in keywords):
                            match_score += score
                
                if match_score > 0.4:  # Good match threshold
                    matching_issues.append({
                        'issue_id': issue.id,
                        'title': issue.title,
                        'severity': issue.severity.value,
                        'match_score': round(match_score, 2),
                        'created_days_ago': (datetime.utcnow() - issue.created_at).days
                    })
            
            # Sort by match score and urgency
            matching_issues.sort(key=lambda x: (x['match_score'], -x['created_days_ago']), reverse=True)
            
            recommendations = {
                'user_profile': {
                    'name': user.full_name,
                    'role': user.role.value,
                    'current_workload': current_issues,
                    'workload_status': workload_status
                },
                'expertise_areas': expertise_analysis,
                'recommended_issues': matching_issues[:5],  # Top 5 matches
                'capacity_assessment': {
                    'can_take_new_issues': current_issues < self._get_capacity_threshold(user.role),
                    'recommended_new_issues': max(0, self._get_capacity_threshold(user.role) - current_issues),
                    'capacity_utilization': round((current_issues / self._get_capacity_threshold(user.role)) * 100, 1)
                },
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return recommendations
            
        except Exception as e:
            logger.error(f"User assignment recommendations failed: {e}")
            return {'error': str(e)}
        finally:
            db.close()
    
    def _analyze_user_expertise(self, resolved_issues: List[Issue]) -> Dict[str, float]:
        """Analyze user's expertise based on resolved issues"""
        expertise_scores = {}
        
        for category, keywords in self.expertise_weights.items():
            score = 0
            total_issues = len(resolved_issues)
            
            if total_issues == 0:
                expertise_scores[category] = 0.0
                continue
            
            for issue in resolved_issues:
                text_content = f"{issue.title} {issue.description}".lower()
                if any(keyword in text_content for keyword in keywords):
                    score += 1
            
            expertise_scores[category] = round(score / total_issues, 2)
        
        return expertise_scores
    
    def _assess_workload_status(self, current_issues: int, role: UserRole) -> str:
        """Assess user's workload status"""
        thresholds = {
            UserRole.ADMIN: 12,
            UserRole.MAINTAINER: 10,
            UserRole.REPORTER: 6
        }
        
        threshold = thresholds.get(role, 8)
        
        if current_issues >= threshold * 1.2:
            return 'overloaded'
        elif current_issues >= threshold:
            return 'at_capacity'
        elif current_issues >= threshold * 0.5:
            return 'moderate'
        else:
            return 'available'
    
    def _get_capacity_threshold(self, role: UserRole) -> int:
        """Get capacity threshold for user role"""
        thresholds = {
            UserRole.ADMIN: 12,
            UserRole.MAINTAINER: 10,
            UserRole.REPORTER: 6
        }
        return thresholds.get(role, 8)
    
    async def predict_assignment_success(self, user_id: int, issue_data: Dict) -> Dict[str, Any]:
        """Predict the success probability of assigning an issue to a specific user"""
        try:
            db = self.get_db()
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                return {'error': 'User not found'}
            
            # Calculate various success factors
            expertise_match = await self._calculate_expertise_score(
                user, self._identify_required_expertise(
                    f"{issue_data.get('title', '')} {issue_data.get('description', '')}"
                )
            )
            
            workload_factor = await self._calculate_workload_score(user)
            availability_factor = await self._calculate_availability_score(user)
            
            # Get user's historical success rate
            resolved_issues = db.query(Issue).filter(
                and_(
                    Issue.assignee_id == user.id,
                    Issue.status == IssueStatus.DONE
                )
            ).count()
            
            total_assigned = db.query(Issue).filter(Issue.assignee_id == user.id).count()
            
            historical_success_rate = (resolved_issues / total_assigned) if total_assigned > 0 else 0.7
            
            # Calculate overall success probability
            success_probability = (
                (expertise_match / 10) * 0.3 +
                (workload_factor / 10) * 0.2 +
                (availability_factor / 10) * 0.2 +
                historical_success_rate * 0.3
            )
            
            # Estimate resolution time based on user's history
            if resolved_issues > 0:
                user_resolved = db.query(Issue).filter(
                    and_(
                        Issue.assignee_id == user.id,
                        Issue.status == IssueStatus.DONE,
                        Issue.updated_at.isnot(None)
                    )
                ).limit(20).all()
                
                if user_resolved:
                    avg_resolution_time = sum(
                        self.get_business_hours_between(i.created_at, i.updated_at)
                        for i in user_resolved
                    ) / len(user_resolved)
                else:
                    avg_resolution_time = 24  # Default 1 day
            else:
                avg_resolution_time = 48  # Default 2 days for new users
            
            return {
                'user_id': user_id,
                'user_name': user.full_name,
                'success_probability': round(success_probability, 3),
                'estimated_resolution_hours': round(avg_resolution_time, 1),
                'estimated_resolution_formatted': self.format_duration(avg_resolution_time),
                'factors': {
                    'expertise_match': round(expertise_match, 1),
                    'workload_score': round(workload_factor, 1),
                    'availability_score': round(availability_factor, 1),
                    'historical_success_rate': round(historical_success_rate, 2)
                },
                'recommendation': 'highly_recommended' if success_probability > 0.8 else
                                'recommended' if success_probability > 0.6 else
                                'consider_alternatives' if success_probability > 0.4 else
                                'not_recommended'
            }
            
        except Exception as e:
            logger.error(f"Assignment success prediction failed: {e}")
            return {'error': str(e)}
        finally:
            db.close()
    
    def get_assignment_engine_stats(self) -> Dict[str, Any]:
        """Get assignment engine statistics and health"""
        return {
            'service_status': 'active',
            'expertise_areas': len(self.expertise_weights),
            'total_keywords': sum(len(keywords) for keywords in self.expertise_weights.values()),
            'capabilities': [
                'Smart assignee suggestions',
                'Workload analysis',
                'Expertise matching',
                'Assignment success prediction',
                'Workload rebalancing'
            ],
            'last_updated': datetime.utcnow().isoformat()
        }