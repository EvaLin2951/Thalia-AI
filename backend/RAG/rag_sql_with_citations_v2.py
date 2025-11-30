

import os
import sys
import re


# to get current pathway
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
        metadata = {k: v for k, v in doc.items() if k != "content"}
        # Ensure a simple 'source' field exists for backward compatibility
        if "file_name" in doc and "source" not in metadata:
            metadata["source"] = doc["file_name"]
        documents.append(Document(page_content=doc["content"], metadata=metadata))
    
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

# Alias for compatibility with citation-based chat helper
vectordb = vectorstore

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

# ========= Citation & chat helpers (integrated from prompt_citation_chat.py) =========

# Basic retrieval / scoring config
TOP_K        = 3
FETCH_K      = 60
MMR_LAMBDA   = 0.5
DOMAIN_TOPICS = [
    "menopause", "perimenopause", "postmenopause", "vasomotor", "hot flash", "night sweat",
    "hormone therapy", "HRT", "estradiol", "progesterone", "vaginal", "urogenital",
    "MRS", "menopause rating scale", "FSH", "AMH", "endometrium", "bone density",
    "Kupperman", "menopausal transition", "climacteric",
]
MIN_SIM_OUT_DOMAIN = 0.55
MIN_SIM_IN_DOMAIN  = 0.25

DOMAIN_RE = re.compile("|".join(re.escape(k) for k in DOMAIN_TOPICS), re.I)

def _looks_in_domain(q: str) -> bool:
    """Roughly decide whether the question is menopause‑related."""
    return bool(DOMAIN_RE.search(q))

def _scores_from_results(results):
    """
    results: List[(Document, distance)]  ->  List[(Document, similarity)]
    Convert the "distance" returned by Chroma into a "similarity" between 0 and 1.
    """
    sims = []
    for d, dist in results:
        try:
            sim = 1.0 - float(dist)
        except Exception:
            sim = 0.0
        sims.append((d, max(0.0, min(1.0, sim))))
    return sims

# ---- Citation formatting ----
def _apa_like_from_metadata(meta: dict) -> str:
    author  = meta.get("authors") or "Unknown"
    year    = str(meta.get("year") or "n.d.")
    title   = meta.get("title") or meta.get("file_name") or "Untitled"
    journal = meta.get("journal") or ""
    doi     = meta.get("doi") or ""

    parts = [f"{author}. ({year}). {title}."]
    if journal:
        parts.append(journal + ".")
    if doi:
        if doi.startswith("10."):
            parts.append(f"https://doi.org/{doi}")
        else:
            parts.append(doi)
    return " ".join(parts)

def numbered_citation(doc, idx: int) -> str:
    meta = doc.metadata or {}
    if meta.get("citation"):
        return f"[{idx}] {meta['citation']}"
    return f"[{idx}] {_apa_like_from_metadata(meta)}"

# ---- Menopause answer template + Gemini helper ----
MENOPAUSE_RAG_TEMPLATE = """You are a compassionate and knowledgeable menopause support assistant.

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
Hot flashes are a common vasomotor symptom of menopause caused by changes in how your body regulates temperature as estrogen levels decline. This drop in estrogen can make the brain's internal "thermostat" more sensitive, so even small changes in body temperature can trigger a strong response.
During a hot flash, blood vessels near the skin surface dilate to release heat, which is why you suddenly feel very warm, flushed, and may start sweating. These episodes can last from seconds to several minutes and are often more frequent at night, sometimes disrupting sleep.
While hot flashes are a normal part of the menopause transition, their frequency and intensity vary from person to person. If they are affecting your daily life or sleep, you might consider speaking with a healthcare provider about options, including hormone therapy or non-hormonal alternatives.

---

[Warm Empathetic Style Example]

Context:
Sleep problems and night sweats are discussed in the context of menopause transition.

Question:
I can't sleep and feel exhausted all the time. Is this normal?

Answer:
I'm so sorry you're feeling this way — it's completely understandable to feel exhausted and frustrated when you're not sleeping well.
Sleep problems and night sweats are very common during perimenopause and menopause. As hormone levels shift, especially estrogen and progesterone, the parts of the brain that regulate temperature and sleep can be disrupted. This can lead to night sweats, frequent awakenings, or feeling tired even after a full night's rest.
Even though this experience is common, it doesn't mean you have to just "put up with it." There are practical steps that may help — like keeping your bedroom cool, wearing breathable sleepwear, reducing caffeine or alcohol near bedtime, and creating a calming wind-down routine. For some people, treatments such as hormone therapy or other medications can make a big difference.
Most importantly, your exhaustion is valid — it's not "in your head." If these symptoms are affecting your ability to function or enjoy daily life, it would be very reasonable to talk with a healthcare provider about what you're going through. You deserve support and rest.

---

[Blended Style Example]

Context:
User describes feeling emotionally overwhelmed, confused, and unsure how to cope with menopausal symptoms.

Question:
I'm scared and confused about these symptoms. Why do I feel so lost during menopause?

Answer:
It's completely understandable to feel scared and lost during menopause — you're not alone in this at all. Menopause is not just a physical transition; it's also an emotional and psychological one, and many people are surprised by how deeply it affects their sense of self.
As estrogen and other hormones fluctuate and decline, they can influence brain chemistry and stress regulation. This can contribute to mood changes, anxiety, irritability, or a sense of being "not yourself." At the same time, you may be juggling work, family, aging, and other life changes, all of which can intensify these feelings.
Feeling confused or overwhelmed doesn't mean you're weak — it means you're going through a real, complex transition that deserves understanding and care. It may help to learn more about what’s happening in your body, track your symptoms, and consider sharing them with a trusted clinician. Support groups, therapy, or even honest conversations with friends can also provide validation.
You deserve to feel heard and supported during this time. With the right information and care plan, many people find that their symptoms can be managed and that they eventually regain a sense of balance. You are not alone, and what you’re feeling is valid.

---

Now, based on the following context and user question, please provide a concise, evidence-informed answer. Respond in a helpful, appropriate tone (expert, warm, or blended):

Context:
{context}

Question:
{question}

Answer:"""

