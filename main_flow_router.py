import sys
import os
from dotenv import load_dotenv

load_dotenv()

# Add paths
current_dir = os.path.dirname(__file__)
sys.path.append(current_dir)
sys.path.append(os.path.join(current_dir, 'backend'))
sys.path.append(os.path.join(current_dir, 'backend', 'RAG'))
sys.path.append(os.path.join(current_dir, 'backend', 'flows'))

# Import symptom assessment flow
try:
    from backend.flows.symptom_assessment_main import symptom_assessment_flow, menopause_support, menopause_support_enhanced
    SYMPTOM_ASSESSMENT_AVAILABLE = True
    print("✅ Symptom assessment flow loaded")
except ImportError as e:
    SYMPTOM_ASSESSMENT_AVAILABLE = False
    print(f"⚠️ Symptom assessment flow not available: {e}")

# Import RAG system
try:
    from backend.RAG.rag_pipeline import get_chatbot_response
    RAG_AVAILABLE = True
    print("✅ RAG system loaded")
except ImportError as e:
    print(f"⚠️ RAG not available: {e}")
    RAG_AVAILABLE = False
    
    def get_chatbot_response(message, history):
        return "RAG system unavailable. Please try again later."


# Import Gemini for intent classification
try:
    import google.generativeai as genai
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
        gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')
        GEMINI_AVAILABLE = True
        print("✅ Gemini loaded for intent classification")
    else:
        print("⚠️ GOOGLE_API_KEY not found")
        GEMINI_AVAILABLE = False
except ImportError:
    print("⚠️ Gemini not available")
    GEMINI_AVAILABLE = False

class SimpleIntentClassifier:
    """Simple intent classifier using Gemini or fallback"""
    
    def __init__(self):
        self.available = GEMINI_AVAILABLE
    
    def classify_intent(self, user_input):
        """Classify user intent"""
        if self.available:
            try:
                prompt = f"""Analyze this user message and classify the intent. Respond with just one word:

SYMPTOM_ASSESSMENT - if user describes personal symptoms or wants symptom evaluation
KNOWLEDGE_QUERY - if user asks general questions about menopause
EMOTIONAL_SUPPORT - if user expresses emotional distress or needs support
OUT_OF_SCOPE - if completely unrelated to menopause

User message: "{user_input}"

Response (one word only):"""

                response = gemini_model.generate_content(prompt)
                intent = response.text.strip().upper()
                
                if intent in ["SYMPTOM_ASSESSMENT", "KNOWLEDGE_QUERY", "EMOTIONAL_SUPPORT", "OUT_OF_SCOPE"]:
                    return intent
                else:
                    return self._keyword_fallback(user_input)
                    
            except Exception as e:
                print(f"Gemini classification error: {e}")
                return self._keyword_fallback(user_input)
        else:
            return self._keyword_fallback(user_input)
    
    def _keyword_fallback(self, user_input):
        """Fallback keyword-based classification"""
        user_lower = user_input.lower()
        
        if any(word in user_lower for word in ["symptom", "having", "experience", "assess", "evaluate"]):
            return "SYMPTOM_ASSESSMENT"
        elif any(word in user_lower for word in ["worried", "scared", "anxious", "feel", "emotional"]):
            return "EMOTIONAL_SUPPORT"
        elif any(word in user_lower for word in ["what", "how", "why", "explain", "tell me"]):
            return "KNOWLEDGE_QUERY"
        else:
            return "OUT_OF_SCOPE"

class SessionState:
    """Simple session state management"""
    def __init__(self, session_id):
        self.session_id = session_id
        self.current_flow = "main_menu"  # "main_menu"|"symptom_assessment"|"knowledge_query"|"emotional_support"
        self.conversation_history = []
    
    def reset_assessment(self):
        """Reset symptom assessment state"""
        if self.current_flow == "symptom_assessment" and SYMPTOM_ASSESSMENT_AVAILABLE:
            # The MRSFlow handles its own state reset via __init__() in _exit_flow and _score_and_respond
            pass
        self.current_flow = "main_menu"

