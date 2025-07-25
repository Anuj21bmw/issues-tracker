# backend/app/ai/analytics.py - Complete Predictive Analytics Implementation (FIXED)
import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, accuracy_score
from sqlalchemy import func, and_
from app.ai.base import AIBaseService
from app.models import Issue, User, IssueStatus, IssueSeverity

logger = logging.getLogger(__name__)

class PredictiveAnalytics(AIBaseService):
    """AI-powered predictive analytics for issue management"""
    
    def __init__(self):
        super().__init__()
        self.resolution_time_model = None
        self.escalation_model = None
        self.workload_model = None
        self.models_trained = False
        self._train_models()
    
    def _train_models(self):
        """Train ML models with historical data"""
        try:
            db = self.get_db()
            
            # Get historical data for training
            issues = db.query(Issue).filter(
                and_(Issue.status == IssueStatus.DONE, Issue.updated_at.isnot(None))
            ).all()
            
            if len(issues) < 50:  # Need minimum data for training
                logger.warning("Insufficient data for ML model training")
                return
            
            # Prepare training data
            training_data = []
            for issue in issues:
                resolution_hours = (issue.updated_at - issue.created_at).total_seconds() / 3600
                if resolution_hours > 0:  # Valid resolution time
                    features = self._extract_issue_features(issue)
                    features['resolution_hours'] = resolution_hours
                    training_data.append(features)
            
            if not training_data:
                return
            
            df = pd.DataFrame(training_data)
            
            # Train resolution time prediction model
            self._train_resolution_model(df)
            
            # Train escalation prediction model
            self._train_escalation_model(df)
            
            self.models_trained = True
            logger.info("ML models trained successfully")
            
        except Exception as e:
            logger.error(f"Model training failed: {e}")
        finally:
            db.close()
    
    def _extract_issue_features(self, issue: Issue) -> Dict[str, Any]:
        """Extract features from an issue for ML models"""
        features = {
            'severity_critical': 1 if issue.severity == IssueSeverity.CRITICAL else 0,
            'severity_high': 1 if issue.severity == IssueSeverity.HIGH else 0,
            'severity_medium': 1 if issue.severity == IssueSeverity.MEDIUM else 0,
            'severity_low': 1 if issue.severity == IssueSeverity.LOW else 0,
            'title_length': len(issue.title) if issue.title else 0,
            'description_length': len(issue.description) if issue.description else 0,
            'has_assignee': 1 if issue.assignee_id else 0,
            'tag_count': len(issue.tags) if issue.tags else 0,
            'reporter_experience': self._get_user_experience_score(issue.reporter_id) if issue.reporter_id else 0,
            'assignee_experience': self._get_user_experience_score(issue.assignee_id) if issue.assignee_id else 0,
            'created_hour': issue.created_at.hour,
            'created_day_of_week': issue.created_at.weekday(),
            'created_month': issue.created_at.month
        }
        
        # Text-based features
        text_content = f"{issue.title} {issue.description}".lower()
        features.update({
            'has_error_keywords': 1 if any(kw in text_content for kw in ['error', 'bug', 'crash', 'fail']) else 0,
            'has_performance_keywords': 1 if any(kw in text_content for kw in ['slow', 'performance', 'timeout']) else 0,
            'has_ui_keywords': 1 if any(kw in text_content for kw in ['ui', 'interface', 'design', 'layout']) else 0,
            'has_backend_keywords': 1 if any(kw in text_content for kw in ['api', 'server', 'database']) else 0,
            'complexity_high': 1 if any(kw in text_content for kw in ['complex', 'architecture', 'refactor']) else 0
        })
        
        return features
    
    def _get_user_experience_score(self, user_id: int) -> float:
        """Calculate user experience score based on resolved issues"""
        if not user_id:
            return 0.0
        
        cache_key = f"user_exp_{user_id}"
        cached_score = self._cache_get(cache_key)
        if cached_score is not None:
            return cached_score
        
        try:
            db = self.get_db()
            
            # Count resolved issues by user
            resolved_count = db.query(Issue).filter(
                and_(
                    Issue.assignee_id == user_id,
                    Issue.status == IssueStatus.DONE
                )
            ).count()
            
            # Simple experience scoring
            if resolved_count >= 50:
                score = 1.0
            elif resolved_count >= 20:
                score = 0.8
            elif resolved_count >= 10:
                score = 0.6
            elif resolved_count >= 5:
                score = 0.4
            else:
                score = 0.2
            
            self._cache_set(cache_key, score)
            return score
            
        except Exception as e:
            logger.error(f"User experience calculation failed: {e}")
            return 0.0
        finally:
            db.close()
    
    def _train_resolution_model(self, df: pd.DataFrame):
        """Train resolution time prediction model"""
        try:
            # Prepare features for resolution time prediction
            feature_columns = [col for col in df.columns if col != 'resolution_hours']
            X = df[feature_columns]
            y = df['resolution_hours']
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Train model
            self.resolution_time_model = RandomForestRegressor(n_estimators=100, random_state=42)
            self.resolution_time_model.fit(X_train, y_train)
            
            # Evaluate model
            y_pred = self.resolution_time_model.predict(X_test)
            mae = mean_absolute_error(y_test, y_pred)
            
            logger.info(f"Resolution time model trained. MAE: {mae:.2f} hours")
            
        except Exception as e:
            logger.error(f"Resolution time model training failed: {e}")
            self.resolution_time_model = None
    
    def _train_escalation_model(self, df: pd.DataFrame):
        """Train escalation prediction model"""
        try:
            # Create escalation labels (issues that took longer than expected)
            df['escalated'] = df.apply(lambda row: self._determine_if_escalated(row), axis=1)
            
            # Prepare features for escalation prediction
            feature_columns = [col for col in df.columns if col not in ['resolution_hours', 'escalated']]
            X = df[feature_columns]
            y = df['escalated']
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Train model
            self.escalation_model = RandomForestClassifier(n_estimators=100, random_state=42)
            self.escalation_model.fit(X_train, y_train)
            
            # Evaluate model
            y_pred = self.escalation_model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            logger.info(f"Escalation model trained. Accuracy: {accuracy:.2f}")
            
        except Exception as e:
            logger.error(f"Escalation model training failed: {e}")
            self.escalation_model = None
    
    def _determine_if_escalated(self, row: pd.Series) -> int:
        """Determine if an issue should be considered escalated based on resolution time"""
        resolution_hours = row['resolution_hours']
        
        # Define thresholds based on severity
        if row['severity_critical']:
            threshold = 8
        elif row['severity_high']:
            threshold = 24
        elif row['severity_medium']:
            threshold = 72
        else:  # Low severity
            threshold = 168
        
        return 1 if resolution_hours > threshold else 0
    
    async def predict_resolution_time(self, issue_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict resolution time for an issue"""
        try:
            if not self.models_trained or not self.resolution_time_model:
                return await self._fallback_time_prediction(issue_data)
            
            # Extract features
            features = self._extract_features_from_data(issue_data)
            feature_vector = np.array([list(features.values())]).reshape(1, -1)
            
            # Make prediction
            predicted_hours = self.resolution_time_model.predict(feature_vector)[0]
            predicted_hours = max(0.5, predicted_hours)  # Minimum 30 minutes
            
            # Get confidence interval
            confidence = self._calculate_prediction_confidence(features, predicted_hours)
            
            return {
                'predicted_hours': round(predicted_hours, 1),
                'predicted_time_formatted': self.format_duration(predicted_hours),
                'confidence': confidence,
                'prediction_range': {
                    'min_hours': round(predicted_hours * 0.7, 1),
                    'max_hours': round(predicted_hours * 1.5, 1)
                },
                'factors': self._get_prediction_factors(features),
                'prediction_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Resolution time prediction failed: {e}")
            return await self._fallback_time_prediction(issue_data)
    
    async def _fallback_time_prediction(self, issue_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback prediction based on historical averages"""
        try:
            severity = issue_data.get('severity', 'MEDIUM')
            
            # Historical averages by severity
            avg_times = {
                'CRITICAL': 6,
                'HIGH': 16,
                'MEDIUM': 24,
                'LOW': 48
            }
            
            predicted_hours = avg_times.get(severity, 24)
            
            return {
                'predicted_hours': predicted_hours,
                'predicted_time_formatted': self.format_duration(predicted_hours),
                'confidence': 0.6,
                'prediction_range': {
                    'min_hours': round(predicted_hours * 0.5, 1),
                    'max_hours': round(predicted_hours * 2, 1)
                },
                'factors': [f"Based on historical average for {severity} severity issues"],
                'prediction_timestamp': datetime.utcnow().isoformat(),
                'fallback': True
            }
            
        except Exception as e:
            logger.error(f"Fallback prediction failed: {e}")
            return {
                'predicted_hours': 24,
                'predicted_time_formatted': '1 day',
                'confidence': 0.3,
                'prediction_range': {'min_hours': 12, 'max_hours': 48},
                'factors': ['Default estimate due to prediction error'],
                'prediction_timestamp': datetime.utcnow().isoformat(),
                'error': True
            }
    
    async def predict_escalation_risk(self, issue_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict escalation risk for an issue"""
        try:
            if not self.models_trained or not self.escalation_model:
                return self._fallback_escalation_prediction(issue_data)
            
            # Extract features
            features = self._extract_features_from_data(issue_data)
            feature_vector = np.array([list(features.values())]).reshape(1, -1)
            
            # Make prediction
            escalation_probability = self.escalation_model.predict_proba(feature_vector)[0][1]
            risk_level = self._categorize_risk_level(escalation_probability)
            
            return {
                'escalation_probability': round(escalation_probability, 3),
                'risk_level': risk_level,
                'risk_factors': self._identify_risk_factors(features, escalation_probability),
                'recommended_actions': self._get_risk_mitigation_actions(risk_level),
                'prediction_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Escalation risk prediction failed: {e}")
            return self._fallback_escalation_prediction(issue_data)
    
    def _fallback_escalation_prediction(self, issue_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback escalation prediction based on simple rules"""
        severity = issue_data.get('severity', 'MEDIUM')
        has_assignee = bool(issue_data.get('assignee_id'))
        
        # Simple rule-based escalation risk
        if severity == 'CRITICAL':
            probability = 0.8 if not has_assignee else 0.6
        elif severity == 'HIGH':
            probability = 0.6 if not has_assignee else 0.4
        elif severity == 'MEDIUM':
            probability = 0.3 if not has_assignee else 0.2
        else:  # LOW
            probability = 0.1 if not has_assignee else 0.05
        
        risk_level = self._categorize_risk_level(probability)
        
        return {
            'escalation_probability': probability,
            'risk_level': risk_level,
            'risk_factors': [f"{severity} severity issue", "No assignee" if not has_assignee else "Has assignee"],
            'recommended_actions': self._get_risk_mitigation_actions(risk_level),
            'prediction_timestamp': datetime.utcnow().isoformat(),
            'fallback': True
        }
    
    def _extract_features_from_data(self, issue_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract features from issue data for prediction"""
        severity = issue_data.get('severity', 'MEDIUM')
        title = issue_data.get('title', '')
        description = issue_data.get('description', '')
        
        features = {
            'severity_critical': 1.0 if severity == 'CRITICAL' else 0.0,
            'severity_high': 1.0 if severity == 'HIGH' else 0.0,
            'severity_medium': 1.0 if severity == 'MEDIUM' else 0.0,
            'severity_low': 1.0 if severity == 'LOW' else 0.0,
            'title_length': float(len(title)),
            'description_length': float(len(description)),
            'has_assignee': 1.0 if issue_data.get('assignee_id') else 0.0,
            'tag_count': float(len(issue_data.get('tags', []))),
            'reporter_experience': float(issue_data.get('reporter_experience', 0.5)),
            'assignee_experience': float(issue_data.get('assignee_experience', 0.5)),
            'created_hour': float(datetime.now().hour),
            'created_day_of_week': float(datetime.now().weekday()),
            'created_month': float(datetime.now().month)
        }
        
        # Text-based features
        text_content = f"{title} {description}".lower()
        features.update({
            'has_error_keywords': 1.0 if any(kw in text_content for kw in ['error', 'bug', 'crash', 'fail']) else 0.0,
            'has_performance_keywords': 1.0 if any(kw in text_content for kw in ['slow', 'performance', 'timeout']) else 0.0,
            'has_ui_keywords': 1.0 if any(kw in text_content for kw in ['ui', 'interface', 'design', 'layout']) else 0.0,
            'has_backend_keywords': 1.0 if any(kw in text_content for kw in ['api', 'server', 'database']) else 0.0,
            'complexity_high': 1.0 if any(kw in text_content for kw in ['complex', 'architecture', 'refactor']) else 0.0
        })
        
        return features
    
    def _calculate_prediction_confidence(self, features: Dict, predicted_value: float) -> float:
        """Calculate confidence in the prediction"""
        confidence = 0.7  # Base confidence
        
        # Adjust based on available information
        if features.get('has_assignee', 0) == 1:
            confidence += 0.1
        
        if features.get('assignee_experience', 0) > 0.7:
            confidence += 0.1
        
        if features.get('description_length', 0) > 100:
            confidence += 0.05
        
        # Reduce confidence for edge cases
        if predicted_value < 1 or predicted_value > 200:  # Very short or very long predictions
            confidence -= 0.2
        
        return min(0.95, max(0.3, confidence))
    
    def _get_prediction_factors(self, features: Dict) -> List[str]:
        """Get factors that influenced the prediction"""
        factors = []
        
        if features.get('severity_critical', 0) == 1:
            factors.append("Critical severity increases urgency")
        elif features.get('severity_high', 0) == 1:
            factors.append("High severity requires priority attention")
        
        if features.get('has_assignee', 0) == 0:
            factors.append("No assignee may delay resolution")
        
        if features.get('assignee_experience', 0) > 0.8:
            factors.append("Experienced assignee may resolve faster")
        elif features.get('assignee_experience', 0) < 0.3:
            factors.append("Less experienced assignee may take longer")
        
        if features.get('complexity_high', 0) == 1:
            factors.append("Complex issue may require more time")
        
        if features.get('has_error_keywords', 0) == 1:
            factors.append("Clear error description helps diagnosis")
        
        return factors[:5]  # Limit to top 5 factors
    
    def _categorize_risk_level(self, probability: float) -> str:
        """Categorize escalation probability into risk levels"""
        if probability >= 0.7:
            return 'high'
        elif probability >= 0.4:
            return 'medium'
        elif probability >= 0.2:
            return 'low'
        else:
            return 'very_low'
    
    def _identify_risk_factors(self, features: Dict, probability: float) -> List[str]:
        """Identify factors contributing to escalation risk"""
        risk_factors = []
        
        if features.get('severity_critical', 0) == 1:
            risk_factors.append("Critical severity increases escalation risk")
        
        if features.get('has_assignee', 0) == 0:
            risk_factors.append("Unassigned issues have higher escalation risk")
        
        if features.get('complexity_high', 0) == 1:
            risk_factors.append("Complex issues are more likely to escalate")
        
        if features.get('assignee_experience', 0) < 0.3:
            risk_factors.append("Less experienced assignee increases risk")
        
        if features.get('description_length', 0) < 50:
            risk_factors.append("Insufficient description may lead to delays")
        
        if probability > 0.6:
            risk_factors.append("Historical patterns suggest high escalation likelihood")
        
        return risk_factors[:5]
    
    def _get_risk_mitigation_actions(self, risk_level: str) -> List[str]:
        """Get recommended actions to mitigate escalation risk"""
        actions = {
            'high': [
                "Assign to senior team member immediately",
                "Set up regular check-ins",
                "Prepare escalation plan",
                "Consider adding additional resources"
            ],
            'medium': [
                "Ensure proper assignment",
                "Monitor progress closely",
                "Provide necessary resources",
                "Set clear expectations"
            ],
            'low': [
                "Standard monitoring",
                "Ensure assignee has necessary information",
                "Regular status updates"
            ],
            'very_low': [
                "Normal process flow",
                "Standard check-ins"
            ]
        }
        
        return actions.get(risk_level, actions['medium'])
    
    async def predict_workload_distribution(self, users: List[User], days_ahead: int = 7) -> Dict[str, Any]:
        """Predict workload distribution for the next period"""
        try:
            db = self.get_db()
            current_time = datetime.utcnow()
            
            workload_predictions = {}
            
            for user in users:
                # Get current active issues
                active_issues = db.query(Issue).filter(
                    and_(
                        Issue.assignee_id == user.id,
                        Issue.status != IssueStatus.DONE
                    )
                ).all()
                
                # Predict completion times
                predicted_completions = []
                ongoing_workload = len(active_issues)
                
                for issue in active_issues:
                    issue_data = {
                        'severity': issue.severity.value,
                        'title': issue.title,
                        'description': issue.description,
                        'assignee_id': issue.assignee_id,
                        'assignee_experience': self._get_user_experience_score(user.id)
                    }
                    
                    time_prediction = await self.predict_resolution_time(issue_data)
                    predicted_hours = time_prediction['predicted_hours']
                    
                    completion_date = current_time + timedelta(hours=predicted_hours)
                    predicted_completions.append({
                        'issue_id': issue.id,
                        'predicted_completion': completion_date,
                        'estimated_hours': predicted_hours
                    })
                
                # Calculate workload over time
                future_workload = self._calculate_future_workload(
                    predicted_completions, current_time, days_ahead
                )
                
                workload_predictions[user.id] = {
                    'user_name': user.full_name,
                    'current_active_issues': ongoing_workload,
                    'predicted_completions': predicted_completions,
                    'workload_forecast': future_workload,
                    'overload_risk': 'high' if ongoing_workload > 10 else 'medium' if ongoing_workload > 6 else 'low'
                }
            
            # Generate team insights
            team_insights = self._generate_team_workload_insights(workload_predictions)
            
            return {
                'individual_predictions': workload_predictions,
                'team_insights': team_insights,
                'prediction_period_days': days_ahead,
                'generated_at': current_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Workload prediction failed: {e}")
            return {
                'individual_predictions': {},
                'team_insights': {'error': str(e)},
                'prediction_period_days': days_ahead,
                'generated_at': datetime.utcnow().isoformat()
            }
        finally:
            db.close()
    
    def _calculate_future_workload(self, completions: List[Dict], start_time: datetime, days: int) -> List[Dict]:
        """Calculate workload distribution over future days"""
        daily_workload = []
        
        for day in range(days):
            day_start = start_time + timedelta(days=day)
            day_end = day_start + timedelta(days=1)
            
            # Count issues active during this day
            active_count = 0
            for completion in completions:
                if completion['predicted_completion'] > day_start:
                    active_count += 1
            
            daily_workload.append({
                'date': day_start.date().isoformat(),
                'active_issues': active_count,
                'workload_level': 'high' if active_count > 8 else 'medium' if active_count > 4 else 'low'
            })
        
        return daily_workload
    
    def _generate_team_workload_insights(self, workload_predictions: Dict) -> Dict[str, Any]:
        """Generate insights about team workload distribution"""
        total_users = len(workload_predictions)
        if total_users == 0:
            return {'message': 'No workload data available'}
        
        # Calculate team statistics
        current_loads = [pred['current_active_issues'] for pred in workload_predictions.values()]
        avg_load = sum(current_loads) / len(current_loads)
        max_load = max(current_loads)
        min_load = min(current_loads)
        
        # Identify overloaded and underloaded users
        overloaded_users = [
            user_data['user_name'] for user_data in workload_predictions.values()
            if user_data['current_active_issues'] > avg_load * 1.5
        ]
        
        underloaded_users = [
            user_data['user_name'] for user_data in workload_predictions.values()
            if user_data['current_active_issues'] < avg_load * 0.5 and user_data['current_active_issues'] < 3
        ]
        
        insights = {
            'team_stats': {
                'average_workload': round(avg_load, 1),
                'max_workload': max_load,
                'min_workload': min_load,
                'load_distribution_balance': 'good' if (max_load - min_load) <= 5 else 'unbalanced'
            },
            'recommendations': [],
            'workload_alerts': []
        }
        
        # Generate recommendations
        if overloaded_users and underloaded_users:
            insights['recommendations'].append(
                f"Consider redistributing work from {', '.join(overloaded_users)} to {', '.join(underloaded_users)}"
            )
        
        if avg_load > 8:
            insights['workload_alerts'].append("Team average workload is high - consider hiring or reprioritization")
        
        if len(overloaded_users) > total_users * 0.3:
            insights['workload_alerts'].append("More than 30% of team members are overloaded")
        
        return insights
    
    async def analyze_resolution_patterns(self, days: int = 30) -> Dict[str, Any]:
        """Analyze resolution patterns and trends"""
        try:
            db = self.get_db()
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Get resolved issues in the period
            resolved_issues = db.query(Issue).filter(
                and_(
                    Issue.status == IssueStatus.DONE,
                    Issue.updated_at >= cutoff_date,
                    Issue.updated_at.isnot(None)
                )
            ).all()
            
            if not resolved_issues:
                return {'message': 'No resolved issues in the analysis period'}
            
            # Analyze patterns
            patterns = {
                'resolution_times_by_severity': self._analyze_resolution_by_severity(resolved_issues),
                'weekly_resolution_trends': self._analyze_weekly_trends(resolved_issues),
                'assignee_performance': self._analyze_assignee_performance(resolved_issues),
                'common_resolution_factors': self._identify_resolution_factors(resolved_issues),
                'bottlenecks': self._identify_resolution_bottlenecks(resolved_issues)
            }
            
            # Generate predictions based on patterns
            future_predictions = self._predict_future_performance(patterns)
            
            return {
                'analysis_period_days': days,
                'total_resolved_issues': len(resolved_issues),
                'patterns': patterns,
                'future_predictions': future_predictions,
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Resolution pattern analysis failed: {e}")
            return {
                'analysis_period_days': days,
                'error': str(e),
                'generated_at': datetime.utcnow().isoformat()
            }
        finally:
            db.close()
    
    def _analyze_resolution_by_severity(self, issues: List[Issue]) -> Dict[str, Any]:
        """Analyze resolution times by severity"""
        severity_stats = {}
        
        for severity in IssueSeverity:
            severity_issues = [i for i in issues if i.severity == severity]
            if severity_issues:
                resolution_times = [
                    self.get_business_hours_between(i.created_at, i.updated_at)
                    for i in severity_issues
                ]
                
                severity_stats[severity.value] = {
                    'count': len(severity_issues),
                    'avg_resolution_hours': round(sum(resolution_times) / len(resolution_times), 1),
                    'min_resolution_hours': round(min(resolution_times), 1),
                    'max_resolution_hours': round(max(resolution_times), 1),
                    'median_resolution_hours': round(sorted(resolution_times)[len(resolution_times)//2], 1)
                }
        
        return severity_stats
    
    def _analyze_weekly_trends(self, issues: List[Issue]) -> Dict[str, Any]:
        """Analyze weekly resolution trends"""
        weekly_data = {}
        
        for issue in issues:
            if issue.updated_at:
                week_start = issue.updated_at - timedelta(days=issue.updated_at.weekday())
                week_key = week_start.strftime('%Y-W%U')
                
                if week_key not in weekly_data:
                    weekly_data[week_key] = {'count': 0, 'total_hours': 0}
                
                resolution_hours = self.get_business_hours_between(issue.created_at, issue.updated_at)
                weekly_data[week_key]['count'] += 1
                weekly_data[week_key]['total_hours'] += resolution_hours
        
        # Calculate averages and trends
        for week_data in weekly_data.values():
            week_data['avg_resolution_hours'] = round(week_data['total_hours'] / week_data['count'], 1)
        
        return weekly_data
    
    def _analyze_assignee_performance(self, issues: List[Issue]) -> Dict[str, Any]:
        """Analyze performance by assignee"""
        assignee_stats = {}
        
        for issue in issues:
            if issue.assignee:
                assignee_name = issue.assignee.full_name
                if assignee_name not in assignee_stats:
                    assignee_stats[assignee_name] = {
                        'resolved_count': 0,
                        'total_resolution_hours': 0,
                        'severity_distribution': {s.value: 0 for s in IssueSeverity}
                    }
                
                resolution_hours = self.get_business_hours_between(issue.created_at, issue.updated_at)
                assignee_stats[assignee_name]['resolved_count'] += 1
                assignee_stats[assignee_name]['total_resolution_hours'] += resolution_hours
                assignee_stats[assignee_name]['severity_distribution'][issue.severity.value] += 1
        
        # Calculate averages
        for stats in assignee_stats.values():
            if stats['resolved_count'] > 0:
                stats['avg_resolution_hours'] = round(
                    stats['total_resolution_hours'] / stats['resolved_count'], 1
                )
        
        return assignee_stats
    
    def _identify_resolution_factors(self, issues: List[Issue]) -> List[str]:
        """Identify common factors in successful resolutions"""
        factors = []
        
        # Analyze assignment timing
        quick_assignments = sum(1 for i in issues if i.assignee_id)
        if quick_assignments / len(issues) > 0.8:
            factors.append("Most issues were properly assigned, leading to faster resolution")
        
        # Analyze severity distribution
        critical_count = sum(1 for i in issues if i.severity == IssueSeverity.CRITICAL)
        if critical_count / len(issues) > 0.2:
            factors.append("High proportion of critical issues resolved efficiently")
        
        # Analyze description quality
        detailed_descriptions = sum(1 for i in issues if len(i.description or '') > 100)
        if detailed_descriptions / len(issues) > 0.7:
            factors.append("Detailed issue descriptions contributed to faster resolution")
        
        return factors[:5]
    
    def _identify_resolution_bottlenecks(self, issues: List[Issue]) -> List[str]:
        """Identify potential bottlenecks in resolution process"""
        bottlenecks = []
        
        # Check for long resolution times
        long_resolutions = [
            i for i in issues 
            if self.get_business_hours_between(i.created_at, i.updated_at) > 72
        ]
        
        if len(long_resolutions) > len(issues) * 0.3:
            bottlenecks.append("30% of issues took longer than 3 business days to resolve")
        
        # Check for unassigned issues
        unassigned_resolutions = sum(1 for i in issues if not i.assignee_id)
        if unassigned_resolutions > len(issues) * 0.2:
            bottlenecks.append("Significant number of issues resolved without proper assignment")
        
        return bottlenecks
    
    def _predict_future_performance(self, patterns: Dict) -> Dict[str, Any]:
        """Predict future performance based on current patterns"""
        predictions = {}
        
        # Predict next week's resolution capacity
        if 'weekly_resolution_trends' in patterns:
            recent_weeks = list(patterns['weekly_resolution_trends'].values())[-4:]  # Last 4 weeks
            if recent_weeks:
                avg_weekly_resolutions = sum(w['count'] for w in recent_weeks) / len(recent_weeks)
                predictions['next_week_estimated_resolutions'] = round(avg_weekly_resolutions)
        
        # Predict workload based on current trends
        if 'assignee_performance' in patterns:
            total_assignees = len(patterns['assignee_performance'])
            if total_assignees > 0:
                predictions['team_capacity'] = f"Team can handle approximately {total_assignees * 3}-{total_assignees * 5} new issues per week"
        
        return predictions
    
    async def analyze_user_workload(self, user: User) -> Dict[str, Any]:
        """Analyze individual user workload patterns"""
        try:
            db = self.get_db()
            
            # Get user's issue history
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            user_issues = db.query(Issue).filter(
                and_(
                    Issue.assignee_id == user.id,
                    Issue.created_at >= thirty_days_ago
                )
            ).all()
            
            # Calculate performance metrics
            resolved_issues = [i for i in user_issues if i.status == IssueStatus.DONE]
            active_issues = [i for i in user_issues if i.status != IssueStatus.DONE]
            
            avg_resolution_time = 0
            if resolved_issues:
                total_hours = sum(
                    self.get_business_hours_between(i.created_at, i.updated_at)
                    for i in resolved_issues if i.updated_at
                )
                avg_resolution_time = total_hours / len(resolved_issues)
            
            # Analyze severity distribution
            severity_distribution = {}
            for severity in IssueSeverity:
                severity_distribution[severity.value] = sum(
                    1 for i in user_issues if i.severity == severity
                )
            
            workload_analysis = {
                'total_issues_30_days': len(user_issues),
                'resolved_issues': len(resolved_issues),
                'active_issues': len(active_issues),
                'resolution_rate': len(resolved_issues) / len(user_issues) if user_issues else 0,
                'avg_resolution_hours': round(avg_resolution_time, 1),
                'avg_resolution_formatted': self.format_duration(avg_resolution_time),
                'severity_distribution': severity_distribution,
                'performance_rating': self._calculate_performance_rating(
                    len(resolved_issues), avg_resolution_time, len(user_issues)
                )
            }
            
            return workload_analysis
            
        except Exception as e:
            logger.error(f"User workload analysis failed: {e}")
            return {}
        finally:
            db.close()
    
    def _calculate_performance_rating(self, resolved_count: int, avg_time: float, total_issues: int) -> str:
        """Calculate user performance rating"""
        if total_issues == 0:
            return 'insufficient_data'
        
        resolution_rate = resolved_count / total_issues
        
        # Simple performance rating logic
        if resolution_rate >= 0.9 and avg_time <= 24:
            return 'excellent'
        elif resolution_rate >= 0.8 and avg_time <= 48:
            return 'good'
        elif resolution_rate >= 0.6 and avg_time <= 72:
            return 'average'
        else:
            return 'needs_improvement'
    
    async def get_predictive_insights(self, days_back: int = 30) -> Dict[str, Any]:
        """Get comprehensive predictive insights for the system"""
        try:
            db = self.get_db()
            
            # Analyze trends
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            recent_issues = db.query(Issue).filter(Issue.created_at >= cutoff_date).all()
            
            if not recent_issues:
                return {'message': 'Insufficient data for insights'}
            
            # Issue creation trends
            daily_creation = {}
            for issue in recent_issues:
                date_key = issue.created_at.date().isoformat()
                if date_key not in daily_creation:
                    daily_creation[date_key] = 0
                daily_creation[date_key] += 1
            
            # Calculate trend
            daily_counts = list(daily_creation.values())
            if len(daily_counts) > 7:
                recent_avg = sum(daily_counts[-7:]) / 7
                older_avg = sum(daily_counts[-14:-7]) / 7 if len(daily_counts) > 14 else recent_avg
                trend_percentage = ((recent_avg - older_avg) / older_avg * 100) if older_avg > 0 else 0
            else:
                trend_percentage = 0
            
            # Severity distribution trends
            severity_trends = {}
            for severity in IssueSeverity:
                severity_count = sum(1 for i in recent_issues if i.severity == severity)
                severity_trends[severity.value] = {
                    'count': severity_count,
                    'percentage': round((severity_count / len(recent_issues)) * 100, 1) if recent_issues else 0
                }
            
            # Resolution efficiency
            resolved_recent = [i for i in recent_issues if i.status == IssueStatus.DONE]
            avg_resolution_time = 0
            if resolved_recent:
                total_hours = sum(
                    self.get_business_hours_between(i.created_at, i.updated_at)
                    for i in resolved_recent if i.updated_at
                )
                avg_resolution_time = total_hours / len(resolved_recent)
            
            # Predict next week
            current_weekly_rate = len(recent_issues) / (days_back / 7)
            predicted_next_week = round(current_weekly_rate * (1 + trend_percentage / 100))
            
            insights = {
                'period_analyzed_days': days_back,
                'total_issues': len(recent_issues),
                'daily_creation_trend': {
                    'trend_percentage': round(trend_percentage, 1),
                    'direction': 'increasing' if trend_percentage > 5 else 'decreasing' if trend_percentage < -5 else 'stable'
                },
                'severity_distribution': severity_trends,
                'resolution_metrics': {
                    'resolved_count': len(resolved_recent),
                    'resolution_rate': round((len(resolved_recent) / len(recent_issues)) * 100, 1) if recent_issues else 0,
                    'avg_resolution_time': self.format_duration(avg_resolution_time),
                    'avg_resolution_hours': round(avg_resolution_time, 1)
                },
                'predictions': {
                    'next_week_issues': predicted_next_week,
                    'workload_status': 'high' if predicted_next_week > current_weekly_rate * 1.2 else 'normal',
                    'recommended_capacity': max(predicted_next_week, round(current_weekly_rate))
                },
                'recommendations': self._generate_system_recommendations(
                    trend_percentage, severity_trends, avg_resolution_time
                ),
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Predictive insights generation failed: {e}")
            return {
                'error': str(e),
                'generated_at': datetime.utcnow().isoformat()
            }
        finally:
            db.close()
    
    def _generate_system_recommendations(self, trend: float, severity_trends: Dict, avg_resolution: float) -> List[str]:
        """Generate system-wide recommendations based on analysis"""
        recommendations = []
        
        # Trend-based recommendations
        if trend > 15:
            recommendations.append("Issue creation is increasing rapidly - consider expanding team capacity")
        elif trend > 5:
            recommendations.append("Moderate increase in issues - monitor team workload closely")
        elif trend < -15:
            recommendations.append("Issue creation decreasing - good opportunity for process improvements")
        
        # Severity-based recommendations
        critical_percentage = severity_trends.get('CRITICAL', {}).get('percentage', 0)
        if critical_percentage > 20:
            recommendations.append("High percentage of critical issues - review quality assurance processes")
        elif critical_percentage > 10:
            recommendations.append("Monitor critical issue patterns for potential systemic problems")
        
        # Resolution time recommendations
        if avg_resolution > 72:
            recommendations.append("Average resolution time is high - consider process optimization")
        elif avg_resolution > 48:
            recommendations.append("Resolution times are above target - review assignment efficiency")
        elif avg_resolution < 12:
            recommendations.append("Excellent resolution times - consider documenting best practices")
        
        # Default recommendation if none apply
        if not recommendations:
            recommendations.append("System performance is stable - continue current practices")
        
        return recommendations[:5]  # Limit to top 5
    
    def get_analytics_stats(self) -> Dict[str, Any]:
        """Get analytics service statistics"""
        return {
            'service_status': 'active',
            'models_trained': self.models_trained,
            'resolution_model_available': self.resolution_time_model is not None,
            'escalation_model_available': self.escalation_model is not None,
            'feature_count': 15,  # Number of features used in models
            'last_updated': datetime.utcnow().isoformat(),
            'capabilities': [
                'Resolution time prediction',
                'Escalation risk assessment',
                'Workload distribution forecasting',
                'Pattern analysis',
                'Performance insights'
            ]
        }