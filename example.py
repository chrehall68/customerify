"""
Usage:

export GROQ_API_KEY=<groq_api_key>
export LMNT_API_KEY=<lmnt_api_key>

python example.py
"""

import asyncio
from openai import AsyncOpenAI
import os
from lmnt.api import Speech


async def main():
    # first generate some text
    client = AsyncOpenAI(api_key=os.environ["GROQ_API_KEY"])
    transcription = await client.audio.transcriptions.create(
        model="whisper-3",
        file=open("example.wav", "rb"),  # TODO - replace with actual audio
    )
    text = transcription.text
    print("=== Transcribed text ===")
    print(text)
    completion = await client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": text}],
    )
    text_completion = completion.choices[0].message.content
    print("=== LLM response ===")
    print(text_completion)

    async with Speech(os.environ["LMNT_API_KEY"]) as speech:
        synthesis = await speech.synthesize(text_completion, voice="lily", format="wav")
        with open("output.wav", "wb") as f:
            f.write(synthesis["audio"])


asyncio.run(main())
