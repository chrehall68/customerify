const PORT = 8080;

import express from "express";
import cors from "cors";
var app = express();
import expressWs from "express-ws";
import bodyParser from "body-parser";
import Speech from "lmnt-node";
import VoiceResponse from "twilio/lib/twiml/VoiceResponse.js";
import { v4 as uuidv4 } from "uuid";
import fs from 'fs'

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
  r.gather({ input: "speech", action: "/respond", speechTimeout: 1 });
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

  const speech = new Speech("590a1049fa244ae8aa8c4a4db9ee9659");
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
  fs.writeFileSync("./public/" + filename, output.audio, (err) => {
    if (err) throw err;
    console.log("The file has been saved!");
  });

  r.play(filename);
  r.redirect("/answer");

  res.send(r.toString());
});

app.ws("/", function (ws, req) {
  ws.on("message", function (msg) {
    console.log(msg);
  });
  console.log("socket", req.testing);
});

app.listen(PORT);
