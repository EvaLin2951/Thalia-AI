# teammate_frontend_app.py
#from .rag_local import rag_chain # Local RAG_Database
from .rag_sql import rag_chain # MySQL Connection

def get_chatbot_response(user_message, chat_history):
    """
    处理用户消息并返回聊天机器人响应
    Args:
        user_message: 用户输入的消息
        chat_history: 聊天历史（Gradio ChatInterface 自动传递）
    Returns:
        response: 聊天机器人的响应
    """
    response = rag_chain.invoke(user_message)
    return response

if __name__ == "__main__":
    user_input = input("Ask me a question: ")
    answer = get_chatbot_response(user_input, [])  # 传递空的聊天历史
    print(f"Bot: {answer}")