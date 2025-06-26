"""
Configurable authentication Thalia application
"""
import gradio as gr
import sys
import os

# Add detailed startup logs
print("🚀 Starting Thalia Menopause Support Platform...")
print(f"📂 Working directory: {os.getcwd()}")

# Ensure path setup is correct
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'api'))

# Import custom modules
from config import APP_CONFIG, USER_DATA_FILE
from auth_handlers import AuthHandler
from response_handler import ThaliaResponseHandler
from ui_components import UIComponents

# =============================================================================
# Configuration Options - You can control features here
# =============================================================================
FORCE_AUTH_MODE = True          # Set to True to force login interface display
FORCE_NO_AUTH_MODE = False      # Set to True to force skip login interface
ENABLE_GUEST_MODE = False        # Allow guest mode (use without login)
# =============================================================================

class ThaliaApp:
    """Thalia application main class"""
    
    def __init__(self):
        self.auth_available = False
        self.main_router_available = False
        self.rag_available = False
        self.user_manager = None
        self.process_user_input = None
        self.rag_response = None
        self.show_auth_interface = False  # Control whether to show auth interface
        self.show_privacy_disclaimer = True  # Control whether to show privacy disclaimer
        self.privacy_consent_given = False   # Track user's privacy consent
        
        self._determine_auth_mode()
        self._initialize_systems()
        self._create_handlers()
        
    def _determine_auth_mode(self):
        """Determine authentication mode"""
        if FORCE_NO_AUTH_MODE:
            print("🔧 Force no-auth mode")
            self.show_auth_interface = False
            return
            
        if FORCE_AUTH_MODE:
            print("🔧 Force auth mode")
            self.show_auth_interface = True
            return
            
        # Default behavior: show auth interface if auth module is available
        self.show_auth_interface = True
        
    def _initialize_systems(self):
        """Initialize various system modules"""
        # Import authentication module
        if self.show_auth_interface:
            print("🔧 Importing authentication module...")
            try:
                from user_auth_with_conversations import UserManager
                self.auth_available = True
                print("✅ user_auth_with_conversations imported successfully")
                
                print("🔧 Initializing UserManager...")
                self.user_manager = UserManager(USER_DATA_FILE)
                print("✅ UserManager initialized successfully")
                print(f"📊 UserManager instance: {self.user_manager}")
                
            except ImportError as e:
                print(f"❌ Authentication module import failed: {e}")
                if ENABLE_GUEST_MODE:
                    print("⚠️ Switching to guest mode")
                    self.show_auth_interface = True  # Still show interface, but provide guest option
                    self.auth_available = False
                else:
                    print("❌ Guest mode disabled, application cannot start")
                    raise Exception("Authentication module unavailable and guest mode disabled")
            except Exception as e:
                print(f"❌ UserManager initialization failed: {e}")
                if ENABLE_GUEST_MODE:
                    print("⚠️ Switching to guest mode")
                    self.show_auth_interface = True  # Still show interface, but provide guest option
                    self.auth_available = False
                else:
                    raise Exception("UserManager initialization failed and guest mode disabled")
        else:
            print("🔧 Skipping authentication module loading (guest mode)")

        # Import main router
        print("🔧 Importing main router...")
        try:
            from main_flow_router import process_user_input
            self.process_user_input = process_user_input
            self.main_router_available = True
            print("✅ Main router loaded successfully")
        except ImportError as e:
            print(f"⚠️ Main router unavailable: {e}")
            self.main_router_available = False
            
            # Try RAG fallback option
            print("🔧 Attempting to import RAG system...")
            try:
                from backend.RAG.rag_pipeline import get_chatbot_response as rag_response
                self.rag_response = rag_response
                self.rag_available = True
                print("✅ RAG system available as fallback")
            except ImportError as e1:
                print(f"⚠️ RAG pipeline unavailable: {e1}")
                # Try other possible RAG modules
                try:
                    from backend.RAG.rag_local import get_chatbot_response as rag_response
                    self.rag_response = rag_response
                    self.rag_available = True
                    print("✅ Local RAG system available as fallback")
                except ImportError as e2:
                    print(f"⚠️ Local RAG system also unavailable: {e2}")
                    self.rag_available = False

    def _create_handlers(self):
        """Create handler instances"""
        print("🔧 Creating handlers...")
        
        # Create authentication handler
        self.auth_handler = AuthHandler(self.user_manager if self.auth_available else None)
        
        # Create response handler
        self.response_handler = ThaliaResponseHandler(
            user_manager=self.user_manager if self.auth_available else None,
            main_router_available=self.main_router_available,
            rag_available=self.rag_available,
            process_user_input=self.process_user_input,
            rag_response=self.rag_response
        )
        
        # Create UI component manager
        self.ui_components = UIComponents()
        
        print("✅ Handlers created successfully")

    def create_interface(self):
        """Create Gradio interface"""
        print("🔧 Creating Gradio interface...")
        
        with gr.Blocks(
            theme=APP_CONFIG["theme"], 
            css=self.ui_components.css, 
            js=self.ui_components.js, 
            title=APP_CONFIG["title"]
        ) as demo:
            # Initialize session state
            session_id = gr.State(value=None)
            privacy_consent_state = gr.State(value=False)
            
            # Trigger JS animation on load
            demo.load(None, js="() => { titleAnimation(); }")

            # Create privacy disclaimer interface (shown first)
            privacy_components = self.ui_components.create_privacy_disclaimer_interface()
            
            # Create authentication interface (initially hidden)
            auth_components = None
            if self.show_auth_interface:
                print("🔧 Creating authentication interface")
                auth_components = self.ui_components.create_auth_interface()
                
                # If guest mode is enabled, add guest login option
                if ENABLE_GUEST_MODE:
                    with auth_components["auth_interface"]:
                        gr.HTML("<hr>")
                        with gr.Row():
                            guest_btn = gr.Button("🔓 Continue as Guest (No Login Required)", 
                                                variant="secondary", size="lg")
                        auth_components["guest_btn"] = guest_btn
            else:
                print("🔧 Skipping authentication interface creation")

            # Create main chat interface (initially hidden)
            main_components = self.ui_components.create_main_interface(self.show_auth_interface)
            
            # If guest mode and no auth interface, show guest status
            if not self.show_auth_interface and main_components["user_status"] is None:
                with main_components["main_interface"]:
                    guest_status = gr.HTML("""
                        <div style='background: linear-gradient(135deg, #e8f4f8, #f0f8ff); 
                                    border-radius: 10px; padding: 15px; margin-bottom: 20px;
                                    border-left: 4px solid #4a90a4; font-weight: 500;'>
                            🔓 Guest Mode - Your conversations are not saved
                        </div>
                    """)
                    main_components["guest_status"] = guest_status

            # Bind privacy events
            self._bind_privacy_events(privacy_components, auth_components, main_components, privacy_consent_state)
            
            # Bind event handlers
            self._bind_events(auth_components, main_components, session_id)

        return demo

    def _bind_privacy_events(self, privacy_components, auth_components, main_components, privacy_consent_state):
        """Bind privacy-related events"""
        
        print("🔧 Binding privacy events...")
        
        # Enable/disable agree button based on checkbox
        def update_agree_button(consent_checked):
            print(f"🔄 Checkbox changed: {consent_checked}")
            return gr.update(interactive=consent_checked)
        
        privacy_components["privacy_consent"].change(
            fn=update_agree_button,
            inputs=[privacy_components["privacy_consent"]],
            outputs=[privacy_components["agree_btn"]]
        )
        
        # Handle privacy agreement
        def handle_privacy_agree(consent_checked):
            print(f"🔘 Privacy agree clicked with consent: {consent_checked}")
            
            if consent_checked:
                if self.show_auth_interface and auth_components:
                    # Show auth interface
                    print("📄 → 🔐 Transitioning from privacy to auth interface")
                    return (
                        gr.update(visible=False),  # Hide privacy interface
                        gr.update(visible=True) if auth_components else gr.update(),   # Show auth interface
                        gr.update(visible=False),  # Keep main interface hidden
                        """<div style='background: #d4edda; color: #155724; padding: 10px; border-radius: 5px; text-align: center;'>
                           ✅ Thank you for your consent! You can now register an account or log in to use Thalia.
                           </div>""",
                        True  # Update consent state
                    )
                else:
                    # Directly show main interface (guest mode)
                    print("📄 → 💬 Transitioning from privacy to main interface")
                    return (
                        gr.update(visible=False),  # Hide privacy interface
                        gr.update() if not auth_components else gr.update(visible=False),  # Handle auth interface
                        gr.update(visible=True),   # Show main interface
                        """<div style='background: #d4edda; color: #155724; padding: 10px; border-radius: 5px; text-align: center;'>
                           ✅ Thank you for your consent! Welcome to Thalia!
                           </div>""",
                        True  # Update consent state
                    )
            else:
                print("⚠️ Privacy agree clicked but consent not checked")
                return (
                    gr.update(visible=True),   # Keep privacy interface visible
                    gr.update() if not auth_components else gr.update(visible=False),  # Hide auth interface
                    gr.update(visible=False),  # Hide main interface
                    """<div style='background: #f8d7da; color: #721c24; padding: 10px; border-radius: 5px; text-align: center;'>
                       ⚠️ Please check the consent checkbox first.
                       </div>""",
                    False  # Update consent state
                )
        
        # Fix output component matching
        outputs_list = [
            privacy_components["privacy_interface"],
            privacy_components["privacy_status"],
            privacy_consent_state
        ]
        
        # Only add related outputs when auth_components exists
        if auth_components:
            outputs_list.insert(1, auth_components["auth_interface"])  # Insert before privacy_status
            outputs_list.insert(2, main_components["main_interface"])  # Insert before privacy_status
        else:
            outputs_list.insert(1, main_components["main_interface"])  # Only add main_interface
        
        privacy_components["agree_btn"].click(
            fn=handle_privacy_agree,
            inputs=[privacy_components["privacy_consent"]],
            outputs=outputs_list
        )
        
        # Handle privacy decline
        def handle_privacy_decline():
            print("❌ Privacy declined")
            return """<div style='background: #f8d7da; color: #721c24; padding: 10px; border-radius: 5px; text-align: center;'>
                      We understand your choice. If you change your mind, you can always revisit the Thalia platform.<br>
                      If you have any questions, please contact our customer service team.
                      </div>"""
        
        privacy_components["decline_btn"].click(
            fn=handle_privacy_decline,
            outputs=[privacy_components["privacy_status"]]
        )
        
        print("✅ Privacy events bound successfully")

    def _bind_events(self, auth_components, main_components, session_id):
        """Bind event handlers"""
        print("🔧 Binding event handlers...")
        
        if self.show_auth_interface and auth_components:
            # Login event
            if self.auth_available:
                auth_components["login_btn"].click(
                    fn=self.auth_handler.handle_login,
                    inputs=[auth_components["login_username"], auth_components["login_password"]],
                    outputs=[
                        auth_components["auth_interface"], 
                        main_components["main_interface"], 
                        auth_components["auth_result"], 
                        session_id, 
                        main_components["user_status"], 
                        main_components["chatbot"]
                    ]
                )
                auth_components["login_username"].change(
                    fn=self.auth_handler.clear_auth_errors,
                    outputs=[auth_components["auth_result"]]
                )
                auth_components["login_password"].change(
                    fn=self.auth_handler.clear_auth_errors,
                    outputs=[auth_components["auth_result"]]
                )
                
                # Registration event
                auth_components["register_btn"].click(
                    fn=self.auth_handler.handle_register,
                    inputs=[
                        auth_components["reg_username"], 
                        auth_components["reg_email"], 
                        auth_components["reg_password"], 
                        auth_components["reg_confirm"], 
                        auth_components["reg_age_range"]
                    ],
                    outputs=[auth_components["auth_result"]]
                )
                
                # Logout event
                if main_components["logout_btn"]:
                    main_components["logout_btn"].click(
                        fn=self.auth_handler.handle_logout,
                        inputs=[session_id],
                        outputs=[
                            auth_components["auth_interface"], 
                            main_components["main_interface"], 
                            auth_components["auth_result"], 
                            session_id, 
                            main_components["user_status"], 
                            main_components["chatbot"]
                        ]
                    )
            
            # Guest mode button
            if ENABLE_GUEST_MODE and "guest_btn" in auth_components:
                def handle_guest_mode():
                    return (
                        gr.update(visible=False),  # Hide auth interface
                        gr.update(visible=True),   # Show main interface
                        "",                        # Clear auth result
                        "guest_session",           # Set guest session ID
                        """<div style='background: linear-gradient(135deg, #e8f4f8, #f0f8ff); 
                                      border-radius: 10px; padding: 15px;
                                      border-left: 4px solid #4a90a4; font-weight: 500;'>
                               🔓 Guest Mode - Your conversations are not saved
                           </div>""",           # Guest status
                        gr.update()                # Keep chat history
                    )
                
                auth_components["guest_btn"].click(
                    fn=handle_guest_mode,
                    outputs=[
                        auth_components["auth_interface"],
                        main_components["main_interface"],
                        auth_components["auth_result"],
                        session_id,
                        main_components["user_status"],
                        main_components["chatbot"]
                    ]
                )
            
            # Chat events with session
            main_components["msg"].submit(
                fn=self.response_handler.custom_chat_function,
                inputs=[main_components["msg"], main_components["chatbot"], session_id],
                outputs=[main_components["msg"], main_components["chatbot"]]
            )
            main_components["submit_btn"].click(
                fn=self.response_handler.custom_chat_function,
                inputs=[main_components["msg"], main_components["chatbot"], session_id],
                outputs=[main_components["msg"], main_components["chatbot"]]
            )
        else:
            # Original chat events without session (guest mode)
            main_components["msg"].submit(
                fn=lambda msg, hist: self.response_handler.custom_chat_function(msg, hist, "guest_session"),
                inputs=[main_components["msg"], main_components["chatbot"]],
                outputs=[main_components["msg"], main_components["chatbot"]]
            )
            main_components["submit_btn"].click(
                fn=lambda msg, hist: self.response_handler.custom_chat_function(msg, hist, "guest_session"),
                inputs=[main_components["msg"], main_components["chatbot"]],
                outputs=[main_components["msg"], main_components["chatbot"]]
            )

        print("✅ Event handlers bound successfully")

    def print_system_status(self):
        """Print system status information"""
        print("\n🚀 Starting Thalia Menopause Support Platform...")
        
        # Show configuration status
        print(f"\n📋 Configuration status:")
        print(f"   🔐 FORCE_AUTH_MODE: {FORCE_AUTH_MODE}")
        print(f"   🚫 FORCE_NO_AUTH_MODE: {FORCE_NO_AUTH_MODE}")
        print(f"   👤 ENABLE_GUEST_MODE: {ENABLE_GUEST_MODE}")
        print(f"   🖥️ show_auth_interface: {self.show_auth_interface}")
        print(f"   🔒 show_privacy_disclaimer: {self.show_privacy_disclaimer}")
        
        # Check system status
        if self.auth_available:
            print("✅ User authentication system loaded")
            if self.user_manager:
                try:
                    stats = self.user_manager.get_user_stats()
                    print(f"📊 Platform statistics: {stats['total_users']} total users, {stats['active_sessions']} active sessions")
                    print("💡 Tip: Use 'python view_users.py' for user management")
                except Exception as e:
                    print(f"⚠️ Cannot get user statistics: {e}")
            else:
                print("⚠️ UserManager not properly initialized")
        else:
            if self.show_auth_interface:
                print("⚠️ Auth interface enabled but auth system unavailable")
            else:
                print("ℹ️ Running in guest mode")
        
        if self.main_router_available:
            print("✅ Complete system available - Intent classification + Symptom assessment + RAG knowledge base")
        elif self.rag_available:
            print("⚠️ RAG fallback mode - Knowledge queries only")
        else:
            print("⚠️ Basic mode - Provides basic chat functionality")
        
        print(f"\n📊 Final status:")
        print(f"   🔒 PRIVACY_DISCLAIMER: {self.show_privacy_disclaimer}")
        print(f"   🔐 AUTH_AVAILABLE: {self.auth_available}")
        print(f"   👤 user_manager: {self.user_manager is not None}")
        print(f"   🤖 MAIN_ROUTER_AVAILABLE: {self.main_router_available}")
        print(f"   📚 RAG_AVAILABLE: {self.rag_available}")

    def launch(self):
        """Launch application"""
        # Print system status
        self.print_system_status()
        
        # Create interface
        demo = self.create_interface()
        
        # Launch interface
        demo.launch(
            share=APP_CONFIG["share"], 
            server_name=APP_CONFIG["server_name"],
            server_port=APP_CONFIG["server_port"],
            show_error=APP_CONFIG["show_error"]
        )


def main():
    """Main function"""
    try:
        app = ThaliaApp()
        app.launch()
    except Exception as e:
        print(f"❌ Application startup failed: {e}")
        import traceback
        traceback.print_exc()
        print("\n💡 Please check:")
        print("   - Whether all required dependencies are installed")
        print("   - Whether running in correct directory")
        print("   - Whether related module files exist")
        print("   - Check configuration options at top of file")


if __name__ == "__main__":
    main()