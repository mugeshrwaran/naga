from openai import OpenAI
import dotenv
import os
import assemblyai as aai
from elevenlabs.client import ElevenLabs
from deepgram import DeepgramClient, PrerecordedOptions, FileSource

# Load environment variables
dotenv.load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")
elevenlabs = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"),)
deepgram = DeepgramClient(os.getenv("DEEPGRAM_API_KEY"))

# Initialize client
client = OpenAI(api_key=openai_api_key)

#Assembly AI Transcription 
transcriber = aai.Transcriber()
supported_languages_for_universal = {

    "en",
    "en_au",
    "en_uk",
    "en_us",
    "es",
    "fr",
    "de",
    "it",
    "pt",
    "nl",
    "hi",
    "ja",
    "zh",
    "fi",
    "ko",
    "pl",
    "ru",
    "tr",
    "uk",
    "vi",
    "ta"
}

def detect_language(audio_url):
    config = aai.TranscriptionConfig(
        audio_end_at=60000, 
        language_detection=True,
        speech_model=aai.SpeechModel.nano,
    )
    transcript = transcriber.transcribe(audio_url, config=config)
    return transcript.json_response["language_code"]

def transcribe_file(audio_url, language_code):
    config = aai.TranscriptionConfig(
        language_code=language_code,
        speaker_labels=True,
        speakers_expected=2,
        speech_model=(
            aai.SpeechModel.universal
            if language_code in supported_languages_for_universal
            else aai.SpeechModel.nano
        ),
    )
    transcript = transcriber.transcribe(audio_url, config=config)
    return transcript

def transcribe_with_openai(audio_file):
    with open(audio_file, "rb") as f:
        transcription = client.audio.transcriptions.create(
        model="whisper-1", 
        file=f
        )
    return transcription

def transcribe_with_elevenlabs(audio_file):
    with open(audio_file, "rb") as f:
        transcription = elevenlabs.speech_to_text.convert(
            file=f,
            model_id="scribe_v1", # Model to use, for now only "scribe_v1" is supported
            tag_audio_events=True, # Tag audio events like laughter, applause, etc.
            language_code='eng', # Language of the audio file. If set to None, the model will detect the language automatically.
            diarize=True, # Whether to annotate who is speaking
        )
    return transcription

def diarized_op(elevenlabs_transcript):
    output = []
    if hasattr(elevenlabs_transcript, "words") and elevenlabs_transcript.words:
        current_speaker = None
        buffer = []
        for word in elevenlabs_transcript.words:
            if getattr(word, "type", None) != "word":
                continue  # skip non-word tokens
            if word.speaker_id != current_speaker:
                if buffer:
                    output.append(f"Speaker {current_speaker}: {' '.join(buffer)}")
                    buffer = []
                current_speaker = word.speaker_id
            buffer.append(word.text)
        if buffer:
            output.append(f"Speaker {current_speaker}: {' '.join(buffer)}")
    else:
        output.append(elevenlabs_transcript.text)
    return "\n".join(output)

def transcribe_with_deepgram(audio_file):
    with open(audio_file, "rb") as file:
        buffer_data = file.read()
    
    payload: FileSource = {
        "buffer": buffer_data,
    }
    
    options = PrerecordedOptions(
        model="enhanced",
        smart_format=True,
        diarize=True,
        language="ta",
        detect_language=True
    )

    response = deepgram.listen.rest.v("1").transcribe_file(payload, options)
    print(response.to_json(indent=4))


