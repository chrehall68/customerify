import os
from pinecone import Pinecone
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.llms.groq import Groq
from llama_index.core import VectorStoreIndex, PromptTemplate
from llama_index.core.query_pipeline import QueryPipeline
from llama_index.core.postprocessor import LLMRerank
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.response_synthesizers import TreeSummarize


def query_index(query, company_name=""):
    pc = Pinecone(os.environ["PINECONE_API_KEY"])

    index_name = "customerify"
    index = pc.Index(index_name)
    vector_store = PineconeVectorStore(pinecone_index=index)

    vector_index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

    prompt_str = (
        f"You are a helpful customer service agent for {company_name}. "
        + "You know who is currently on a phone call and tries to answer user questions factually. You are given the following query and should return only a factual answer without preliminary mentions of if the text is mentioned in the context of the provided documents or where you're referencing unless otherwise stated. There may exist a series of questions and answers. Those represent the context of the query. ONLY THE LAST 'QUESTION' SHOULD BE ANSWERED. If an answer cannot be inferred from the text, say that.\n\nText:\n\n {query}"
    )

    prompt_tmpl = PromptTemplate(prompt_str)
    llm = Groq(model="llama3-70b-8192", api_key=os.environ["GROQ_API_KEY"])
    retriever = VectorIndexRetriever(index=vector_index, similarity_top_k=3)
    # reranker = LLMRerank(top_n=3)
    # summarizer = TreeSummarize(llm=llm)

    # p = QueryPipeline(verbose=True)
    # p.add_modules(
    #     {
    #         "llm": llm,
    #         # "prompt_tmpl": prompt_tmpl,
    #         "retriever": retriever,
    #         # "reranker": reranker,
    #         # "summarizer": summarizer,
    #     }
    # )
    p = vector_index.as_query_engine()

    # p.add_link('prompt_tmpl', 'llm')
    # p.add_link('llm', 'retriever')
    # p.add_link('retriever', 'reranker', dest_key="nodes")
    # p.add_link('llm', 'reranker', dest_key="query_str")
    # p.add_link('reranker', 'summarizer', dest_key="nodes")
    # p.add_link('llm', 'summarizer', dest_key="query_str")

    output = p.query(query)

    return output


def main():
    query = input("Query: ")
    response = query_index(query)
    print(str(response))


if __name__ == "__main__":
    main()
