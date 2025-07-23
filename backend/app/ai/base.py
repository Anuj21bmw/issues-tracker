# backend/app/ai/base.py
import os
import logging
import openai
import redis
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.core.config import settings
from app.database import SessionLocal

logger = logging.getLogger(__name__)

class AIBaseService:
    """Base service for all AI components"""
    
    def __init__(self):
        # Initialize OpenAI
        openai.api_key = os.getenv("OPENAI_API_KEY")
        if not openai.api_key:
            logger.warning("OpenAI API key not found. Some AI features may not work.")
        
        # Initialize Redis for caching
        try:
            self.redis_client = redis.Redis(host='localhost', port=6379, db=1, decode_responses=True)
            self.redis_client.ping()
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. AI caching disabled.")
            self.redis_client = None
    
    def get_db(self) -> Session:
        """Get database session"""
        return SessionLocal()
    
    def cache_result(self, key: str, data: Any, ttl: int = 3600):
        """Cache AI results to avoid repeated API calls"""
        if self.redis_client:
            try:
                import json
                self.redis_client.setex(key, ttl, json.dumps(data))
            except Exception as e:
                logger.error(f"Cache write failed: {e}")
    
    def get_cached_result(self, key: str) -> Optional[Any]:
        """Retrieve cached AI results"""
        if self.redis_client:
            try:
                import json
                cached = self.redis_client.get(key)
                return json.loads(cached) if cached else None
            except Exception as e:
                logger.error(f"Cache read failed: {e}")
        return None
    
    async def call_openai_chat(self, messages: List[Dict], model: str = "gpt-3.5-turbo", max_tokens: int = 500) -> str:
        """Make OpenAI API call with error handling"""
        try:
            response = await openai.ChatCompletion.acreate(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            return "I'm sorry, I'm experiencing technical difficulties. Please try again later."
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        try:
            from textblob import TextBlob
            blob = TextBlob(text)
            # Extract noun phrases and important words
            keywords = []
            for phrase in blob.noun_phrases:
                if len(phrase.split()) <= 3:  # Keep short phrases
                    keywords.append(phrase)
            return list(set(keywords))[:10]  # Limit to top 10
        except Exception as e:
            logger.error(f"Keyword extraction failed: {e}")
            return []
    
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts"""
        try:
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer('all-MiniLM-L6-v2')
            embeddings = model.encode([text1, text2])
            from sklearn.metrics.pairwise import cosine_similarity
            similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
            return float(similarity)
        except Exception as e:
            logger.error(f"Similarity calculation failed: {e}")
            return 0.0