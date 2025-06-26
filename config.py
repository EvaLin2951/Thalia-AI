"""
Configuration file - Stores application configuration and constants
"""
import os

# Get our logo
LOGO_PATH = "assets/thalia_final.png"

# Application configuration
APP_CONFIG = {
    "title": "Thalia - Menopause Support Platform",
    "theme": "soft",
    "server_name": "0.0.0.0", 
    "server_port": 7860,
    "max_width": "1200px",
    "share": False,
    "show_error": True
}

# File paths
USER_DATA_FILE = "thalia_users.json"
AVATAR_PATH = "assets/thalia_avatar.png"

# UI text and messages
WELCOME_MESSAGE = """Hello and welcome! I'm Thalia 🦋 your trusted companion for navigating menopause with confidence and clarity.

**Having specific symptoms?** I can help you assess what you're experiencing using validated tools and guide you on when it might be time to talk with your healthcare provider.

**Need reliable information?** I'll share the latest evidence-based research on everything from hormone therapy to natural approaches, lifestyle strategies, and long-term health considerations—all explained in plain language you can trust.

**Just need someone who gets it?** I'm here to listen without judgment, validate your experiences, and offer practical support for the emotional ups and downs that come with this transition.

You've got this, and I've got you. Let's begin wherever feels right. 💕"""

PLATFORM_DESCRIPTION = {
    "title": "🌸 Menopause Support & Education Platform",
    "content": """Evidence-based menopause education for women 35+, whether you're just starting to notice changes or are well into your transition. 
Every conversation is confidential, culturally sensitive, and tailored to your unique needs.<br>
<strong>Disclaimer:</strong> This platform provides educational information only and does not replace professional medical consultation."""
}

# Privacy and Terms Configuration
PRIVACY_DISCLAIMER = {
    "content": """
    <div style='color: #333; font-size: 16px; margin: 20px 0; padding: 25px; background: linear-gradient(135deg, #e4a9df, #8cc8f0); border-radius: 10px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);'>
        <p style='font-weight: bold; margin-bottom: 15px;'><strong>🦋 Please Read Before Starting</strong></p>
        
        <div style='line-height: 1.6;'>
            <p><strong>About Thalia</strong></p>
            <p>Thalia is an AI-powered chatbot designed to provide evidence-based menopause education, explain symptoms, and offer emotional support. We are committed to offering an empowering and inclusive space where you can access up-to-date health information throughout your menopause journey.</p>
            
            <p><strong>How We Use Your Data</strong></p>
            <p>Thalia uses advanced language models to process the symptoms and health-related information you provide. All personal data is securely handled and stored on trusted cloud services. Your information is confidential, used only to deliver personalized support, and never shared with third parties.</p>
            
            <p><strong>About Medical Information</strong></p>
            <p>Thalia provides research-based information and assessment tools like the MRS (Menopause Rating Scale) for educational purposes. It does not replace professional medical advice, diagnosis, or treatment. Always consult your healthcare provider regarding medical concerns or questions.</p>
            
            <div style='margin: 15px 0; padding: 15px; background: #f6f3f8; border-radius: 8px;'>
                <p style='font-weight: 500; margin: 0;'><strong>Safe Use Guidelines</strong></p>
                <p style='margin: 10px 0 0 0;'>To protect your privacy, please avoid sharing personally identifiable details such as full names, medical record numbers, social security numbers, or specific addresses. Provide information clearly and descriptively to ensure meaningful and secure support.</p>
            </div>
        </div>
    </div>
    """,
    "checkbox_text": "I have read and understand the above statement, and agree to have my information processed by advanced language models to receive personalized menopause support services",
    "button_text": "Start My Journey with Thalia",
    "decline_text": "No, Thank You"
}

# Example questions
EXAMPLE_QUESTIONS = [
    "I've been having irregular periods and hot flashes",
    "My sleep is terrible and I'm gaining weight", 
    "I'm so moody lately - could this be perimenopause?",
    "What's the difference between perimenopause and menopause?",
    "Is HRT right for me?",
    "What are the best natural options for hot flashes?",
    "I feel like I'm losing myself in this transition",
    "Nobody seems to understand what I'm going through"
]

# Age range options
AGE_RANGES = ["25-34", "35-44", "45-54", "55-64", "65+"]

# Error messages
ERROR_MESSAGES = {
    "auth_unavailable": "❌ Authentication system unavailable",
    "user_manager_uninitialized": "❌ UserManager not initialized",
    "invalid_session": "❌ Invalid session, user not logged in",
    "system_unavailable": ("I apologize, but my systems are currently unavailable. "
                          "Please try again later or consult with a healthcare professional "
                          "for immediate menopause-related concerns."),
    "processing_error": ("I encountered an error processing your request. "
                        "Please try rephrasing your question or try again.")
}

# Success messages
SUCCESS_MESSAGES = {
    "registration_success": "✅ {message}\n\nPlease go to the login tab to sign in with your new account.",
    "login_success": "✅ {message}",
    "logout_success": "✅ Logout: {message}"
}