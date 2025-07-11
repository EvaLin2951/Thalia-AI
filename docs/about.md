---
layout: page
title: "About"
permalink: /about/
---

# Thalia AI – AI-Powered Menopause Support Chatbot

> Python-powered platform providing symptom assessment using MRS scale, knowledge query with medical research, and emotional support for menopause care. Built with LangChain, Gradio, OpenAI/Gemini APIs.


[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Gradio](https://img.shields.io/badge/Gradio-UI-orange.svg)](https://gradio.app)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Project Structure](#-project-structure)
- [License](#-license)

## 🌟 Overview

Thalia AI was initiated during the 2025 AI4Good Lab at Mila - Quebec Artificial Intelligence Institute, based on an idea co-pitched by Eva (Yifan) Lin and Paria Jafarian, and developed in collaboration with KK (Jieqi) Luo, Ameline Ramesan, Sabia Irfan, and Qi Zeng.

The project explores how conversational AI can support individuals experiencing menopause — guiding users through symptom reflection and assessment, providing trusted answers grounded in medical research, and offering empathetic emotional support tailored to their experiences.

We’re continuing to grow Thalia beyond the lab, with ongoing efforts to expand its capabilities, enhance the user experience, and build a more inclusive, accessible support tool.

### Key Capabilities

- **Symptom Assessment**: Validated MRS (Menopause Rating Scale) implementation
- **Knowledge Base**: RAG-powered medical information retrieval
- **Emotional Support**: AI-driven conversational therapy
- **User Management**: Secure authentication and conversation history
- **Multi-Modal Interface**: Web-based chat interface with privacy controls

## ✨ Features

### 🔍 Intelligent Symptom Assessment
- **MRS Scale Integration**: Clinical-grade menopause rating scale
- **Personalized Scoring**: Automated assessment with detailed feedback
- **Progress Tracking**: Historical symptom monitoring
- **Medical Recommendations**: Evidence-based guidance

### 💡 Knowledge Query System
- **RAG Pipeline**: Retrieval-Augmented Generation for medical accuracy
- **Research-Backed**: Current menopause research and guidelines
- **Natural Language**: Easy-to-understand explanations
- **Citation Support**: Transparent source referencing

### 💝 Emotional Support
- **Empathetic AI**: Conversational emotional support
- **Crisis Detection**: Identification of distress signals
- **Coping Strategies**: Practical mental health tools
- **Community Connection**: Resource sharing and support

### 🔐 Privacy & Security
- **GDPR Compliant**: Privacy-first data handling
- **Secure Authentication**: Encrypted user sessions
- **Consent Management**: Granular privacy controls
- **Data Minimization**: Only necessary data collection

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Gradio UI     │    │   Main Router    │    │   MRS Engine    │
│   Web Interface │◄──►│ Intent Detection │◄──►│ Symptom Assess  │
└─────────────────┘    └─────────┬────────┘    └─────────────────┘
                                 │
                       ┌─────────▼────────┐    ┌─────────────────┐
                       │   RAG System     │    │ Authentication  │
                       │ Knowledge Base   │    │ User Management │
                       └──────────────────┘    └─────────────────┘
```

### Core Components

- **UI Layer**: Gradio-based responsive web interface
- **Flow Router**: Intent classification and conversation management
- **RAG System**: LangChain-powered knowledge retrieval
- **Auth System**: Secure user management with conversation persistence
- **Assessment Engine**: MRS scale implementation and scoring

## 🚀 Installation

### Prerequisites

- Python 3.8+
- pip package manager
- Google API key (for Gemini) or OpenAI API key

### Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/thalia-menopause-platform.git
cd thalia-menopause-platform
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. **Run the application**
```bash
python app.py
```

5. **Access the interface**
   - Open your browser to `http://localhost:7860`
   - Complete privacy consent and registration
   - Start your menopause support journey!

### Environment Variables

Create a `.env` file with the following:

```env
# Required API Keys
GOOGLE_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Optional Configuration
THALIA_PORT=7860
THALIA_HOST=0.0.0.0
DEBUG_MODE=false
```

## ⚙️ Configuration

### Application Modes

The platform supports multiple deployment modes:

```python
# In app.py - Configuration Options
FORCE_AUTH_MODE = True          # Require user authentication
FORCE_NO_AUTH_MODE = False      # Skip authentication (guest mode)
ENABLE_GUEST_MODE = False       # Allow guest access
```

### Feature Toggles

- **Privacy Disclaimer**: Configurable consent management
- **Authentication**: Optional user registration/login
- **RAG System**: Knowledge base with fallback options
- **Symptom Assessment**: MRS scale integration

## 📖 Usage

### For End Users

1. **Privacy Consent**: Review and accept privacy terms
2. **Registration**: Create account or use guest mode
3. **Assessment**: Complete symptom evaluation using MRS scale
4. **Knowledge Queries**: Ask questions about menopause
5. **Emotional Support**: Access conversational therapy
6. **Progress Tracking**: Monitor symptoms over time

### For Developers

```python
# Process user input through main router
from main_flow_router import process_user_input

result = process_user_input("I'm having hot flashes", session_id="user123")
print(result["response"])
```

```python
# Direct RAG knowledge query
from menopause_knowledge_api import process_knowledge_query

result = process_knowledge_query("What is hormone therapy?")
print(result["response"])
```

## 📚 API Documentation

### Main Router API

```python
def process_user_input(user_input: str, session_id: str = "default") -> Dict[str, Any]:
    """
    Process user input through the main conversation flow.
    
    Args:
        user_input: User's message
        session_id: Unique session identifier
        
    Returns:
        Dict containing response, intent, flow status, and metadata
    """
```

### Knowledge API

```python
def process_knowledge_query(user_message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Process knowledge queries using RAG system.
    
    Args:
        user_message: User's query
        context: Optional conversation context
        
    Returns:
        Dict with response, sources, confidence, and session data
    """
```

### Authentication API

```python
class UserManager:
    def register_user(self, username: str, email: str, password: str, 
                     confirm_password: str, age_range: str) -> Tuple[bool, str]
    
    def login_user(self, username: str, password: str) -> Tuple[bool, str, str]
    
    def save_message(self, session_id: str, user_message: str, 
                    bot_response: str) -> bool
```

## 📁 Project Structure

```
Thalia-Chatbot-main/
├── app.py                           # Main application entry point
├── config.py                       # Configuration constants
├── requirements.txt                 # Python dependencies
│
├── backend/                        # Backend services
│   ├── RAG/                       # Knowledge retrieval system
│   │   ├── RAG_Database/          # Document storage
│   │   │   └── guideline-menopause-healthcare-2010-UNFPA.pdf
│   │   ├── rag_pipeline.py        # Main RAG pipeline
│   │   ├── rag_local.py           # Local RAG implementation
│   │   └── rag_sql.py             # SQL-based RAG system
│   │
│   ├── flows/                     # Conversation flows
│   │   ├── symptom_assessment_main.py         # Main symptom assessment
│   │   ├── symptom_assessment_flow.py         # Assessment flow logic
│   │   ├── symptom_assessment_processors.py   # Assessment processors
│   │   └── mrs_symptom_tracker.py             # MRS scale tracker
│   │
│   ├── prompts/                   # AI prompt templates
│   │   ├── mrs_question_generator.yaml        # Question generation
│   │   ├── mrs_response_analyzer.yaml         # Response analysis
│   │   └── mrs_score_calculator.yaml          # Score calculation
│   │
│   └── utils/                     # Backend utilities
│       ├── openai_client.py       # OpenAI API client
│       └── template_loader.py     # Template loading utilities
│
├── core/                          # Core application modules
│   ├── main_flow_router.py        # Main conversation routing
│   ├── menopause_knowledge_api.py # Knowledge API interface
│   ├── response_handler.py        # Response handling logic
│   ├── auth_handlers.py           # Authentication handlers
│   └── ui_components.py           # Gradio UI components
│
├── auth/                          # Authentication system
│   └── user_auth_with_conversations.py  # User management with chat history
│
├── static/                        # Static assets
│   ├── thalia_logo.png           # Main logo
│   ├── thalia_logo copy.png      # Logo backup
│   └── thalia_background.png     # Background image
│
├── utils/                         # Utility functions
│   └── utils.py                  # Common utilities
│
└── archive/                       # Archive and backups
    └── Thalia_final.zip          # Final version archive
```

## 🧪 Testing

Run the test suite:

```bash
# Unit tests
python -m pytest tests/

# Integration tests
python -m pytest tests/integration/

# Test specific modules
python main_flow_router.py
python menopause_knowledge_api.py
```

## 🔧 Development

### Local Development

1. **Clone and setup**
```bash
git clone https://github.com/yourusername/thalia-menopause-platform.git
cd thalia-menopause-platform
pip install -r requirements-dev.txt
```

2. **Run in development mode**
```bash
python app.py
```

3. **Code formatting**
```bash
black .
flake8 .
```

### Adding New Features

1. **Symptom Assessment**: Extend `symptom_assessment_main.py`
2. **Knowledge Base**: Add documents to RAG system
3. **UI Components**: Modify `ui_components.py`
4. **Authentication**: Enhance `user_auth_with_conversations.py`

## 🚀 Deployment

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 7860

CMD ["python", "app.py"]
```

### Cloud Deployment

- **Heroku**: Ready for Heroku deployment
- **AWS**: Compatible with EC2, ECS, Lambda
- **Google Cloud**: Cloud Run deployment supported
- **Azure**: App Service compatible


## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Medical Research**: Based on validated menopause rating scales
- **Open Source Community**: Built with amazing open-source tools
- **Healthcare Providers**: Input from menopause specialists
- **User Community**: Feedback from women experiencing menopause


## 🔮 Roadmap

- [ ] **Symptom radar to spot patterns** - Advanced analytics and trend visualization
- [ ] **Community hub to share stories** - Safe peer support and experience sharing
- [ ] **Multilingual & cultural care for every context** - Global localization and cultural sensitivity
- [ ] **Clinician bridge for seamless follow-up** - Healthcare provider integration and reporting

---

**Made with 💜 for women's health**

*Thalia empowers women with evidence-based menopause support, combining medical expertise with compassionate AI assistance.*
