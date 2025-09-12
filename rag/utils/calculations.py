"""
Calculation Helper Functions for RAG Pipeline
Provides data validation, calculations, and sanity checks for fitness analytics
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
import re
from dataclasses import dataclass


@dataclass
class CalculationResult:
    """Represents a calculation result with validation"""
    value: float
    unit: str
    confidence: float
    validation_passed: bool
    warnings: List[str]
    data_points_used: int
    calculation_method: str


class FitnessCalculations:
    """Helper class for fitness data calculations and validation"""
    
    def __init__(self):
        """Initialize calculation helper"""
        self.weight_units = ['kg', 'lbs', 'g']
        self.measurement_units = ['cm', 'inches', 'mm']
        self.percentage_units = ['%', 'percent']
        
    def validate_weight_loss_calculation(self, start_date: datetime, end_date: datetime, 
                                       claimed_loss: float, actual_data: List[Dict]) -> Dict[str, Any]:
        """
        Validate weight loss calculation against actual data
        
        Args:
            start_date: Start date for calculation
            end_date: End date for calculation
            claimed_loss: Claimed weight loss amount
            actual_data: List of actual weight measurements
            
        Returns:
            Validation result with details
        """
        try:
            # Get actual measurements for the period
            start_weight = self.get_weight_at_specific_date(start_date, actual_data)
            end_weight = self.get_weight_at_specific_date(end_date, actual_data)
            
            if start_weight is None or end_weight is None:
                return {
                    'valid': False,
                    'error': 'Missing weight data for specified dates',
                    'suggestions': ['Check if data exists for the specified date range']
                }
            
            actual_loss = start_weight - end_weight
            difference = abs(claimed_loss - actual_loss)
            
            # Validate the calculation
            if difference > 0.1:  # Allow small rounding differences
                return {
                    'valid': False,
                    'actual_loss': actual_loss,
                    'claimed_loss': claimed_loss,
                    'difference': difference,
                    'start_weight': start_weight,
                    'end_weight': end_weight,
                    'suggestions': [f'Actual weight loss: {actual_loss:.2f} kg']
                }
            
            return {
                'valid': True,
                'actual_loss': actual_loss,
                'claimed_loss': claimed_loss,
                'start_weight': start_weight,
                'end_weight': end_weight
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': f'Calculation error: {str(e)}',
                'suggestions': ['Check data format and date ranges']
            }
    
    def count_actual_weeks_of_data(self, data: List[Dict]) -> int:
        """
        Count actual weeks of data available
        
        Args:
            data: List of fitness measurements
            
        Returns:
            Number of weeks with data
        """
        try:
            if not data:
                return 0
            
            # Convert to DataFrame for easier processing
            df = pd.DataFrame(data)
            # Parse dates in DD-MM-YYYY format
            df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y', errors='coerce')
            
            # Group by week and count unique weeks
            df['week'] = df['date'].dt.isocalendar().week
            df['year'] = df['date'].dt.year
            df['year_week'] = df['year'].astype(str) + '-' + df['week'].astype(str)
            
            unique_weeks = df['year_week'].nunique()
            return unique_weeks
            
        except Exception as e:
            print(f"Error counting weeks: {e}")
            return 0
    
    def get_weight_at_specific_date(self, target_date: datetime, data: List[Dict]) -> Optional[float]:
        """
        Get weight measurement at a specific date
        
        Args:
            target_date: Target date to find weight for
            data: List of fitness measurements
            
        Returns:
            Weight value or None if not found
        """
        try:
            if not data:
                return None
            
            # Convert target date to datetime if it's a string
            if isinstance(target_date, str):
                target_date = pd.to_datetime(target_date, format='%d-%m-%Y', errors='coerce')
            
            # Find exact match or closest match
            for record in data:
                record_date = pd.to_datetime(record.get('date'), format='%d-%m-%Y', errors='coerce')
                if record_date == target_date:
                    return record.get('weight')
            
            # If no exact match, find closest within 7 days
            closest_record = None
            min_difference = timedelta(days=7)
            
            for record in data:
                record_date = pd.to_datetime(record.get('date'), format='%d-%m-%Y', errors='coerce')
                difference = abs(record_date - target_date)
                
                if difference < min_difference:
                    min_difference = difference
                    closest_record = record
            
            return closest_record.get('weight') if closest_record else None
            
        except Exception as e:
            print(f"Error getting weight at date: {e}")
            return None
    
    def calculate_weight_loss_between_dates(self, start_date: datetime, end_date: datetime, 
                                          data: List[Dict]) -> Optional[float]:
        """
        Calculate weight loss between two dates
        
        Args:
            start_date: Start date
            end_date: End date
            data: List of fitness measurements
            
        Returns:
            Weight loss amount or None if calculation fails
        """
        try:
            start_weight = self.get_weight_at_specific_date(start_date, data)
            end_weight = self.get_weight_at_specific_date(end_date, data)
            
            if start_weight is None or end_weight is None:
                return None
            
            return start_weight - end_weight
            
        except Exception as e:
            print(f"Error calculating weight loss: {e}")
            return None
    
    def validate_data_consistency(self, data: List[Dict]) -> Dict[str, Any]:
        """
        Validate consistency of fitness data
        
        Args:
            data: List of fitness measurements
            
        Returns:
            Validation result with issues found
        """
        try:
            if not data:
                return {'valid': False, 'issues': ['No data provided']}
            
            issues = []
            warnings = []
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['date'])
            
            # Check for duplicate dates
            duplicates = df[df.duplicated(subset=['date'], keep=False)]
            if not duplicates.empty:
                issues.append(f"Found {len(duplicates)} duplicate date entries")
            
            # Check for missing required fields
            required_fields = ['date', 'weight']
            for field in required_fields:
                missing_count = df[field].isna().sum()
                if missing_count > 0:
                    issues.append(f"Missing {field} in {missing_count} records")
            
            # Check for impossible weight values
            if 'weight' in df.columns:
                impossible_weights = df[(df['weight'] < 30) | (df['weight'] > 300)]
                if not impossible_weights.empty:
                    warnings.append(f"Found {len(impossible_weights)} potentially impossible weight values")
            
            # Check for future dates
            future_dates = df[df['date'] > datetime.now()]
            if not future_dates.empty:
                warnings.append(f"Found {len(future_dates)} future dates")
            
            # Check for very old dates (more than 10 years ago)
            old_dates = df[df['date'] < datetime.now() - timedelta(days=3650)]
            if not old_dates.empty:
                warnings.append(f"Found {len(old_dates)} very old dates (more than 10 years ago)")
            
            return {
                'valid': len(issues) == 0,
                'issues': issues,
                'warnings': warnings,
                'total_records': len(df),
                'date_range': {
                    'start': df['date'].min().strftime('%Y-%m-%d'),
                    'end': df['date'].max().strftime('%Y-%m-%d')
                }
            }
            
        except Exception as e:
            return {
                'valid': False,
                'issues': [f'Validation error: {str(e)}'],
                'warnings': []
            }
    
    def calculate_total_weight_loss(self, data: List[Dict]) -> CalculationResult:
        """
        Calculate total weight loss from the dataset
        
        Args:
            data: List of fitness measurements
            
        Returns:
            Calculation result with validation
        """
        try:
            if not data:
                return CalculationResult(
                    value=0.0,
                    unit='kg',
                    confidence=0.0,
                    validation_passed=False,
                    warnings=['No data available'],
                    data_points_used=0,
                    calculation_method='total_weight_loss'
                )
            
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            if 'weight' not in df.columns:
                return CalculationResult(
                    value=0.0,
                    unit='kg',
                    confidence=0.0,
                    validation_passed=False,
                    warnings=['No weight data available'],
                    data_points_used=0,
                    calculation_method='total_weight_loss'
                )
            
            # Get first and last weight measurements
            first_weight = df.iloc[0]['weight']
            last_weight = df.iloc[-1]['weight']
            total_loss = first_weight - last_weight
            
            # Validate the calculation
            warnings = []
            if total_loss < 0:
                warnings.append('Weight loss is negative (weight gain detected)')
            
            if abs(total_loss) >= 50:
                warnings.append('Unusually large weight loss detected - please verify data')
            
            confidence = 0.9 if len(warnings) == 0 else 0.7
            
            return CalculationResult(
                value=total_loss,
                unit='kg',
                confidence=confidence,
                validation_passed=len(warnings) == 0,
                warnings=warnings,
                data_points_used=len(df),
                calculation_method='total_weight_loss'
            )
            
        except Exception as e:
            return CalculationResult(
                value=0.0,
                unit='kg',
                confidence=0.0,
                validation_passed=False,
                warnings=[f'Calculation error: {str(e)}'],
                data_points_used=0,
                calculation_method='total_weight_loss'
            )
    
    def calculate_weight_loss_in_period(self, start_date: datetime, end_date: datetime, 
                                       data: List[Dict]) -> CalculationResult:
        """
        Calculate weight loss in a specific time period
        
        Args:
            start_date: Start date of period
            end_date: End date of period
            data: List of fitness measurements
            
        Returns:
            Calculation result with validation
        """
        try:
            if not data:
                return CalculationResult(
                    value=0.0,
                    unit='kg',
                    confidence=0.0,
                    validation_passed=False,
                    warnings=['No data available'],
                    data_points_used=0,
                    calculation_method='period_weight_loss'
                )
            
            # Filter data for the period
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['date'])
            period_data = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
            
            if len(period_data) == 0:
                return CalculationResult(
                    value=0.0,
                    unit='kg',
                    confidence=0.0,
                    validation_passed=False,
                    warnings=['No data available for specified period'],
                    data_points_used=0,
                    calculation_method='period_weight_loss'
                )
            
            # Get first and last weight in period
            period_data = period_data.sort_values('date')
            first_weight = period_data.iloc[0]['weight']
            last_weight = period_data.iloc[-1]['weight']
            period_loss = first_weight - last_weight
            
            # Validate calculation
            warnings = []
            if period_loss < 0:
                warnings.append('Weight loss is negative (weight gain detected)')
            
            if abs(period_loss) > 50:
                warnings.append('Unusually large weight loss for period - please verify data')
            
            # Check if we have enough data points
            if len(period_data) < 2:
                warnings.append('Limited data points for period calculation')
                confidence = 0.6
            else:
                confidence = 0.9 if len(warnings) == 0 else 0.7
            
            return CalculationResult(
                value=period_loss,
                unit='kg',
                confidence=confidence,
                validation_passed=len(warnings) == 0,
                warnings=warnings,
                data_points_used=len(period_data),
                calculation_method='period_weight_loss'
            )
            
        except Exception as e:
            return CalculationResult(
                value=0.0,
                unit='kg',
                confidence=0.0,
                validation_passed=False,
                warnings=[f'Calculation error: {str(e)}'],
                data_points_used=0,
                calculation_method='period_weight_loss'
            )
    
    def get_measurement_at_date(self, measurement_type: str, target_date: datetime, 
                               data: List[Dict]) -> Optional[float]:
        """
        Get specific measurement at a target date
        
        Args:
            measurement_type: Type of measurement (weight, bmi, etc.)
            target_date: Target date
            data: List of fitness measurements
            
        Returns:
            Measurement value or None if not found
        """
        try:
            if not data:
                return None
            
            # Convert target date to datetime if it's a string
            if isinstance(target_date, str):
                target_date = pd.to_datetime(target_date)
            
            # Find exact match or closest match
            for record in data:
                record_date = pd.to_datetime(record.get('date'))
                if record_date == target_date and measurement_type in record:
                    return record.get(measurement_type)
            
            # If no exact match, find closest within 7 days
            closest_record = None
            min_difference = timedelta(days=7)
            
            for record in data:
                if measurement_type not in record:
                    continue
                    
                record_date = pd.to_datetime(record.get('date'))
                difference = abs(record_date - target_date)
                
                if difference < min_difference:
                    min_difference = difference
                    closest_record = record
            
            return closest_record.get(measurement_type) if closest_record else None
            
        except Exception as e:
            print(f"Error getting measurement at date: {e}")
            return None
    
    def count_data_points_in_period(self, start_date: datetime, end_date: datetime, 
                                   data: List[Dict]) -> int:
        """
        Count number of data points in a specific period
        
        Args:
            start_date: Start date of period
            end_date: End date of period
            data: List of fitness measurements
            
        Returns:
            Number of data points in period
        """
        try:
            if not data:
                return 0
            
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['date'])
            period_data = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
            
            return len(period_data)
            
        except Exception as e:
            print(f"Error counting data points: {e}")
            return 0
    
    def validate_calculation_sanity(self, result: float, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate if a calculation result makes sense given the context
        
        Args:
            result: Calculation result to validate
            context: Context information for validation
            
        Returns:
            Validation result with details
        """
        try:
            warnings = []
            is_sane = True
            
            # Get context information
            calculation_type = context.get('type', 'unknown')
            time_period = context.get('time_period', 'unknown')
            data_points = context.get('data_points', 0)
            
            # Weight loss sanity checks
            if calculation_type == 'weight_loss':
                if result < -50:  # More than 50kg weight gain
                    warnings.append('Unusually large weight gain detected')
                    is_sane = False
                elif result > 100:  # More than 100kg weight loss
                    warnings.append('Unusually large weight loss detected')
                    is_sane = False
                elif result < 0 and time_period == 'week':
                    warnings.append('Weekly weight gain detected - verify if this is expected')
            
            # BMI sanity checks
            elif calculation_type == 'bmi':
                if result < 10 or result > 60:
                    warnings.append('BMI value outside normal range (10-60)')
                    is_sane = False
            
            # Percentage sanity checks
            elif calculation_type == 'percentage':
                if result < 0 or result > 100:
                    warnings.append('Percentage value outside valid range (0-100)')
                    is_sane = False
            
            # Data point validation
            if data_points < 2:
                warnings.append('Limited data points for calculation')
                is_sane = False
            
            return {
                'sane': is_sane,
                'warnings': warnings,
                'confidence': 0.9 if is_sane and len(warnings) == 0 else 0.6
            }
            
        except Exception as e:
            return {
                'sane': False,
                'warnings': [f'Validation error: {str(e)}'],
                'confidence': 0.0
            } 