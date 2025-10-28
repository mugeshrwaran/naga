import streamlit as st
import google.generativeai as genai
import dotenv
import os
from docx import Document
from io import BytesIO
import pandas as pd
import plotly.express as px

# Load environment variables
dotenv.load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def analyze_audio_with_gemini(audio_file):
    # Configure generation parameters for consistency
    generation_config = genai.types.GenerationConfig(
        temperature=0.0,  # Low temperature for more consistent responses
        top_p=0.1,        # Reduce randomness in token selection
        top_k=1,         # Limit vocabulary choices
        max_output_tokens=4000,
        candidate_count=1
    )
    
    model = genai.GenerativeModel(
        "gemini-2.0-flash",
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
- [List of Products from Manufacturer, Schemes are not discussed]
- [List of Products from Manufacturer, where schemes are discussed]

B. Competitor Brands Mentioned
- [List EACH competitor brand separately with details]

------------------------------------------------------------

Comprehensive Sales Analysis

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
    [Give details of all the schemes mentioned with specifics like which product is offered with which scheme, discount %, which item is free for which scheme, etc.]
- Cross-selling within Naga portfolio: Were multiple Naga products bundled?
    [Give details of any cross-selling efforts]
- Acceptance/Rejection: Which Naga products did customer accept or reject?

Sales Barriers
- Objections raised: What prevented Naga sales?
- Competitor advantages cited: What specific advantages did competitors have?

------------------------------------------------------------
3. Customer Buying Patterns

A. Regularly buying products (Customer commits to buy BEFORE schemes are explained OR shows clear intent to buy regardless of schemes)
    - [List products where customer showed immediate interest or agreed to buy before any schemes/offers were mentioned]
    - [Also include products where customer clearly intended to buy but scheme was mentioned first - analyze if the purchase decision was truly influenced by the scheme or not]
    - [Note: These are products customer buys based on regular demand/habit/necessity]

B. Scheme Based Orders (Customer commits to buy ONLY BECAUSE schemes influenced their decision)
    - [List products where customer showed hesitation, said no initially, or was undecided BUT changed their mind specifically because of the scheme/offer]
    - [Include products where customer increased quantity due to schemes]
    - [Note: These purchases were clearly driven by the schemes/offers - customer behavior changed due to the incentive]

CRITICAL ANALYSIS REQUIRED - Look for these indicators:

**For Regular Buying:**
- Customer asks for the product immediately without hearing schemes
- Customer says "I need this" or "Give me [quantity]" before schemes are mentioned
- Customer shows clear intent to purchase regardless of offers
- Customer maintains same quantity even after hearing schemes

**For Scheme-Based Buying:**
- Customer initially hesitates or says "Let me think" but changes mind after scheme
- Customer says "No" first but then says "Okay" after hearing the offer
- Customer increases quantity specifically for the scheme (e.g., "Then give me 10kg instead of 5kg")
- Customer explicitly mentions the scheme as reason for buying (e.g., "Because of the free piece, I'll take it")
- Customer compares and decides based on the offer value

**IMPORTANT:** If customer was already planning to buy and scheme was just mentioned coincidentally, categorize as REGULAR buying, not scheme-based.
------------------------------------------------------------

4. Competitive Intelligence & Customer Psychology

A. Competitor Brand Analysis
For EACH competitor brand mentioned, document separately:

**Brand 1:**
- Brand Name: [e.g., Shakti, Nandi, etc.]
- Products: Which product categories?
- Customer's Current Status: Does customer stock it? How much?
- Reasons for Preference: Why does customer prefer this brand than Naga in detail?
    - [Price? Consumers Choice? Taste? Local brand? Habit? Promotions? etc..]

**Brand 2:**
- Brand Name: [Next competitor brand]
- Products: Which product categories?
- Customer's Current Status: Does customer stock it? How much?
- Reasons for Preference: Why does customer prefer this brand than Naga in detail?
    - [Price? Consumers Choice? Taste? Local brand? Habit? Promotions? etc..]

**Brand 3:** (Continue for each additional competitor brand mentioned until all are covered)
- Brand Name: [Next competitor brand]
- Products: Which product categories?
- Customer's Current Status: Does customer stock it? How much?
- Reasons for Preference: Why does customer prefer this brand than Naga in detail?
    - [Price? Consumers Choice? Taste? Local brand? Habit? Promotions? etc..]

B. Customer Buying Psychology
- What truly drives purchase decisions? (rank by importance)
- Is it price, brand recognition, customer demand, margins, or something else?
- Customer's risk tolerance (willing to try new brands?)
- Stock rotation preferences (fast-moving vs slow-moving)
- Is he open to switching if Naga offers better schemes or prices?
- How is the customer buying behaviour? (Like is he buys product if more schemes are offered, or if the product is on discount, or if the product is a well-known brand, or if more free pieces are offered, etc.)

------------------------------------------------------------

5. Salesperson Effectiveness Score:

Based on specific criteria - Score each component objectively.  

IMPORTANT: If any criterion does not apply to this conversation (e.g., no competitor brands mentioned → Competitor handling = N/A), then:
1. Mark that category as "N/A".
2. Give full score for that category.

---

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

---

**Final Score Calculation:**
- If all 4 criteria apply:  
  (Product promotion × 0.3) + (Scheme leverage × 0.2) + (Competitor handling × 0.25) + (Customer psychology × 0.25)  

------------------------------------------------------------

6. Salesperson Ability Analysis
- How salesperson handles the conversation, objections, competitor mentions, and customer concerns.

------------------------------------------------------------

7. Product Price Analysis
 What are all the Naga products that the customer thinks the price is too high?
 If so, list them with details like which product, what price point, and customer's exact concerns.

------------------------------------------------------------

8. Salesperson Strengths
- [Strength 1]
- [Strength 2]
- [Strength 3]

------------------------------------------------------------

9. Areas for Improvement
- [Improvement 1]
- [Improvement 2]
- [Improvement 3]

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

------------------------------------------------------------

MANDATORY OUTPUT FORMAT - FOLLOW THIS EXACT STRUCTURE

You MUST follow this precise format. Do NOT write in paragraph style.

**TEMPLATE STRUCTURE:**

# Brand & Product Mapping

A. Naga Brand Products
- [Product 1]
- [Product 2]
- [Product 3]

B. Competitor Brands Mentioned
- [Brand Name]: [Product categories]

------------------------------------------------------------

# 1. Conversation Summary
- [Summary point 1]
- [Summary point 2]
- [Summary point 3]

------------------------------------------------------------

# 2. Sales Matrix

**Naga Products Performance**
- Naga products promoted: [Details]
- Volume pushed / upselling: [Details]
- Schemes offered: [Details with specifics]
- Cross-selling within Naga portfolio: [Details]
- Acceptance/Rejection: [Details]

**Sales Barriers**
- Objections raised: [Details]
- Competitor advantages cited: [Details]

------------------------------------------------------------

# 3. Customer Buying Patterns

A. Regularly buying products (Customer commits to buy BEFORE schemes OR shows clear intent regardless of schemes)
    - [Products List - immediate interest/commitment or clear intent to buy regardless]
    
B. Scheme Based Orders (Customer commits to buy ONLY BECAUSE schemes influenced their decision)
    - [Products List - hesitation turned to purchase, or quantity increased due to schemes]------------------------------------------------------------

# 4. Competitive Intelligence & Customer Psychology

A. Competitor Brand Analysis

**Brand 1:**
- Brand Name: [Name]
- Products: [Categories]
- Customer's Current Status: [Details]
- Reasons for Preference: [Detailed reasons]

**Brand 2:**
- Brand Name: [Name]
- Products: [Categories]
- Customer's Current Status: [Details]
- Reasons for Preference: [Detailed reasons]

**Brand 3:** (Continue for each additional competitor brand mentioned until all are covered)
- Brand Name: [Name]
- Products: [Categories]    
- Customer's Current Status: [Details]
- Reasons for Preference: [Detailed reasons]

B. Customer Buying Psychology
- What truly drives purchase decisions: [Ranked list]
- Customer's risk tolerance: [Details]
- Stock rotation preferences: [Details]
- Openness to switching brands: [Details]
- How is the customer buying behaviour: [Details]

------------------------------------------------------------

# 5. Salesperson Effectiveness Score

**Product promotion (30% weight):** _/10
**Scheme leverage (20% weight):** _/10
**Competitor handling (25% weight):** _/10
**Customer psychology understanding (25% weight):** _/10

**Final Score Calculation:**
[Calculation formula] = _/10

------------------------------------------------------------

# 6. Salesperson Ability Analysis
- [Summary]

------------------------------------------------------------

# 7. Product Price Analysis
- [Summary]

------------------------------------------------------------

# 8. Salesperson Strengths
- [Strength 1]
- [Strength 2]
- [Strength 3]

------------------------------------------------------------

# 9. Areas for Improvement
- [Improvement 1]
- [Improvement 2]
- [Improvement 3]

------------------------------------------------------------

CRITICAL REMINDERS

- DO NOT assume any brand is Naga unless explicitly stated
- DO NOT group competitors as "other brands" – name each specifically
- DO capture both stated reasons AND underlying psychology
- DO identify non-price factors driving brand preference
- DO note when customer prefers competitor despite Naga being cheaper/better
- FOLLOW THE EXACT FORMAT ABOVE - DO NOT DEVIATE TO PARAGRAPH STYLE
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

    # Initialize page state
    if 'page' not in st.session_state:
        st.session_state['page'] = 'home'

    def render_dashboard():

        st.title("📊 Naga Sales Performance Dashboard")

        excel_path = 'C:/Users/w1mug/Desktop/naga/data/Sales_Performance_Summary_Sample_Data.xlsx'

        # Load Data
        try:
            df = pd.read_excel(excel_path)
        except Exception as e:
            st.error(f"Failed to read Excel file: {e}")
            if st.button("⬅️ Back to Home"):
                st.session_state['page'] = 'home'
            return

        # --- KPIs ---
        st.subheader("📈 Key Weekly Summary Metrics")
        kpi_cols = st.columns(4)
        kpi_cols[0].metric("📋 Total Weeks", len(df))
        kpi_cols[1].metric("🧾 Avg Reports/Week", f"{df['Total Reports Analysed'].mean():.1f}")
        kpi_cols[2].metric("🛒 Avg Acceptance Rate", f"{df['Avg Acceptance Rate (%)'].mean():.1f}%")
        kpi_cols[3].metric("💰 Avg Scheme Influence", f"{df['Scheme Influence %'].mean():.1f}%")

        st.divider()

        # --- Product Performance Trends ---
        st.subheader("🧺 Product Performance Trends")
        fig1 = px.bar(df, x='Period', y=['Total Products Accepted', 'Total Products Rejected'],
                    barmode='group', title="Accepted vs Rejected Products per Week")
        st.plotly_chart(fig1, use_container_width=True)

        # Acceptance rate trend
        fig2 = px.line(df, x='Period', y='Avg Acceptance Rate (%)',
                    title="Acceptance Rate Trend", markers=True)
        st.plotly_chart(fig2, use_container_width=True)

        st.divider()

        # --- Scheme Effectiveness ---
        st.subheader("🎯 Scheme Effectiveness Overview")
        fig3 = px.bar(df, x='Period', y='Scheme Influence %', color='Most Effective Scheme Type',
                    title="Scheme Influence % by Week and Scheme Type")
        st.plotly_chart(fig3, use_container_width=True)

        fig4 = px.line(df, x='Period', y='Scheme-Driven Buyers (%)',
                    title="Scheme-Driven Buyers Trend", markers=True)
        st.plotly_chart(fig4, use_container_width=True)

        st.divider()

        # --- Competitor Insights ---
        st.subheader("🏁 Competitor Insights")
        fig5 = px.bar(df, x='Period', y='Competitor Mentions (Total)', color='Most Common Competitor Advantage',
                    title="Competitor Mentions per Week")
        st.plotly_chart(fig5, use_container_width=True)

        fig6 = px.line(df, x='Period', y='% Reports Mentioning Online Price Issue',
                    title="Online Price Issue Mentions (%)", markers=True)
        st.plotly_chart(fig6, use_container_width=True)

        st.divider()

        # --- Objection Analysis ---
        st.subheader("🗣️ Objection Analysis")
        fig7 = px.bar(df, x='Period',
                    y=['% Pricing Objection', '% Brand Loyalty Objection', '% Product Fit / Stock Concerns'],
                    barmode='group', title="Customer Objection Breakdown per Week")
        st.plotly_chart(fig7, use_container_width=True)

        st.divider()

        # --- Overall Effectiveness ---
        st.subheader("⭐ Overall Sales Effectiveness")
        fig8 = px.line(df, x='Period', y=['Avg Product Promotion Score',
                                        'Avg Scheme Leverage Score',
                                        'Avg Competitor Handling Score',
                                        'Overall Sales Effectiveness'],
                    title="Performance Score Trends", markers=True)
        st.plotly_chart(fig8, use_container_width=True)

    st.title("Sales Call Analysis Tool")

    # Sidebar for instructions and navigation
    with st.sidebar:
        
        if st.button("Home"):
            st.session_state['page'] = 'home'
            st.rerun()

        if st.button("View Dashboard"):
            st.session_state['page'] = 'dashboard'
            st.rerun()

    # Route pages
    if st.session_state.get('page', 'home') == 'dashboard':
        render_dashboard()
        return

    # Main content area (home)
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

            if st.button("Clear Analysis"):
                if 'analysis_result' in st.session_state:
                    del st.session_state['analysis_result']
                st.rerun()

            # Display analysis in a nice format
            st.markdown("### 📈 Sales Performance Analysis")

            # Create tabs for better organization
            tab1, tab2 = st.tabs(["📋 Full Report", "💾 Export"])

            with tab1:
                # Display the analysis with proper formatting
                analysis_text = st.session_state['analysis_result']
                st.markdown(analysis_text)

            with tab2:
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

                # Remove file extension from uploaded file name for the report
                base_filename = os.path.splitext(uploaded_file.name)[0]
                st.download_button(
                    label="📄 Download Analysis Report (Word)",
                    data=doc_buffer.getvalue(),
                    file_name=f"{base_filename}_report.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

        else:
            st.info("👆 Upload an audio file and click 'Analyze Audio' to see results here.")

if __name__ == "__main__":
    main()