import streamlit as st
import google.generativeai as genai
import dotenv
import os
from docx import Document
from io import BytesIO

# Load environment variables
dotenv.load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def analyze_audio_with_gemini(audio_file):
    # Configure generation parameters for consistency
    generation_config = genai.types.GenerationConfig(
        temperature=0.1,  # Low temperature for more consistent responses
        top_p=0.8,        # Reduce randomness in token selection
        top_k=20,         # Limit vocabulary choices
        max_output_tokens=4000,
        candidate_count=1
    )
    
    model = genai.GenerativeModel(
        "gemini-2.0-flash-lite",
        generation_config=generation_config
    )
    
    # Combined prompt for direct audio analysis
    analysis_prompt = """
CONFIGURATION

Manufacturer/Company: Naga
Sales Representative: Naga Foods salesperson

------------------------------------------------------------

CRITICAL INSTRUCTION - Brand Identification

1. Naga's OWN Products
- "Naga brand"
- "Our product" / "Our company's product"
- "Naga Foods product"
- If no brand is mentioned, assume it's Naga's

2. Competitor Brands – ALL other brand names mentioned, including:
- Nandi, Sankar, Shakti, Aachi, MTR, Britannia, etc.
- Online retailers like Amazon, Flipkart, etc.

IMPORTANT: DO NOT assume a product is Naga's unless explicitly stated!

------------------------------------------------------------

Brand & Product Mapping (Complete this FIRST)

Before analysis, categorize ALL brands and products mentioned in the conversation:

A. Naga Brand Products
- [List ONLY product names]

B. Competitor Brands Mentioned
- [List EACH competitor brand separately with details]

------------------------------------------------------------

STEP 2: Comprehensive Sales Analysis

Listen to this tamil audio conversation and provide analysis without transcribing first.

IMPORTANT: Start directly with the analysis content. Do not include introductory phrases.

------------------------------------------------------------

1. Conversation Summary
    - give a brief summary of the conversation (3-5 sentences)

------------------------------------------------------------

2. Sales Matrix

Naga Products Performance
- Naga products promoted: Which Naga products were pitched? Customer response?
- Volume pushed / upselling: Bulk orders or larger pack sizes attempted? Quantities?
- Schemes offered: Naga schemes, discounts, free-piece offers mentioned?
- Cross-selling within Naga portfolio: Were multiple Naga products bundled?
- Acceptance/Rejection: Which Naga products did customer accept or reject?

Sales Barriers
- Objections raised: What prevented Naga sales?
- Competitor advantages cited: What specific advantages did competitors have?

------------------------------------------------------------

3. Competitive Intelligence & Customer Psychology

A. Competitor Brand Analysis
For EACH competitor brand mentioned, document separately:

**Brand 1:**
- Brand Name: [e.g., Shakti, Nandi, etc.]
- Products: Which product categories?
- Customer's Current Status: Does customer stock it? How much?
- Reasons for Preference: Why does customer prefer this brand in detail?

**Brand 2:**
- Brand Name: [Next competitor brand]
- Products: Which product categories?
- Customer's Current Status: Does customer stock it? How much?
- Reasons for Preference: Why does customer prefer this brand in detail?

**Brand 3:** (Continue for each additional competitor brand mentioned)
- Brand Name: [Next competitor brand]
- Products: Which product categories?
- Customer's Current Status: Does customer stock it? How much?
- Reasons for Preference: Why does customer prefer this brand in detail?

B. Customer Buying Psychology
- What truly drives purchase decisions? (rank by importance)
- Is it price, brand recognition, customer demand, margins, or something else?
- Customer's risk tolerance (willing to try new brands?)
- Stock rotation preferences (fast-moving vs slow-moving)

------------------------------------------------------------

4. Salesperson Effectiveness Score: _/10

Based on specific criteria - Score each component objectively:

**Product promotion (30% weight):** _/10
- 8-10: Presented 5+ Naga products with clear benefits and schemes
- 6-7: Presented 3-4 Naga products adequately  
- 4-5: Presented 1-2 Naga products with limited detail
- 1-3: Minimal product presentation

**Scheme leverage (20% weight):** _/10
- 8-10: Actively promoted multiple schemes and free offers
- 6-7: Mentioned some schemes but didn't emphasize strongly
- 4-5: Basic mention of schemes without detail
- 1-3: No schemes mentioned or poorly explained

**Competitor handling (25% weight):** _/10
- 8-10: Directly addressed competitor advantages with counter-arguments
- 6-7: Acknowledged competitors but weak counter-positioning
- 4-5: Mentioned competitors but didn't address customer concerns
- 1-3: Failed to address competitive threats

**Customer psychology understanding (25% weight):** _/10
- 8-10: Clearly understood customer's priorities and adapted pitch accordingly
- 6-7: Showed some understanding of customer needs
- 4-5: Basic awareness of customer concerns
- 1-3: Poor understanding of what drives customer decisions

**Final Score Calculation:**
(Product promotion × 0.3) + (Scheme leverage × 0.2) + (Competitor handling × 0.25) + (Customer psychology × 0.25) = _/10

------------------------------------------------------------

5. Salesperson Strengths
- [Strength 1]
- [Strength 2]
- [Strength 3]

------------------------------------------------------------

6. Areas for Improvement
- [Improvement 1]
- [Improvement 2]
- [Improvement 3]

------------------------------------------------------------

7. Strategic Recommendations

A. Competitor Counter-Strategies
- How to compete with [Specific Competitor Brand]?
- What unique value propositions can Naga offer?
- Should Naga adjust pricing, schemes, or positioning?

B. Customer-Specific Action Plan
- What are this customer's top 3 priorities?
- Which Naga products align best with their needs?
- Recommended approach for next visit?

C. Objection Handling Playbook
For each major objection raised, provide separately:

**Objection 1:**
- Objection: [What customer said]
- Root cause: [Why they feel this way]
- Recommended response: [How to counter effectively]
- Long-term solution: [Systemic fix from Naga's side]

**Objection 2:**
- Objection: [What customer said]
- Root cause: [Why they feel this way]
- Recommended response: [How to counter effectively]
- Long-term solution: [Systemic fix from Naga's side]

**Objection 3:** (Continue for each additional objection)
- Objection: [What customer said]
- Root cause: [Why they feel this way]
- Recommended response: [How to counter effectively]
- Long-term solution: [Systemic fix from Naga's side]

------------------------------------------------------------

ANALYSIS RULES

✓ Extract ALL numeric data (quantities, prices, pack sizes, margins, discounts)
✓ Clearly separate Naga products from ALL competitor brands
✓ Note EVERY competitor brand name mentioned - don't group them generically
✓ Capture the customer's REAL reasons for preferences (not just what they say on surface)
✓ Identify psychological factors beyond price (brand loyalty, habit, risk aversion, etc.)
✓ Highlight cases where customer prefers competitor DESPITE Naga advantages
✓ Document local/regional brand dynamics and home-ground advantages
✓ Assess whether salesperson understood the customer's true concerns
✓ Provide actionable, specific recommendations - not generic advice
✓ Use a dynamic matrix - only include categories relevant to THIS conversation
✓ Analyze audio directly without transcribing first

------------------------------------------------------------

CONSISTENCY REQUIREMENTS

For SCORING: Use the exact scoring rubric provided. Base scores on objective evidence from the conversation, not subjective impressions.

For ANALYSIS: Focus on factual observations. Use specific quotes and examples from the conversation rather than generalizations.

For RECOMMENDATIONS: Base suggestions on specific gaps identified in the conversation, not generic sales advice.

------------------------------------------------------------

CRITICAL REMINDERS

- DO NOT assume any brand is Naga unless explicitly stated
- DO NOT group competitors as "other brands" – name each specifically
- DO capture both stated reasons AND underlying psychology
- DO identify non-price factors driving brand preference
- DO note when customer prefers competitor despite Naga being cheaper/better
"""
    
    response = model.generate_content([
        analysis_prompt,
        {"mime_type": "audio/mp3", "data": audio_file}
    ])
    
    return response.text