class MainFlowRouter:
    """Simplified main flow router"""
    
    def __init__(self):
        self.sessions = {}
        self.intent_classifier = SimpleIntentClassifier()
        
        self.welcome_message = """👋 Welcome to the Menopause Health Support System!

I can help you with:
1. 🔍 **Symptom Assessment** - Evaluate your menopause symptoms
2. 💡 **Knowledge Queries** - Answer questions about menopause
3. 💝 **Emotional Support** - Provide psychological support

What would you like help with today?"""

        self.out_of_scope_message = """I'm specifically designed to help with menopause-related health concerns. Your question seems to be outside my area of expertise.

I can help you with:
- Understanding menopause symptoms
- Symptom assessment and evaluation
- Information about treatments and lifestyle changes
- Emotional support during menopause transition

Is there anything about menopause I can help you with?"""

    def get_session(self, session_id):
        """Get or create session"""
        if session_id not in self.sessions:
            self.sessions[session_id] = SessionState(session_id)
        return self.sessions[session_id]

    def route_request(self, user_input, session_id="default"):
        """Main routing function"""
        session = self.get_session(session_id)
        user_input = user_input.strip()
        
        if not user_input:
            return {
                "response": self.welcome_message,
                "status": "success",
                "flow": "main_menu",
                "action_needed": "none"
            }
        
        # Record conversation history
        session.conversation_history.append({"role": "user", "content": user_input})
        
        try:
            # Handle global commands
            user_lower = user_input.lower()
            if user_lower in ["help", "?", "start", "restart", "main menu", "home"]:
                session.reset_assessment()
                return {
                    "response": self.welcome_message,
                    "status": "success",
                    "flow": "main_menu",
                    "action_needed": "none"
                }
            
            if user_lower in ["quit", "exit", "goodbye", "bye"]:
                session.reset_assessment()
                return {
                    "response": "Thank you for using the Menopause Health Support System! Take care! 👋",
                    "status": "success",
                    "flow": "ended",
                    "action_needed": "none"
                }
            
            # Route based on current state
            if session.current_flow == "main_menu":
                result = self._handle_main_menu(user_input, session)
            elif session.current_flow == "symptom_assessment":
                result = self._handle_symptom_assessment(user_input, session)
            elif session.current_flow == "knowledge_query":
                result = self._handle_knowledge_query(user_input, session)
            elif session.current_flow == "emotional_support":
                result = self._handle_emotional_support(user_input, session)
            else:
                result = self._handle_unknown_state(session)
            
            # Record response in history
            session.conversation_history.append({"role": "assistant", "content": result["response"]})
            
            return result
            
        except Exception as e:
            print(f"❌ Error in main router: {e}")
            return {
                "response": "Sorry, I encountered an error. Please try again.",
                "status": "error",
                "flow": session.current_flow,
                "action_needed": "restart"
            }
    
    def _handle_main_menu(self, user_input, session):
        """Handle main menu state with intent classification"""
        # Classify intent
        intent = self.intent_classifier.classify_intent(user_input)
        print(f"🎯 Classified intent: {intent}")
        
        # Route based on intent
        if intent == "OUT_OF_SCOPE":
            return {
                "response": self.out_of_scope_message,
                "status": "success",
                "flow": "main_menu",
                "action_needed": "none"
            }
        
        elif intent == "SYMPTOM_ASSESSMENT":
            session.current_flow = "symptom_assessment"
            if SYMPTOM_ASSESSMENT_AVAILABLE:
                # Start symptom assessment using the real flow
                print(f"🧪 Calling menopause_support_enhanced with: {user_input}")
                assessment_result = menopause_support_enhanced(user_input)
                print(f"🧪 Assessment result: {assessment_result}")
                
                return self._process_symptom_result(assessment_result, session)
            else:
                # Fallback to RAG with symptom context
                if RAG_AVAILABLE:
                    rag_response = get_chatbot_response(f"symptom assessment: {user_input}", [])
                    response = "I understand you want to assess your symptoms. Let me provide you with some information that might help.\n\n" + rag_response
                else:
                    response = "I understand you want to assess your symptoms. For a detailed symptom assessment, I recommend consulting with a healthcare professional."
                
                return {
                    "response": response,
                    "status": "success", 
                    "flow": "symptom_assessment",
                    "action_needed": "none"
                }
        
        elif intent == "EMOTIONAL_SUPPORT":
            session.current_flow = "emotional_support"
            return self._handle_emotional_support(user_input, session)
        
        else:  # KNOWLEDGE_QUERY
            session.current_flow = "knowledge_query"
            return self._handle_knowledge_query(user_input, session)
    
    def _handle_symptom_assessment(self, user_input, session):
        """Handle symptom assessment flow"""
        if SYMPTOM_ASSESSMENT_AVAILABLE:
            assessment_result = menopause_support_enhanced(user_input)
            print(f"🧪 Assessment result: {assessment_result}")
            
            return self._process_symptom_result(assessment_result, session)
        else:
            # Fallback when symptom assessment not available
            if RAG_AVAILABLE:
                rag_response = get_chatbot_response(f"symptom assessment: {user_input}", [])
                response = "I understand you want to continue with symptom assessment. Here's some relevant information:\n\n" + rag_response
            else:
                response = "I'm sorry, the symptom assessment system is currently unavailable. Please consult with a healthcare professional."
            
            return {
                "response": response,
                "status": "success",
                "flow": "symptom_assessment",
                "action_needed": "none"
            }
    
    def _process_symptom_result(self, assessment_result, session):
        """Process the result from symptom assessment flow"""
        if not isinstance(assessment_result, dict):
            # Handle unexpected format
            return {
                "response": str(assessment_result),
                "status": "success",
                "flow": "symptom_assessment",
                "action_needed": "none"
            }
        
        status = assessment_result.get("status", "success")
        message = assessment_result.get("message", str(assessment_result))
        
        # Handle different statuses from the latest symptom flow
        if status == "exit_confirmation_pending":
            # The symptom flow is asking for exit confirmation
            return {
                "response": message,
                "status": "success",
                "flow": "symptom_assessment",
                "action_needed": "none"
            }
        
        elif status == "zero_confirmation_pending":
            # The symptom flow is asking for zero score confirmation
            return {
                "response": message,
                "status": "success",
                "flow": "symptom_assessment",
                "action_needed": "none"
            }
        
        elif status == "clarification_needed":
            # The symptom flow needs clarification
            return {
                "response": message,
                "status": "success",
                "flow": "symptom_assessment",
                "action_needed": "none"
            }
        
        elif status == "asking_next_symptom":
            # Continue with next symptom question
            return {
                "response": message,
                "status": "success",
                "flow": "symptom_assessment",
                "action_needed": "none"
            }
        
        elif status == "continue_assessment":
            # Continue with the assessment
            return {
                "response": message,
                "status": "success",
                "flow": "symptom_assessment",
                "action_needed": "none"
            }
        
        elif status == "scoring_completed_and_exited":
            # Assessment completed with score
            mrs_score = assessment_result.get("mrs_score", "N/A")
            completion_msg = message + f"\n\n📊 Your MRS Score: {mrs_score}"
            completion_msg += "\n\nDo you have any other questions? I can provide information about menopause or offer emotional support."
            session.current_flow = "knowledge_query"
            return {
                "response": completion_msg,
                "status": "success",
                "flow": "knowledge_query",
                "action_needed": "none"
            }
        
        elif status == "exit_confirmed":
            # User exited the assessment
            original_question = assessment_result.get("original_question")
            
            # Reset to main menu
            session.reset_assessment()
            
            # If there was an original question, try to handle it
            if original_question:
                print(f"🔄 Processing original question after exit: {original_question}")
                intent = self.intent_classifier.classify_intent(original_question)
                
                if intent == "KNOWLEDGE_QUERY":
                    session.current_flow = "knowledge_query"
                    return self._handle_knowledge_query(original_question, session)
                elif intent == "EMOTIONAL_SUPPORT":
                    session.current_flow = "emotional_support"
                    return self._handle_emotional_support(original_question, session)
                else:
                    # Default to knowledge query for the original question
                    session.current_flow = "knowledge_query"
                    if RAG_AVAILABLE:
                        rag_response = get_chatbot_response(original_question, [])
                        response = message + "\n\nRegarding your original question:\n" + rag_response
                    else:
                        response = message + "\n\n" + self.welcome_message
                    return {
                        "response": response,
                        "status": "success",
                        "flow": "knowledge_query",
                        "action_needed": "none"
                    }
            else:
                # No original question, return to main menu
                return {
                    "response": message + "\n\n" + self.welcome_message,
                    "status": "success",
                    "flow": "main_menu",
                    "action_needed": "none"
                }
        
        elif status == "error":
            # Handle error from symptom flow
            return {
                "response": message + "\n\nLet's try again. Please describe your symptoms.",
                "status": "error",
                "flow": "symptom_assessment",
                "action_needed": "none"
            }
        
        else:
            # Unknown status, continue with assessment
            print(f"⚠️ Unknown symptom assessment status: {status}")
            return {
                "response": message,
                "status": "success",
                "flow": "symptom_assessment",
                "action_needed": "none"
            }
    
    def _handle_knowledge_query(self, user_input, session):
        """Handle knowledge query flow"""
        # Check if user wants to start symptom assessment
        intent = self.intent_classifier.classify_intent(user_input)
        
        if intent == "SYMPTOM_ASSESSMENT":
            session.current_flow = "symptom_assessment"
            if SYMPTOM_ASSESSMENT_AVAILABLE:
                assessment_result = menopause_support_enhanced(user_input)
                intro_message = "I understand you want to assess your symptoms. Let me help you with that.\n\n"
                
                result = self._process_symptom_result(assessment_result, session)
                result["response"] = intro_message + result["response"]
                return result
            else:
                # Fallback to RAG
                if RAG_AVAILABLE:
                    rag_response = get_chatbot_response(f"symptom assessment: {user_input}", [])
                    response = "I understand you want to assess your symptoms. Let me provide you with some information that might help.\n\n" + rag_response
                else:
                    response = "I understand you want to assess your symptoms. For a detailed assessment, I recommend consulting with a healthcare professional."
                return {
                    "response": response,
                    "status": "success",
                    "flow": "symptom_assessment",
                    "action_needed": "none"
                }
        
        elif intent == "EMOTIONAL_SUPPORT":
            session.current_flow = "emotional_support"
            return self._handle_emotional_support(user_input, session)
        
        elif intent == "OUT_OF_SCOPE":
            return {
                "response": self.out_of_scope_message,
                "status": "success",
                "flow": "knowledge_query",
                "action_needed": "none"
            }
        
        # Process knowledge query with RAG
        if RAG_AVAILABLE:
            rag_response = get_chatbot_response(user_input, [])
            response = rag_response + "\n\n💡 Is there anything else about menopause you'd like to know?"
        else:
            response = "I apologize, but my knowledge system is currently unavailable. Please consult with a healthcare professional for menopause-related questions."
        
        return {
            "response": response,
            "status": "success",
            "flow": "knowledge_query",
            "action_needed": "none"
        }
    
    def _handle_emotional_support(self, user_input, session):
        """Handle emotional support flow"""
        # Check if user wants to switch to other flows
        intent = self.intent_classifier.classify_intent(user_input)
        
        if intent == "SYMPTOM_ASSESSMENT":
            session.current_flow = "symptom_assessment"
            if SYMPTOM_ASSESSMENT_AVAILABLE:
                assessment_result = menopause_support_enhanced(user_input)
                intro_message = "I understand you want to assess your symptoms. Let me help you with that.\n\n"
                
                result = self._process_symptom_result(assessment_result, session)
                result["response"] = intro_message + result["response"]
                return result
            # If symptom assessment not available, fall through to other options
        
        elif intent == "KNOWLEDGE_QUERY":
            session.current_flow = "knowledge_query"
            return self._handle_knowledge_query(user_input, session)
        
        elif intent == "OUT_OF_SCOPE":
            return {
                "response": self.out_of_scope_message,
                "status": "success",
                "flow": "emotional_support",
                "action_needed": "none"
            }
        
        # Provide emotional support using RAG with emotional context
        if RAG_AVAILABLE:
            emotional_context = f"emotional support needed: {user_input}"
            rag_response = get_chatbot_response(emotional_context, [])
            response = rag_response + "\n\n💝 Remember, you're not alone in this journey. Would you like to:\n• Learn more about managing specific symptoms\n• Continue talking about your feelings\n• Get a systematic symptom assessment"
        else:
            response = """I hear you, and I want you to know that what you're feeling is completely valid. Menopause is a significant life transition, and it's normal to feel overwhelmed or anxious about the changes.

You're not alone in this journey. Many women experience similar feelings during menopause. Consider reaching out to healthcare providers, support groups, or trusted friends and family.

💝 I'm here to support you. What specific aspect of your menopause experience would you like to talk about?"""
        
        return {
            "response": response,
            "status": "success",
            "flow": "emotional_support",
            "action_needed": "none"
        }
    
    def _handle_unknown_state(self, session):
        """Handle unknown state"""
        session.reset_assessment()
        return {
            "response": "I seem to have lost track of our conversation. Let's start fresh.\n\n" + self.welcome_message,
            "status": "success",
            "flow": "main_menu",
            "action_needed": "none"
        }

# Global router instance
main_router = MainFlowRouter()

def process_user_input(user_input, session_id="default"):
    """
    Main interface function for external use
    """
    try:
        return main_router.route_request(user_input, session_id)
    except Exception as e:
        print(f"❌ Error in process_user_input: {e}")
        return {
            "response": "I apologize, but I encountered an error. Please try again.",
            "status": "error",
            "flow": "main_menu",
            "action_needed": "none"
        }

# Test function
if __name__ == "__main__":
    print("🧪 Testing Main Flow Router...")
    
    test_messages = [
        "What is menopause?",
        "I'm having hot flashes and mood swings", 
        "I feel anxious about these changes",
        "What's the weather like today?"
    ]
    
    for msg in test_messages:
        print(f"\n❓ Testing: {msg}")
        result = process_user_input(msg)
        print(f"📝 Intent/Flow: {result['flow']}")
        print(f"💬 Response: {result['response'][:100]}...")
        print("-" * 50)