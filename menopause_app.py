import gradio as gr
import sys
import os

# Add paths for imports
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'api'))

# Try to import the main flow router (your full system)
try:
    from main_flow_router import process_user_input
    MAIN_ROUTER_AVAILABLE = True
    print("✅ Main flow router loaded successfully")
except ImportError as e:
    print(f"⚠️ Main router not available: {e}")
    MAIN_ROUTER_AVAILABLE = False
    
    # Fallback to RAG only
    try:
        from backend.RAG.rag_pipeline import get_chatbot_response as rag_response
        RAG_AVAILABLE = True
        print("✅ RAG system available as fallback")
    except ImportError:
        print("❌ Neither main router nor RAG available")
        RAG_AVAILABLE = False

class ThaliaResponseHandler:
    """Handles responses for the Thalia Gradio interface"""
    
    def __init__(self):
        self.session_data = {}  # Store session data for each user
        
    def get_chatbot_response(self, user_message: str, chat_history, session_id="default"):
        """
        Main response function for Gradio ChatInterface
        
        Args:
            user_message: User's input message
            chat_history: Gradio chat history (list of tuples)
            session_id: Session identifier
        
        Returns:
            response: Chatbot response string
        """
        
        if not user_message.strip():
            return "I'm here to help with your menopause journey. What would you like to know?"
        
        try:
            if MAIN_ROUTER_AVAILABLE:
                # Use the full system with intent classification and flow routing
                result = process_user_input(user_message, session_id)
                
                # Extract response from the router result
                response = result.get("response", "I'm having trouble processing your request.")
                status = result.get("status", "unknown")
                flow = result.get("flow", "unknown")
                
                # Log system status for debugging
                print(f"🔄 Flow: {flow}, Status: {status}")
                
                # Handle special cases
                if status == "needs_exit_confirmation":
                    print("🤔 User may want to switch topics - waiting for confirmation")
                elif status == "scoring_completed":
                    mrs_score = result.get("mrs_score", "N/A")
                    print(f"📊 MRS Assessment completed with score: {mrs_score}")
                elif status == "user_exit":
                    print("🚪 User exited current flow")
                
                return response
                
            elif RAG_AVAILABLE:
                # Fallback to RAG only
                print("⚠️ Using RAG fallback mode")
                return rag_response(user_message, [])
                
            else:
                # No system available
                return ("I apologize, but my systems are currently unavailable. "
                       "Please try again later or consult with a healthcare professional "
                       "for immediate menopause-related concerns.")
                
        except Exception as e:
            print(f"❌ Error in response handler: {e}")
            return ("I encountered an error processing your request. "
                   "Please try rephrasing your question or try again.")

# Create the response handler
response_handler = ThaliaResponseHandler()

def chatbot_response_wrapper(user_message, chat_history):
    """
    Wrapper function for Gradio ChatInterface
    This is what gets passed to gr.ChatInterface()
    """
    return response_handler.get_chatbot_response(user_message, chat_history)

# JavaScript and CSS (keep your existing styling)
js = """
function titleAnimation() {
    var container = document.createElement('div');
    container.id = 'animation';
    container.style.fontSize = '2.2em';
    container.style.fontWeight = 'bold';
    container.style.textAlign = 'center';
    container.style.marginBottom = '20px';
    container.style.color = '#8B4A8B';

    var text = "Thalia";
    for (var i = 0; i < text.length; i++) {
        (function(i){
            setTimeout(function(){
                var letter = document.createElement('span');
                letter.style.opacity = '0';
                letter.style.transition = 'opacity 0.6s ease-in-out';
                letter.innerText = text[i];

                container.appendChild(letter);

                setTimeout(function() {
                    letter.style.opacity = '1';
                }, 100);
            }, i * 150);
        })(i);
    }

    var gradioContainer = document.querySelector('.gradio-container');
    if (gradioContainer) {
        gradioContainer.insertBefore(container, gradioContainer.firstChild);
    }

    return 'Animation created';
}
"""

css = """
.gradio-container {
   max-width: 1000px !important;
   margin: auto;
}

.chat-message {
   font-size: 16px;
   line-height: 1.6;
}

.message.assistant {
   background: linear-gradient(135deg, #fdf2f8, #f8e8f5);
}
"""

# Create the Gradio interface
interface = gr.ChatInterface(
    chatbot_response_wrapper,  # Use our wrapper function
    description="""
    <div style='text-align: left; padding: 20px; background: linear-gradient(135deg, #f8f5f8, #f0e8f0); border-radius: 10px; margin-bottom: 20px;'>
        <h3 style='color: #8B4A8B; margin-bottom: 15px;'>🌸 Menopause Support & Education Platform</h3>
        <p style='font-size: 16px; color: #5d4e5d; line-height: 1.6;'>
            Evidence-based menopause education for women 35+, whether you're just starting to notice changes or are well into your transition. 
            Every conversation is confidential, culturally sensitive, and tailored to your unique needs.<br>
            <strong>Disclaimer:</strong> This platform provides educational information only and does not replace professional medical consultation.
        </p>
    </div>
    """,
    chatbot=gr.Chatbot(
        value=[(None, """Hello and welcome! I'm Thalia 🦋 your trusted companion for navigating menopause with confidence and clarity.

**Having specific symptoms?** I can help you assess what you're experiencing using validated tools and guide you on when it might be time to talk with your healthcare provider.

**Need reliable information?** I'll share the latest evidence-based research on everything from hormone therapy to natural approaches, lifestyle strategies, and long-term health considerations—all explained in plain language you can trust.

**Just need someone who gets it?** I'm here to listen without judgment, validate your experiences, and offer practical support for the emotional ups and downs that come with this transition.

You've got this, and I've got you. Let's begin wherever feels right. 💕""")],
        height=600,
        show_copy_button=False,
        show_share_button=False,
        avatar_images=(None, "frontend/assets/thalia_avatar.png")
    ),
    textbox=gr.Textbox(
        placeholder="What's on your mind today?",
        scale=10
    ),
    examples=[
        "I've been having irregular periods and hot flashes",
        "My sleep is terrible and I'm gaining weight", 
        "I'm so moody lately - could this be perimenopause?",
        "What's the difference between perimenopause and menopause?",
        "Is HRT right for me?",
        "What are the best natural options for hot flashes?",
        "I feel like I'm losing myself in this transition",
        "Nobody seems to understand what I'm going through"
    ],
    submit_btn="SHARE",
    stop_btn=None,
    theme="soft",
    css=css,
    js=js
)

if __name__ == "__main__":
    print("🚀 Starting Thalia Menopause Support Platform...")
    
    # Check system status
    if MAIN_ROUTER_AVAILABLE:
        print("✅ Full system available - Intent classification + Symptom assessment + RAG knowledge")
    elif RAG_AVAILABLE:
        print("⚠️ RAG fallback mode - Knowledge queries only")
    else:
        print("❌ Limited functionality - Please check your system setup")
    
    # Launch the interface
    interface.launch(
        share=False, 
        server_name="0.0.0.0",
        show_error=True  # Show errors in interface for debugging
    )