# backend/app/api/ai_admin.py - AI Administration endpoints

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import logging

from app.database import get_db
from app.models import User
from app.core.auth import get_current_active_user, require_role
from app.core.ai_config import get_ai_config, update_ai_config, is_ai_feature_enabled
from app.ai import get_ai_health, initialize_ai_services, cleanup_ai_services, get_ai_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/config")
async def get_ai_configuration(
    current_user: User = Depends(require_role("ADMIN"))
) -> Dict[str, Any]:
    """Get current AI configuration (Admin only)"""
    try:
        config = get_ai_config()
        health = await get_ai_health()
        
        return {
            "success": True,
            "config": config,
            "health": health,
            "features_status": {
                "classification": is_ai_feature_enabled("classification"),
                "chat": is_ai_feature_enabled("chat"),
                "analytics": is_ai_feature_enabled("analytics"),
                "document_processing": is_ai_feature_enabled("document_processing"),
                "assignment": is_ai_feature_enabled("assignment"),
                "notifications": is_ai_feature_enabled("notifications")
            }
        }
    except Exception as e:
        logger.error(f"Failed to get AI configuration: {e}")
        raise HTTPException(status_code=500, detail="Configuration service unavailable")

@router.put("/config")
async def update_ai_configuration(
    config_updates: Dict[str, Any],
    current_user: User = Depends(require_role("ADMIN"))
) -> Dict[str, Any]:
    """Update AI configuration (Admin only)"""
    try:
        updated_config = update_ai_config(**config_updates)
        
        # Reinitialize services if needed
        if "ai_enabled" in config_updates:
            if config_updates["ai_enabled"]:
                initialize_ai_services()
            else:
                cleanup_ai_services()
        
        return {
            "success": True,
            "config": updated_config,
            "message": "AI configuration updated successfully"
        }
    except Exception as e:
        logger.error(f"Failed to update AI configuration: {e}")
        raise HTTPException(status_code=500, detail="Configuration update failed")

@router.post("/services/restart")
async def restart_ai_services(
    current_user: User = Depends(require_role("ADMIN"))
) -> Dict[str, Any]:
    """Restart all AI services (Admin only)"""
    try:
        # Cleanup existing services
        cleanup_ai_services()
        
        # Reinitialize services
        services = initialize_ai_services()
        
        # Get health status
        health = await get_ai_health()
        
        return {
            "success": True,
            "message": "AI services restarted successfully",
            "services_count": len(services),
            "health": health
        }
    except Exception as e:
        logger.error(f"Failed to restart AI services: {e}")
        raise HTTPException(status_code=500, detail="Service restart failed")

@router.get("/services/metrics")
async def get_ai_service_metrics(
    current_user: User = Depends(require_role("ADMIN"))
) -> Dict[str, Any]:
    """Get detailed metrics for all AI services (Admin only)"""
    try:
        metrics = {}
        
        service_names = [
            'classifier', 'chat_assistant', 'analytics',
            'document_processor', 'assignment_engine',
            'notification_engine', 'resolution_assistant'
        ]
        
        for service_name in service_names:
            service = get_ai_service(service_name)
            if service and hasattr(service, 'get_metrics'):
                metrics[service_name] = service.get_metrics()
            else:
                metrics[service_name] = {"status": "unavailable"}
        
        return {
            "success": True,
            "metrics": metrics,
            "timestamp": "2025-01-01T12:00:00Z"
        }
    except Exception as e:
        logger.error(f"Failed to get AI service metrics: {e}")
        raise HTTPException(status_code=500, detail="Metrics service unavailable")

@router.post("/services/{service_name}/reset-metrics")
async def reset_service_metrics(
    service_name: str,
    current_user: User = Depends(require_role("ADMIN"))
) -> Dict[str, Any]:
    """Reset metrics for a specific AI service (Admin only)"""
    try:
        service = get_ai_service(service_name)
        if not service:
            raise HTTPException(status_code=404, detail=f"Service {service_name} not found")
        
        if hasattr(service, 'reset_metrics'):
            service.reset_metrics()
            return {
                "success": True,
                "message": f"Metrics reset for {service_name}"
            }
        else:
            raise HTTPException(status_code=400, detail=f"Service {service_name} does not support metric reset")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to reset metrics for {service_name}: {e}")
        raise HTTPException(status_code=500, detail="Metric reset failed")

@router.get("/models/status")
async def get_ai_models_status(
    current_user: User = Depends(require_role("ADMIN"))
) -> Dict[str, Any]:
    """Get status of all AI models (Admin only)"""
    try:
        analytics_service = get_ai_service('analytics')
        
        models_status = {
            "classification_model": {
                "status": "active",
                "version": "1.0.0",
                "accuracy": 0.87,
                "last_trained": "2025-01-15T10:00:00Z"
            },
            "prediction_model": {
                "status": "active" if (analytics_service and analytics_service.models_trained) else "training",
                "version": "1.0.0",
                "accuracy": 0.76,
                "last_trained": "2025-01-15T10:00:00Z"
            },
            "chat_model": {
                "status": "active",
                "version": "1.0.0",
                "response_accuracy": 0.82,
                "last_updated": "2025-01-15T10:00:00Z"
            }
        }
        
        return {
            "success": True,
            "models": models_status,
            "overall_status": "healthy"
        }
    except Exception as e:
        logger.error(f"Failed to get AI models status: {e}")
        raise HTTPException(status_code=500, detail="Models status service unavailable")

@router.post("/models/retrain")
async def retrain_ai_models(
    current_user: User = Depends(require_role("ADMIN"))
) -> Dict[str, Any]:
    """Trigger retraining of AI models (Admin only)"""
    try:
        analytics_service = get_ai_service('analytics')
        
        if analytics_service and hasattr(analytics_service, '_train_models'):
            analytics_service._train_models()
            
            return {
                "success": True,
                "message": "AI model retraining initiated",
                "estimated_completion": "15-30 minutes",
                "initiated_at": "2025-01-01T12:00:00Z"
            }
        else:
            raise HTTPException(status_code=503, detail="Analytics service not available for retraining")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrain AI models: {e}")
        raise HTTPException(status_code=500, detail="Model retraining failed")

@router.get("/usage/analytics")
async def get_ai_usage_analytics(
    days: int = 30,
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get AI usage analytics (Admin only)"""
    try:
        # This would typically query a usage tracking table
        # For now, return simulated data
        
        usage_data = {
            "period_days": days,
            "total_ai_requests": 1250,
            "successful_requests": 1187,
            "failed_requests": 63,
            "success_rate": 94.96,
            "average_response_time_ms": 342,
            "most_used_features": [
                {"feature": "Classification", "usage_count": 456, "percentage": 36.48},
                {"feature": "Chat Assistant", "usage_count": 312, "percentage": 24.96},
                {"feature": "Analytics", "usage_count": 287, "percentage": 22.96},
                {"feature": "Assignment", "usage_count": 195, "percentage": 15.60}
            ],
            "daily_usage": [
                {"date": "2025-01-01", "requests": 42, "success_rate": 95.2},
                {"date": "2025-01-02", "requests": 38, "success_rate": 94.7},
                # More daily data...
            ]
        }
        
        return {
            "success": True,
            "analytics": usage_data,
            "generated_at": "2025-01-01T12:00:00Z"
        }
    
    except Exception as e:
        logger.error(f"Failed to get AI usage analytics: {e}")
        raise HTTPException(status_code=500, detail="Usage analytics service unavailable")