# Import for fatal errors
import warnings
warnings.filterwarnings("ignore")
# Imports for API
import google.generativeai as genai
from google.api_core import exceptions
import json
# Import for cleaning JSON response
import re
# Import for secure API key implementation
import os 

# API CONFIGURATION
MY_API_KEY = os.getenv('GEMINI_API_KEY')
if not MY_API_KEY:
    raise ValueError("Error: GEMINI_API_KEY environment variable not set.")

# MODEL CONFIGURATION

# List of Gemini models to try (in order of preference)
# Falls back to next model if current one hits rate limits
MODELS_TO_TRY = [
    'gemini-3-flash-preview',
    'gemini-2.5-flash',
    'gemini-2.5-flash-lite-preview-09-2025'
]


# Directory paths for assets
CERT_DIR = "assets/certifications"
ICON_DIR = "assets/icons"

# Available certification images (used in response schema)
certifications = ["sedex.png", "iso 9001.png"]

# Available icon images (used in response schema)
icons = ["growth.png", "market.png", "revenue.png", "team.png"]


def generate_slide_text(private_data, public_data):
    
    genai.configure(api_key=MY_API_KEY)
    
    # Defines the expected JSON structure for the AI response
    response_schema = {
        "type": "OBJECT",
        "properties": {
            # Sector classification (Manufacturing, Consumer, Tech, Pharma, Logistics)
            "sector": {"type": "STRING"}, 
            
            # Business overview bullets (4-5 points)
            "business_overview": {
                "type": "ARRAY",
                "items": {"type": "STRING"}
            },
            
            # Legacy field for backward compatibility (D2C brands)
            "brand_overview": {
                "type": "ARRAY",
                "items": {"type": "STRING"}
            },
            
            # At-a-glance summary (3 concise points)
            "at_a_glance": {
                "type": "ARRAY",
                "items": {"type": "STRING"}
            },
            
            # Portfolio and products list (3 points)
            "portfolio_and_products": {
                "type": "ARRAY",
                "items": {"type": "STRING"}
            },
            
            # Investment highlights (5-7 points)
            "investment_highlights": {
                "type": "ARRAY",
                "items": {"type": "STRING"}
            },
            
            # Descriptive text explaining the bar chart
            "bar_chart_text": {"type": "STRING"},
            
            # Descriptive text explaining the pie chart
            "pie_chart_text": {"type": "STRING"},
            
            # Certification images (format: "cert1.png||cert2.png")
            "certifications": {"type": "STRING"},
            
            # Icon images for visual representation (format: "icon1.png||icon2.png")
            "icons": {"type": "STRING"},
            
            # Source URLs used for research
            "source_urls": {
                "type": "ARRAY",
                "items": {"type": "STRING"}
            },
            
            # Pie chart data structure
            "pie_chart_data": {
                "type": "OBJECT",
                "properties": {
                    "title": {"type": "STRING"},
                    "categories": {"type": "ARRAY", "items": {"type": "STRING"}},
                    "values": {"type": "ARRAY", "items": {"type": "NUMBER"}}
                },
                "required": ["title", "categories", "values"]
            },
            
            # Bar chart data structure
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
        # Minimum required fields for valid response
        "required": ["sector", "at_a_glance", "portfolio_and_products", "investment_highlights"]
    }

    # Ensures API returns structured JSON matching our schema
    generation_config = {
        "response_mime_type": "application/json",
        "response_schema": response_schema
    }
    
    # Detailed instructions for the AI to generate sector-specific content
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
      - You may use the internet to clarify, verify, or supplement information when needed.
      - If you use any external URLs for research, add them to the "source_urls" array in your response.

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
       - Choose ONLY from: {certifications}. Max 3.

    7. "icons":
       - String format: "icon1.png||icon2.png"
       - Choose ONLY from: {icons}. Max 5.
       - Select icons that match the content theme of each section.
       - Icon filenames contain keywords describing what they represent - choose accordingly.

    8. "pie_chart_data" & "bar_chart_data":
       - Pick the most important metric based on the Sector Guidelines.
       - Use 3 to 5 categories per chart.
       - If there are more than 2 decimal places, truncate to two.
       - If values are > 100, truncate decimals completely.

    9. "source_urls":
       - Array of any external URLs you used for research or verification.
       - Leave empty if you only used the provided PRIVATE and PUBLIC data.

    --- CONTENT ---
    PRIVATE DATA (SOURCE OF TRUTH):
    {private_data}

    PUBLIC DATA (SCRAPED):
    {public_data}

    PRIORITY: Always prioritize PRIVATE DATA and PUBLIC DATA over internet sources.
    """
    
    # MODEL FALLBACK LOOP 
    for model_name in MODELS_TO_TRY:
        try:
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
            
            # Backward compatibility fix
            if result.get("brand_overview") and not result.get("business_overview"):
                result["business_overview"] = result.pop("brand_overview")
            
            return result
            
        except exceptions.ResourceExhausted:
            print(f"Limit hit for {model_name}. Switching...")
            continue
        except Exception as e:
            print(f"Error with {model_name}: {e}")
            continue

    raise RuntimeError("All models failed.")
