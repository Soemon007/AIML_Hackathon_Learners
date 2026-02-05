import warnings
warnings.filterwarnings("ignore")
import google.generativeai as genai
from google.api_core import exceptions
import json
import re

# --- API CONFIGURATION ---
# YOUR ORIGINAL MODEL LIST
MODELS_TO_TRY = [
    'gemini-3-flash-preview',
    'gemini-2.5-flash',
    'gemini-2.5-flash-lite-preview-09-2025']

IMG_DIR = "assets"
images = ["sedex.png", "iso 9001.png"]

def generate_slide_text(private_data, public_data):
    genai.configure(api_key=MY_API_KEY)
    
    # 1. Unified Schema (Matches your latest file exactly)
    response_schema = {
        "type": "OBJECT",
        "properties": {
            "sector": {"type": "STRING"}, 
            "business_overview": {
                "type": "ARRAY",
                "items": {"type": "STRING"}
            },
            # We keep 'brand_overview' for backward compatibility, 
            # but the prompt will mostly use 'business_overview' for all sectors now.
            "brand_overview": {
                "type": "ARRAY",
                "items": {"type": "STRING"}
            },
            "at_a_glance": {
                "type": "ARRAY",
                "items": {"type": "STRING"}
            },
            "portfolio_and_products": {
                "type": "ARRAY",
                "items": {"type": "STRING"}
            },
            "investment_highlights": {
                "type": "ARRAY",
                "items": {"type": "STRING"}
            },
            "bar_chart_text": {"type": "STRING"},
            "pie_chart_text": {"type": "STRING"},
            "certifications": {"type": "STRING"},
            "pie_chart_data": {
                "type": "OBJECT",
                "properties": {
                    "title": {"type": "STRING"},
                    "categories": {"type": "ARRAY", "items": {"type": "STRING"}},
                    "values": {"type": "ARRAY", "items": {"type": "NUMBER"}}
                },
                "required": ["title", "categories", "values"]
            },
            "bar_chart_data": {
                "type": "OBJECT",
                "properties": {
                    "title": {"type": "STRING"},
                    "categories": {"type": "ARRAY", "items": {"type": "STRING"}},
                    "values": {"type": "ARRAY", "items": {"type": "NUMBER"}}
                },
                "required": ["title", "categories", "values"]
            }
        },
        "required": ["sector", "at_a_glance", "portfolio_and_products", "investment_highlights"]
    }

    generation_config = {
        "response_mime_type": "application/json",
        "response_schema": response_schema
    }

    # 2. Rich Context Prompt with Sector Intelligence
    prompt = f"""
    You are an M&A investment analyst.
    
    TASK: Analyze the provided data to create a "Blind Teaser" deck.
    
    STEP 1: IDENTIFY SECTOR
    Classify the company into exactly ONE of these categories:
    - "Manufacturing" (Industrial, Automotive, Chemicals, B2B)
    - "Consumer" (D2C, Retail, FMCG, Food, Wellness)
    - "Tech" (SaaS, AI, IT Services, Platforms)
    - "Pharma" (Biotech, CDMO, Drug Formulations)
    - "Logistics" (Supply Chain, Transport, Warehousing)

    STEP 2: APPLY SECTOR GUIDELINES
    Based on the sector you identified, strictly follow these content rules:

    CASE: MANUFACTURING
    - business_overview: Focus on Product Segments, End-User Industries, and Manufacturing Footprint.
    - investment_highlights: Emphasize "Entry Barriers (Capex)," "Critical Supplier Status," and "Operating Leverage."
    - Charts: Focus on "Revenue Growth vs. EBITDA Margins" or "Export Contribution."

    CASE: CONSUMER (D2C)
    - business_overview: Focus on Portfolio Mix (SKUs), Channel Presence (Online/Offline), and Brand Identity.
    - investment_highlights: Emphasize "Brand Loyalty," "Unit Economics (LTV/CAC)," and "Market Whitespace."
    - Charts: Focus on "Sales Growth," "Repeat Rates," or "Average Order Value (AOV)."

    CASE: TECH (SaaS)
    - business_overview: Focus on Tech Stack, Engagement Models, and IP/Proprietary Platforms.
    - investment_highlights: Emphasize "Scalability," "Recurring Revenue (ARR)," and "Sticky Client Relationships."
    - Charts: Focus on "ARR Growth" or "Revenue per Employee."

    CASE: PHARMA
    - business_overview: Focus on Therapeutic Areas, Regulatory Approvals (USFDA), and R&D Capabilities.
    - investment_highlights: Emphasize "Compliance Track Record," "Complex Chemistry," and "Molecule Pipeline."
    - Charts: Focus on "R&D Spend %" or "Regulated Market Revenue."

    CASE: LOGISTICS
    - business_overview: Focus on Network Reach (Pin codes), Fleet/Warehouse Infrastructure, and Service Mix.
    - investment_highlights: Emphasize "Last-Mile Connectivity," "Tech-Enabled Efficiency," and "Sector Tailwinds."
    - Charts: Focus on "Volume Growth" or "Fuel Efficiency."

    GENERAL RULES:
      - Do NOT invent numbers. Use the source data.
      - Use professional, concise investor language.
      - Anonymize the company name (use "The Company" or "Project X").
      - Output valid JSON only.
      - In case of a lack of data on a topic you may search the web for it.

    CONTENT GUIDELINES (Flexible Ranges):

    1. "business_overview" (Provide 4 to 5 bullet points):
       - Summarize the business model, key offerings, and market position based on Sector Guidelines above.
    
    2. "at_a_glance" (Provide 3 concise bullet points):
       - Summarize the organization, key identity, scale, and core strengths.

    3. "portfolio_and_products" (Provide 3 bullet points):
       - List main products/services. Emphasize flagship offerings.

    4. "investment_highlights" (Provide 5 to 7 bullet points, 1 line each):
       - Focus on the "Hook" described in the Sector Guidelines above.

    5. "bar_chart_text" & "pie_chart_text":
       - Explain in 2-4 lines what the specific chart shows.
       - Explain its significance (e.g., "High margins indicate efficiency").

    6. "certifications": 
       - String format: "cert1.png||cert2.png" 
       - Choose ONLY from: {images}. Max 3.

    7. "pie_chart_data" & "bar_chart_data":
       - Pick the most important metric based on the Sector Guidelines.
       - Format: "Title||Cat1,Cat2,Cat3||Val1,Val2,Val3"
       - Use 3 to 5 categories per chart.
       - If there are more than 2 decimal places, truncate to two.
       - If values are > 100, truncate decimals completely.

    --- CONTENT --
    PRIVATE DATA (SOURCE OF TRUTH):
    {private_data}

    PUBLIC DATA (SCRAPED):
    {public_data}
    """

    for model_name in MODELS_TO_TRY:
        try:
            print(f"🤖 Generating with {model_name}...")
            model = genai.GenerativeModel(model_name)
            
            response = model.generate_content(
                prompt, 
                generation_config=generation_config
            )
            
            # Clean response
            text_response = response.text.strip()
            text_response = re.sub(r"^```json|^```", "", text_response).strip()
            text_response = re.sub(r"```$", "", text_response).strip()
            
            result = json.loads(text_response)
            
            # Helper: If the model used 'brand_overview' for D2C, move it to 'business_overview'
            # so the rest of the pipeline (PPT generator) only has to look in one place.
            if result.get("brand_overview") and not result.get("business_overview"):
                result["business_overview"] = result.pop("brand_overview")
                
            print(f"✅ Success with {model_name}! (Sector: {result.get('sector', 'Unknown')})")
            return result
            
        except exceptions.ResourceExhausted:
            print(f"⚠️ Limit hit for {model_name}. Switching...")
            continue
        except Exception as e:
            print(f"❌ Error with {model_name}: {e}")
            continue

    raise RuntimeError("❌ All models failed.")
