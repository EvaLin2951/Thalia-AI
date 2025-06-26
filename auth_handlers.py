"""
Authentication Handler - Handles user registration, login, logout functionality
"""
import gradio as gr
import traceback
from config import ERROR_MESSAGES, SUCCESS_MESSAGES, WELCOME_MESSAGE  

class AuthHandler:
    """Handles user authentication related operations"""
    
    def __init__(self, user_manager=None):
        self.user_manager = user_manager
        self.auth_available = user_manager is not None
        print(f"🔧 AuthHandler initialization completed, user_manager: {self.auth_available}")
    
    def handle_privacy_consent(self, consent_given):
        """Handle privacy consent"""
        if consent_given:
            return (
                gr.update(visible=False),  # Hide privacy interface
                gr.update(visible=True),   # Show auth interface
                """<div style='background: #d4edda; color: #155724; padding: 10px; border-radius: 5px; text-align: center;'>
                   ✅ Thank you for your consent! You can now register an account or log in to use Thalia.
                   </div>"""
            )
        else:
            return (
                gr.update(visible=True),   # Keep privacy interface visible
                gr.update(visible=False),  # Hide auth interface
                """<div style='background: #f8d7da; color: #721c24; padding: 10px; border-radius: 5px; text-align: center;'>
                   ⚠️ You must agree to the privacy statement to use the Thalia platform.
                   </div>"""
            )

    def handle_privacy_decline(self):
        """Handle privacy decline"""
        return """<div style='background: #f8d7da; color: #721c24; padding: 10px; border-radius: 5px; text-align: center;'>
                  We understand your choice. If you change your mind, you can always revisit the Thalia platform.<br>
                  If you have any questions, please contact our customer service team.
                  </div>"""

    def handle_register(self, username: str, email: str, password: str, confirm_password: str, age_range: str):
        """Handle user registration"""
        print(f"🔧 handle_register called: username='{username}', email='{email}', age='{age_range}'")
        
        if not self.auth_available:
            result = ERROR_MESSAGES["auth_unavailable"]
            print(f"Returning: {result}")
            return result
        
        if not self.user_manager:
            result = ERROR_MESSAGES["user_manager_uninitialized"]
            print(f"Returning: {result}")
            return result
        
        try:
            print("🔧 Calling user_manager.register_user...")
            success, message = self.user_manager.register_user(username, email, password, confirm_password, age_range)
            print(f"🔧 Registration result: success={success}, message='{message}'")
            
            if success:
                result = SUCCESS_MESSAGES["registration_success"].format(message=message)
            else:
                result = f"❌ {message}"
            
            print(f"Returning: {result}")
            return result
            
        except Exception as e:
            error_msg = f"❌ Registration error: {str(e)}"
            print(f"Returning: {error_msg}")
            traceback.print_exc()
            return error_msg

    def handle_login(self, username: str, password: str):
        """Handle user login - 匹配现有输出顺序"""
        print(f"🔑 handle_login called: username='{username}'")
        
        # 基础验证
        if not username or username.strip() == "":
            error_msg = "Please enter a valid username"
            return self._create_error_response(error_msg)
        
        if not password or password.strip() == "":
            error_msg = "Please enter a valid password"
            return self._create_error_response(error_msg)
        
        if not self.auth_available:
            error_msg = ERROR_MESSAGES["auth_unavailable"]
            return self._create_error_response(error_msg)
        
        if not self.user_manager:
            error_msg = ERROR_MESSAGES["user_manager_uninitialized"]
            return self._create_error_response(error_msg)
        
        try:
            print("🔧 Calling user_manager.login_user...")
            success, message, session_id = self.user_manager.login_user(username, password)
            print(f"🔧 Login result: success={success}, message='{message}', session_id='{session_id}'")
            
            if success:
                user_info = self.user_manager.get_user_info(session_id)
                preferred_name = user_info.get('profile', {}).get('preferred_name', username)
                age_range = user_info.get('age_range', 'Not specified')
                total_convs = user_info.get('total_conversations', 0)
                
                print(f"✅ User {username} logged in successfully")
                
                # Personalized welcome chat
                initial_chat = [{
                    "role": "assistant", 
                    "content": WELCOME_MESSAGE
                }]
                
                user_status = f"👋 Welcome back, {preferred_name}! | Age: {age_range} | Conversations: {total_convs}"
                
                # 登录成功 - 按照你的输出顺序返回
                return (
                    gr.update(visible=False),           # auth_interface - 隐藏登录界面
                    gr.update(visible=True),            # main_interface - 显示主界面
                    gr.update(value="", visible=False), # auth_result - 隐藏状态框 ⭐
                    session_id,                         # session_id
                    user_status,                        # user_status
                    gr.update(value=initial_chat)       # chatbot
                )
            else:
                error_msg = f"❌ {message}"
                return self._create_error_response(error_msg)
                
        except Exception as e:
            error_msg = f"❌ Login error：{str(e)}"
            print(f"Returning error: {error_msg}")
            traceback.print_exc()
            return self._create_error_response(error_msg)

    def _create_error_response(self, error_message: str):
        """创建错误响应 - 返回HTML格式"""
        # 简单的红框HTML
        error_html = f"""
        <div style='background: #f8d7da; color: #721c24; padding: 10px; border-radius: 5px; text-align: center;'>
            🚨 {error_message}
        </div>
        """
        
        return (
            gr.update(visible=True),                    # auth_interface
            gr.update(visible=False),                   # main_interface
            gr.update(value=error_html, visible=True),  # auth_result - 显示HTML
            None,                                       # session_id
            "",                                         # user_status
            gr.update(value=[])                         # chatbot
        )

    def clear_auth_errors(self):
        """清除错误"""
        return gr.update(value="", visible=False)

    def handle_logout(self, session_id: str):
        """Handle user logout"""
        print(f"🚪 handle_logout called: session_id={session_id[:8] if session_id else 'None'}")
        
        if not self.auth_available or not self.user_manager:
            return self._create_logout_response()
        
        try:
            success, message = self.user_manager.logout_user(session_id)
            print(f"✅ Logout: {message}")
            return self._create_logout_response()
            
        except Exception as e:
            print(f"❌ Logout error: {e}")
            return self._create_logout_response()

    def _create_login_response(self, success: bool, message: str):
        """Create login response"""
        if success:
            return (
                gr.update(visible=False),  # Hide login interface
                gr.update(visible=True),   # Show main interface
                message,
                None,  # session_id will be set in successful login
                "",    # user_status will be set in successful login
                gr.update(value=[])
            )
        else:
            return (
                gr.update(visible=True),   # Keep login interface visible
                gr.update(visible=False),  # Hide main interface
                message,
                None,
                "",
                gr.update(value=[])
            )

    def _create_logout_response(self):
        """Create logout response"""
        return (
            gr.update(visible=True),   # Show login interface
            gr.update(visible=False),  # Hide main interface
            "",
            None,
            "",
            gr.update(value=[])
        )