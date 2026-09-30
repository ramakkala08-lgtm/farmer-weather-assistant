from flask import Flask, request, jsonify
from flask_cors import CORS

import os
import re

from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_huggingface import HuggingFaceEndpoint
from langchain_huggingface import ChatHuggingFace

from langchain_google_genai import ChatGoogleGenerativeAI

model = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    temperature=0.2
)
# =========================================================
# ENVIRONMENT
# =========================================================

app = Flask(__name__)
CORS(app)


# =========================================================
# EMBEDDING MODEL
# MUST MATCH THE MODEL USED WHEN CHROMA WAS CREATED
# =========================================================

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# =========================================================
# LOAD EXISTING CHROMA DATABASE
# =========================================================

vectorstore = Chroma(
    persist_directory="chroma_db",
    embedding_function=embeddings
)


# =========================================================
# HUGGING FACE LLM
# =========================================================




# =========================================================
# DETECT NITW-SPECIFIC QUESTIONS
# =========================================================

def is_nitw_question(message):

    text = message.lower()

    nitw_keywords = [
        "nitw",
        "nit warangal",
        "warangal campus",
        "hostel",
        "mess",
        "library",
        "gym",
        "washerman",
        "campus",
        "department",
        "curriculum",
        "syllabus",
        "semester",
        "academic calendar",
        "holiday",
        "holidays",
        "class schedule",
        "class timetable",
        "timetable",
        "course",
        "subject",
        "subjects",
        "b.tech",
        "mechanical engineering",
        "mechanical",
        "cse",
        "ece",
        "eee",
        "civil",
        "chemical",
        "metallurgy",
        "academic",
        "admission",
        "fees",
        "faculty",
        "club",
        "clubs",
        "exam",
        "examination"
    ]

    return any(
        keyword in text
        for keyword in nitw_keywords
    )


# =========================================================
# SIMPLE CASUAL QUESTIONS
# =========================================================

def is_casual(message):

    text = message.lower().strip()

    casual_patterns = [
        r"^hi$",
        r"^hello$",
        r"^hey$",
        r"^hey there$",
        r"^good morning$",
        r"^good afternoon$",
        r"^good evening$",
        r"^how are you\??$"
    ]

    return any(
        re.match(pattern, text)
        for pattern in casual_patterns
    )


# =========================================================
# GENERAL LLM RESPONSE
# =========================================================

def general_response(user_message):

    prompt = f"""
You are the NITW Fresher Assistant.

You are friendly, natural, student-friendly, and slightly
humorous when appropriate.

Your identity:
- You are the NITW Fresher Assistant.
- You were built by Ram from Team Paradise,
  Mechanical Department, NIT Warangal.

For normal casual or general questions, answer naturally.

USER QUESTION:
{user_message}

Give a useful and conversational answer.
"""

    response = model.invoke(prompt)

    return response.content


# =========================================================
# RAG RESPONSE
# =========================================================

def rag_response(user_message):

    # -----------------------------------------------------
    # Retrieve top 5 results WITH SCORES
    # -----------------------------------------------------

    results = vectorstore.similarity_search_with_score(
        user_message,
        k=5
    )

    print("\n")
    print("=" * 70)
    print("RAG RETRIEVAL DEBUG")
    print("=" * 70)

    for i, (doc, score) in enumerate(results):

        print(f"\nRESULT {i + 1}")
        print("-" * 40)

        print("Distance :", score)

        print(
            "Source   :",
            doc.metadata.get("source")
        )

        print(
            "Page     :",
            doc.metadata.get("page")
        )

        print("Preview  :")
        print(
            doc.page_content[:500]
        )

    print("=" * 70)

    # -----------------------------------------------------
    # TEMPORARY:
    # Use top retrieved documents directly.
    #
    # We are NOT applying an arbitrary distance threshold
    # yet. We need to see real scores first.
    # -----------------------------------------------------

    relevant_docs = [
        doc
        for doc, score in results
    ]

    if not relevant_docs:

        return (
            "I don't have verified information about "
            "that yet 😅"
        )

    # -----------------------------------------------------
    # Build context
    # -----------------------------------------------------

    context_parts = []

    for doc in relevant_docs:

        source = doc.metadata.get(
            "source",
            "Unknown"
        )

        page = doc.metadata.get(
            "page",
            "Unknown"
        )

        method = doc.metadata.get(
            "method",
            "Unknown"
        )

        context_parts.append(
            f"""
SOURCE: {source}
PAGE: {page}
EXTRACTION METHOD: {method}

{doc.page_content}
"""
        )

    context = "\n\n".join(
        context_parts
    )

    # -----------------------------------------------------
    # RAG PROMPT
    # -----------------------------------------------------

    prompt = f"""
You are the NITW Fresher Assistant.

PERSONALITY:
- Friendly
- Natural
- Student-friendly
- Slightly humorous when appropriate
- Speak like a helpful senior

IMPORTANT KNOWLEDGE RULE:

The context below was retrieved from the NITW document
knowledge base.

For NITW-specific factual questions:

1. Use the retrieved context as your source.
2. Do not invent NITW facts.
3. Do not use outside/general knowledge to fill missing
   NITW information.
4. Do not give "typical college" information.
5. Do not guess.
6. If the context clearly does not contain the answer,
   say exactly:

"I don't have verified information about that yet 😅"

Do not add unsupported advice after that sentence.

For example:
- A Mechanical curriculum question should be answered
  from the Mechanical curriculum document.
- A holiday question should be answered from the
  holiday/calendar documents.

RETRIEVED NITW CONTEXT:
--------------------------------------------------
{context}
--------------------------------------------------

USER QUESTION:
{user_message}

Answer the user's question clearly and naturally.
"""

    response = model.invoke(prompt)

    return response.content


# =========================================================
# CHAT API
# =========================================================

@app.route("/chat", methods=["POST"])
def chat():

    try:

        data = request.get_json()

        if not data:

            return jsonify({
                "response": "I didn't receive your question 😅"
            })

        user_message = data.get(
            "message",
            ""
        ).strip()

        if not user_message:

            return jsonify({
                "response": "Ask me something, fresher 😄"
            })

        print("\n")
        print("=" * 70)
        print("USER QUESTION:")
        print(user_message)
        print("=" * 70)

        # -------------------------------------------------
        # CASUAL
        # -------------------------------------------------

        if is_casual(user_message):

            answer = general_response(
                user_message
            )

        # -------------------------------------------------
        # NITW-SPECIFIC → RAG
        # -------------------------------------------------

        elif is_nitw_question(user_message):

            answer = rag_response(
                user_message
            )

        # -------------------------------------------------
        # GENERAL → LLM
        # -------------------------------------------------

        else:

            answer = general_response(
                user_message
            )

        return jsonify({
            "response": answer
        })

    except Exception as e:

        print("\nSERVER ERROR:")
        print(e)

        return jsonify({
            "response": (
                "Something went wrong on my side 😅 "
                "Check the Python terminal."
            )
        }), 500


# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":

    print("\n==============================================")
    print("      NITW FRESHER ASSISTANT BACKEND")
    print("==============================================")
    print("Running on: http://127.0.0.1:5000")
    print("")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )