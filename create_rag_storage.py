import os
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from pinecone import Pinecone, ServerlessSpec
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.vector_stores.pinecone import PineconeVectorStore

# Variables
api_key = "" # The Pinecone API key
pinecone_index_name = "" # The name of the index for your EBM sources
ebm_source_path = "" # The path to your EBM sources, without subfolders. No trailing slash.

# Code (remove CUDA if you don't have a GPU)
# Feel free to change settings or models to your liking. If you change the embedding model, make sure to change the model in the central back end code as well (same lines of code).

pc = Pinecone(api_key=api_key)

pc.create_index(
    name=pinecone_index_name,
    dimension=1024,
    metric="euclidean",
    spec=ServerlessSpec(cloud="aws", region="us-east-1"),
)

pinecone_index = pc.Index("reviews")

embed_model = HuggingFaceEmbedding(
    model_name="dunzhang/stella_en_400M_v5",
    target_devices=["cuda:0"],
    trust_remote_code=True
)
documents = SimpleDirectoryReader(ebm_source_path).load_data()
vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
index = VectorStoreIndex.from_documents(
    documents, storage_context=storage_context, show_progress = True, embed_model=embed_model
)