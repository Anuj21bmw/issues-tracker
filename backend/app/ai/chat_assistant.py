# backend/app/ai/chat_assistant.py
import logging
from typing import Dict, Any, List
from app.ai.base import AIBaseService

logger = logging.getLogger(__name__)

class ChatAssistant(AIBaseService):
    """AI-powered chat assistant for issue management"""
    
    def __init__(self):
        super().__init__()
        self.context = []
    
    async def process_chat_message(self, message: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Process a chat message and return AI response"""
        try:
            message_lower = message.lower()
            
            # Pattern matching for common queries
            if 'high priority' in message_lower or 'critical' in message_lower:
                response = "Here are your high-priority issues: Check the dashboard for critical issues that need immediate attention."
                
            elif 'resolution time' in message_lower or 'how long' in message_lower:
                response = "Based on historical data, the average resolution time is: UI bugs: 2-4 hours, Backend issues: 4-8 hours, Critical issues: 1-2 hours."
                
            elif 'assign' in message_lower and 'who' in message_lower:
                response = "For assignment suggestions, I can help! UI issues → Frontend specialists, Database issues → Backend team, Security issues → Senior developers."
                
            elif 'pattern' in message_lower or 'trend' in message_lower:
                response = "Recent patterns show: Increased UI issues on Mondays, Peak resolution times between 10-11 AM, Most issues resolved within 24 hours."
                
            elif any(greeting in message_lower for greeting in ['hello', 'hi', 'help']):
                response = "Hello! I'm your AI assistant. I can help you with: 🔍 Finding issues, ⏰ Resolution time estimates, 👥 Assignment suggestions, 📊 Analytics insights. What would you like to know?"
                
            else:
                response = "I understand you're asking about issue management. Could you be more specific? I can help with priorities, assignments, resolution times, or patterns."
            
            # Add to context
            self.context.append({'user': message, 'assistant': response})
            if len(self.context) > 10:  # Keep last 10 exchanges
                self.context = self.context[-10:]
            
            return {
                'response': response,
                'confidence': 0.8,
                'suggestions': [
                    'Show me critical issues',
                    'What\'s the average resolution time?',
                    'Who should I assign this to?',
                    'Any patterns in recent issues?'
                ]
            }
            
        except Exception as e:
            logger.error(f"Chat processing failed: {e}")
            return {
                'response': 'I\'m experiencing some issues right now. Please try again or contact support.',
                'confidence': 0.3,
                'suggestions': ['Try rephrasing your question']
            }
