import markdownify
import requests
from openai import OpenAI
import os

req = requests.get("https://rev.ai/pricing")
md = markdownify.markdownify(req.content)

open("output.md", "w").write(md)
client = OpenAI(
    api_key=os.environ["GROQ_API_KEY"], base_url="https://api.groq.com/openai/v1"
)

completion = client.chat.completions.create(
    model="llama3-70b-8192",
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant who tries to answer user questions factually. You are given the following document(s) to answer questions from. If an answer cannot be inferred from the text, say that.\n\nText:\n\n"
            + md,
        },
        {"role": "user", "content": "What is the pricing like for Rev.ai?"},
    ],
)
print(completion.choices[0].message.content)
open("output.txt", "w").write(completion.choices[0].message.content)
