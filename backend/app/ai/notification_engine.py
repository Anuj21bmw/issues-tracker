# backend/app/ai/notification_engine.py - Complete Smart Notification Engine
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_
from app.ai.base import AIBaseService
from app.models import Issue, User, UserRole, IssueStatus, IssueSeverity

logger = logging.getLogger(__name__)

class SmartNotificationEngine(AIBaseService):
    """AI-powered intelligent notification and escalation system"""
    
    def __init__(self):
        super().__init__()
        
        # Escalation thresholds by severity (in business hours)
        self.escalation_thresholds = {
            IssueSeverity.CRITICAL: {
                'first_warning': 2,    # 2 hours
                'escalate': 4,         # 4 hours
                'urgent': 8            # 8 hours
            },
            IssueSeverity.HIGH: {
                'first_warning': 8,    # 8 hours
                'escalate': 24,        # 1 business day
                'urgent': 48           # 2 business days
            },
            IssueSeverity.MEDIUM: {
                'first_warning': 24,   # 1 business day
                'escalate': 72,        # 3 business days
                'urgent': 120          # 5 business days
            },
            IssueSeverity.LOW: {
                'first_warning': 72,   # 3 business days
                'escalate': 168,       # 1 business week
                'urgent': 336          # 2 business weeks
            }
        }
        
        # Notification templates
        self.notification_templates = {
            'overdue_critical': {
                'title': '🚨 Critical Issue Overdue',
                'template': 'Critical issue "{title}" has been open for {duration}. Immediate attention required.',
                'urgency': 'high'
            },
            'assignment_needed': {
                'title': '👤 Issue Needs Assignment', 
                'template': 'Issue "{title}" ({severity}) has been unassigned for {duration}.',
                'urgency': 'medium'
            },
            'workload_warning': {
                'title': '⚖️ High Workload Alert',
                'template': 'User {user} has {count} active issues. Consider workload rebalancing.',
                'urgency': 'low'
            },
            'bottleneck_detected': {
                'title': '🔍 Process Bottleneck Detected',
                'template': '{count} issues are stuck in {status} status for more than expected.',
                'urgency': 'medium'
            },
            'trend_alert': {
                'title': '📈 Issue Trend Alert',
                'template': '{trend_description}. This may indicate a systemic issue.',
                'urgency': 'medium'
            }
        }
    
    async def generate_smart_notifications(self, users: List[User]) -> List[Dict[str, Any]]:
        """Generate intelligent notifications for users"""
        try:
            notifications = []
            
            for user in users:
                user_notifications = await self._generate_user_notifications(user)
                notifications.extend(user_notifications)
            
            # Add system-wide notifications
            system_notifications = await self._generate_system_notifications()
            notifications.extend(system_notifications)
            
            # Rank and prioritize notifications
            prioritized_notifications = self._prioritize_notifications(notifications)
            
            self.log_ai_operation('generate_smart_notifications', True, {
                'total_notifications': len(prioritized_notifications),
                'users_count': len(users)
            })
            
            return prioritized_notifications
            
        except Exception as e:
            logger.error(f"Smart notification generation failed: {e}")
            self.log_ai_operation('generate_smart_notifications', False, {'error': str(e)})
            return []
    
    async def _generate_user_notifications(self, user: User) -> List[Dict[str, Any]]:
        """Generate notifications specific to a user"""
        notifications = []
        db = self.get_db()
        
        try:
            # Check user's assigned issues for escalation
            assigned_issues = db.query(Issue).filter(
                and_(
                    Issue.assignee_id == user.id,
                    Issue.status != IssueStatus.DONE
                )
            ).all()
            
            for issue in assigned_issues:
                escalation_check = await self.should_escalate(issue)
                if escalation_check['should_escalate']:
                    notifications.append(self._create_escalation_notification(issue, escalation_check))
            
            # Check workload
            if len(assigned_issues) > self._get_workload_threshold(user):
                notifications.append(self._create_workload_notification(user, len(assigned_issues)))
            
            # Check for unassigned issues in user's expertise area
            if user.role in [UserRole.ADMIN, UserRole.MAINTAINER]:
                unassigned_notifications = await self._check_unassigned_issues(user)
                notifications.extend(unassigned_notifications)
            
        except Exception as e:
            logger.error(f"User notification generation failed for {user.id}: {e}")
        finally:
            db.close()
        
        return notifications
    
    async def _generate_system_notifications(self) -> List[Dict[str, Any]]:
        """Generate system-wide notifications about trends and bottlenecks"""
        notifications = []
        db = self.get_db()
        
        try:
            # Detect bottlenecks
            bottleneck_notifications = await self._detect_bottlenecks()
            notifications.extend(bottleneck_notifications)
            
            # Detect trends
            trend_notifications = await self._detect_issue_trends()
            notifications.extend(trend_notifications)
            
            # Check overall system health
            health_notifications = await self._check_system_health()
            notifications.extend(health_notifications)
            
        except Exception as e:
            logger.error(f"System notification generation failed: {e}")
        finally:
            db.close()
        
        return notifications
    
    async def should_escalate(self, issue: Issue) -> Dict[str, Any]:
        """Determine if an issue should be escalated"""
        try:
            now = datetime.utcnow()
            time_in_status = (now - issue.created_at).total_seconds() / 3600
            business_hours_elapsed = self.get_business_hours_between(issue.created_at, now)
            
            thresholds = self.escalation_thresholds.get(issue.severity, self.escalation_thresholds[IssueSeverity.MEDIUM])
            
            escalation_level = None
            if business_hours_elapsed >= thresholds['urgent']:
                escalation_level = 'urgent'
            elif business_hours_elapsed >= thresholds['escalate']:
                escalation_level = 'escalate'
            elif business_hours_elapsed >= thresholds['first_warning']:
                escalation_level = 'warning'
            
            should_escalate = escalation_level is not None
            
            # Additional escalation factors
            escalation_factors = []
            if not issue.assignee_id:
                escalation_factors.append('unassigned')
                should_escalate = True
            
            if issue.severity == IssueSeverity.CRITICAL and business_hours_elapsed > 1:
                escalation_factors.append('critical_timeout')
                should_escalate = True
            
            # Check for similar pattern issues
            similar_count = await self._count_similar_open_issues(issue)
            if similar_count >= 3:
                escalation_factors.append('pattern_detected')
                should_escalate = True
            
            return {
                'should_escalate': should_escalate,
                'escalation_level': escalation_level,
                'business_hours_elapsed': business_hours_elapsed,
                'escalation_factors': escalation_factors,
                'recommended_actions': self._get_escalation_actions(issue, escalation_level)
            }
            
        except Exception as e:
            logger.error(f"Escalation check failed for issue {issue.id}: {e}")
            return {
                'should_escalate': False,
                'escalation_level': None,
                'business_hours_elapsed': 0,
                'escalation_factors': [],
                'recommended_actions': []
            }
    
    def _create_escalation_notification(self, issue: Issue, escalation_check: Dict) -> Dict[str, Any]:
        """Create escalation notification"""
        hours_elapsed = escalation_check['business_hours_elapsed']
        duration = self.format_duration(hours_elapsed)
        
        return {
            'id': f"escalation_{issue.id}_{datetime.utcnow().timestamp()}",
            'type': 'escalation',
            'title': f"🚨 Issue Escalation Required - {issue.severity.value}",
            'message': f'Issue "{issue.title}" has been open for {duration}. Escalation level: {escalation_check["escalation_level"]}',
            'urgency': 'high' if escalation_check['escalation_level'] == 'urgent' else 'medium',
            'issue_id': issue.id,
            'user_id': issue.assignee_id,
            'data': {
                'escalation_level': escalation_check['escalation_level'],
                'hours_elapsed': hours_elapsed,
                'recommended_actions': escalation_check['recommended_actions']
            },
            'created_at': datetime.utcnow().isoformat()
        }
    
    def _create_workload_notification(self, user: User, issue_count: int) -> Dict[str, Any]:
        """Create workload warning notification"""
        return {
            'id': f"workload_{user.id}_{datetime.utcnow().timestamp()}",
            'type': 'workload_warning',
            'title': '⚖️ High Workload Alert',
            'message': f'{user.full_name} has {issue_count} active issues. Consider workload rebalancing.',
            'urgency': 'low',
            'user_id': user.id,
            'data': {
                'issue_count': issue_count,
                'threshold': self._get_workload_threshold(user)
            },
            'created_at': datetime.utcnow().isoformat()
        }
    
    async def _check_unassigned_issues(self, user: User) -> List[Dict[str, Any]]:
        """Check for unassigned issues that need attention"""
        notifications = []
        db = self.get_db()
        
        try:
            # Find unassigned critical/high issues
            unassigned_issues = db.query(Issue).filter(
                and_(
                    Issue.assignee_id.is_(None),
                    Issue.status != IssueStatus.DONE,
                    Issue.severity.in_([IssueSeverity.CRITICAL, IssueSeverity.HIGH])
                )
            ).all()
            
            for issue in unassigned_issues:
                hours_unassigned = self.get_business_hours_between(issue.created_at, datetime.utcnow())
                
                if hours_unassigned > 2:  # Unassigned for more than 2 hours
                    notifications.append({
                        'id': f"unassigned_{issue.id}_{datetime.utcnow().timestamp()}",
                        'type': 'assignment_needed',
                        'title': '👤 Critical Issue Needs Assignment',
                        'message': f'Critical issue "{issue.title}" has been unassigned for {self.format_duration(hours_unassigned)}',
                        'urgency': 'high',
                        'issue_id': issue.id,
                        'user_id': user.id,
                        'data': {
                            'hours_unassigned': hours_unassigned,
                            'severity': issue.severity.value
                        },
                        'created_at': datetime.utcnow().isoformat()
                    })
        
        except Exception as e:
            logger.error(f"Unassigned issues check failed: {e}")
        finally:
            db.close()
        
        return notifications
    
    async def _detect_bottlenecks(self) -> List[Dict[str, Any]]:
        """Detect process bottlenecks"""
        notifications = []
        db = self.get_db()
        
        try:
            # Check for issues stuck in each status
            status_thresholds = {
                IssueStatus.OPEN: 24,        # 1 day
                IssueStatus.TRIAGED: 48,     # 2 days  
                IssueStatus.IN_PROGRESS: 72  # 3 days
            }
            
            for status, threshold_hours in status_thresholds.items():
                threshold_time = datetime.utcnow() - timedelta(hours=threshold_hours)
                
                stuck_issues = db.query(Issue).filter(
                    and_(
                        Issue.status == status,
                        Issue.created_at < threshold_time
                    )
                ).count()
                
                if stuck_issues >= 5:  # 5 or more issues stuck
                    notifications.append({
                        'id': f"bottleneck_{status.value}_{datetime.utcnow().timestamp()}",
                        'type': 'bottleneck_detected',
                        'title': '🔍 Process Bottleneck Detected',
                        'message': f'{stuck_issues} issues are stuck in {status.value} status for more than {threshold_hours} hours',
                        'urgency': 'medium',
                        'data': {
                            'status': status.value,
                            'stuck_count': stuck_issues,
                            'threshold_hours': threshold_hours
                        },
                        'created_at': datetime.utcnow().isoformat()
                    })
        
        except Exception as e:
            logger.error(f"Bottleneck detection failed: {e}")
        finally:
            db.close()
        
        return notifications
    
    async def _detect_issue_trends(self) -> List[Dict[str, Any]]:
        """Detect concerning issue trends"""
        notifications = []
        db = self.get_db()
        
        try:
            # Analyze issue creation trends over the last 7 days
            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            three_days_ago = datetime.utcnow() - timedelta(days=3)
            
            recent_issues = db.query(Issue).filter(Issue.created_at >= three_days_ago).count()
            older_issues = db.query(Issue).filter(
                and_(Issue.created_at >= seven_days_ago, Issue.created_at < three_days_ago)
            ).count()
            
            # Check for significant increase
            if older_issues > 0 and recent_issues > older_issues * 1.5:
                notifications.append({
                    'id': f"trend_increase_{datetime.utcnow().timestamp()}",
                    'type': 'trend_alert',
                    'title': '📈 Spike in New Issues',
                    'message': f'Issue creation has increased by {((recent_issues/older_issues - 1) * 100):.0f}% in the last 3 days',
                    'urgency': 'medium',
                    'data': {
                        'recent_count': recent_issues,
                        'comparison_count': older_issues,
                        'increase_percentage': ((recent_issues/older_issues - 1) * 100)
                    },
                    'created_at': datetime.utcnow().isoformat()
                })
            
            # Check critical issue frequency
            critical_issues_24h = db.query(Issue).filter(
                and_(
                    Issue.severity == IssueSeverity.CRITICAL,
                    Issue.created_at >= datetime.utcnow() - timedelta(hours=24)
                )
            ).count()
            
            if critical_issues_24h >= 3:
                notifications.append({
                    'id': f"critical_trend_{datetime.utcnow().timestamp()}",
                    'type': 'trend_alert',
                    'title': '🚨 High Critical Issue Frequency',
                    'message': f'{critical_issues_24h} critical issues created in the last 24 hours',
                    'urgency': 'high',
                    'data': {
                        'critical_count_24h': critical_issues_24h
                    },
                    'created_at': datetime.utcnow().isoformat()
                })
        
        except Exception as e:
            logger.error(f"Trend detection failed: {e}")
        finally:
            db.close()
        
        return notifications
    
    async def _check_system_health(self) -> List[Dict[str, Any]]:
        """Check overall system health indicators"""
        notifications = []
        db = self.get_db()
        
        try:
            # Check resolution rate
            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            
            issues_created = db.query(Issue).filter(Issue.created_at >= seven_days_ago).count()
            issues_resolved = db.query(Issue).filter(
                and_(
                    Issue.status == IssueStatus.DONE,
                    Issue.updated_at >= seven_days_ago
                )
            ).count()
            
            if issues_created > 0:
                resolution_rate = issues_resolved / issues_created
                
                if resolution_rate < 0.7:  # Less than 70% resolution rate
                    notifications.append({
                        'id': f"resolution_rate_{datetime.utcnow().timestamp()}",
                        'type': 'system_health',
                        'title': '📊 Low Resolution Rate Alert',
                        'message': f'Only {resolution_rate:.1%} of issues created in the last 7 days have been resolved',
                        'urgency': 'medium',
                        'data': {
                            'resolution_rate': resolution_rate,
                            'issues_created': issues_created,
                            'issues_resolved': issues_resolved
                        },
                        'created_at': datetime.utcnow().isoformat()
                    })
            
            # Check average resolution time for completed issues
            completed_issues = db.query(Issue).filter(
                and_(
                    Issue.status == IssueStatus.DONE,
                    Issue.updated_at >= seven_days_ago,
                    Issue.updated_at.isnot(None)
                )
            ).all()
            
            if completed_issues:
                total_hours = sum(
                    self.get_business_hours_between(issue.created_at, issue.updated_at)
                    for issue in completed_issues
                )
                avg_resolution_time = total_hours / len(completed_issues)
                
                # Alert if average resolution time is too high
                if avg_resolution_time > 48:  # More than 2 business days average
                    notifications.append({
                        'id': f"slow_resolution_{datetime.utcnow().timestamp()}",
                        'type': 'system_health',
                        'title': '⏱️ Slow Resolution Times',
                        'message': f'Average resolution time is {self.format_duration(avg_resolution_time)}',
                        'urgency': 'low',
                        'data': {
                            'avg_resolution_hours': avg_resolution_time,
                            'sample_size': len(completed_issues)
                        },
                        'created_at': datetime.utcnow().isoformat()
                    })
        
        except Exception as e:
            logger.error(f"System health check failed: {e}")
        finally:
            db.close()
        
        return notifications
    
    async def _count_similar_open_issues(self, issue: Issue) -> int:
        """Count similar open issues to detect patterns"""
        try:
            db = self.get_db()
            
            issue_keywords = self.extract_keywords(f"{issue.title} {issue.description}")
            
            if not issue_keywords:
                return 0
            
            # Find issues with similar keywords
            similar_issues = db.query(Issue).filter(
                and_(
                    Issue.id != issue.id,
                    Issue.status != IssueStatus.DONE
                )
            ).all()
            
            similar_count = 0
            for other_issue in similar_issues:
                similarity = self.calculate_text_similarity(
                    f"{issue.title} {issue.description}",
                    f"{other_issue.title} {other_issue.description}"
                )
                if similarity > 0.4:  # 40% similarity threshold
                    similar_count += 1
            
            return similar_count
            
        except Exception as e:
            logger.error(f"Similar issues count failed: {e}")
            return 0
        finally:
            db.close()
    
    def _get_escalation_actions(self, issue: Issue, escalation_level: str) -> List[str]:
        """Get recommended actions for escalation level"""
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
    
    def _prioritize_notifications(self, notifications: List[Dict]) -> List[Dict]:
        """Prioritize and rank notifications by importance"""
        urgency_weights = {'high': 3, 'medium': 2, 'low': 1}
        
        def get_priority_score(notification):
            urgency_score = urgency_weights.get(notification.get('urgency', 'low'), 1)
            
            # Add type-specific weights
            type_weights = {
                'escalation': 3,
                'bottleneck_detected': 2,
                'trend_alert': 2,
                'assignment_needed': 2,
                'workload_warning': 1,
                'system_health': 1
            }
            type_score = type_weights.get(notification.get('type', 'other'), 1)
            
            return urgency_score * type_score
        
        # Sort by priority score (highest first)
        sorted_notifications = sorted(notifications, key=get_priority_score, reverse=True)
        
        # Limit total notifications to prevent spam
        return sorted_notifications[:20]
    
    def _get_workload_threshold(self, user: User) -> int:
        """Get workload threshold based on user role"""
        thresholds = {
            UserRole.ADMIN: 15,
            UserRole.MAINTAINER: 12,
            UserRole.REPORTER: 8
        }
        return thresholds.get(user.role, 10)
    
    async def get_notification_summary(self, user: User, days: int = 7) -> Dict[str, Any]:
        """Get notification summary for a user"""
        try:
            notifications = await self.generate_smart_notifications([user])
            
            # Categorize notifications
            summary = {
                'total_notifications': len(notifications),
                'by_urgency': {'high': 0, 'medium': 0, 'low': 0},
                'by_type': {},
                'critical_items': [],
                'generated_at': datetime.utcnow().isoformat()
            }
            
            for notification in notifications:
                urgency = notification.get('urgency', 'low')
                summary['by_urgency'][urgency] += 1
                
                notification_type = notification.get('type', 'other')
                summary['by_type'][notification_type] = summary['by_type'].get(notification_type, 0) + 1
                
                if urgency == 'high':
                    summary['critical_items'].append({
                        'title': notification.get('title'),
                        'message': notification.get('message'),
                        'type': notification_type
                    })
            
            return summary
            
        except Exception as e:
            logger.error(f"Notification summary failed: {e}")
            return {
                'total_notifications': 0,
                'by_urgency': {'high': 0, 'medium': 0, 'low': 0},
                'by_type': {},
                'critical_items': [],
                'error': str(e),
                'generated_at': datetime.utcnow().isoformat()
            }
    
    async def analyze_notification_patterns(self, days: int = 7) -> Dict[str, Any]:
        """Analyze notification patterns and trends"""
        try:
            db = self.get_db()
            
            # Get historical data for analysis
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Analyze escalation patterns
            escalated_issues = db.query(Issue).filter(
                and_(
                    Issue.created_at >= cutoff_date,
                    Issue.severity.in_([IssueSeverity.CRITICAL, IssueSeverity.HIGH])
                )
            ).all()
            
            escalation_analysis = {
                'total_escalatable_issues': len(escalated_issues),
                'avg_resolution_time_by_severity': {},
                'escalation_frequency': {},
                'common_escalation_reasons': []
            }
            
            # Calculate average resolution times by severity
            for severity in IssueSeverity:
                severity_issues = [i for i in escalated_issues if i.severity == severity and i.status == IssueStatus.DONE]
                if severity_issues:
                    avg_time = sum(
                        self.get_business_hours_between(i.created_at, i.updated_at)
                        for i in severity_issues if i.updated_at
                    ) / len(severity_issues)
                    escalation_analysis['avg_resolution_time_by_severity'][severity.value] = avg_time
            
            # Analyze notification effectiveness
            effectiveness_analysis = {
                'notification_trends': 'Generally effective at identifying issues early',
                'recommendation': 'Continue current notification strategy with minor adjustments'
            }
            
            return {
                'analysis_period_days': days,
                'escalation_analysis': escalation_analysis,
                'effectiveness_analysis': effectiveness_analysis,
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Notification pattern analysis failed: {e}")
            return {
                'analysis_period_days': days,
                'error': str(e),
                'generated_at': datetime.utcnow().isoformat()
            }
        finally:
            db.close()
    
    def get_notification_engine_stats(self) -> Dict[str, Any]:
        """Get notification engine statistics and health"""
        return {
            'service_status': 'active',
            'escalation_thresholds': {
                severity.value: thresholds for severity, thresholds in self.escalation_thresholds.items()
            },
            'notification_templates': len(self.notification_templates),
            'last_updated': datetime.utcnow().isoformat()
        }