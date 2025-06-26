"""
Response Handler - Handles user input and generates chat responses
"""
import traceback
from config import ERROR_MESSAGES


class ThaliaResponseHandler:
    """Handles responses for Thalia Gradio interface"""
    
    def __init__(self, user_manager=None, main_router_available=False, rag_available=False, 
                 process_user_input=None, rag_response=None):
        self.session_data = {}
        self.user_manager = user_manager
        self.auth_available = user_manager is not None
        self.main_router_available = main_router_available
        self.rag_available = rag_available
        self.process_user_input = process_user_input
        self.rag_response = rag_response
        print(f"🔧 ThaliaResponseHandler initialization completed, user_manager: {self.auth_available}")
        
    def get_chatbot_response(self, message: str, session_id="default"):
        """Main response function for processing user input"""
        print(f"💬 get_chatbot_response called: message='{message[:50]}...', session_id='{session_id[:8] if session_id else 'None'}'")
        
        if not message.strip():
            return "I'm here to help with your menopause journey. What would you like to know?"
        
        # Check user authentication
        if self.auth_available and self.user_manager and session_id != "default":
            if not self.user_manager.is_logged_in(session_id):
                return "Please log in to continue our conversation."
            
            # Update user activity
            self.user_manager.update_user_activity(session_id)
            self.user_manager.increment_conversation_count(session_id)
            
            # Get user info for personalization
            username = self.user_manager.get_username(session_id)
            print(f"👤 User: {username} - processing message")
        
        try:
            if self.main_router_available and self.process_user_input:
                # Use full system
                result = self.process_user_input(message, session_id)
                response = result.get("response", "I'm having trouble processing your request.")
                status = result.get("status", "unknown")
                flow = result.get("flow", "unknown")
                
                print(f"🔄 Flow: {flow}, Status: {status}")
                
                # Add personalization
                if (self.auth_available and self.user_manager and 
                    session_id != "default" and self.user_manager.is_logged_in(session_id)):
                    user_info = self.user_manager.get_user_info(session_id)
                    if user_info and "hello" in message.lower() and status == "conversation_start":
                        preferred_name = user_info.get('profile', {}).get('preferred_name', 'there')
                        response = f"Hello {preferred_name}! " + response
                
                return response
                
            elif self.rag_available and self.rag_response:
                print("⚠️ Using RAG fallback mode")
                return self.rag_response(message, [])
                
            else:
                # If no systems are available, provide basic response
                print("⚠️ Using basic response mode")
                return self._get_basic_response(message)
                
        except Exception as e:
            print(f"❌ Response handler error: {e}")
            traceback.print_exc()
            return ERROR_MESSAGES["processing_error"]

    def _get_basic_response(self, message: str) -> str:
        """Provide basic responses when no other systems are available"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['hello', 'hi', 'hey']):
            return """Hello! Welcome to Thalia, your menopause support companion. 

I'm here to help you navigate your menopause journey with reliable information and support. While some of my advanced features aren't currently available, I can still provide basic guidance and be a listening ear.

What would you like to know about menopause today?"""
        
        elif any(word in message_lower for word in ['symptom', 'hot flash', 'period', 'mood']):
            return """I understand you're experiencing symptoms that might be related to menopause. This is completely normal and you're not alone in this journey.

Common menopause symptoms include:
- Hot flashes and night sweats
- Irregular periods
- Mood changes
- Sleep disturbances
- Changes in energy levels

For personalized guidance and symptom assessment, I recommend consulting with your healthcare provider. They can help determine the best approach for your specific situation.

Is there anything specific you'd like to know more about?"""
        
        elif any(word in message_lower for word in ['help', 'support', 'guidance']):
            return """I'm here to support you through your menopause journey. While my full capabilities aren't currently available, I can still offer:

- General information about menopause
- Emotional support and understanding
- Basic guidance on common concerns
- Encouragement that you're not alone

Remember, every woman's menopause experience is unique, and it's always best to consult with healthcare professionals for personalized medical advice.

What aspect of menopause would you like to explore?"""
        
        else:
            return """Thank you for reaching out. I'm Thalia, and I'm here to support you through your menopause journey. 

While some of my advanced features aren't currently available, I'm still here to listen and provide what guidance I can. Please feel free to share what's on your mind, and I'll do my best to help.

For comprehensive medical advice, always consult with your healthcare provider."""

    def custom_chat_function(self, message, chat_history, session_id=None):
        """Custom chat function with conversation saving functionality"""
        print(f"💬 custom_chat_function called: message_length={len(message) if message else 0}, session={session_id[:8] if session_id else 'None'}")
        
        if not message.strip():
            return "", chat_history
        
        # If authentication is available, check session
        if self.auth_available and self.user_manager and session_id:
            if not self.user_manager.is_logged_in(session_id):
                print("❌ Invalid session, user not logged in")
                return "", chat_history
            
            # Call response handler with session
            bot_response_content = self.get_chatbot_response(message, session_id)
            
            # Save message
            try:
                self.user_manager.save_message(session_id, message, bot_response_content)
                print("💾 Message saved")
            except Exception as e:
                print(f"⚠️ Failed to save message: {e}")
            
        else:
            # Fallback behavior without authentication
            bot_response_content = self.get_chatbot_response(message)

        # Update Gradio Chatbot display history
        chat_history.append({"role": "user", "content": message})
        chat_history.append({"role": "assistant", "content": bot_response_content})
        
        print(f"✅ Chat response generation completed, history length: {len(chat_history)}")
        return "", chat_history