# Streamlit app
def main():
    st.set_page_config(
        page_title="Sales Call Analyzer",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("Sales Call Analysis Tool")
    st.markdown("Upload an audio file of a sales conversation to get detailed analysis.")
    
    # Sidebar for instructions
    with st.sidebar:
        st.header("Instructions")
        st.markdown("""
        1. Upload an audio file (MP3, WAV, MP4, etc.)
        2. Click 'Analyze Audio' to process
        
        **Supported formats:**
        - MP3, WAV, MP4, M4A, OGG
        """)
        
        if st.button("Clear Analysis"):
            if 'analysis_result' in st.session_state:
                del st.session_state['analysis_result']
            st.rerun()
    
    # Main content area
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.header("📁 Upload Audio")
        
        # Audio file uploader
        uploaded_file = st.file_uploader(
            "Choose an audio file",
            type=['mp3', 'wav', 'mp4', 'm4a', 'ogg'],
            help="Upload your sales conversation audio file"
        )
        
        if uploaded_file is not None:
            st.success(f"✅ File uploaded: {uploaded_file.name}")
            
            # Audio player
            st.audio(uploaded_file)
            
            # Analyze button
            if st.button("🚀 Analyze Audio", type="primary"):
                with st.spinner("🔄 Analyzing audio with Gemini AI..."):
                    try:
                        # Read the uploaded file
                        audio_data = uploaded_file.read()
                        
                        # Analyze with Gemini
                        analysis = analyze_audio_with_gemini(audio_data)
                        
                        # Store in session state
                        st.session_state['analysis_result'] = analysis
                        
                        st.success("✅ Analysis completed!")
                        
                    except Exception as e:
                        st.error(f"❌ Error analyzing audio: {str(e)}")
    
    with col2:
        st.header("📊 Analysis Results")
        
        if 'analysis_result' in st.session_state:
            # Display analysis in a nice format
            st.markdown("### 📈 Sales Performance Analysis")
            
            # Create tabs for better organization
            tab1, tab2 = st.tabs(["📋 Full Report", "💾 Export"])
            
            with tab1:
                # Display the analysis with proper formatting
                analysis_text = st.session_state['analysis_result']
                st.markdown(analysis_text)
            
            with tab2:
                # # Download button for the analysis as text
                # st.download_button(
                #     label="📄 Download Analysis Report (TXT)",
                #     data=st.session_state['analysis_result'],
                #     file_name="sales_analysis_report.txt",
                #     mime="text/plain"
                # )
                
                # Download button for the analysis as Word document
                analysis_text = st.session_state['analysis_result']
                
                # Create Word document
                doc = Document()
                doc.add_heading('Sales Performance Analysis Report', 0)
                
                # Process content to handle markdown formatting
                def process_line_to_word(doc, line):
                    line = line.strip()
                    if not line:
                        return
                    
                    # Check if it's a heading (starts with #)
                    if line.startswith('#'):
                        # Count the number of # to determine heading level
                        heading_level = 0
                        for char in line:
                            if char == '#':
                                heading_level += 1
                            else:
                                break
                        
                        # Remove the # symbols and add as heading
                        heading_text = line.lstrip('#').strip()
                        if heading_text:
                            doc.add_heading(heading_text, min(heading_level, 9))
                    else:
                        # Handle regular paragraphs with bold formatting
                        paragraph = doc.add_paragraph()
                        
                        # Split text by ** to handle bold formatting
                        parts = line.split('**')
                        
                        for i, part in enumerate(parts):
                            if part:  # Only add non-empty parts
                                if i % 2 == 0:  # Even index = normal text
                                    paragraph.add_run(part)
                                else:  # Odd index = bold text
                                    paragraph.add_run(part).bold = True
                
                # Add content to document
                for line in analysis_text.split('\n'):
                    process_line_to_word(doc, line)
                
                # Save to BytesIO
                doc_buffer = BytesIO()
                doc.save(doc_buffer)
                doc_buffer.seek(0)
                
                st.download_button(
                    label="📄 Download Analysis Report (Word)",
                    data=doc_buffer.getvalue(),
                    file_name="sales_analysis_report.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
        
        else:
            st.info("👆 Upload an audio file and click 'Analyze Audio' to see results here.")

if __name__ == "__main__":
    main()