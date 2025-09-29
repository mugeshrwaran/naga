import streamlit as st
import google.generativeai as genai
import dotenv
import os

# Load environment variables
dotenv.load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def analyze_audio_with_gemini(audio_file):
    model = genai.GenerativeModel("gemini-2.0-flash")
    
    # Combined prompt for direct audio analysis
    analysis_prompt = """
    You are a sales analyst for the manufacturer, evaluating a salesperson's audio conversation with a retailer/shopkeeper.

    Listen to this audio conversation and provide a comprehensive analysis without needing to transcribe it first.

    IMPORTANT: Start directly with the analysis content. Do not include any introductory phrases.

    Your tasks:

    1. Summarize the conversation, focusing on how the salesperson represents the manufacturer's products, schemes, and volumes.

    2. Build a dynamic Sales Matrix (adapt fields based on conversation relevance), including only relevant categories such as: not in a table format, just bullet points.
    - Products promoted: Which manufacturer products were pitched?
    - Volume pushed / upselling: Did the salesperson push bulk orders or larger pack sizes? Include quantities.
    - Scheme / promotional leverage: Did they use manufacturer schemes, discounts, or free-piece offers?
    - Cross-selling / complementary products: Were other manufacturer products bundled or suggested?
    - Objections / resistance: What prevented higher manufacturer sales?

    3. Give the salesperson an effectiveness score out of 10 based on:
    - How well they maximize manufacturer's sales and revenue.
    - How well they push schemes and bulk orders.
    - Alignment with manufacturer's product promotion goals.

    4. List 3 strengths of the salesperson from the manufacturer's perspective.

    5. List 3 areas to improve to increase manufacturer sales or scheme adoption.

    6. Keep analysis structured, concise, and actionable for the manufacturer's sales management.

    Rules:
    - Extract numeric data (quantities, prices, packs) wherever mentioned in the audio.
    - Highlight scheme adoption and product mix alignment with manufacturer goals.
    - Focus on maximizing sales and manufacturer benefits, not just customer satisfaction.
    - Use a dynamic matrix — only include relevant categories for this conversation.
    - Analyze the audio directly without providing a transcript first.
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
                # Download button for the analysis
                st.download_button(
                    label="📄 Download Analysis Report",
                    data=st.session_state['analysis_result'],
                    file_name="sales_analysis_report.txt",
                    mime="text/plain"
                )
        
        else:
            st.info("👆 Upload an audio file and click 'Analyze Audio' to see results here.")

if __name__ == "__main__":
    main()