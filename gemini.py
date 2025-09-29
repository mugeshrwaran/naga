import asyncio
import pyaudio
from google.genai import live, types
from google import genai
import os
import dotenv
dotenv.load_dotenv()


# Ensure your API key is set as an environment variable (e.g., GEMINI_API_KEY)
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
# or pass it directly to the client.

async def main():
    # Audio configuration for the microphone
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000 # 16kHz
    CHUNK = 1024 # Buffer size

    p = pyaudio.PyAudio()

    # Open a microphone stream
    input_stream = p.open(format=FORMAT,
                          channels=CHANNELS,
                          rate=RATE,
                          input=True,
                          frames_per_buffer=CHUNK)

    # Gemini Live API configuration
    live_config = types.LiveConnectConfig(
        response_modalities=[
            types.Modality.TEXT
            # types.Modality.AUDIO
        ],
        input_audio_transcription={})
    
    # You need to use a model that supports live interaction
    model_id = "gemini-live-2.5-flash"

    print("Connecting to Gemini Live API...")
    async with client.aio.live.connect(model=model_id, config=live_config) as session:
        print("Connected. Start speaking...")
        
        # Send initial setup instructions
        await session.send_client_content(
            turns=types.Content(role="user", parts=[types.Part(text="Transcribe the following audio.")])
        )

        async def audio_producer():
            """Continuously captures audio and sends it to the session."""
            try:
                while True:
                    audio_chunk = input_stream.read(CHUNK)
                    await session.send_realtime_input(
                        audio=types.Blob(
                            data=audio_chunk,
                            mime_type=f"audio/pcm;rate={RATE}"
                        )
                    )
                    await asyncio.sleep(0.01) # Small delay to avoid overloading
            except asyncio.CancelledError:
                pass

        async def transcription_consumer():
            """Receives responses and prints transcriptions."""
            async for message in session.receive():
                # Check for input transcription from the server
                if message.server_content and hasattr(message.server_content, "input_transcription"):
                    transcription = message.server_content.input_transcription
                    if transcription and transcription.text:
                        print(f"Transcription: {transcription.text}")

        producer_task = asyncio.create_task(audio_producer())
        consumer_task = asyncio.create_task(transcription_consumer())

        # Let it run for a bit, or add logic to handle interruption/ending
        await asyncio.sleep(60) # Runs for 60 seconds
        
        producer_task.cancel()
        consumer_task.cancel()

    input_stream.stop_stream()
    input_stream.close()
    p.terminate()

if __name__ == "__main__":
    asyncio.run(main())