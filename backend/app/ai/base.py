# backend/app/ai/base.py
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import time

logger = logging.getLogger(__name__)

class AIBaseService(ABC):
    """Base class for all AI services"""
    
    def __init__(self):
        self.service_name = self.__class__.__name__
        self.is_healthy = True
        self.last_health_check = None
        self.performance_metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0.0,
            'last_error': None
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check for this service"""
        try:
            self.last_health_check = time.time()
            
            # Basic health check - can be overridden by subclasses
            health_status = {
                'service': self.service_name,
                'status': 'healthy' if self.is_healthy else 'degraded',
                'last_check': self.last_health_check,
                'metrics': self.performance_metrics.copy()
            }
            
            return health_status
            
        except Exception as e:
            logger.error(f"Health check failed for {self.service_name}: {e}")
            self.is_healthy = False
            return {
                'service': self.service_name,
                'status': 'error',
                'error': str(e),
                'last_check': time.time()
            }
    
    def _record_request(self, success: bool = True, response_time: float = 0.0, error: Optional[str] = None):
        """Record request metrics"""
        self.performance_metrics['total_requests'] += 1
        
        if success:
            self.performance_metrics['successful_requests'] += 1
        else:
            self.performance_metrics['failed_requests'] += 1
            if error:
                self.performance_metrics['last_error'] = error
        
        # Update average response time
        if response_time > 0:
            total_requests = self.performance_metrics['total_requests']
            current_avg = self.performance_metrics['average_response_time']
            self.performance_metrics['average_response_time'] = (
                (current_avg * (total_requests - 1) + response_time) / total_requests
            )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for this service"""
        return self.performance_metrics.copy()
    
    def reset_metrics(self):
        """Reset performance metrics"""
        self.performance_metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0.0,
            'last_error': None
        }
    
    def cleanup(self):
        """Cleanup resources when service is shut down"""
        logger.info(f"Cleaning up {self.service_name}")
        # Override in subclasses if needed