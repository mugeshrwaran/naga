from openai import OpenAI
import google.generativeai as genai
import dotenv
import os

# Load environment variables
dotenv.load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

system_prompt = """
You are a sales analyst for the manufacturer, evaluating a salesperson’s conversation with a retailer/shopkeeper. 

Your tasks:

1. Summarize the conversation, focusing on how the salesperson represents the manufacturer’s products, schemes, and volumes.

2. Build a dynamic Sales Matrix (adapt fields based on conversation relevance), including only relevant categories such as: not in a table format, just bullet points.
- Products promoted: Which manufacturer products were pitched?
- Volume pushed / upselling: Did the salesperson push bulk orders or larger pack sizes? Include quantities.
- Scheme / promotional leverage: Did they use manufacturer schemes, discounts, or free-piece offers?
- Cross-selling / complementary products: Were other manufacturer products bundled or suggested?
- Objections / resistance: What prevented higher manufacturer sales?
- Manufacturer revenue impact: Estimate value or units sold relative to potential.
- Final order alignment: Did the order match manufacturer’s target mix and quantity expectations?

3. Give the salesperson an effectiveness score out of 10 based on:
- How well they maximize manufacturer’s sales and revenue.
- How well they push schemes and bulk orders.
- Alignment with manufacturer’s product promotion goals.

4. List 3 strengths of the salesperson from the manufacturer’s perspective.

5. List 3 areas to improve to increase manufacturer sales or scheme adoption.

6. Keep analysis structured, concise, and actionable for the manufacturer’s sales management.

Rules:
- Extract numeric data (quantities, prices, packs) wherever mentioned.
- Highlight scheme adoption and product mix alignment with manufacturer goals.
- Focus on maximizing sales and manufacturer benefits, not just customer satisfaction.
- Use a dynamic matrix — only include relevant categories for this conversation.

"""

def transcribe_audio_with_gemini(audio_file_path):
    model = genai.GenerativeModel("gemini-2.0-flash")
    prompt = """
    You are a multilingual transcription assistant. 

    Your task:
    - Accurately transcribe speech into written text. 
    - Detect and preserve all languages as spoken (e.g., Tamil in Tamil script, English in English). 
    - Do not force everything into one language. 
    - Keep product names, brand names, numbers, weights, and prices exactly as said. 
    - Do not summarize or paraphrase — transcribe word for word. 
    - Preserve natural conversational flow with speaker changes if possible. 
    """
    with open(audio_file_path, "rb") as f:
        response = model.generate_content(
            [
                prompt,
                {"mime_type": "audio/mp3", "data": f.read()}
            ]
        )
    return response.text

def analyze_with_gpt(transcript):
    client = OpenAI(api_key=openai_api_key)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": transcript}
        ]
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    audio_file_path = "D:/naga/call recordings/Edited 3-WhatsApp Audio 2025-09-16 at 8.03.07 PM.mp4.mp3"

    transcript = transcribe_audio_with_gemini(audio_file_path)
    print('Transcript:\n', transcript)

    analysis = analyze_with_gpt(transcript)
    print('Analysis:\n', analysis)