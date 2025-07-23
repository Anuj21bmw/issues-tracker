# backend/app/ai/analytics.py
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
    
    def _extract_issue_features(self, issue: Issue) -> Dict:
        """Extract features from issue for ML models"""
        title_length = len(issue.title) if issue.title else 0
        desc_length = len(issue.description) if issue.description else 0
        
        # Count keywords
        text = f"{issue.title} {issue.description}".lower()
        bug_keywords = ['bug', 'error', 'crash', 'fail', 'broken']
        feature_keywords = ['feature', 'enhancement', 'improvement', 'request']
        critical_keywords = ['critical', 'urgent', 'asap', 'down', 'outage']
        
        return {
            'severity_critical': 1 if issue.severity == IssueSeverity.CRITICAL else 0,
            'severity_high': 1 if issue.severity == IssueSeverity.HIGH else 0,
            'severity_medium': 1 if issue.severity == IssueSeverity.MEDIUM else 0,
            'severity_low': 1 if issue.severity == IssueSeverity.LOW else 0,
            'title_length': title_length,
            'desc_length': desc_length,
            'has_attachment': 1 if issue.file_path else 0,
            'has_tags': 1 if issue.tags else 0,
            'bug_keyword_count': sum(1 for keyword in bug_keywords if keyword in text),
            'feature_keyword_count': sum(1 for keyword in feature_keywords if keyword in text),
            'critical_keyword_count': sum(1 for keyword in critical_keywords if keyword in text),
            'reporter_experience': self._get_user_experience(issue.reporter_id),
            'hour_created': issue.created_at.hour,
            'day_of_week': issue.created_at.weekday()
        }
    
    def _get_user_experience(self, user_id: int) -> int:
        """Get user experience level (number of issues reported/resolved)"""
        try:
            db = self.get_db()
            count = db.query(Issue).filter(Issue.reporter_id == user_id).count()
            return min(count, 100)  # Cap at 100 for normalization
        except:
            return 0
        finally:
            db.close()
    
    def _train_resolution_model(self, df: pd.DataFrame):
        """Train model to predict resolution time"""
        try:
            feature_cols = [col for col in df.columns if col != 'resolution_hours']
            X = df[feature_cols]
            y = df['resolution_hours']
            
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            self.resolution_time_model = RandomForestRegressor(n_estimators=100, random_state=42)
            self.resolution_time_model.fit(X_train, y_train)
            
            # Evaluate model
            y_pred = self.resolution_time_model.predict(X_test)
            mae = mean_absolute_error(y_test, y_pred)
            logger.info(f"Resolution time model MAE: {mae:.2f} hours")
            
        except Exception as e:
            logger.error(f"Resolution model training failed: {e}")
    
    def _train_escalation_model(self, df: pd.DataFrame):
        """Train model to predict if issue needs escalation"""
        try:
            # Define escalation based on resolution time vs severity
            escalation_threshold = {
                1: 8,   # Critical: >8 hours
                2: 48,  # High: >48 hours  
                3: 168, # Medium: >1 week
                4: 336  # Low: >2 weeks
            }
            
            df['needs_escalation'] = df.apply(
                lambda row: 1 if row['resolution_hours'] > escalation_threshold.get(
                    row['severity_critical'] + row['severity_high'] * 2 + 
                    row['severity_medium'] * 3 + row['severity_low'] * 4, 168
                ) else 0, axis=1
            )
            
            feature_cols = [col for col in df.columns if col not in ['resolution_hours', 'needs_escalation']]
            X = df[feature_cols]
            y = df['needs_escalation']
            
            if y.sum() > 5:  # Need some positive cases
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
                
                self.escalation_model = RandomForestClassifier(n_estimators=100, random_state=42)
                self.escalation_model.fit(X_train, y_train)
                
                # Evaluate model
                y_pred = self.escalation_model.predict(X_test)
                accuracy = accuracy_score(y_test, y_pred)
                logger.info(f"Escalation model accuracy: {accuracy:.2f}")
            
        except Exception as e:
            logger.error(f"Escalation model training failed: {e}")
    
    async def predict_resolution_time(self, issue_data: Dict) -> Dict:
        """Predict how long an issue will take to resolve"""
        try:
            if not self.models_trained or not self.resolution_time_model:
                return await self._fallback_time_prediction(issue_data)
            
            # Extract features for prediction
            features = self._extract_prediction_features(issue_data)
            feature_array = np.array([list(features.values())])
            
            # Make prediction
            predicted_hours = self.resolution_time_model.predict(feature_array)[0]
            predicted_hours = max(1, int(predicted_hours))  # Minimum 1 hour
            
            # Get confidence based on similar historical issues
            confidence = self._calculate_prediction_confidence(issue_data, predicted_hours)
            
            return {
                'predicted_hours': predicted_hours,
                'predicted_days': round(predicted_hours / 24, 1),
                'confidence_score': confidence,
                'factors': self._identify_time_factors(features),
                'recommendation': self._get_time_recommendation(predicted_hours, issue_data.get('severity', 'MEDIUM'))
            }
            
        except Exception as e:
            logger.error(f"Resolution time prediction failed: {e}")
            return await self._fallback_time_prediction(issue_data)
    
    def _extract_prediction_features(self, issue_data: Dict) -> Dict:
        """Extract features from issue data for prediction"""
        text = f"{issue_data.get('title', '')} {issue_data.get('description', '')}".lower()
        severity = issue_data.get('severity', 'MEDIUM')
        
        bug_keywords = ['bug', 'error', 'crash', 'fail', 'broken']
        feature_keywords = ['feature', 'enhancement', 'improvement', 'request']
        critical_keywords = ['critical', 'urgent', 'asap', 'down', 'outage']
        
        return {
            'severity_critical': 1 if severity == 'CRITICAL' else 0,
            'severity_high': 1 if severity == 'HIGH' else 0,
            'severity_medium': 1 if severity == 'MEDIUM' else 0,
            'severity_low': 1 if severity == 'LOW' else 0,
            'title_length': len(issue_data.get('title', '')),
            'desc_length': len(issue_data.get('description', '')),
            'has_attachment': 1 if issue_data.get('file_path') else 0,
            'has_tags': 1 if issue_data.get('tags') else 0,
            'bug_keyword_count': sum(1 for keyword in bug_keywords if keyword in text),
            'feature_keyword_count': sum(1 for keyword in feature_keywords if keyword in text),
            'critical_keyword_count': sum(1 for keyword in critical_keywords if keyword in text),
            'reporter_experience': issue_data.get('reporter_experience', 5),
            'hour_created': datetime.now().hour,
            'day_of_week': datetime.now().weekday()
        }
    
    async def _fallback_time_prediction(self, issue_data: Dict) -> Dict:
        """Fallback prediction when ML model is not available"""
        severity_hours = {
            'CRITICAL': 4,
            'HIGH': 24,
            'MEDIUM': 72,
            'LOW': 168
        }
        
        base_hours = severity_hours.get(issue_data.get('severity', 'MEDIUM'), 72)
        
        # Adjust based on complexity indicators
        text = f"{issue_data.get('title', '')} {issue_data.get('description', '')}".lower()
        complexity_multiplier = 1.0
        
        if any(word in text for word in ['database', 'security', 'performance']):
            complexity_multiplier *= 1.3
        if any(word in text for word in ['integration', 'api', 'third-party']):
            complexity_multiplier *= 1.2
        if issue_data.get('file_path'):
            complexity_multiplier *= 1.1
        
        predicted_hours = int(base_hours * complexity_multiplier)
        
        return {
            'predicted_hours': predicted_hours,
            'predicted_days': round(predicted_hours / 24, 1),
            'confidence_score': 0.6,
            'factors': ['Based on severity and complexity indicators'],
            'recommendation': self._get_time_recommendation(predicted_hours, issue_data.get('severity', 'MEDIUM'))
        }
    
    def _get_time_recommendation(self, predicted_hours: int, severity: str) -> str:
        """Get recommendation based on predicted time"""
        if severity == 'CRITICAL' and predicted_hours > 8:
            return "⚠️ Critical issue may take longer than expected. Consider immediate escalation."
        elif severity == 'HIGH' and predicted_hours > 48:
            return "🚨 High priority issue needs attention. Review complexity and assign experienced developer."
        elif predicted_hours > 168:  # More than a week
            return "📅 Long-term issue. Consider breaking into smaller tasks."
        else:
            return "✅ Timeline looks reasonable. Monitor progress regularly."
    
    async def predict_escalation_risk(self, issue_data: Dict) -> Dict:
        """Predict if issue needs escalation"""
        try:
            if not self.models_trained or not self.escalation_model:
                return self._fallback_escalation_prediction(issue_data)
            
            features = self._extract_prediction_features(issue_data)
            feature_array = np.array([list(features.values())])
            
            escalation_probability = self.escalation_model.predict_proba(feature_array)[0][1]
            needs_escalation = escalation_probability > 0.7
            
            return {
                'escalation_probability': round(escalation_probability, 2),
                'needs_escalation': needs_escalation,
                'risk_level': self._get_risk_level(escalation_probability),
                'factors': self._identify_escalation_factors(features),
                'recommendations': self._get_escalation_recommendations(escalation_probability, issue_data)
            }
            
        except Exception as e:
            logger.error(f"Escalation prediction failed: {e}")
            return self._fallback_escalation_prediction(issue_data)
    
    def _fallback_escalation_prediction(self, issue_data: Dict) -> Dict:
        """Fallback escalation prediction"""
        severity = issue_data.get('severity', 'MEDIUM')
        text = f"{issue_data.get('title', '')} {issue_data.get('description', '')}".lower()
        
        risk_score = 0.3  # Base risk
        
        if severity == 'CRITICAL':
            risk_score = 0.8
        elif severity == 'HIGH':
            risk_score = 0.6
        
        if any(word in text for word in ['production', 'outage', 'down', 'critical']):
            risk_score += 0.2
        
        risk_score = min(risk_score, 1.0)
        
        return {
            'escalation_probability': risk_score,
            'needs_escalation': risk_score > 0.7,
            'risk_level': self._get_risk_level(risk_score),
            'factors': ['Severity level', 'Keyword analysis'],
            'recommendations': self._get_escalation_recommendations(risk_score, issue_data)
        }
    
    def _get_risk_level(self, probability: float) -> str:
        """Convert probability to risk level"""
        if probability >= 0.8:
            return 'HIGH'
        elif probability >= 0.6:
            return 'MEDIUM'
        elif probability >= 0.4:
            return 'LOW'
        else:
            return 'MINIMAL'
    
    async def analyze_team_trends(self, days: int = 30) -> Dict:
        """Analyze team trends and patterns"""
        try:
            db = self.get_db()
            
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Get issues from the period
            issues = db.query(Issue).filter(
                Issue.created_at >= start_date
            ).all()
            
            if not issues:
                return {'message': 'No data available for the selected period'}
            
            # Analyze trends
            daily_counts = self._analyze_daily_trends(issues)
            severity_trends = self._analyze_severity_trends(issues)
            team_performance = await self._analyze_team_performance(issues)
            bottlenecks = await self._identify_bottlenecks(issues)
            predictions = self._make_trend_predictions(daily_counts)
            
            return {
                'period_days': days,
                'total_issues': len(issues),
                'daily_trends': daily_counts,
                'severity_distribution': severity_trends,
                'team_performance': team_performance,
                'bottlenecks': bottlenecks,
                'predictions': predictions,
                'insights': self._generate_trend_insights(issues, daily_counts, team_performance)
            }
            
        except Exception as e:
            logger.error(f"Team trends analysis failed: {e}")
            return {'error': 'Failed to analyze team trends'}
        finally:
            db.close()
    
    def _generate_trend_insights(self, issues: List[Issue], daily_counts: Dict, team_performance: Dict) -> List[str]:
        """Generate actionable insights from trend analysis"""
        insights = []
        
        # Volume insights
        avg_daily = sum(daily_counts.values()) / len(daily_counts) if daily_counts else 0
        if avg_daily > 10:
            insights.append(f"📈 High issue volume: averaging {avg_daily:.1f} issues per day")
        
        # Critical issue insights
        critical_issues = [i for i in issues if i.severity == IssueSeverity.CRITICAL]
        if len(critical_issues) > len(issues) * 0.1:  # More than 10%
            insights.append(f"🚨 High critical issue ratio: {len(critical_issues)} out of {len(issues)} issues")
        
        # Team workload insights
        if team_performance:
            max_workload = max(team_performance.values()) if team_performance.values() else 0
            min_workload = min(team_performance.values()) if team_performance.values() else 0
            if max_workload > min_workload * 2:
                insights.append("⚖️ Uneven workload distribution detected across team members")
        
        return insights[:5]  # Limit to top 5 insights