from flask import Flask, render_template, jsonify, request
from src.helper import download_embeddings as download_hugging_face_embeddings
from langchain_pinecone import PineconeVectorStore
from langchain_openai import ChatOpenAI
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import (
    create_stuff_documents_chain,
)
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from src.prompt import *
import os
from langchain_groq import ChatGroq


app = Flask(__name__)


load_dotenv()

print("✓ Step 1: Environment variables loaded")

PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY

print("✓ Step 2: API keys configured")

print("⏳ Step 3: Downloading HuggingFace embeddings (this may take a minute on first run)...")
embeddings = download_hugging_face_embeddings()
print("✓ Step 3: Embeddings downloaded successfully")

index_name = "medical-chatbot-index"

print("⏳ Step 4: Connecting to Pinecone index...")
# Embed each chunk and upsert the embeddings into your Pinecone index.
docsearch = PineconeVectorStore.from_existing_index(
    index_name=index_name, embedding=embeddings
)
print("✓ Step 4: Pinecone connected successfully")

print("⏳ Step 5: Setting up retriever...")
retriever = docsearch.as_retriever(search_type="similarity", search_kwargs={"k": 3})
print("✓ Step 5: Retriever configured")

print("⏳ Step 6: Initializing ChatGroq LLM...")
chatModel = ChatGroq(model="openai/gpt-oss-120b", temperature=0.7)
print("✓ Step 6: LLM initialized")

print("⏳ Step 7: Creating prompt template...")
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}"),
    ]
)
print("✓ Step 7: Prompt configured")

print("⏳ Step 8: Building RAG chain...")
question_answer_chain = create_stuff_documents_chain(chatModel, prompt)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)
print("✓ Step 8: RAG pipeline ready!")
print("\n" + "="*60)
print("✅ ALL INITIALIZATION COMPLETE!")
print("🚀 Flask server is starting...")
print("="*60 + "\n")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/get", methods=["GET", "POST"])
def chat():
    try:
        msg = request.form.get("msg", "").strip()
        if not msg:
            return "Please enter a message.", 400

        print(f"User message: {msg}")
        response = rag_chain.invoke({"input": msg})
        answer = response.get("answer", "I couldn't generate a response.")
        print(f"Bot response: {answer}")
        return str(answer)
    except Exception as e:
        print(f"Error: {str(e)}")
        return f"Error processing your request: {str(e)}", 500


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 MEDICAL CHATBOT STARTING...")
    print("="*60)
    print("Open your browser: http://localhost:8080")
    print("="*60 + "\n")
    app.run(host="0.0.0.0", port=8080, debug=True)
