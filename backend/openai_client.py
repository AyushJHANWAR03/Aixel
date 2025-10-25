import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

INSIGHTS_PROMPT = """You are a marketing analyst. Given these aggregated funnel metrics (JSON), return 3 short observations and 3 action recommendations in JSON format.

Keep each sentence concise and focused on conversions or campaign actions.

Return ONLY valid JSON in this exact format:
{{
  "observations": ["observation 1", "observation 2", "observation 3"],
  "recommendations": ["recommendation 1", "recommendation 2", "recommendation 3"]
}}

Metrics:
{metrics}
"""

def generate_insights(metrics: dict) -> dict:
    """Call OpenAI API to generate insights from metrics"""

    # Fallback mock if no API key
    if not os.getenv("OPENAI_API_KEY"):
        return {
            "observations": [
                "Conversion rate from landing to purchase is 4.8%",
                "Mobile users have 50% lower conversion than desktop",
                "Google campaigns drive 60% of traffic but only 40% of purchases"
            ],
            "recommendations": [
                "Optimize mobile checkout flow to reduce friction",
                "Increase budget for high-converting Facebook campaigns",
                "A/B test landing page CTAs to improve product view rate"
            ]
        }

    try:
        prompt = INSIGHTS_PROMPT.format(metrics=json.dumps(metrics, indent=2))

        print(f"\n=== CALLING OPENAI API ===")
        print(f"Model: gpt-4-turbo-preview")
        print(f"Prompt length: {len(prompt)} chars")

        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are a marketing analytics expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )

        content = response.choices[0].message.content

        print(f"\n=== RAW OPENAI RESPONSE ===")
        print(f"Response type: {type(content)}")
        print(f"Response length: {len(content)} chars")
        print(f"Raw content:\n{content}")
        print(f"=== END RAW RESPONSE ===\n")

        # Strip markdown code fences if present
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]  # Remove ```json
        elif content.startswith("```"):
            content = content[3:]  # Remove ```
        if content.endswith("```"):
            content = content[:-3]  # Remove trailing ```
        content = content.strip()

        print(f"\n=== CLEANED CONTENT ===")
        print(f"Cleaned content:\n{content}")
        print(f"=== END CLEANED CONTENT ===\n")

        # Parse JSON from response
        insights = json.loads(content)

        print(f"\n=== PARSED SUCCESSFULLY ===")
        print(f"Observations: {len(insights.get('observations', []))}")
        print(f"Recommendations: {len(insights.get('recommendations', []))}")
        print(f"=== END ===\n")

        return insights

    except Exception as e:
        print(f"\n=== ERROR GENERATING INSIGHTS ===")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        import traceback
        print(f"Full traceback:\n{traceback.format_exc()}")
        print(f"=== END ERROR ===\n")

        # Return fallback on error
        return {
            "observations": ["Error generating insights. Using fallback."],
            "recommendations": ["Please check API key and try again."]
        }
