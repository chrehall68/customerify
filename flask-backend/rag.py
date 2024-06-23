import os
from pinecone import Pinecone
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.llms.groq import Groq
from llama_index.core import VectorStoreIndex
from llama_index.core.llms import ChatMessage
# from llama_index.core.query_pipeline import QueryPipeline
# from llama_index.core.postprocessor import LLMRerank
from llama_index.core.retrievers import VectorIndexRetriever
# from llama_index.core.response_synthesizers import TreeSummarize


def query_index(query, company_name=" a company"):
    pc = Pinecone(os.environ["PINECONE_API_KEY"])

    index_name = 'customerify'
    index = pc.Index(index_name)
    vector_store = PineconeVectorStore(pinecone_index=index)

    vector_index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store)

    # init_prompt = "Given the following query, please rephrase the very LAST 'QUESTION' following the line of hashtags in the given query that does not have an answer right after.\n\nQuery: {query}\n\nAnswer:"

    # prompt_tmpl = PromptTemplate(init_prompt)
    # summary_prompt = PromptTemplate(prompt_str)
    llm = Groq(model="llama3-70b-8192", api_key=os.environ["GROQ_API_KEY"])
    retriever = VectorIndexRetriever(index=vector_index, similarity_top_k=3)

    retrieved_docs = retriever.retrieve(query)
    similar_docs = [doc.text for doc in retrieved_docs]

    prompt_str = f"You are a helpful customer service agent for {company_name}. " + \
        f"""You are currently on a phone call with a customer and will attempt to answer users' questions factually making use of the context provided below:\n
    ------------------------------------------------------
    CONTEXT:
    {'\n\n'.join(similar_docs)}
    ------------------------------------------------------
    \n
    Given the context information and not prior knowledge, answer the query. Please keep your answer down to at most 4 sentences"""

    messages = [
        ChatMessage(
            role="system",
            content=prompt_str
        ),
        ChatMessage(
            role="user",
            content=query
        )
    ]

    response = llm.chat(messages)
    # print(response.message.content.strip())

    return response.message.content.strip()


def main():
    query = input("Query: ")
    response = query_index(query)
    print(str(response))


if __name__ == "__main__":
    main()
