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

## Running Twilio server:

To run the Twilio server, you need to have [ngrok](https://ngrok.com/download) installed. You will also need Twilio, LMNT, and Deepgram accounts.

First, run

```sh
ngrok https 8080
```

to start our ngrok server (handles forwarding to our machine)

Next, run

```sh
export TWILIO_ACCOUNT_SID=<your_twilio_account_id>
export TWILIO_API_KEY=<your_twilio_api_key>
export LMNT_API_KEY=<your_lmnt_api_key>
export DEEPGRAM_API_KEY=<your_deepgram_api_key>
export NGROK_URL=<ngrok_url_without_the_https://>
cd server
npm i
npm start
```
