from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import google.generativeai as genai
import dotenv
import requests
import os

# Load environment variables
dotenv.load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

app = FastAPI(
    title="Sales Call Audio Analysis API",
    description="Send a public audio file URL (e.g., Salesforce file link) for Gemini analysis.",
    version="3.0.0"
)

# ===== Gemini Model Setup =====
# MODEL_NAME = "gemini-2.5-pro"
MODEL_NAME = "gemini-2.0-flash"

# ===== Prompt Definition =====
ANALYSIS_PROMPT = """
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
- Do not repeat products if already mentioned

2. Competitor Brands – ALL other brand names mentioned, including:
- Nandi, Sankar, Shakti, Aachi, MTR, Britannia, etc.

3. Online Retailers – Any online platforms mentioned (e.g., Amazon, Flipkart, BigBasket, etc.)

IMPORTANT: DO NOT assume a product is Naga's unless explicitly stated!

------------------------------------------------------------

SPEAKER CONTEXT RULES (CRITICAL)
 
Before mapping brands and products, determine who is speaking:
 
- If the **Sales Representative** mentions a product, assume it is **Naga’s product** unless they clearly say it’s a competitor.
- If the **Customer (store owner)** mentions a product or brand name, assume it is a **competitor brand**, unless the Sales Rep later confirms it belongs to Naga.
- If both speakers mention the same product name, assign ownership based on context and tone:
  - If Sales Rep is promoting or explaining → Naga’s product.
  - If Customer is comparing or complaining → Competitor product.
- When uncertain, label it as **“Ambiguous – Needs context”** and do not count it in Naga product analysis.
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
- Category:
    - [Based on the reason Categorize whether it is due to Price Concern or Discount Concern or Product Variety or Product Package Size or Other factors]
      IMPORTANT - Choose the Category only on the list of reasons mentioned above, dont change the list.

**Brand 2:**
- Brand Name: [Next competitor brand]
- Products: Which product categories?
- Customer's Current Status: Does customer stock it? How much?
- Reasons for Preference: Why does customer prefer this brand than Naga in detail?
    - [Price? Consumers Choice? Taste? Local brand? Habit? Promotions? etc..]
- Category:
    - [Based on the reason Categorize whether it is due to Price Concern or Discount Concern or Product Variety or Product Package Size or Other factors]
      IMPORTANT - Choose the Category only on the list of reasons mentioned above, dont change the list.

**Brand 3:** (Continue for each additional competitor brand mentioned until all are covered)
- Brand Name: [Next competitor brand]
- Products: Which product categories?
- Customer's Current Status: Does customer stock it? How much?
- Reasons for Preference: Why does customer prefer this brand than Naga in detail?
    - [Price? Consumers Choice? Taste? Local brand? Habit? Promotions? etc..]
- Category:
    - [Based on the reason Categorize whether it is due to Price Concern or Discount Concern or Product Variety or Product Package Size or Other factors]
      IMPORTANT - Choose the Category only on the list of reasons mentioned above, dont change the list.

B. Online Retailers Mentioned
For EACH online retailer mentioned, document separately:

**Retailer 1:**
- Name: [e.g., Amazon]
- Product Range: What products do they offer?
- Pricing Strategy: How do their prices compare to Naga?
- Customer Perception: How do customers view this retailer?
- Unique Selling Points: What makes this retailer stand out?

**Retailer 2:**
- Name: [Next online retailer]
- Product Range: What products do they offer?
- Pricing Strategy: How do their prices compare to Naga?
- Customer Perception: How do customers view this retailer?
- Unique Selling Points: What makes this retailer stand out?

C. Customer Buying Psychology
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
✓ Analyze audio by using both transcription as well as audio, as sometimes transcription might help in understanding the context better and audio might give better clarity on tone, emphasis, pauses, etc.
✓ Clearly Identify the Salesperson and the Customer in the conversation before analysis by the conversation context.
✓ Identify in what context does the salesperson is addressing about the price of the Naga product is high or low than the competitors before adding it to the price analysis section or at some other sections, Because sometimes the salesperson might be saying that the price is low compared to competitors, not high so it should not be added to the price analysis section as a high price concern. These things should be addressed carefully.
✓ IMPORTANT: The Analysis report should be in English only.
✓ Always cross-check the speaker before assigning brand ownership:
  - Sales Rep statements = Naga context
  - Customer statements = Competitor context
  - Never assume ownership without confirming who said it.
------------------------------------------------------------

Brand & Product Mapping
 
# Speaker & Brand Context Mapping
| Speaker | Brand | Product | Context / Ownership Confirmation |
|----------|--------|----------|--------------------------------|
| Sales Rep | Naga | [Product] | Confirmed as Naga (own product) |
| Customer | [Brand] | [Product] | Competitor product mentioned by customer |
| Sales Rep | — | [Product] | No brand mentioned → assumed Naga |
| Customer | — | [Product] | Ambiguous – Needs context |

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
- Category: Price Concern / Discount Concern / Product Variety / Product Package Size / Other factors

**Brand 2:**
- Brand Name: [Name]
- Products: [Categories]
- Customer's Current Status: [Details]
- Reasons for Preference: [Detailed reasons]
- Category: Price Concern / Discount Concern / Product Variety / Product Package Size / Other factors

**Brand 3:** (Continue for each additional competitor brand mentioned until all are covered)
- Brand Name: [Name]
- Products: [Categories]    
- Customer's Current Status: [Details]
- Reasons for Preference: [Detailed reasons]
- Category: Price Concern / Discount Concern / Product Variety / Product Package Size / Other factors

B. Online Retailers Mentioned
**Retailer 1:**
- Name: [Name]
- Product Range: [Details]
- Pricing Strategy: [Details]
- Customer Perception: [Details]
- Unique Selling Points: [Details]

**Retailer 2:** (Continue for each additional online retailer mentioned until all are covered) 
- Name: [Name]
- Product Range: [Details]
- Pricing Strategy: [Details]
- Customer Perception: [Details]
- Unique Selling Points: [Details]

C. Customer Buying Psychology
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

# ===== Gemini Helper Functions =====
def analyze_audio_with_gemini(audio_bytes: bytes, mime_type: str = "audio/mp3") -> str:
    model = genai.GenerativeModel(MODEL_NAME)
    response = model.generate_content([
        ANALYSIS_PROMPT,
        {"mime_type": mime_type, "data": audio_bytes}
    ])
    return response.text


def convert_analysis_to_json(analysis_text: str) -> dict:
    sections = {}
    current_section = None
    lines = analysis_text.split("\n")

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line.startswith("#"):
            current_section = line.lstrip("#").strip()
            sections[current_section] = []
        elif current_section:
            sections[current_section].append(line)

    return {k: "\n".join(v) for k, v in sections.items()}


# ===== API Endpoint =====
@app.post("/analyze-audio/")
async def analyze_audio_from_url(request: Request):
    """
    Accepts a JSON body like:
    {
        "file_url": "https://your.salesforce.public.link/audio.mp3"
    }
    """
    try:
        data = await request.json()
        file_url = data.get("file_url")

        if not file_url:
            raise HTTPException(status_code=400, detail="Missing 'file_url' in request body")

        # Step 1️⃣: Download the audio file from URL
        response = requests.get(file_url, stream=True)
        if response.status_code != 200:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to download file (HTTP {response.status_code})"
            )

        audio_bytes = response.content

        # Step 2️⃣: Detect MIME type if available
        mime_type = response.headers.get("Content-Type", "audio/mp3")

        # Step 3️⃣: Analyze with Gemini
        analysis_text = analyze_audio_with_gemini(audio_bytes, mime_type=mime_type)

        # Step 4️⃣: Convert text to structured JSON
        report_json = convert_analysis_to_json(analysis_text)

        return JSONResponse(
            content={
                "status": "success",
                "source_url": file_url,
                "report": report_json
            },
            status_code=200
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during analysis: {str(e)}")


@app.get("/")
def root():
    return {"message": "Sales Call Audio Analysis API (URL mode) is running!"}
