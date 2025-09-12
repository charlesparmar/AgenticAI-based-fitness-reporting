"""
Analytics Module for RAG Pipeline
Advanced analytics, insights, and personalized recommendations
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from .vector_store import VectorStore
from .query_processor import QueryProcessor
from .retriever import Retriever


@dataclass
class TrendAnalysis:
    """Represents a trend analysis result"""
    metric: str
    period: str
    start_value: float
    end_value: float
    change: float
    change_percentage: float
    trend_direction: str  # 'increasing', 'decreasing', 'stable'
    confidence: float
    insights: List[str]
    recommendations: List[str]


@dataclass
class GoalAnalysis:
    """Represents a goal analysis result"""
    goal_type: str
    current_value: float
    target_value: float
    progress_percentage: float
    days_remaining: int
    projected_completion: datetime
    recommendations: List[str]
    risk_factors: List[str]


@dataclass
class InsightReport:
    """Represents a comprehensive insight report"""
    user_id: str
    generated_at: datetime
    period_analyzed: str
    key_metrics: Dict[str, float]
    trends: List[TrendAnalysis]
    goals: List[GoalAnalysis]
    recommendations: List[str]
    risk_alerts: List[str]
    achievements: List[str]


class FitnessAnalytics:
    """Advanced analytics and insights for fitness data"""
    
    def __init__(self, vector_store: VectorStore, 
                 query_processor: QueryProcessor = None,
                 retriever: Retriever = None):
        """
        Initialize fitness analytics
        
        Args:
            vector_store: Vector store instance
            query_processor: Query processor instance (optional)
            retriever: Retriever instance (optional)
        """
        self.vector_store = vector_store
        self.query_processor = query_processor or QueryProcessor()
        self.retriever = retriever or Retriever(vector_store, query_processor)
        
        # Analytics configuration
        self.metrics = ['weight', 'bmi', 'fat_percent', 'chest', 'waist', 'arms', 'legs']
        self.trend_periods = ['week', 'month', 'quarter', 'year']
        self.confidence_threshold = 0.7
    
    def analyze_trends(self, metric: str, period: str = 'month', 
                      n_results: int = 20) -> List[TrendAnalysis]:
        """
        Analyze trends for a specific metric
        
        Args:
            metric: Metric to analyze (weight, bmi, etc.)
            period: Analysis period (week, month, quarter, year)
            n_results: Number of results to retrieve
            
        Returns:
            List of trend analysis results
        """
        try:
            # Retrieve relevant data
            query = f"{metric} trend analysis {period}"
            results = self.retriever.retrieve(query, n_results=n_results)
            
            if not results:
                return []
            
            # Extract measurement data
            measurements = self._extract_measurements(results, metric)
            
            if len(measurements) < 2:
                return []
            
            # Analyze trends
            trends = []
            
            # Overall trend
            overall_trend = self._calculate_trend(measurements, metric)
            if overall_trend:
                trends.append(overall_trend)
            
            # Period-specific trends
            if period == 'month':
                weekly_trends = self._analyze_weekly_trends(measurements, metric)
                trends.extend(weekly_trends)
            
            # Seasonal trends
            seasonal_trends = self._analyze_seasonal_trends(measurements, metric)
            trends.extend(seasonal_trends)
            
            return trends
            
        except Exception as e:
            print(f"❌ Error analyzing trends: {e}")
            return []
    
    def _extract_measurements(self, results: List[Dict], metric: str) -> List[Dict]:
        """Extract measurement data from search results"""
        measurements = []
        
        for result in results:
            metadata = result.get('metadata', {})
            measurements_data = metadata.get('measurements', {})
            
            if metric in measurements_data:
                measurement = {
                    'date': metadata.get('date'),
                    'week_number': metadata.get('week_number'),
                    'value': measurements_data[metric],
                    'type': metadata.get('type', 'measurement')
                }
                measurements.append(measurement)
        
        # Sort by date
        measurements.sort(key=lambda x: x['date'] if x['date'] else '')
        
        return measurements
    
    def _calculate_trend(self, measurements: List[Dict], metric: str) -> Optional[TrendAnalysis]:
        """Calculate overall trend for measurements"""
        try:
            if len(measurements) < 2:
                return None
            
            # Get first and last measurements
            first = measurements[0]
            last = measurements[-1]
            
            start_value = first['value']
            end_value = last['value']
            change = end_value - start_value
            change_percentage = (change / start_value) * 100 if start_value != 0 else 0
            
            # Determine trend direction
            if abs(change_percentage) < 1.0:
                trend_direction = 'stable'
            elif change_percentage > 0:
                trend_direction = 'increasing'
            else:
                trend_direction = 'decreasing'
            
            # Calculate confidence based on consistency
            values = [m['value'] for m in measurements]
            std_dev = np.std(values)
            mean_val = np.mean(values)
            coefficient_of_variation = std_dev / mean_val if mean_val != 0 else 0
            confidence = max(0.1, 1.0 - coefficient_of_variation)
            
            # Generate insights
            insights = self._generate_trend_insights(measurements, metric, change_percentage)
            
            # Generate recommendations
            recommendations = self._generate_trend_recommendations(metric, trend_direction, change_percentage)
            
            return TrendAnalysis(
                metric=metric,
                period='overall',
                start_value=start_value,
                end_value=end_value,
                change=change,
                change_percentage=change_percentage,
                trend_direction=trend_direction,
                confidence=confidence,
                insights=insights,
                recommendations=recommendations
            )
            
        except Exception as e:
            print(f"❌ Error calculating trend: {e}")
            return None
    
    def _analyze_weekly_trends(self, measurements: List[Dict], metric: str) -> List[TrendAnalysis]:
        """Analyze weekly trends"""
        trends = []
        
        try:
            # Group by week
            weekly_data = {}
            for measurement in measurements:
                week = measurement.get('week_number', 'Unknown')
                if week not in weekly_data:
                    weekly_data[week] = []
                weekly_data[week].append(measurement['value'])
            
            # Calculate weekly averages
            weekly_averages = []
            for week, values in weekly_data.items():
                if values:
                    weekly_averages.append({
                        'week': week,
                        'average': np.mean(values),
                        'count': len(values)
                    })
            
            # Analyze weekly trends
            if len(weekly_averages) >= 2:
                for i in range(len(weekly_averages) - 1):
                    current = weekly_averages[i]
                    next_week = weekly_averages[i + 1]
                    
                    change = next_week['average'] - current['average']
                    change_percentage = (change / current['average']) * 100 if current['average'] != 0 else 0
                    
                    if abs(change_percentage) > 0.5:  # Significant change
                        trend_direction = 'increasing' if change_percentage > 0 else 'decreasing'
                        
                        trend = TrendAnalysis(
                            metric=metric,
                            period=f"Week {current['week']} to {next_week['week']}",
                            start_value=current['average'],
                            end_value=next_week['average'],
                            change=change,
                            change_percentage=change_percentage,
                            trend_direction=trend_direction,
                            confidence=0.8,
                            insights=[f"Weekly {metric} {trend_direction} by {abs(change_percentage):.1f}%"],
                            recommendations=self._generate_trend_recommendations(metric, trend_direction, change_percentage)
                        )
                        trends.append(trend)
            
        except Exception as e:
            print(f"❌ Error analyzing weekly trends: {e}")
        
        return trends
    
    def _analyze_seasonal_trends(self, measurements: List[Dict], metric: str) -> List[TrendAnalysis]:
        """Analyze seasonal trends"""
        trends = []
        
        try:
            # Group by month (simplified seasonal analysis)
            monthly_data = {}
            for measurement in measurements:
                date_str = measurement.get('date', '')
                if date_str:
                    try:
                        date = datetime.strptime(date_str, '%Y-%m-%d')
                        month = date.strftime('%Y-%m')
                        if month not in monthly_data:
                            monthly_data[month] = []
                        monthly_data[month].append(measurement['value'])
                    except:
                        continue
            
            # Calculate monthly averages
            monthly_averages = []
            for month, values in monthly_data.items():
                if values:
                    monthly_averages.append({
                        'month': month,
                        'average': np.mean(values),
                        'count': len(values)
                    })
            
            # Analyze seasonal patterns
            if len(monthly_averages) >= 3:
                # Compare first and last month
                first_month = monthly_averages[0]
                last_month = monthly_averages[-1]
                
                change = last_month['average'] - first_month['average']
                change_percentage = (change / first_month['average']) * 100 if first_month['average'] != 0 else 0
                
                if abs(change_percentage) > 2.0:  # Significant seasonal change
                    trend_direction = 'increasing' if change_percentage > 0 else 'decreasing'
                    
                    trend = TrendAnalysis(
                        metric=metric,
                        period=f"Seasonal ({first_month['month']} to {last_month['month']})",
                        start_value=first_month['average'],
                        end_value=last_month['average'],
                        change=change,
                        change_percentage=change_percentage,
                        trend_direction=trend_direction,
                        confidence=0.7,
                        insights=[f"Seasonal {metric} {trend_direction} by {abs(change_percentage):.1f}%"],
                        recommendations=self._generate_trend_recommendations(metric, trend_direction, change_percentage)
                    )
                    trends.append(trend)
            
        except Exception as e:
            print(f"❌ Error analyzing seasonal trends: {e}")
        
        return trends
    
    def _generate_trend_insights(self, measurements: List[Dict], metric: str, change_percentage: float) -> List[str]:
        """Generate insights from trend data"""
        insights = []
        
        try:
            # Basic trend insight
            if abs(change_percentage) < 1.0:
                insights.append(f"Your {metric} has remained relatively stable")
            elif change_percentage > 0:
                insights.append(f"Your {metric} has increased by {change_percentage:.1f}%")
            else:
                insights.append(f"Your {metric} has decreased by {abs(change_percentage):.1f}%")
            
            # Consistency insight
            values = [m['value'] for m in measurements]
            std_dev = np.std(values)
            mean_val = np.mean(values)
            coefficient_of_variation = std_dev / mean_val if mean_val != 0 else 0
            
            if coefficient_of_variation < 0.05:
                insights.append("Your measurements show high consistency")
            elif coefficient_of_variation > 0.15:
                insights.append("Your measurements show high variability")
            
            # Rate of change insight
            if len(measurements) >= 3:
                recent_values = values[-3:]
                recent_change = (recent_values[-1] - recent_values[0]) / recent_values[0] * 100
                
                if abs(recent_change) > abs(change_percentage):
                    insights.append("Recent changes are more pronounced than the overall trend")
                elif abs(recent_change) < abs(change_percentage) * 0.5:
                    insights.append("Recent progress has slowed compared to the overall trend")
            
        except Exception as e:
            print(f"❌ Error generating insights: {e}")
        
        return insights
    
    def _generate_trend_recommendations(self, metric: str, trend_direction: str, change_percentage: float) -> List[str]:
        """Generate recommendations based on trend"""
        recommendations = []
        
        try:
            if metric == 'weight':
                if trend_direction == 'increasing' and change_percentage > 2:
                    recommendations.extend([
                        "Consider reviewing your caloric intake",
                        "Increase physical activity levels",
                        "Monitor portion sizes more closely"
                    ])
                elif trend_direction == 'decreasing' and change_percentage < -2:
                    recommendations.extend([
                        "Ensure you're maintaining a healthy rate of weight loss",
                        "Focus on strength training to preserve muscle mass",
                        "Monitor your energy levels and adjust accordingly"
                    ])
            
            elif metric == 'bmi':
                if trend_direction == 'increasing':
                    recommendations.extend([
                        "Focus on balanced nutrition",
                        "Increase cardiovascular exercise",
                        "Consider consulting a nutritionist"
                    ])
                elif trend_direction == 'decreasing':
                    recommendations.extend([
                        "Maintain your current healthy habits",
                        "Ensure adequate protein intake",
                        "Continue with regular exercise routine"
                    ])
            
            elif metric == 'fat_percent':
                if trend_direction == 'increasing':
                    recommendations.extend([
                        "Increase strength training frequency",
                        "Review your macronutrient balance",
                        "Consider high-intensity interval training"
                    ])
                elif trend_direction == 'decreasing':
                    recommendations.extend([
                        "Excellent progress on body composition",
                        "Maintain your current training approach",
                        "Consider tracking muscle mass changes"
                    ])
            
            # General recommendations
            if abs(change_percentage) > 5:
                recommendations.append("Consider consulting with a fitness professional")
            
            if len(recommendations) == 0:
                recommendations.append("Continue monitoring your progress")
            
        except Exception as e:
            print(f"❌ Error generating recommendations: {e}")
        
        return recommendations
    
    def analyze_goals(self, user_goals: Dict[str, Any]) -> List[GoalAnalysis]:
        """
        Analyze progress towards user goals
        
        Args:
            user_goals: Dictionary of user goals
            
        Returns:
            List of goal analysis results
        """
        try:
            goal_analyses = []
            
            for goal_type, goal_data in user_goals.items():
                # Get current value
                current_value = self._get_current_value(goal_type)
                target_value = goal_data.get('target_value', 0)
                start_date = goal_data.get('start_date')
                target_date = goal_data.get('target_date')
                
                if current_value is None or target_value == 0:
                    continue
                
                # Calculate progress
                if goal_type in ['weight', 'bmi', 'fat_percent']:
                    # For decreasing metrics
                    start_value = goal_data.get('start_value', current_value)
                    total_change_needed = start_value - target_value
                    current_change = start_value - current_value
                    progress_percentage = (current_change / total_change_needed) * 100 if total_change_needed != 0 else 0
                else:
                    # For increasing metrics
                    start_value = goal_data.get('start_value', current_value)
                    total_change_needed = target_value - start_value
                    current_change = current_value - start_value
                    progress_percentage = (current_change / total_change_needed) * 100 if total_change_needed != 0 else 0
                
                # Calculate projected completion
                days_remaining = 0
                projected_completion = None
                
                if start_date and target_date:
                    try:
                        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                        target_dt = datetime.strptime(target_date, '%Y-%m-%d')
                        total_days = (target_dt - start_dt).days
                        
                        if total_days > 0:
                            days_elapsed = (datetime.now() - start_dt).days
                            if progress_percentage > 0:
                                projected_days = (days_elapsed / progress_percentage) * 100
                                days_remaining = max(0, int(projected_days - days_elapsed))
                                projected_completion = datetime.now() + timedelta(days=days_remaining)
                            else:
                                days_remaining = total_days - days_elapsed
                                projected_completion = target_dt
                    except:
                        pass
                
                # Generate recommendations
                recommendations = self._generate_goal_recommendations(goal_type, progress_percentage, days_remaining)
                
                # Identify risk factors
                risk_factors = self._identify_goal_risks(goal_type, progress_percentage, days_remaining)
                
                goal_analysis = GoalAnalysis(
                    goal_type=goal_type,
                    current_value=current_value,
                    target_value=target_value,
                    progress_percentage=progress_percentage,
                    days_remaining=days_remaining,
                    projected_completion=projected_completion,
                    recommendations=recommendations,
                    risk_factors=risk_factors
                )
                
                goal_analyses.append(goal_analysis)
            
            return goal_analyses
            
        except Exception as e:
            print(f"❌ Error analyzing goals: {e}")
            return []
    
    def _get_current_value(self, metric: str) -> Optional[float]:
        """Get current value for a metric"""
        try:
            query = f"latest {metric} measurement"
            results = self.retriever.retrieve(query, n_results=5)
            
            for result in results:
                metadata = result.get('metadata', {})
                measurements = metadata.get('measurements', {})
                
                if metric in measurements:
                    return measurements[metric]
            
            return None
            
        except Exception as e:
            print(f"❌ Error getting current value: {e}")
            return None
    
    def _generate_goal_recommendations(self, goal_type: str, progress_percentage: float, days_remaining: int) -> List[str]:
        """Generate recommendations for goal achievement"""
        recommendations = []
        
        try:
            if progress_percentage < 25:
                recommendations.extend([
                    "You're in the early stages of your goal",
                    "Focus on building consistent habits",
                    "Set smaller weekly milestones"
                ])
            elif progress_percentage < 50:
                recommendations.extend([
                    "Good progress so far",
                    "Maintain your current momentum",
                    "Consider increasing intensity gradually"
                ])
            elif progress_percentage < 75:
                recommendations.extend([
                    "Excellent progress",
                    "You're on track to achieve your goal",
                    "Stay focused and consistent"
                ])
            elif progress_percentage < 100:
                recommendations.extend([
                    "Almost there!",
                    "Maintain your current approach",
                    "Prepare for goal maintenance phase"
                ])
            else:
                recommendations.extend([
                    "Goal achieved!",
                    "Focus on maintaining your results",
                    "Consider setting new goals"
                ])
            
            # Time-based recommendations
            if days_remaining < 7 and progress_percentage < 90:
                recommendations.append("Urgent: Consider adjusting your goal timeline or approach")
            elif days_remaining < 30 and progress_percentage < 70:
                recommendations.append("Consider increasing your effort or adjusting your strategy")
            
        except Exception as e:
            print(f"❌ Error generating goal recommendations: {e}")
        
        return recommendations
    
    def _identify_goal_risks(self, goal_type: str, progress_percentage: float, days_remaining: int) -> List[str]:
        """Identify risks to goal achievement"""
        risks = []
        
        try:
            if progress_percentage < 25 and days_remaining < 30:
                risks.append("Significant risk of not achieving goal on time")
            
            if progress_percentage < 50 and days_remaining < 14:
                risks.append("High risk of missing target date")
            
            if progress_percentage > 100:
                risks.append("Goal exceeded - consider setting more challenging targets")
            
            if days_remaining < 0:
                risks.append("Target date has passed")
            
        except Exception as e:
            print(f"❌ Error identifying risks: {e}")
        
        return risks
    
    def generate_insight_report(self, user_id: str = "default", 
                               period: str = "month") -> InsightReport:
        """
        Generate comprehensive insight report
        
        Args:
            user_id: User identifier
            period: Analysis period
            
        Returns:
            Comprehensive insight report
        """
        try:
            # Get current key metrics
            key_metrics = {}
            for metric in self.metrics:
                current_value = self._get_current_value(metric)
                if current_value is not None:
                    key_metrics[metric] = current_value
            
            # Analyze trends for all metrics
            trends = []
            for metric in self.metrics:
                metric_trends = self.analyze_trends(metric, period)
                trends.extend(metric_trends)
            
            # Analyze goals (placeholder - would need user goals)
            goals = []
            
            # Generate overall recommendations
            recommendations = self._generate_overall_recommendations(trends, key_metrics)
            
            # Identify risk alerts
            risk_alerts = self._identify_risk_alerts(trends, key_metrics)
            
            # Identify achievements
            achievements = self._identify_achievements(trends, key_metrics)
            
            report = InsightReport(
                user_id=user_id,
                generated_at=datetime.now(),
                period_analyzed=period,
                key_metrics=key_metrics,
                trends=trends,
                goals=goals,
                recommendations=recommendations,
                risk_alerts=risk_alerts,
                achievements=achievements
            )
            
            return report
            
        except Exception as e:
            print(f"❌ Error generating insight report: {e}")
            return None
    
    def _generate_overall_recommendations(self, trends: List[TrendAnalysis], 
                                        key_metrics: Dict[str, float]) -> List[str]:
        """Generate overall recommendations"""
        recommendations = []
        
        try:
            # Analyze trend patterns
            improving_metrics = [t for t in trends if t.trend_direction == 'decreasing' and t.metric in ['weight', 'bmi', 'fat_percent']]
            declining_metrics = [t for t in trends if t.trend_direction == 'increasing' and t.metric in ['weight', 'bmi', 'fat_percent']]
            
            if len(improving_metrics) > len(declining_metrics):
                recommendations.append("Overall positive progress - maintain your current approach")
            elif len(declining_metrics) > len(improving_metrics):
                recommendations.append("Consider reviewing your fitness and nutrition strategy")
            
            # Specific recommendations based on current metrics
            if 'bmi' in key_metrics:
                bmi = key_metrics['bmi']
                if bmi > 30:
                    recommendations.append("Consider consulting with a healthcare professional about weight management")
                elif bmi < 18.5:
                    recommendations.append("Focus on healthy weight gain and muscle building")
            
            if 'fat_percent' in key_metrics:
                fat_percent = key_metrics['fat_percent']
                if fat_percent > 25:
                    recommendations.append("Increase strength training to improve body composition")
                elif fat_percent < 10:
                    recommendations.append("Ensure adequate fat intake for health")
            
            if len(recommendations) == 0:
                recommendations.append("Continue monitoring your progress and maintain healthy habits")
            
        except Exception as e:
            print(f"❌ Error generating overall recommendations: {e}")
        
        return recommendations
    
    def _identify_risk_alerts(self, trends: List[TrendAnalysis], 
                             key_metrics: Dict[str, float]) -> List[str]:
        """Identify risk alerts"""
        alerts = []
        
        try:
            # Rapid changes
            for trend in trends:
                if abs(trend.change_percentage) > 10:
                    alerts.append(f"Rapid {trend.change_percentage:.1f}% change in {trend.metric} - monitor closely")
                
                if trend.change_percentage > 5 and trend.metric in ['weight', 'bmi']:
                    alerts.append(f"Significant increase in {trend.metric} - review nutrition and exercise")
            
            # Extreme values
            if 'bmi' in key_metrics:
                bmi = key_metrics['bmi']
                if bmi > 35:
                    alerts.append("High BMI detected - consider medical consultation")
                elif bmi < 16:
                    alerts.append("Very low BMI detected - seek medical advice")
            
            if 'fat_percent' in key_metrics:
                fat_percent = key_metrics['fat_percent']
                if fat_percent > 35:
                    alerts.append("High body fat percentage - focus on fat loss strategies")
                elif fat_percent < 5:
                    alerts.append("Very low body fat - ensure adequate nutrition")
            
        except Exception as e:
            print(f"❌ Error identifying risk alerts: {e}")
        
        return alerts
    
    def _identify_achievements(self, trends: List[TrendAnalysis], 
                              key_metrics: Dict[str, float]) -> List[str]:
        """Identify achievements"""
        achievements = []
        
        try:
            # Positive trends
            for trend in trends:
                if trend.trend_direction == 'decreasing' and trend.metric in ['weight', 'bmi', 'fat_percent']:
                    if trend.change_percentage < -5:
                        achievements.append(f"Significant {trend.metric} reduction: {abs(trend.change_percentage):.1f}%")
                    elif trend.change_percentage < -2:
                        achievements.append(f"Steady {trend.metric} improvement: {abs(trend.change_percentage):.1f}%")
                
                if trend.trend_direction == 'increasing' and trend.metric in ['chest', 'arms', 'legs']:
                    if trend.change_percentage > 2:
                        achievements.append(f"Muscle growth in {trend.metric}: {trend.change_percentage:.1f}%")
            
            # Healthy ranges
            if 'bmi' in key_metrics:
                bmi = key_metrics['bmi']
                if 18.5 <= bmi <= 24.9:
                    achievements.append("Maintaining healthy BMI range")
            
            if 'fat_percent' in key_metrics:
                fat_percent = key_metrics['fat_percent']
                if 10 <= fat_percent <= 20:
                    achievements.append("Optimal body fat percentage")
            
            # Consistency
            consistent_trends = [t for t in trends if t.confidence > 0.8]
            if len(consistent_trends) >= 3:
                achievements.append("Consistent measurement tracking")
            
        except Exception as e:
            print(f"❌ Error identifying achievements: {e}")
        
        return achievements
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get analytics system summary"""
        try:
            return {
                "metrics_tracked": self.metrics,
                "trend_periods": self.trend_periods,
                "confidence_threshold": self.confidence_threshold,
                "capabilities": [
                    "Trend analysis for all fitness metrics",
                    "Goal progress tracking and projection",
                    "Personalized recommendations",
                    "Risk identification and alerts",
                    "Achievement recognition",
                    "Comprehensive insight reports"
                ]
            }
        except Exception as e:
            print(f"❌ Error getting analytics summary: {e}")
            return {"error": str(e)} 