# Customerify

A simple factory for customer service agents. Open up our application, specify your data sources (we take online websites documents)

Then, select a phone number to deploy your agent with. Once done, customers can simply call that phone number and get answers
to their questions from our fast, lifelike customer service agents.

## Built with

- Express JS - for our Twilio / Websocket endpoints
- Flask - for our Agent response api
- Streamlit - for our frontend
- Twilio - Voice call integrations
- Deepgram - STT
- Groq - LLM provider
- LMNT - TTS
- OpenAI - embeddings
- PineCone - Vector DB

## Running our application:

To run our application, you need to have [ngrok](https://ngrok.com/download) installed. You will also need Twilio, LMNT, Deepgram, OpenAI, PineCone, and Groq accounts.

First, run

```sh
ngrok https 8080
```

to start the ngrok server (handles forwarding to your machine). Next, go to your Twilio console and set
the webhook url as `https://<NGROK_URL_WITHOUT_HTTPS>/start`. Make sure to replace `<NGROK_URL_WITHOUT_HTTPS>`
with the url that ngrok is forwarding to your machine.

Next, run the below script to get all the components up and running

```sh
# api keys
export DEEPGRAM_API_KEY=<your_deepgram_api_key>
export TWILIO_API_KEY=<your_twilio_api_key>
export TWILIO_ACCOUNT_SID=<your_twilio_accound_sid>
export GROQ_API_KEY=<your_groq_api_key>
export PINECONE_API_KEY=<your_pinecone_api_key>
export LMNT_API_KEY=<your_lmnt_api_key>
export OPENAI_API_KEY=<your_openai>api_key>

export FLASK_URL=http://localhost:5000
export NGROK_URL=<ngrok_url_without_https://>
export PHONE_NUMBER="123 456 7890"  # currently, we mandate that the Twilio user provide the phone number they set up
cd server
npm i
npm start &
cd ..
cd ./flask-backent
flask --app api.py run &
cd ..
streamlit run ui.py
```

Finally, open up the UI and configure your agent. Press deploy and call your agent to see the results!
