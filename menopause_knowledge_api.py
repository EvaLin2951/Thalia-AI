"""
Menopause Knowledge & Support API
Bridge between main flow router and RAG system
"""

import sys
import os
from typing import Dict, Any

# Add RAG module path
sys.path.append(os.path.join(os.path.dirname(__file__), 'RAG'))

try:
    from RAG.rag_pipeline import get_chatbot_response
    RAG_AVAILABLE = True
    print("✅ RAG system loaded successfully")
except ImportError as e:
    print(f"⚠️ Warning: RAG module not available: {e}")
    RAG_AVAILABLE = False

class MenopauseKnowledgeAPI:
    """Menopause Knowledge and Support API"""
    
    def __init__(self):
        self.rag_available = RAG_AVAILABLE
        if not self.rag_available:
            print("⚠️ Running in fallback mode without RAG")
    
    def process_query(self, user_message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process user query using RAG system
        
        Args:
            user_message (str): User input message
            context (dict): Context information from main router
            
        Returns:
            dict: Response with metadata
        """
        
        if context is None:
            context = {}
            
        try:
            if self.rag_available:
                # Call RAG system (uses Gemini)
                rag_response = get_chatbot_response(user_message, [])
                
                # Analyze response for intent and metadata
                intent_info = self._analyze_response(user_message, rag_response, context)
                
                return {
                    "response": rag_response,
                    "intent": intent_info["intent"],
                    "confidence": intent_info["confidence"],
                    "sources": intent_info.get("sources", []),
                    "next_action": intent_info.get("next_action", "continue"),
                    "session_data": self._update_session_data(context, intent_info)
                }
            else:
                return self._fallback_response(user_message, context)
                
        except Exception as e:
            print(f"❌ Error processing query: {e}")
            return self._error_response(str(e))
    
    def _analyze_response(self, user_message: str, rag_response: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze response and determine metadata"""
        user_lower = user_message.lower()
        response_lower = rag_response.lower()
        
        # Detect response type based on content
        if any(phrase in response_lower for phrase in [
            'i understand', 'you\'re not alone', 'it\'s normal to feel', 'many women experience'
        ]):
            intent = "emotional_support"
            confidence = 0.8
        elif any(phrase in response_lower for phrase in [
            'not in my expertise', 'recommend consulting', 'outside my scope'
        ]):
            intent = "out_of_scope"
            confidence = 0.9
        elif any(word in user_lower for word in ['what', 'how', 'why', 'explain', 'tell me']):
            intent = "knowledge_query"
            confidence = 0.7
        else:
            intent = "general_query"
            confidence = 0.6
        
        return {
            "intent": intent,
            "confidence": confidence,
            "sources": ["medical_guidelines"] if intent != "out_of_scope" else [],
            "next_action": "redirect" if intent == "out_of_scope" else "continue"
        }
    
    def _update_session_data(self, context: Dict[str, Any], intent_info: Dict[str, Any]) -> Dict[str, Any]:
        """Update session data"""
        session_data = context.get("session_data", {})
        
        if "query_history" not in session_data:
            session_data["query_history"] = []
        
        session_data["query_history"].append({
            "intent": intent_info["intent"],
            "confidence": intent_info["confidence"],
            "source_flow": context.get("source_flow", "unknown")
        })
        
        # Keep last 10 queries
        if len(session_data["query_history"]) > 10:
            session_data["query_history"] = session_data["query_history"][-10:]
        
        return session_data
    
    def _fallback_response(self, user_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback when RAG unavailable"""
        return {
            "response": "I apologize, but my knowledge system is currently unavailable. Please consult with a healthcare professional for menopause-related questions.",
            "intent": "system_error",
            "confidence": 1.0,
            "sources": [],
            "next_action": "redirect",
            "session_data": context.get("session_data", {})
        }
    
    def _error_response(self, error_message: str) -> Dict[str, Any]:
        """Error response"""
        return {
            "response": "I'm sorry, I encountered an error processing your request. Please try again.",
            "intent": "system_error",
            "confidence": 1.0,
            "sources": [],
            "next_action": "retry",
            "session_data": {},
            "error": error_message
        }
    
    def health_check(self) -> Dict[str, Any]:
        """System health check"""
        return {
            "status": "healthy" if self.rag_available else "degraded",
            "rag_available": self.rag_available,
            "version": "1.0.0"
        }

# Global API instance
knowledge_api = MenopauseKnowledgeAPI()

# Convenience functions for external use
def process_knowledge_query(user_message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Process knowledge query - main interface function"""
    return knowledge_api.process_query(user_message, context)

def get_api_status() -> Dict[str, Any]:
    """Get API status"""
    return knowledge_api.health_check()

# Test function
if __name__ == "__main__":
    print("🧪 Testing Menopause Knowledge API...")
    
    # Test API status
    status = get_api_status()
    print(f"API Status: {status}")
    
    # Test queries
    test_queries = [
        "What is menopause?",
        "I'm feeling anxious about these changes",
        "How do I manage hot flashes?",
        "What's the weather like today?"
    ]
    
    for query in test_queries:
        print(f"\n❓ Query: {query}")
        result = process_knowledge_query(query)
        print(f"📝 Intent: {result['intent']}")
        print(f"💬 Response: {result['response'][:100]}...")
        print(f"➡️  Next action: {result['next_action']}")
        print("-" * 50)