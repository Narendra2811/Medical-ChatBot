from dotenv import load_dotenv
import os
from pinecone import Pinecone, ServerlessSpec
from src.helper import (
    download_embeddings,
    filter_to_minimal_docs,
    load_pdf_files,
    text_splits,
)
from langchain_pinecone import PineconeVectorStore


load_dotenv()

os.environ["PINECONE_API_KEY"] = os.getenv("PINECONE_API_KEY")
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")


extracted_docs = load_pdf_files("data")
minimal_docs = filter_to_minimal_docs(extracted_docs)
text_chunks = text_splits(minimal_docs)
embedding = download_embeddings()


pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))


index_name = "medical-chatbot-index"

# Check if index exists
existing_indexes = [i.name for i in pc.list_indexes()]

if index_name not in existing_indexes:
    pc.create_index(
        name=index_name,
        dimension=384,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )

index = pc.Index(index_name)


docsearch = PineconeVectorStore.from_documents(
    documents=text_chunks, embedding=embedding, index_name=index_name
)
