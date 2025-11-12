

import os
import sys

# print("\n--- sys.path for debugging ---")
# for p in sys.path:
#     print(p)
# print("----------------------------\n")


current_script_dir = os.path.dirname(os.path.abspath(__file__))


project_root_dir = os.path.join(current_script_dir, "..")
sys.path.append(project_root_dir)



# --- 1. Configuration ---
from dotenv import load_dotenv
persist_directory = "./chroma_db"

load_dotenv()

print("❗️ Please ensure all necessary libraries are installed via pip install.")
# ----------------------------------------------------

# --- 2. Connecting to Gemini API ---
gemini_api_key = os.getenv("GOOGLE_API_KEY")

if gemini_api_key:
    os.environ["GOOGLE_API_KEY"] = gemini_api_key
    print("✅ Google API Key has been successfully loaded from environment or .env file.")
else:
    print("Warning: GOOGLE_API_KEY environment variable not set. Please set it to proceed.")
    print("Exiting script. Please set GOOGLE_API_KEY and restart.")
    exit()
# ----------------------------------------------------

# --- 3. Documents/Database Loading ---
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from db.fetch_pdfs import fetch_pdf_texts

print("Loading documents from MySQL database...")
try:
    db_documents = fetch_pdf_texts()
    documents = []
    for doc in db_documents:
        documents.append(Document(page_content=doc['content'], metadata={"source": doc['file_name']}))
    
    print(f"✅ Loaded {len(documents)} documents from the database.")
except Exception as e:
    print(f"Error loading documents from database: {e}")
    print("Please ensure your MySQL database is running and accessible, and 'pdf_documents' table exists.")
    print("Exiting script. Please check your database connection.")
    exit()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
texts = text_splitter.split_documents(documents)

print(f"Number of text chunks after splitting: {len(texts)}")
if not texts:
    print("No text chunks were generated. Please check your documents and splitting parameters.")
    print("Exiting script.")
    exit()
else:
    print(f"Example of the first text chunk (first 200 chars):\n{texts[0].page_content[:200]}...")
# ----------------------------------------------------


# --- 4. Import embedding model and vector store ---
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma

print("Initializing Gemini Embedding Model and creating Vector Store...")
embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

if os.path.exists(persist_directory) and os.listdir(persist_directory):
    print(f"Loading existing vector store from: {persist_directory}")
    vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
else:
    print(f"Creating new vector store and saving to: {persist_directory}")
    vectorstore = Chroma.from_documents(texts, embeddings, persist_directory=persist_directory)

print(f"✅ All {len(texts)} text chunks successfully embedded and stored in a single vector store!")
print(f"Vector store saved to: {persist_directory}")
# ----------------------------------------------------


# --- 5. Import LLM model and RAG chain components ---
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

print("Initializing Gemini LLM Model and building RAG chain...")
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.5)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

template = """You are a compassionate and knowledgeable menopause support assistant.

Before answering, please:
1. Analyze the user's query to understand their core intent
2. If the query is vague or uses colloquial terms, mentally rephrase it using proper medical terminology
3. Consider related menopause symptoms or concerns that might be relevant
4. If the query is incomplete, use your menopause knowledge to provide comprehensive context

You provide responses in different helpful tones depending on the situation.

---

[Expert Style Example]

Context:
Hot flashes are sudden sensations of intense heat due to changes in thermoregulation linked to declining estrogen.

Question:
Why do I keep getting hot flashes?

Answer:
Hot flashes are a common vasomotor symptom of menopause caused by disruptions in the hypothalamus, which regulates body temperature. These changes are primarily driven by declining estrogen levels. The body responds by dilating blood vessels and triggering sweating as a cooling mechanism. If they interfere with your quality of life, consult a healthcare provider to explore treatment options, including hormone therapy or non-hormonal alternatives.

---

[Warm Empathetic Style Example]

Context:
Sleep problems and night sweats are discussed in the context of menopause transition.

Question:
I can't sleep and feel exhausted all the time. Is this normal?

Answer:
I'm so sorry you're feeling this way — it's completely understandable. Many women experience sleep issues during menopause, especially due to night sweats or hormonal changes. You're not alone. One step that might help is keeping your bedroom cool, using breathable sheets, and tracking your symptoms. Please know that support is available, and you're doing your best in a challenging time. You're not alone.

---

[Blended Style Example]

Context:
User describes feeling emotionally overwhelmed, confused, and unsure how to cope with menopausal symptoms.

Question:
I'm scared and confused about these symptoms. Why do I feel so lost during menopause?

Answer:
It's completely understandable to feel lost during menopause — your body is going through major changes, and it can affect your emotions, energy, and clarity. Many women feel overwhelmed at this stage. On a medical level, hormone shifts — especially the drop in estrogen — can impact mood regulation, sleep, and mental clarity. If you feel ready, journaling your symptoms and talking to a supportive doctor can really help. You're not alone — we can take it one step at a time.

---

[Expert Style Example #2]

Context:
Estrogen levels drop significantly during menopause.

Question:
What does low estrogen actually do to the body?

Answer:
Low estrogen during menopause can affect multiple systems — it may lead to symptoms like hot flashes, vaginal dryness, mood changes, and decreased bone density. Estrogen helps regulate temperature, maintains urogenital tissue health, and protects against osteoporosis. If symptoms are severe, options like hormone replacement therapy (HRT) may be discussed with your doctor.

---

[Warm Empathetic Style Example #2]

Context:
User shares that they feel alone and unsupported during menopause.

Question:
Why does no one talk about menopause? I feel like I'm going through this alone.

Answer:
You're absolutely not alone, even if it feels that way. So many women go through this transition silently because it's not talked about enough. But your experience is real and valid. It's okay to feel confused or isolated. There are supportive communities, resources, and health professionals who truly care — you deserve that support. Thank you for speaking up.

---


Now, based on the following context and user question, please respond in a helpful, appropriate tone (expert, warm, or blended):

Context:
{context}

Question:
{question}

Answer:"""
prompt = ChatPromptTemplate.from_template(template)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

print("RAG chain successfully built.")
# ----------------------------------------------------

#  --- 6. Local Testing RAG ---
def test_rag_local_output():
    """
    Tests the RAG chain with predefined questions and prints responses to the console.
    """
    print("\n--- Testing RAG Chain (SQL Output) ---")

    questions = [
        "What are the impact of menopause?",
        "What are vasomotor symptoms (VMS)?",
        "What should I know about menopause?",
        "When does the 2026 World Cup take place?",
        "What should I know about menopause?",
        "Does menopause affect sleep quality?",
        "Is hormone therapy (HRT) safe for menopausal symptoms?",
        "What lifestyle changes can help with menopause symptoms?"
    ]

    for question in questions:
        print(f"\nQuestion: {question}")
        response = rag_chain.invoke(question)
        print(f"Answer: {response}")

    print("\n ✅ RAG pipeline setup complete. SQL RAG testing finished.")

if __name__ == "__main__":
    test_rag_local_output()
# ----------------------------------------------------
