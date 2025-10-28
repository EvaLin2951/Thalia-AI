# teammate_frontend_app.py
#from .rag_local import rag_chain # Local RAG_Database
from .rag_sql import rag_chain # MySQL Connection

def get_chatbot_response(user_message, chat_history):
    response = rag_chain.invoke(user_message)
    return response

if __name__ == "__main__":
    user_input = input("Ask me a question: ")
    answer = get_chatbot_response(user_input, []) 
    print(f"Bot: {answer}")