def _gen_short_answer(context_snips, question, in_domain, top_sim, max_chars=800):
    """
    Use the existing LangChain `llm` (ChatGoogleGenerativeAI) plus MENOPAUSE_RAG_TEMPLATE
    to generate an answer based on retrieved context. On failure, fall back to a generic
    but safe message.
    """
    ctx = "\n\n".join(context_snips)
    prompt_text = MENOPAUSE_RAG_TEMPLATE.format(context=ctx, question=question)

    try:
        # `llm` is the ChatGoogleGenerativeAI instance defined above.
        resp = llm.invoke(prompt_text)
        # LangChain chat models usually return an AIMessage with `.content`
        text = getattr(resp, "content", None) or str(resp)
        text = text.strip()
        if not text:
            raise RuntimeError("Empty response from LLM")

        return text[:max_chars] if max_chars else text

    except Exception as e:
        print("⚠️ LLM call failed, using fallback message: ", repr(e))

        if (not in_domain) and (top_sim < MIN_SIM_OUT_DOMAIN):
            return (
                "This question appears outside the menopause domain of your local library. "
                "Please ask a menopause-related question."
            )

        if in_domain and (top_sim < MIN_SIM_IN_DOMAIN):
            return (
                "I found some potentially related sources in your menopause library. "
                "If it's not specific enough, try a narrower query."
            )

        return "I found relevant professional sources for your question and listed them below."


# ---- High level chat() that returns answer + numbered citations ----# ---- High level chat() that returns answer + numbered citations ----
def chat(question: str, top_k: int | None = None, use_mmr: bool = True) -> str:
    q = question.strip()
    assert "vectordb" in globals(), "vectordb is not defined. Please build the vector library first."
    if top_k is None:
        top_k = TOP_K

    in_domain = _looks_in_domain(q)

    CAND_MULT   = 3
    MMR_FETCH_K = max(FETCH_K, top_k * 8)

    try:
        mmr_hits = []
        if use_mmr:
            retriever = vectordb.as_retriever(
                search_type="mmr",
                search_kwargs={
                    "k": top_k * CAND_MULT,
                    "fetch_k": MMR_FETCH_K,
                    "lambda_mult": MMR_LAMBDA,
                },
            )
            mmr_hits = retriever.invoke(q)

        try:
            scored = vectordb.similarity_search_with_score(q, k=top_k * CAND_MULT)
            if not scored and mmr_hits:
                scored = [(d, 1.0) for d in mmr_hits]
        except Exception:
            base = mmr_hits or vectordb.similarity_search(q, k=top_k * CAND_MULT)
            scored = [(d, 1.0) for d in base]
    except Exception:
        base = vectordb.similarity_search(q, k=top_k * CAND_MULT)
        scored = [(d, 1.0) for d in base]

    sims = _scores_from_results(scored)
    if not sims:
        msg = "No documents found in your local menopause library."
        #print(msg)
        return msg

    sims.sort(key=lambda x: x[1], reverse=True)
    top_sim = sims[0][1]

    # Use the top-k docs as context snippets
    docs = [d for (d, _) in sims[:top_k]]
    ctx_snips = [d.page_content for d in docs]

    answer = _gen_short_answer(ctx_snips, q, in_domain, top_sim)

    # Citations: de-duplicate based on doi/title/source/file_path
    unique_docs = []
    seen_keys = set()
    for d in docs:
        md_meta = d.metadata or {}
        key = (
            md_meta.get("doi")
            or md_meta.get("title")
            or md_meta.get("source")
            or md_meta.get("file_path")
        )
        if not key:
            continue
        if key in seen_keys:
            continue
        seen_keys.add(key)
        unique_docs.append(d)

    refs = [numbered_citation(d, i + 1) for i, d in enumerate(unique_docs)]

    md = (
        f"{answer}\n\n"
        "References:\n\n" + "\n".join(f"— {r}" for r in refs)
    )
    #print(md)
    return md

class ChatWithCitationsChain:
    """Simple wrapper so front-end can keep using rag_chain.invoke(question)."""
    def invoke(self, question: str):
        return chat(question)

rag_chain = ChatWithCitationsChain()

print("RAG chain with citation-aware chat successfully built.")
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