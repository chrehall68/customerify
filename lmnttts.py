from flask import Flask, request
import lmnt.api
import twilio.twiml.voice_response as vr
import lmnt
import os
import uuid

app = Flask(__name__)


@app.route("/answer", methods=["GET", "POST"])
async def answer_call():
    """Respond to incoming phone calls with a brief message."""
    # Start our TwiML response
    resp = vr.VoiceResponse()

    # Read a message aloud to the caller
    resp.say("Please say something.")
    resp.gather(input="speech", action="/respond", speech_timeout="auto")

    return str(resp)


@app.route("/respond", methods=["GET", "POST"])
async def reply():
    form = request.form
    print(form)
    speech_result = form.get("SpeechResult")
    confidence = form.get("Confidence")
    print(speech_result)
    print(confidence)

    resp = vr.VoiceResponse()
    synth = await lmnt.api.Speech(os.environ["LMNT_API_KEY"]).synthesize(
        f"Alright, I'm {float(confidence)*100:.0f}% sure that you said: {speech_result}",
        voice="lily",
        format="wav",
        sample_rate=8000,
    )
    fname = f"output{uuid.uuid4()}.wav"
    open(f"./static/{fname}", "wb").write(synth["audio"])
    resp.play(f"/static/{fname}")
    resp.redirect("/answer")

    return str(resp)


if __name__ == "__main__":
    app.run(debug=True, port=8080)