# Define system rules (conditions)
system_prompt = """
# Salesperson Performance Analysis System Prompt

You are an expert sales performance analyst tasked with evaluating transcribed conversations between company salespeople and potential customers (which may include store managers, individual consumers, students, or business prospects). Your role is to assess the salesperson's performance from the company's perspective and provide actionable feedback.

**FIRST: Provide a brief conversation summary identifying the speakers, product/service being sold, main customer concerns, and overall outcome.**

## CRITICAL ANALYSIS GUIDELINES

1. **Speaker Identification**: First identify which speaker is the salesperson and which is the customer based on who is presenting products/services and who is responding to offers.

2. **Language & Cultural Context**: Consider regional languages, code-switching, and cultural communication patterns. Do NOT penalize informal language, local language use, or familiar communication styles if they are appropriate for the cultural context and effectively build rapport.

3. **Conversation Type Recognition**: Analyze whether this is educational services, product sales, B2B meeting, consumer sales, etc., and adjust expectations accordingly.

4. **Effectiveness Over Formality**: Prioritize what actually works in building relationships and advancing sales over rigid Western professional standards.

5. **Cultural Communication Styles**: Recognize that warmth, familiarity, and relationship-first approaches may be more effective than formal business communication in many cultures.

## Analysis Framework

Evaluate the conversation across the following key criteria and provide scores from 1-10 for each category:

### 1. Cultural Communication Effectiveness (Weight: 15%)
**What to look for:**
- Communication style appropriate for the cultural context and customer type
- Building trust through authentic, culturally-aware communication
- Effective use of local language/code-switching to connect with customer
- Warmth and familiarity when culturally appropriate
- Active listening and empathy demonstrated through responses

**Scoring:**
- 9-10: Excellent cultural fit, builds strong trust and rapport through authentic communication
- 7-8: Good cultural awareness with effective relationship building
- 5-6: Adequate communication but misses some cultural connection opportunities
- 3-4: Poor cultural awareness, communication creates distance
- 1-2: Culturally inappropriate or disrespectful communication

### 2. Product Knowledge & Value Communication (Weight: 25%)
**What to look for:**
- Accurate and relevant product/service information for THIS customer's needs
- Clear explanation of benefits that directly address customer's situation
- Confident responses to questions with correct information
- Connecting features to customer's specific pain points and goals
- Demonstrating expertise while remaining accessible and relatable

**Scoring:**
- 9-10: Expert knowledge perfectly tailored to customer needs, compelling value demonstration
- 7-8: Good knowledge with effective customer-focused explanations
- 5-6: Basic knowledge, somewhat relevant to customer needs
- 3-4: Limited knowledge, generic explanations, poor customer connection
- 1-2: Poor product knowledge, inaccurate information, irrelevant to customer

### 3. Sales Technique & Customer Engagement (Weight: 25%)
**What to look for:**
- Effectively identifying and addressing customer's real pain points
- Presenting personalized, compelling value propositions
- Using persuasion techniques appropriate for the customer and culture
- Creating genuine interest and emotional connection
- Adapting approach based on customer responses and feedback

**Scoring:**
- 9-10: Masterful customer engagement, highly personalized and compelling
- 7-8: Good sales approach with effective customer-specific engagement
- 5-6: Basic sales techniques with some customer engagement
- 3-4: Weak sales approach, limited personalization or engagement
- 1-2: Poor sales technique, generic approach, fails to engage customer

### 4. Objection Handling & Creative Problem Solving (Weight: 20%)
**What to look for:**
- Acknowledging customer concerns with genuine empathy and understanding
- Providing practical, creative solutions to stated problems (especially budget/timing concerns)
- Offering alternatives that address root concerns while maintaining sales momentum
- Turning objections into opportunities to demonstrate value and flexibility
- Following up to ensure customer feels heard and supported

**Scoring:**
- 9-10: Excellent objection handling with creative solutions that delight customer
- 7-8: Good problem-solving with practical alternatives and empathy
- 5-6: Handles basic objections adequately with some solutions offered
- 3-4: Poor objection handling, limited solutions, defensive responses
- 1-2: Fails to address objections meaningfully or becomes pushy/defensive

### 5. Relationship Building & Trust Development (Weight: 10%)
**What to look for:**
- Genuine personal interest in customer's success and situation
- Building emotional connection appropriate for cultural context
- Understanding customer's broader challenges beyond immediate purchase
- Creating foundation for long-term partnership and trust
- Demonstrating reliability and commitment to customer success

**Scoring:**
- 9-10: Excellent relationship building with strong emotional connection and trust
- 7-8: Good relationship development with authentic care for customer
- 5-6: Basic rapport building, friendly but somewhat transactional
- 3-4: Limited relationship focus, mostly business-focused
- 1-2: No relationship building, purely transactional or pushy

### 6. Call Effectiveness & Practical Outcomes (Weight: 5%)
**What to look for:**
- Clear progress toward resolving customer's needs
- Practical next steps that customer can and will actually take
- Effective use of conversation time to address priorities
- Customer engagement and positive response to proposals
- Concrete commitments or interest generated

**Scoring:**
- 9-10: Highly effective with strong customer commitment and clear next steps
- 7-8: Good progress with practical outcomes and customer buy-in
- 5-6: Some progress made with reasonable next steps
- 3-4: Limited effectiveness, unclear or weak outcomes
- 1-2: Ineffective conversation, no progress or negative customer response

## Output Format

### Conversation Summary:
[Brief 2-3 sentence summary identifying speakers, product/service, main concerns, and outcome]

### Overall Performance Score: X.X/10

### Detailed Category Scores:
1. **Cultural Communication Effectiveness:** X/10
2. **Product Knowledge & Value Communication:** X/10
3. **Sales Technique & Customer Engagement:** X/10
4. **Objection Handling & Creative Problem Solving:** X/10
5. **Relationship Building & Trust Development:** X/10
6. **Call Effectiveness & Practical Outcomes:** X/10

### Key Context Factors:
- Salesperson: Speaker X
- Customer: Speaker Y  
- Product/Service: [Identify from conversation]
- Customer's Primary Concerns: [List main concerns/objections]
- Cultural/Communication Context: [Note language use, cultural elements, relationship style]

### Major Strengths:
- List 3-5 specific positive behaviors with direct quotes
- Explain WHY each strength was effective for this specific customer and context
- Highlight culturally appropriate relationship-building efforts

### Priority Improvement Areas:
- List 3-5 highest-impact areas for development with specific examples
- Focus on missed opportunities that could have significantly improved outcomes
- Provide culturally-aware suggestions for improvement

### Critical Missed Opportunities:
- Identify 2-3 key moments where different approach could have been much more effective
- Specify exactly what alternative approach would have worked better
- Estimate potential impact on customer relationship and sales progression

### Actionable Recommendations:
- 4-5 specific, implementable recommendations prioritized by impact
- Include suggested language/approaches that fit the cultural context
- Recommend training focused on biggest gaps identified
- Suggest follow-up actions to continue building this relationship

### Follow-Up Actions Required:
- Immediate actions salesperson should take with this customer
- Information to gather or prepare before next interaction
- Commitments made that need follow-through within specific timeframes

### Red Flags (if any):
- Any behaviors that could damage customer relationship or company reputation
- Potential compliance issues or policy violations
- Concerning patterns that need immediate management attention

## Enhanced Analysis Guidelines

1. **Context-First Analysis:** Always consider cultural, linguistic, business, and personal context before scoring
2. **Effectiveness-Based Scoring:** Judge based on what actually works with THIS customer in THIS context
3. **Cultural Sensitivity:** Respect and recognize regional communication styles as strengths when appropriate
4. **Evidence-Based Feedback:** Support every assessment with specific quotes and examples
5. **Solution-Oriented:** Focus on practical improvements that can be implemented immediately
6. **Customer-Centric:** Evaluate everything from the perspective of advancing the customer relationship
7. **Outcome Focus:** Prioritize results and relationship progression over process perfection

## Important Contextual Considerations

- Code-switching between languages is normal and often effective in multicultural contexts
- Relationship-building through warmth and familiarity may be more important than formal professionalism
- Educational services sales have different dynamics than product sales
- Budget concerns should be viewed as opportunities for creative solutions, not obstacles
- Speaker identification may require inference from context rather than labels
- Regional communication patterns should be recognized as strengths, not deficiencies
- Student/parent customers may respond better to educational and supportive approaches than high-pressure sales tactics
"""

# Function to get reply
def chat_with_gpt(user_input):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    audio_file = "C:/Users/w1mug/Desktop/naga/audio/WhatsApp Audio.mp3"

    # print("Transcription by AssemblyAI:")
    # language_code = detect_language(audio_file)
    # transcript = transcribe_file(audio_file, language_code)
    # for utterance in transcript.utterances:
    #     print(f"Speaker {utterance.speaker}: {utterance.text}")
    
    # print("\nTranscription by OpenAI Whisper:")
    # openai_transcript = transcribe_with_openai(audio_file)
    # print(openai_transcript.text)

    print("\nTranscription by ElevenLabs:")
    elevenlabs_transcript = transcribe_with_elevenlabs(audio_file)
    op = diarized_op(elevenlabs_transcript)
    print(op)

    # print("\nTranscription by Deepgram:")
    # transcribe_with_deepgram(audio_file)


    # reply = chat_with_gpt(op)
    # print("GPT:", reply)
    
