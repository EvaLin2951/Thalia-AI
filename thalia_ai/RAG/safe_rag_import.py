"""
Safe RAG import wrapper
Safely imports RAG chain without crashing the app
Uses SQL version (connects to MySQL database)
"""
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from root .env
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

# Initialize as None
rag_chain = None

# Check for quick-start mode (skip RAG loading)
skip_rag = os.getenv("SKIP_RAG", "").lower() in ['true', '1', 'yes']

if skip_rag:
    print("⚠️  SKIP_RAG enabled - RAG loading skipped for quick start")
    print("   Remove SKIP_RAG from environment to enable RAG features")
elif not os.getenv("GOOGLE_API_KEY"):
    print("⚠️  GOOGLE_API_KEY not set in .env file")
    print("   RAG/AI chat will be unavailable")
    print("   Add GOOGLE_API_KEY to enable AI features")
else:
    print("🔄 Loading RAG chain from MySQL database...")
    try:
        # Import SQL RAG version (connects to MySQL)
        from RAG import rag_sql
        rag_chain = getattr(rag_sql, 'rag_chain', None)

        if rag_chain is not None:
            print("✅ RAG chain loaded successfully (SQL/MySQL version)")
        else:
            print("⚠️  RAG chain initialized but is None")
            print("   Check if database has PDF documents")
    except Exception as e:
        print(f"❌ RAG import failed: {type(e).__name__}: {e}")
        print("   RAG/AI chat will be unavailable")
        rag_chain = None

# Export rag_chain
__all__ = ['rag_chain']
