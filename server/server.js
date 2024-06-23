const PORT = 8080;

import express from "express";
import cors from "cors";
var app = express();
import expressWs from "express-ws";
import bodyParser from "body-parser";
import Speech from "lmnt-node";
import VoiceResponse from "twilio/lib/twiml/VoiceResponse.js";
import { v4 as uuidv4 } from "uuid";
import fs, { writeFileSync } from "fs";
import { createClient, LiveTranscriptionEvents } from "@deepgram/sdk";
import twilio from 'twilio';

// globals
const client = twilio(process.env.TWILIO_ACCOUNT_SID, process.env.TWILIO_API_KEY);
const deepgramClient = createClient(process.env.DEEPGRAM_API_KEY);
var transcript;
var callSid;
var done;
var totalBytes = Buffer.alloc(0)
var companyName;
var welcomMessageDict = {}

// allow websockets
const a = expressWs(app);

// use
app.use(cors());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.static("public"));

// debug purposes
app.get("/dev", (req, res) => {
  return res.json({"result":"hello"});
});

app.post("/deploy", async (req, res) => {
  companyName = req.body["company_name"];
  console.log("received deploy request for ", companyName);
  if (welcomMessageDict[companyName] === undefined) {
    // synthesize welcome message
    const speech = new Speech(process.env.LMNT_API_KEY);
    const text = "Hello, I'm a virtual assistant representing " + companyName + ". How can I help you today?";
    console.log(text);
    var output = await speech.synthesize(text, "lily", {
      format: "wav",
      sample_rate: 8000,
    });

    const filename = uuidv4() + ".wav";
    fs.writeFileSync("./public/" + filename, output.audio);

    welcomMessageDict[companyName] = filename
  }
  return res.status(200).send({});
})

// initialize workflow
app.post("/start", (req, res) => {
  var r = new VoiceResponse();
  r.play(welcomMessageDict[companyName]);
  r.redirect("/listen");
  res.send(r.toString());
})

app.post("/listen", (req, res) => {
  var r = new VoiceResponse();
  const start = r.start();
  start.stream({
    url: `wss://${process.env.NGROK_URL}/`,
  });
  r.pause({ length: 120 })  // hardcoded constant;

  transcript = "";
  done = false;

  // send response
  res.send(r.toString());
});

app.post("/respond", async (req, res) => {
  const speechResult = transcript;
  var r = new VoiceResponse();

  const speech = new Speech(process.env.LMNT_API_KEY);
  const text = await fetch(process.env.FLASK_URL + "/api/customerify/query", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      query: speechResult,
      call_id: callSid,
    }),
  })
  console.log("received text: " + text);
  var output = await speech.synthesize(text, "lily", {
    format: "wav",
    sample_rate: 8000,
  });

  const filename = uuidv4() + ".wav";
  fs.writeFileSync("./public/" + filename, output.audio);

  r.play(filename);
  r.redirect("/lsten");

  res.send(r.toString());
});

app.ws("/", function (ws, req) {
  console.log("ws: client connected");
  const deepgram = deepgramClient.listen.live({
    smart_format: true,
    model: "nova-2",
    encoding:"mulaw",
    sample_rate:8000,
    channels: 1,
  });
  ws.on("message", (message) => {
    message = JSON.parse(message);
    if (message['event'] === "start") {
      callSid = message['start']['callSid'];
    }
  })

  deepgram.addListener(LiveTranscriptionEvents.Open, async () => {
    console.log("deepgram: connected");

    deepgram.addListener(LiveTranscriptionEvents.Transcript, async (data) => {
      console.log("deepgram: transcript received");
      const tempTranscript = data.channel.alternatives[0].transcript;
      console.log("Transcript: " + data.channel.alternatives[0].transcript);
      if (tempTranscript === ""){
        console.log("empty transcript, stopping with final transcript: " + transcript);
        if (!done) {
          done = true;
          const msg = `<?xml version="1.0" encoding="UTF-8"?><Response><Stop><Stream/></Stop><Redirect>https://${process.env.NGROK_URL}/respond</Redirect></Response>`;
          await client.calls(callSid).update({
            twiml: msg
          })
        }
        deepgram.finish();
      }
      else{
        transcript += " " +  tempTranscript;
      }
    });

    deepgram.addListener(LiveTranscriptionEvents.Close, async () => {
      console.log("deepgram: disconnected");
    });

    deepgram.addListener(LiveTranscriptionEvents.Error, async (error) => {
      console.log("deepgram: error received");
      console.error(error);
    });

    deepgram.addListener(LiveTranscriptionEvents.Warning, async (warning) => {
      console.log("deepgram: warning received");
      console.warn(warning);
    });

    ws.on("message", (message) => {
      message = JSON.parse(message);
      if (message['event'] === "media"){
        totalBytes = Buffer.concat([totalBytes, Buffer.from(message["media"]["payload"], "base64")]);
        deepgram.send(Buffer.from(message["media"]["payload"], "base64"));
      }
    });
    ws.on("close", () => {
      console.log("ws: client disconnected");
      writeFileSync("totalBytes.txt", totalBytes);
    });
  });
});

app.listen(PORT);
