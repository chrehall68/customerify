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


const deepgramClient = createClient(process.env.DEEPGRAM_API_KEY);
var totalBytes = Buffer.alloc(0)

const a = expressWs(app);

app.use(cors());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.static("public"));

app.use(function (req, res, next) {
  console.log("middleware");
  req.testing = "testing";
  return next();
});

app.get("/dev", (req, res) => {
  console.log("get route", req.testing);
  res.end();
});

app.post("/answer", (req, res) => {
  console.log("post route", req.testing);
  var r = new VoiceResponse();
  r.say("Please say something");
  const start = r.start();
  start.stream({
    name: "testStream",
    url: "wss://116c-2607-f140-6000-8006-593f-a7d5-8b98-a55e.ngrok-free.app/",
  });
  r.pause({ length: 2 });
  res.send(r.toString());
});

app.post("/respond", async (req, res) => {
  console.log("post route", req.testing);
  var f = req.body;
  //console.log(f);
  // now take SpeechResult and Confidence
  const speechResult = f.SpeechResult;
  const confidence = f.Confidence;
  var r = new VoiceResponse();

  const speech = new Speech(process.env.LMNT_API_KEY);
  const text =
    "Alright, I'm " +
    parseInt("" + confidence * 100) +
    "% sure that you said: " +
    speechResult;
  console.log(text);
  var output = await speech.synthesize(text, "lily", {
    format: "wav",
    sample_rate: 8000,
  });
  console.log("finished await");

  const filename = uuidv4() + ".wav";
  fs.writeFileSync("./public/" + filename, output.audio);

  r.play(filename);
  r.redirect("/answer");

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

  deepgram.addListener(LiveTranscriptionEvents.Open, async () => {
    console.log("deepgram: connected");

    deepgram.addListener(LiveTranscriptionEvents.Transcript, (data) => {
      console.log("deepgram: transcript received");
      console.log("ws: transcript sent to client");
      console.log(JSON.stringify(data));
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

    deepgram.addListener(LiveTranscriptionEvents.Metadata, (data) => {
      console.log("deepgram: metadata received");
      console.log("ws: metadata sent to client");
      console.log(JSON.stringify({ metadata: data }));
    });

    ws.on("message", (message) => {
      message = JSON.parse(message);
      console.log("ws: client data received");
      if (message['event'] === "media"){
        console.log("ws: data sent to deepgram");
        totalBytes = Buffer.concat([totalBytes, Buffer.from(message["media"]["payload"], "base64")]);
        deepgram.send(Buffer.from(message["media"]["payload"], "base64"));
      }
    });
    ws.on("close", () => {
      console.log("ws: client disconnected");
      //deepgram.finish();
      //console.log("finished removing listeners");
      writeFileSync("totalBytes.txt", totalBytes);
    });
  });
});

app.listen(PORT);
