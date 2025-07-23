# backend/app/ai/notification_engine.py
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy import and_
from app.ai.base import AIBaseService
from app.models import Issue, User, IssueStatus, IssueSeverity

logger = logging.getLogger(__name__)

class SmartNotificationEngine(AIBaseService):
    """AI-powered intelligent notification and escalation system"""
    
    def __init__(self):
        super().__init__()
        
        # Escalation thresholds by severity (hours)
        self.escalation_thresholds = {
            IssueSeverity.CRITICAL: {
                'warning': 2,    # Warn after 2 hours
                'escalate': 4,   # Escalate after 4 hours
                'urgent': 8      # Urgent escalation after 8 hours
            },
            IssueSeverity.HIGH: {
                'warning': 8,    # Warn after 8 hours
                'escalate': 24,  # Escalate after 24 hours
                'urgent': 48     # Urgent escalation after 48 hours
            },
            IssueSeverity.MEDIUM: {
                'warning': 24,   # Warn after 1 day
                'escalate': 72,  # Escalate after 3 days
                'urgent': 168    # Urgent escalation after 1 week
            },
            IssueSeverity.LOW: {
                'warning': 72,   # Warn after 3 days
                'escalate': 336, # Escalate after 2 weeks
                'urgent': 504    # Urgent escalation after 3 weeks
            }
        }
        
        # Notification patterns
        self.notification_types = {
            'status_stuck': 'Issue has been in same status too long',
            'high_priority_unassigned': 'High priority issue remains unassigned',
            'critical_aging': 'Critical issue is aging without resolution',
            'workload_imbalance': 'Team workload is significantly imbalanced',
            'pattern_detected': 'Unusual pattern detected in issue flow',
            'sla_breach_risk': 'Issue at risk of SLA breach',
            'escalation_needed': 'Issue requires immediate escalation'
        }
    
    async def should_escalate(self, issue: Issue) -> Dict[str, Any]:
        """Determine if an issue needs escalation"""
        try:
            current_time = datetime.utcnow()
            
            # Calculate time in current status
            time_in_status = self._calculate_time_in_status(issue, current_time)
            
            # Get escalation thresholds for this severity
            thresholds = self.escalation_thresholds.get(issue.severity, 
                                                       self.escalation_thresholds[IssueSeverity.MEDIUM])
            
            escalation_level = None
            escalation_needed = False
            
            if time_in_status >= thresholds['urgent']:
                escalation_level = 'urgent'
                escalation_needed = True
            elif time_in_status >= thresholds['escalate']:
                escalation_level = 'escalate'
                escalation_needed = True
            elif time_in_status >= thresholds['warning']:
                escalation_level = 'warning'
            
            # Additional escalation factors
            additional_factors = await self._assess_additional_escalation_factors(issue)
            
            # Adjust escalation based on additional factors
            if additional_factors['risk_score'] > 0.7:
                escalation_needed = True
                if escalation_level in [None, 'warning']:
                    escalation_level = 'escalate'
            
            return {
                'escalation_needed': escalation_needed,
                'escalation_level': escalation_level,
                'time_in_status_hours': time_in_status,
                'threshold_hours': thresholds,
                'additional_factors': additional_factors,
                'recommended_actions': self._get_escalation_actions(escalation_level, issue),
                'priority_score': self._calculate_priority_score(issue, time_in_status),
                'analysis_timestamp': current_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Escalation assessment failed for issue {issue.id}: {e}")
            return {
                'escalation_needed': False,
                'error': str(e),
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
    
    def _calculate_time_in_status(self, issue: Issue, current_time: datetime) -> float:
        """Calculate how long issue has been in current status"""
        # Use updated_at if available, otherwise created_at
        reference_time = issue.updated_at if issue.updated_at else issue.created_at
        delta = current_time - reference_time
        return delta.total_seconds() / 3600  # Convert to hours
    
    async def _assess_additional_escalation_factors(self, issue: Issue) -> Dict[str, Any]:
        """Assess additional factors that might require escalation"""
        try:
            db = self.get_db()
            risk_factors = []
            risk_score = 0.0
            
            # Factor 1: Unassigned high/critical priority
            if not issue.assignee_id and issue.severity in [IssueSeverity.CRITICAL, IssueSeverity.HIGH]:
                risk_factors.append("High priority issue unassigned")
                risk_score += 0.3
            
            # Factor 2: Similar issues pattern
            similar_issues = db.query(Issue).filter(
                and_(
                    Issue.id != issue.id,
                    Issue.status != IssueStatus.DONE,
                    Issue.severity == issue.severity
                )
            ).limit(10).all()
            
            if len(similar_issues) >= 3:
                risk_factors.append(f"Pattern: {len(similar_issues)} similar severity issues active")
                risk_score += 0.2
            
            # Factor 3: Weekend or holiday (simplified check)
            current_weekday = datetime.utcnow().weekday()
            if current_weekday >= 5:  # Saturday or Sunday
                risk_factors.append("Issue aging over weekend")
                risk_score += 0.1
            
            # Factor 4: Reporter experience level
            reporter_issue_count = db.query(Issue).filter(Issue.reporter_id == issue.reporter_id).count()
            if reporter_issue_count <= 2:  # New user
                risk_factors.append("Reported by new user")
                risk_score += 0.1
            
            # Factor 5: Keywords indicating urgency
            urgent_keywords = ['production', 'down', 'outage', 'critical', 'urgent', 'asap']
            issue_text = f"{issue.title} {issue.description}".lower()
            urgent_keyword_count = sum(1 for keyword in urgent_keywords if keyword in issue_text)
            
            if urgent_keyword_count >= 2:
                risk_factors.append(f"Multiple urgency keywords detected ({urgent_keyword_count})")
                risk_score += 0.2
            
            return {
                'risk_score': min(risk_score, 1.0),
                'risk_factors': risk_factors,
                'factor_count': len(risk_factors)
            }
            
        except Exception as e:
            logger.error(f"Additional escalation factors assessment failed: {e}")
            return {
                'risk_score': 0.0,
                'risk_factors': [],
                'error': str(e)
            }
        finally:
            db.close()
    
    def _get_escalation_actions(self, escalation_level: str, issue: Issue) -> List[str]:
        """Get recommended actions based on escalation level"""
        actions = []
        
        if escalation_level == 'urgent':
            actions.extend([
                "Immediately notify admin team",
                "Escalate to senior management if critical",
                "Consider emergency response procedures",
                "Reassign to most experienced available developer"
            ])
        elif escalation_level == 'escalate':
            actions.extend([
                "Notify team lead or manager",
                "Review issue complexity and requirements",
                "Consider reassignment to different team member",
                "Add additional resources if needed"
            ])
        elif escalation_level == 'warning':
            actions.extend([
                "Send reminder to assigned developer",
                "Review issue status with team",
                "Check for any blockers or dependencies"
            ])
        
        # Add severity-specific actions
        if issue.severity == IssueSeverity.CRITICAL:
            actions.append("Monitor continuously until resolved")
        elif not issue.assignee_id:
            actions.append("Assign to available team member immediately")
        
        return actions[:5]  # Limit to top 5 actions
    
    def _calculate_priority_score(self, issue: Issue, time_in_status: float) -> float:
        """Calculate overall priority score for the issue"""
        severity_weights = {
            IssueSeverity.CRITICAL: 1.0,
            IssueSeverity.HIGH: 0.7,
            IssueSeverity.MEDIUM: 0.4,
            IssueSeverity.LOW: 0.2
        }
        
        base_score = severity_weights.get(issue.severity, 0.4)
        
        # Time factor (increases with age)
        time_factor = min(time_in_status / 24, 2.0)  # Cap at 2x for very old issues
        
        # Assignment factor
        assignment_factor = 0.8 if issue.assignee_id else 1.2  # Higher if unassigned
        
        # Status factor
        status_factors = {
            IssueStatus.OPEN: 1.3,
            IssueStatus.TRIAGED: 1.0,
            IssueStatus.IN_PROGRESS: 0.8,
            IssueStatus.DONE: 0.0
        }
        status_factor = status_factors.get(issue.status, 1.0)
        
        priority_score = base_score * (1 + time_factor * 0.3) * assignment_factor * status_factor
        
        return min(priority_score, 10.0)  # Cap at 10
    
    async def analyze_notification_patterns(self, days: int = 7) -> Dict[str, Any]:
        """Analyze notification patterns and trends"""
        try:
            db = self.get_db()
            
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Get issues from the period
            issues = db.query(Issue).filter(Issue.created_at >= start_date).all()
            
            # Analyze escalation patterns
            escalation_analysis = []
            for issue in issues:
                escalation_check = await self.should_escalate(issue)
                if escalation_check.get('escalation_needed'):
                    escalation_analysis.append({
                        'issue_id': issue.id,
                        'severity': issue.severity.value,
                        'status': issue.status.value,
                        'escalation_level': escalation_check.get('escalation_level'),
                        'time_in_status': escalation_check.get('time_in_status_hours'),
                        'priority_score': escalation_check.get('priority_score')
                    })
            
            # Generate insights
            insights = self._generate_notification_insights(escalation_analysis, issues)
            
            return {
                'analysis_period_days': days,
                'total_issues': len(issues),
                'escalation_candidates': len(escalation_analysis),
                'escalation_rate': len(escalation_analysis) / len(issues) if issues else 0,
                'escalation_breakdown': self._breakdown_escalations(escalation_analysis),
                'insights': insights,
                'recommendations': self._generate_notification_recommendations(escalation_analysis),
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Notification pattern analysis failed: {e}")
            return {'error': 'Analysis failed', 'details': str(e)}
        finally:
            db.close()
    
    def _breakdown_escalations(self, escalation_analysis: List[Dict]) -> Dict[str, Any]:
        """Break down escalations by various categories"""
        breakdown = {
            'by_severity': {},
            'by_escalation_level': {},
            'by_status': {},
            'average_time_in_status': 0
        }
        
        if not escalation_analysis:
            return breakdown
        
        # Count by severity
        for item in escalation_analysis:
            severity = item['severity']
            breakdown['by_severity'][severity] = breakdown['by_severity'].get(severity, 0) + 1
        
        # Count by escalation level
        for item in escalation_analysis:
            level = item['escalation_level']
            breakdown['by_escalation_level'][level] = breakdown['by_escalation_level'].get(level, 0) + 1
        
        # Count by status
        for item in escalation_analysis:
            status = item['status']
            breakdown['by_status'][status] = breakdown['by_status'].get(status, 0) + 1
        
        # Calculate average time in status
        total_time = sum(item['time_in_status'] for item in escalation_analysis)
        breakdown['average_time_in_status'] = round(total_time / len(escalation_analysis), 1)
        
        return breakdown
    
    def _generate_notification_insights(self, escalation_analysis: List[Dict], all_issues: List[Issue]) -> List[str]:
        """Generate insights from notification analysis"""
        insights = []
        
        if not escalation_analysis:
            insights.append("✅ No issues currently need escalation")
            return insights
        
        escalation_rate = len(escalation_analysis) / len(all_issues) if all_issues else 0
        
        if escalation_rate > 0.3:
            insights.append(f"🚨 High escalation rate: {len(escalation_analysis)} out of {len(all_issues)} issues need attention")
        elif escalation_rate > 0.15:
            insights.append(f"⚠️ Moderate escalation rate: {len(escalation_analysis)} issues need escalation")
        else:
            insights.append(f"📊 Normal escalation rate: {len(escalation_analysis)} issues flagged")
        
        # Critical issue insights
        critical_escalations = [item for item in escalation_analysis if item['severity'] == 'CRITICAL']
        if critical_escalations:
            insights.append(f"🔥 {len(critical_escalations)} critical issues require immediate attention")
        
        # Status insights
        open_escalations = [item for item in escalation_analysis if item['status'] == 'OPEN']
        if open_escalations:
            insights.append(f"📋 {len(open_escalations)} open issues have been sitting too long")
        
        # Time insights
        if escalation_analysis:
            avg_time = sum(item['time_in_status'] for item in escalation_analysis) / len(escalation_analysis)
            if avg_time > 72:  # More than 3 days
                insights.append(f"⏰ Issues are sitting in status for an average of {avg_time:.1f} hours")
        
        return insights[:5]  # Limit to top 5 insights
    
    def _generate_notification_recommendations(self, escalation_analysis: List[Dict]) -> List[str]:
        """Generate recommendations based on escalation analysis"""
        recommendations = []
        
        if not escalation_analysis:
            recommendations.append("Continue monitoring issue flow")
            return recommendations
        
        # Check for patterns
        urgent_count = len([item for item in escalation_analysis if item['escalation_level'] == 'urgent'])
        if urgent_count > 0:
            recommendations.append(f"Immediately address {urgent_count} urgent escalations")
        
        # Unassigned issues
        critical_unassigned = len([item for item in escalation_analysis 
                                 if item['severity'] == 'CRITICAL' and item['escalation_level']])
        if critical_unassigned > 0:
            recommendations.append("Prioritize assignment of critical issues")
        
        # Process improvements
        if len(escalation_analysis) > 5:
            recommendations.extend([
                "Review triage process for efficiency",
                "Consider additional team capacity",
                "Implement automated assignment rules"
            ])
        
        # Time-based recommendations
        long_duration_issues = [item for item in escalation_analysis if item['time_in_status'] > 168]  # 1 week
        if long_duration_issues:
            recommendations.append(f"Review {len(long_duration_issues)} issues stuck for over a week")
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    async def generate_smart_notifications(self, target_users: List[User] = None) -> List[Dict[str, Any]]:
        """Generate intelligent notifications for users"""
        try:
            db = self.get_db()
            notifications = []
            
            # Get users to notify (default to all maintainers and admins)
            if not target_users:
                target_users = db.query(User).filter(
                    and_(
                        User.role.in_(['MAINTAINER', 'ADMIN']),
                        User.is_active == True
                    )
                ).all()
            
            # Check for issues needing escalation
            active_issues = db.query(Issue).filter(
                Issue.status.in_([IssueStatus.OPEN, IssueStatus.TRIAGED, IssueStatus.IN_PROGRESS])
            ).all()
            
            for issue in active_issues:
                escalation_check = await self.should_escalate(issue)
                
                if escalation_check.get('escalation_needed'):
                    # Determine who should be notified
                    if issue.assignee_id:
                        notify_users = [user for user in target_users if user.id == issue.assignee_id]
                        if escalation_check.get('escalation_level') == 'urgent':
                            # Also notify admins for urgent issues
                            notify_users.extend([user for user in target_users if user.role == 'ADMIN'])
                    else:
                        # Unassigned issue - notify all
                        notify_users = target_users
                    
                    for user in notify_users:
                        notifications.append({
                            'user_id': user.id,
                            'user_name': user.full_name,
                            'issue_id': issue.id,
                            'issue_title': issue.title,
                            'notification_type': 'escalation_needed',
                            'severity': issue.severity.value,
                            'escalation_level': escalation_check.get('escalation_level'),
                            'message': self._generate_notification_message(issue, escalation_check),
                            'actions': escalation_check.get('recommended_actions', []),
                            'priority': escalation_check.get('priority_score', 1),
                            'created_at': datetime.utcnow().isoformat()
                        })
            
            # Check for workload imbalances
            workload_notifications = await self._check_workload_notifications(target_users)
            notifications.extend(workload_notifications)
            
            # Check for pattern-based notifications
            pattern_notifications = await self._check_pattern_notifications(target_users)
            notifications.extend(pattern_notifications)
            
            # Sort by priority and limit
            notifications.sort(key=lambda x: x.get('priority', 0), reverse=True)
            
            return notifications[:50]  # Limit to top 50 notifications
            
        except Exception as e:
            logger.error(f"Smart notification generation failed: {e}")
            return []
        finally:
            db.close()
    
    def _generate_notification_message(self, issue: Issue, escalation_check: Dict) -> str:
        """Generate human-readable notification message"""
        escalation_level = escalation_check.get('escalation_level', 'warning')
        time_in_status = escalation_check.get('time_in_status_hours', 0)
        
        if escalation_level == 'urgent':
            return f"URGENT: Issue #{issue.id} '{issue.title}' has been {issue.status.value} for {time_in_status:.1f} hours and requires immediate attention"
        elif escalation_level == 'escalate':
            return f"ESCALATION: Issue #{issue.id} '{issue.title}' needs escalation - {issue.status.value} for {time_in_status:.1f} hours"
        else:
            return f"WARNING: Issue #{issue.id} '{issue.title}' has been {issue.status.value} for {time_in_status:.1f} hours"
    
    async def _check_workload_notifications(self, target_users: List[User]) -> List[Dict[str, Any]]:
        """Check for workload-related notifications"""
        try:
            db = self.get_db()
            notifications = []
            
            # Calculate workloads
            workloads = {}
            for user in target_users:
                active_count = db.query(Issue).filter(
                    and_(
                        Issue.assignee_id == user.id,
                        Issue.status != IssueStatus.DONE
                    )
                ).count()
                workloads[user.id] = {'user': user, 'count': active_count}
            
            if not workloads:
                return notifications
            
            avg_workload = sum(w['count'] for w in workloads.values()) / len(workloads)
            
            # Find significantly overloaded users
            for user_id, data in workloads.items():
                if data['count'] > avg_workload * 1.8 and data['count'] > 8:  # Significantly overloaded
                    notifications.append({
                        'user_id': user_id,
                        'user_name': data['user'].full_name,
                        'notification_type': 'workload_imbalance',
                        'message': f"High workload detected: {data['count']} active issues (team avg: {avg_workload:.1f})",
                        'priority': 3,
                        'actions': [
                            'Consider redistributing some issues',
                            'Review issue complexity and priorities',
                            'Request additional team support if needed'
                        ],
                        'created_at': datetime.utcnow().isoformat()
                    })
            
            return notifications
            
        except Exception as e:
            logger.error(f"Workload notification check failed: {e}")
            return []
        finally:
            db.close()
    
    async def _check_pattern_notifications(self, target_users: List[User]) -> List[Dict[str, Any]]:
        """Check for pattern-based notifications"""
        try:
            db = self.get_db()
            notifications = []
            
            # Check for unusual patterns in the last 24 hours
            day_ago = datetime.utcnow() - timedelta(days=1)
            recent_issues = db.query(Issue).filter(Issue.created_at >= day_ago).all()
            
            if len(recent_issues) > 10:  # Unusual spike
                for admin in [user for user in target_users if user.role == 'ADMIN']:
                    notifications.append({
                        'user_id': admin.id,
                        'user_name': admin.full_name,
                        'notification_type': 'pattern_detected',
                        'message': f"Unusual activity: {len(recent_issues)} issues created in last 24 hours",
                        'priority': 4,
                        'actions': [
                            'Investigate potential system issues',
                            'Review issue sources and patterns',
                            'Consider team capacity adjustments'
                        ],
                        'created_at': datetime.utcnow().isoformat()
                    })
            
            # Check for multiple critical issues
            critical_issues = [i for i in recent_issues if i.severity == IssueSeverity.CRITICAL]
            if len(critical_issues) >= 3:
                for admin in [user for user in target_users if user.role == 'ADMIN']:
                    notifications.append({
                        'user_id': admin.id,
                        'user_name': admin.full_name,
                        'notification_type': 'pattern_detected',
                        'message': f"Multiple critical issues: {len(critical_issues)} critical issues in 24 hours",
                        'priority': 5,
                        'actions': [
                            'Initiate incident response procedures',
                            'Review system stability',
                            'Consider emergency team mobilization'
                        ],
                        'created_at': datetime.utcnow().isoformat()
                    })
            
            return notifications
            
        except Exception as e:
            logger.error(f"Pattern notification check failed: {e}")
            return []
        finally:
            db.close()
    
    async def get_notification_summary(self, user: User, days: int = 7) -> Dict[str, Any]:
        """Get notification summary for a specific user"""
        try:
            # Generate notifications for this user
            notifications = await self.generate_smart_notifications([user])
            
            # Filter notifications for this user
            user_notifications = [n for n in notifications if n['user_id'] == user.id]
            
            # Categorize notifications
            urgent = [n for n in user_notifications if n.get('escalation_level') == 'urgent']
            escalations = [n for n in user_notifications if n.get('notification_type') == 'escalation_needed']
            workload = [n for n in user_notifications if n.get('notification_type') == 'workload_imbalance']
            patterns = [n for n in user_notifications if n.get('notification_type') == 'pattern_detected']
            
            return {
                'user_id': user.id,
                'user_name': user.full_name,
                'total_notifications': len(user_notifications),
                'urgent_count': len(urgent),
                'escalation_count': len(escalations),
                'workload_alerts': len(workload),
                'pattern_alerts': len(patterns),
                'notifications': user_notifications[:10],  # Top 10 notifications
                'summary_message': self._generate_summary_message(user_notifications),
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Notification summary failed for user {user.id}: {e}")
            return {
                'error': 'Failed to generate notification summary',
                'details': str(e)
            }
    
    def _generate_summary_message(self, notifications: List[Dict]) -> str:
        """Generate summary message for notifications"""
        if not notifications:
            return "✅ No urgent notifications at this time"
        
        urgent_count = len([n for n in notifications if n.get('escalation_level') == 'urgent'])
        escalation_count = len([n for n in notifications if n.get('notification_type') == 'escalation_needed'])
        
        if urgent_count > 0:
            return f"🚨 {urgent_count} urgent issues require immediate attention"
        elif escalation_count > 0:
            return f"⚠️ {escalation_count} issues need escalation or review"
        else:
            return f"📊 {len(notifications)} notifications for your review"