import os
# from pinecone import Pinecone, ServerlessSpec
from llama_index.llms.groq import Groq
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.core import Settings
# from llama_index.vector_stores.pinecone import PineconeVectorStore
# from llama_index.embeddings.huggingface import HuggingFaceEmbedding


# pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])

# pc.create_index("customerify", dimension=1536, metric="cosine", spec=ServerlessSpec(
#     cloud='aws',
#     region='us-east-1'
# ))


# pinecone.init(
#     api_key=os.environ["PINECONE_API_KEY"], environment="us-west1-gcp")
# pinecone.create_index("customerify", dimension=1536, metric="cosine")

# construct vector store and customize storage context
# storage_context = StorageContext.from_defaults(
#     vector_store=PineconeVectorStore(pc.Index("customerify")))

# extend overlap of chunks
# Settings.chunk_overlap = 50
# Settings.embed_model = HuggingFaceEmbedding(
#     model_name="BAAI/bge-small-en-v1.5"
# )
# load documents and build index
documents = SimpleDirectoryReader('./docs').load_data()
# index = VectorStoreIndex.from_documents(
#     documents, storage_context=storage_context)
index = VectorStoreIndex.from_documents(
    documents)


llm = Groq(model="llama3-70b-8192", api_key=os.environ["GROQ_API_KEY"])

query_engine = index.as_query_engine(llm=llm)
response = query_engine.query(
    "Will I be able to trade in my iPhone with a cracked screen?")
print(response)
