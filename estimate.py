"""
ETA Estimation Module
Calculates estimated approval dates for PERM applications based on queue position and processing rates
"""

import logging
from typing import Dict, Any
from datetime import datetime, timedelta
import math
import config

logger = logging.getLogger(__name__)


class ETAEstimator:
    """Estimates approval ETA for PERM applications"""
    
    def __init__(self):
        self.confidence_levels = config.CONFIDENCE_LEVELS
        self.default_processing_rate = config.DEFAULT_PROCESSING_RATE
    
    def calculate_eta(self, position: int, processing_rate: int, submission_date: str) -> Dict[str, Any]:
        """Calculate estimated approval date based on current position and processing rate"""
        try:
            logger.info(f"Calculating ETA for position {position} with processing rate {processing_rate}")
            
            # Calculate days remaining
            days_remaining = self._calculate_days_remaining(position, processing_rate)
            
            # Calculate estimated approval date
            estimated_date = self._calculate_approval_date(days_remaining)
            
            # Determine confidence level
            confidence_level = self._determine_confidence_level(position, processing_rate, days_remaining)
            
            # Calculate progress percentage
            progress_percentage = self._calculate_progress_percentage(position)
            
            # Calculate estimated processing date
            processing_date = self._calculate_processing_date(position, processing_rate)
            
            eta_info = {
                'estimated_approval_date': estimated_date.strftime('%Y-%m-%d'),
                'days_remaining': days_remaining,
                'confidence_level': confidence_level,
                'progress_percentage': progress_percentage,
                'estimated_processing_date': processing_date.strftime('%Y-%m-%d'),
                'processing_rate': processing_rate,
                'position_in_queue': position,
                'submission_date': submission_date
            }
            
            logger.info(f"ETA calculation complete: {eta_info}")
            return eta_info
            
        except Exception as e:
            logger.error(f"Error calculating ETA: {e}")
            return self._get_fallback_eta(submission_date)
    
    def _calculate_days_remaining(self, position: int, processing_rate: int) -> int:
        """Calculate days remaining until approval"""
        if processing_rate <= 0:
            logger.warning(f"Invalid processing rate: {processing_rate}, using default")
            processing_rate = self.default_processing_rate
        
        # Basic calculation: position / processing rate
        days_remaining = math.ceil(position / processing_rate)
        
        # Add buffer for weekends, holidays, and processing delays
        buffer_days = math.ceil(days_remaining * 0.2)  # 20% buffer
        total_days = days_remaining + buffer_days
        
        logger.info(f"Days remaining: {days_remaining} + {buffer_days} buffer = {total_days}")
        return max(1, total_days)  # Minimum 1 day
    
    def _calculate_approval_date(self, days_remaining: int) -> datetime:
        """Calculate the estimated approval date"""
        approval_date = datetime.now() + timedelta(days=days_remaining)
        
        # Adjust for weekends (skip to Monday if falls on weekend)
        while approval_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
            approval_date += timedelta(days=1)
        
        return approval_date
    
    def _determine_confidence_level(self, position: int, processing_rate: int, days_remaining: int) -> str:
        """Determine confidence level based on various factors"""
        confidence_score = 0.0
        
        # Factor 1: Position in queue (lower position = higher confidence)
        if position <= 100:
            confidence_score += 0.3
        elif position <= 500:
            confidence_score += 0.2
        elif position <= 1000:
            confidence_score += 0.1
        else:
            confidence_score += 0.05
        
        # Factor 2: Processing rate stability (higher rate = higher confidence)
        if processing_rate >= 100:
            confidence_score += 0.3
        elif processing_rate >= 50:
            confidence_score += 0.2
        elif processing_rate >= 25:
            confidence_score += 0.1
        else:
            confidence_score += 0.05
        
        # Factor 3: Days remaining (shorter time = higher confidence)
        if days_remaining <= 30:
            confidence_score += 0.2
        elif days_remaining <= 90:
            confidence_score += 0.15
        elif days_remaining <= 180:
            confidence_score += 0.1
        else:
            confidence_score += 0.05
        
        # Factor 4: Historical accuracy (mock data = lower confidence)
        confidence_score += 0.1  # Base confidence
        
        # Determine confidence level
        if confidence_score >= 0.7:
            return "High"
        elif confidence_score >= 0.5:
            return "Medium"
        else:
            return "Low"
    
    def _calculate_progress_percentage(self, position: int) -> float:
        """Calculate progress percentage based on estimated total queue"""
        # Estimate total queue size (this could be refined with historical data)
        estimated_total_queue = config.MOCK_TOTAL_APPLICATIONS
        
        if estimated_total_queue <= 0:
            return 0.0
        
        progress = max(0.0, min(100.0, ((estimated_total_queue - position) / estimated_total_queue) * 100))
        return round(progress, 1)
    
    def _calculate_processing_date(self, position: int, processing_rate: int) -> datetime:
        """Calculate when the application will start being processed"""
        if processing_rate <= 0:
            processing_rate = self.default_processing_rate
        
        # Calculate when processing will begin
        processing_days = math.ceil(position / processing_rate)
        processing_date = datetime.now() + timedelta(days=processing_days)
        
        # Adjust for weekends
        while processing_date.weekday() >= 5:
            processing_date += timedelta(days=1)
        
        return processing_date
    
    def _get_fallback_eta(self, submission_date: str) -> Dict[str, Any]:
        """Get fallback ETA when calculation fails"""
        logger.warning("Using fallback ETA calculation")
        
        try:
            sub_date = datetime.strptime(submission_date, '%Y-%m-%d')
            days_since_submission = (datetime.now() - sub_date).days
            
            # Estimate based on typical PERM processing times
            estimated_days_remaining = max(30, 180 - days_since_submission)
            estimated_date = datetime.now() + timedelta(days=estimated_days_remaining)
            
            return {
                'estimated_approval_date': estimated_date.strftime('%Y-%m-%d'),
                'days_remaining': estimated_days_remaining,
                'confidence_level': 'Low',
                'progress_percentage': 50.0,
                'estimated_processing_date': (datetime.now() + timedelta(days=60)).strftime('%Y-%m-%d'),
                'processing_rate': self.default_processing_rate,
                'position_in_queue': config.MOCK_POSITION,
                'submission_date': submission_date,
                'is_fallback': True
            }
            
        except Exception as e:
            logger.error(f"Error in fallback ETA: {e}")
            return {
                'estimated_approval_date': '2024-06-15',
                'days_remaining': 120,
                'confidence_level': 'Low',
                'progress_percentage': 50.0,
                'estimated_processing_date': '2024-03-15',
                'processing_rate': self.default_processing_rate,
                'position_in_queue': config.MOCK_POSITION,
                'submission_date': submission_date,
                'is_fallback': True
            }
    
    def get_processing_trends(self) -> Dict[str, Any]:
        """Get historical processing trends (placeholder for future enhancement)"""
        # This could be enhanced to analyze historical data
        return {
            'average_processing_rate': self.default_processing_rate,
            'peak_processing_rate': self.default_processing_rate * 1.5,
            'slow_processing_rate': self.default_processing_rate * 0.7,
            'seasonal_factors': {
                'holiday_slowdown': True,
                'fiscal_year_end': False,
                'summer_slowdown': False
            }
        } 