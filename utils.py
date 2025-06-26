"""
Utility functions module - Stores common helper functions
"""
import os
import sys
from datetime import datetime


def setup_paths():
    """Set up system paths"""
    current_dir = os.path.dirname(__file__)
    sys.path.append(current_dir)
    sys.path.append(os.path.join(current_dir, 'backend', 'api'))
    print(f"📂 Working directory: {os.getcwd()}")


def log_message(level: str, message: str, emoji: str = ""):
    """Unified logging function"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {emoji} {level}: {message}")


def format_user_welcome(user_info: dict, username: str) -> dict:
    """Format user welcome message"""
    preferred_name = user_info.get('profile', {}).get('preferred_name', username)
    age_range = user_info.get('age_range', 'Not specified')
    total_convs = user_info.get('total_conversations', 0)
    
    welcome_content = f"""Hello {preferred_name}! Welcome back to Thalia 🦋

I'm so glad you're here. As your trusted companion for navigating menopause, I'm ready to continue supporting you on this journey.

**Your Profile:**
- Preferred name: {preferred_name}
- Age range: {age_range}
- Previous conversations: {total_convs}

**What would you like to explore today?**
- Check in about any new symptoms or changes
- Continue our previous discussions  
- Learn about new treatment options
- Take a symptom assessment
- Just chat about how you're feeling

Your privacy and comfort are my top priorities. Let's continue wherever feels right for you. 💕"""

    user_status = f"👋 Welcome back, {preferred_name}! | Age: {age_range} | Conversations: {total_convs}"
    
    return {
        "welcome_content": welcome_content,
        "user_status": user_status
    }


def truncate_session_id(session_id: str, length: int = 8) -> str:
    """Truncate session ID for log display"""
    if not session_id:
        return 'None'
    return session_id[:length]


def validate_message_input(message: str) -> bool:
    """Validate user input message"""
    return bool(message and message.strip())


def safe_get_nested_value(data: dict, keys: list, default=None):
    """Safely get nested dictionary value"""
    try:
        value = data
        for key in keys:
            value = value[key]
        return value
    except (KeyError, TypeError):
        return default


def create_error_response(error_type: str, details: str = "") -> str:
    """Create standardized error response"""
    error_messages = {
        "auth_error": "Authentication system is currently unavailable.",
        "session_error": "Your session has expired. Please log in again.",
        "processing_error": "I encountered an error processing your request. Please try again.",
        "system_error": "System temporarily unavailable. Please try again later."
    }
    
    base_message = error_messages.get(error_type, "An unexpected error occurred.")
    if details:
        return f"{base_message} Details: {details}"
    return base_message


def format_system_stats(stats: dict) -> str:
    """Format system statistics"""
    return (f"📊 Platform stats: {stats.get('total_users', 0)} total users, "
            f"{stats.get('active_sessions', 0)} active sessions")


class SystemStatus:
    """System status management class"""
    
    def __init__(self):
        self.auth_available = False
        self.main_router_available = False
        self.rag_available = False
        self.user_manager_available = False
    
    def update_status(self, **kwargs):
        """Update system status"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def get_status_summary(self) -> dict:
        """Get status summary"""
        return {
            "auth_available": self.auth_available,
            "main_router_available": self.main_router_available,
            "rag_available": self.rag_available,
            "user_manager_available": self.user_manager_available
        }
    
    def print_status(self):
        """Print detailed status"""
        print(f"\n📊 System Status:")
        print(f"   🔐 Authentication: {'✅' if self.auth_available else '❌'}")
        print(f"   👤 User Management: {'✅' if self.user_manager_available else '❌'}")
        print(f"   🤖 Main Router: {'✅' if self.main_router_available else '❌'}")
        print(f"   📚 RAG System: {'✅' if self.rag_available else '❌'}")
        
        if self.main_router_available:
            print("✅ Full system available - Intent classification + Symptom assessment + RAG knowledge base")
        elif self.rag_available:
            print("⚠️ RAG fallback mode - Knowledge query only")
        else:
            print("❌ Limited functionality - Please check system settings")