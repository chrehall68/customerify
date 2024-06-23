import os
from pinecone import Pinecone, ServerlessSpec
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core import SimpleDirectoryReader, StorageContext, VectorStoreIndex
import markdownify
from bs4 import BeautifulSoup
import aiofiles


async def save_document(document: BeautifulSoup, uuid: str):
    md = markdownify.MarkdownConverter().convert_soup(document)
    async with aiofiles.open(f"docs/sample{uuid}.md", "w") as f:
        await f.write(md)


def embed_documents():
    pc = Pinecone(os.environ["PINECONE_API_KEY"])
    index_name = "customerify"

    if index_name in [index["name"] for index in pc.list_indexes()]:
        pc.delete_index(index_name)

    pc.create_index(
        name=index_name,
        dimension=1536,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1",
        ),
    )

    pinecone_index = pc.Index(index_name)
    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    documents = SimpleDirectoryReader("./docs").load_data()

    index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)

    docs = os.path.dirname(__file__) + "/docs"
    for filename in os.listdir(docs):
        file_path = os.path.join(docs, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
        except Exception as e:
            print("Failed to delete %s. Reason: %s" % (file_path, e))
