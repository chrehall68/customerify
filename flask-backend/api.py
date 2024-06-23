from flask import Flask, request
from embed import load_documents, embed_documents
from rag import query_index
import scrape
from typing import Dict, List

app = Flask(__name__)

# maps Call ID: message history
user_context: Dict[str, List[str]] = {}
company_name = "ACME Inc."


@app.route("/api/customerify/store", methods=["POST"])
def store():
    global company_name
    if request.method == "POST":
        try:
            base_url = request.json.get("url")
            company_name = request.json.get("company_name")
            print(base_url)
            urls = scrape.main(base_url, 10, 1)
            print(urls)
            load_documents(urls)
            embed_documents()
        except:
            return "", 500


@app.route("/api/customerify/query", methods=["POST"])
def query():
    if request.method == "POST":
        try:
            query = request.json.get("query")
            # print(query, company_name)
            user_context.append("QUESTION: " + query)
            response = query_index("\n\n".join(user_context))
            user_context[-1] = "\nANSWER: " + str(response)
            return str(response), 200

        except:
            return "", 500


if __name__ == "__main__":
    app.run("0.0.0.0")
