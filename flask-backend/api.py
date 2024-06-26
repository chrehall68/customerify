from flask import Flask, request
from embed import save_document, embed_documents
from rag import query_index
import scrape
from typing import Dict, List
from collections import defaultdict

app = Flask(__name__)

# maps Call ID: message history
user_context: Dict[str, List[str]] = defaultdict(list)
company_name = "ACME Inc."


@app.route("/api/customerify/store", methods=["POST"])
async def store():
    global company_name
    if request.method == "POST":
        try:
            base_url = request.json.get("url")
            company_name = request.json.get("company_name")
            print(base_url)
            urls = await scrape.main(base_url, 10, 5, save_document)
            print("got urls", urls)
            embed_documents()
            return "", 200
        except Exception as e:
            print("Got exception", e)
            raise e
            return "", 500


@app.route("/api/customerify/query", methods=["POST"])
def query():
    # request should have
    # query
    # call_id
    if request.method == "POST":
        try:
            query = request.json.get("query")
            # print(query, company_name)
            user_context[request.json.get("call_id")].append("QUESTION: " + query)
            print(query)
            response = query_index(
                "\n\n".join(user_context[request.json.get("call_id")]),
                company_name=company_name,
            )
            user_context[request.json.get("call_id")][-1] += "\nANSWER: " + str(
                response
            )
            return str(response), 200

        except Exception as e:
            print(e)
            return "", 500


if __name__ == "__main__":
    app.run("0.0.0.0")
