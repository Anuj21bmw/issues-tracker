# backend/app/core/ai_config.py - 


import os
from typing import Dict, Any
from pydantic import BaseSettings

class AISettings(BaseSettings):
    """AI service configuration settings"""
    
    # General AI settings
    ai_enabled: bool = True
    ai_debug_mode: bool = False
    ai_confidence_threshold: float = 0.6
    ai_batch_size: int = 100
    ai_timeout_seconds: int = 30
    
    # Classification settings
    classification_enabled: bool = True
    classification_threshold: float = 0.7
    auto_classification: bool = True
    
    # Chat assistant settings
    chat_enabled: bool = True
    chat_history_limit: int = 50
    chat_response_timeout: int = 10
    
    # Analytics settings
    analytics_enabled: bool = True
    prediction_enabled: bool = True
    model_retrain_interval_hours: int = 24
    analytics_cache_ttl: int = 300
    
    # Document processing settings
    document_processing_enabled: bool = True
    max_document_size_mb: int = 10
    ocr_enabled: bool = True
    supported_formats: str = ".pdf,.jpg,.jpeg,.png,.gif,.doc,.docx,.txt"
    
    # Assignment engine settings
    assignment_suggestions_enabled: bool = True
    workload_balancing_enabled: bool = True
    assignment_confidence_threshold: float = 0.5
    
    # Notification settings
    smart_notifications_enabled: bool = True
    escalation_detection_enabled: bool = True
    notification_batch_size: int = 50
    
    # Performance settings
    ai_worker_threads: int = 4
    enable_caching: bool = True
    cache_ttl_seconds: int = 300
    enable_metrics: bool = True
    
    # Model settings
    model_storage_path: str = "models/"
    enable_model_versioning: bool = True
    model_backup_enabled: bool = True
    
    class Config:
        env_prefix = "AI_"
        case_sensitive = False

# Global AI settings instance
ai_settings = AISettings()

def get_ai_config() -> Dict[str, Any]:
    """Get current AI configuration"""
    return ai_settings.dict()

def update_ai_config(**kwargs) -> Dict[str, Any]:
    """Update AI configuration"""
    for key, value in kwargs.items():
        if hasattr(ai_settings, key):
            setattr(ai_settings, key, value)
    
    return get_ai_config()

def is_ai_feature_enabled(feature: str) -> bool:
    """Check if a specific AI feature is enabled"""
    feature_map = {
        'classification': ai_settings.classification_enabled,
        'chat': ai_settings.chat_enabled,
        'analytics': ai_settings.analytics_enabled,
        'document_processing': ai_settings.document_processing_enabled,
        'assignment': ai_settings.assignment_suggestions_enabled,
        'notifications': ai_settings.smart_notifications_enabled,
        'prediction': ai_settings.prediction_enabled
    }
    
    return ai_settings.ai_enabled and feature_map.get(feature, False)
