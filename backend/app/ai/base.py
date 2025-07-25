# backend/app/ai/base.py - Complete AI Base Service Implementation
import logging
import os
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import openai
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.core.config import settings

logger = logging.getLogger(__name__)

class AIBaseService:
    """Base class for all AI services with common functionality"""
    
    def __init__(self):
        # Initialize OpenAI client (if API key is provided)
        self.openai_client = None
        if hasattr(settings, 'openai_api_key') and settings.openai_api_key:
            openai.api_key = settings.openai_api_key
            self.openai_client = openai
        
        # Rate limiting
        self.last_api_call = {}
        self.api_call_delays = {
            'openai': 1.0,  # 1 second between calls
            'classification': 0.5,
            'analysis': 2.0
        }
        
        # Cache for frequent operations
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
        
        logger.info(f"Initialized {self.__class__.__name__}")
    
    def get_db(self) -> Session:
        """Get database session"""
        return SessionLocal()
    
    async def call_openai_chat(
        self, 
        messages: List[Dict], 
        model: str = "gpt-3.5-turbo",
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> str:
        """Make OpenAI chat completion call with rate limiting and fallbacks"""
        try:
            # Rate limiting
            await self._rate_limit('openai')
            
            if not self.openai_client:
                # Fallback to mock response if no OpenAI API key
                return await self._mock_ai_response(messages)
            
            response = await asyncio.to_thread(
                self.openai_client.ChatCompletion.create,
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            return await self._mock_ai_response(messages)
    
    async def _mock_ai_response(self, messages: List[Dict]) -> str:
        """Generate mock AI responses for development/fallback"""
        last_message = messages[-1]['content'].lower()
        
        # Issue classification mock responses
        if 'classify' in last_message or 'severity' in last_message:
            if 'critical' in last_message or 'urgent' in last_message:
                return "HIGH"
            elif 'minor' in last_message or 'low' in last_message:
                return "LOW"
            else:
                return "MEDIUM"
        
        # Time prediction mock responses
        if 'time' in last_message or 'estimate' in last_message:
            return "Based on similar issues, this will likely take 2-4 hours to resolve."
        
        # Assignment mock responses
        if 'assign' in last_message or 'who should' in last_message:
            return "I recommend assigning this to a senior developer with expertise in the relevant technology stack."
        
        # General helpful response
        return "I understand your request. Let me analyze the available data and provide you with insights."
    
    async def _rate_limit(self, service: str):
        """Apply rate limiting for API calls"""
        if service in self.last_api_call:
            elapsed = datetime.now() - self.last_api_call[service]
            delay_needed = self.api_call_delays.get(service, 1.0)
            
            if elapsed.total_seconds() < delay_needed:
                sleep_time = delay_needed - elapsed.total_seconds()
                await asyncio.sleep(sleep_time)
        
        self.last_api_call[service] = datetime.now()
    
    def _cache_get(self, key: str) -> Optional[Any]:
        """Get cached value if not expired"""
        if key in self.cache:
            cached_item = self.cache[key]
            if datetime.now() - cached_item['timestamp'] < timedelta(seconds=self.cache_ttl):
                return cached_item['value']
            else:
                del self.cache[key]
        return None
    
    def _cache_set(self, key: str, value: Any):
        """Set cached value with timestamp"""
        self.cache[key] = {
            'value': value,
            'timestamp': datetime.now()
        }
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text for analysis"""
        if not text:
            return []
        
        # Simple keyword extraction (could be enhanced with NLP libraries)
        common_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 
            'has', 'had', 'will', 'would', 'could', 'should', 'this', 'that', 'it'
        }
        
        words = text.lower().split()
        keywords = []
        
        for word in words:
            # Clean word
            cleaned = ''.join(c for c in word if c.isalnum())
            if len(cleaned) > 2 and cleaned not in common_words:
                keywords.append(cleaned)
        
        return list(set(keywords))  # Remove duplicates
    
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts using simple keyword overlap"""
        if not text1 or not text2:
            return 0.0
        
        keywords1 = set(self.extract_keywords(text1))
        keywords2 = set(self.extract_keywords(text2))
        
        if not keywords1 or not keywords2:
            return 0.0
        
        intersection = keywords1.intersection(keywords2)
        union = keywords1.union(keywords2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def format_duration(self, hours: float) -> str:
        """Format duration in hours to human-readable string"""
        if hours < 1:
            minutes = int(hours * 60)
            return f"{minutes} minutes"
        elif hours < 24:
            return f"{hours:.1f} hours"
        else:
            days = int(hours // 24)
            remaining_hours = int(hours % 24)
            if remaining_hours > 0:
                return f"{days} days, {remaining_hours} hours"
            else:
                return f"{days} days"
    
    def get_business_hours_between(self, start: datetime, end: datetime) -> float:
        """Calculate business hours between two datetimes"""
        # Simple implementation - assumes 8 hours/day, 5 days/week
        total_hours = (end - start).total_seconds() / 3600
        
        # Rough business hours calculation (can be made more sophisticated)
        business_hours = total_hours * 0.33  # Assuming 8/24 hours per day, 5/7 days per week
        
        return max(0, business_hours)
    
    def validate_ai_response(self, response: str, expected_type: str = 'text') -> bool:
        """Validate AI response based on expected type"""
        if not response:
            return False
        
        if expected_type == 'severity':
            return response.upper() in ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
        elif expected_type == 'boolean':
            return response.lower() in ['true', 'false', 'yes', 'no']
        elif expected_type == 'number':
            try:
                float(response)
                return True
            except ValueError:
                return False
        
        return True  # Default validation for text
    
    async def batch_process(
        self, 
        items: List[Any], 
        process_func, 
        batch_size: int = 10,
        delay_between_batches: float = 1.0
    ) -> List[Any]:
        """Process items in batches to avoid rate limits"""
        results = []
        
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            batch_results = []
            
            for item in batch:
                try:
                    result = await process_func(item)
                    batch_results.append(result)
                except Exception as e:
                    logger.error(f"Batch processing error for item {i}: {e}")
                    batch_results.append(None)
            
            results.extend(batch_results)
            
            # Delay between batches
            if i + batch_size < len(items):
                await asyncio.sleep(delay_between_batches)
        
        return results
    
    def log_ai_operation(self, operation: str, success: bool, details: Dict = None):
        """Log AI operations for monitoring and debugging"""
        log_data = {
            'service': self.__class__.__name__,
            'operation': operation,
            'success': success,
            'timestamp': datetime.now().isoformat()
        }
        
        if details:
            log_data.update(details)
        
        if success:
            logger.info(f"AI Operation Success: {log_data}")
        else:
            logger.error(f"AI Operation Failed: {log_data}")