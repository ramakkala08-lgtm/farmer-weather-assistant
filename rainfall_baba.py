from rainfall import get_weather
from app import model


def extract_text(response):

    content = response.content

    # Normal string
    if isinstance(content, str):
        return content

    # Gemini/LangChain may return a list of content blocks
    if isinstance(content, list):

        text_parts = []

        for item in content:

            # Example:
            # {"type": "text", "text": "..."}
            if isinstance(item, dict):

                if "text" in item:
                    text_parts.append(
                        str(item["text"])
                    )

            # Sometimes the item itself is a string
            elif isinstance(item, str):

                text_parts.append(item)

        return "\n".join(text_parts)

    # Fallback
    return str(content)


def generate_weather_response(latitude, longitude):

    # =========================
    # GET WEATHER
    # =========================

    result = get_weather(
        latitude,
        longitude
    )

    if "error" in result:

        return {
            "error": result["error"]
        }

    today = result["today"]

    hourly = result["hourly"]


    # =========================
    # GEMINI PROMPT
    # =========================

    prompt = f"""
You are an expert agricultural weather assistant
helping an ordinary farmer in Telangana.

You have been given ONLY today's weather data.

TODAY'S WEATHER:
{today}

HOURLY WEATHER:
{hourly}

Analyze this data and give useful conclusions
for the farmer.

Do NOT simply repeat the raw numbers.

Find useful patterns from the hourly weather data.

Your response MUST be written in simple,
natural Telugu that an ordinary farmer can understand.

Use these sections:

🌦️ ఈరోజు వాతావరణం

Give a short overall summary of today's weather.

🌧️ వర్షం పరిస్థితి

Clearly explain:

- Whether meaningful rain is expected today.
- When rain probability is highest.
- When rain probability is lowest.
- If rainfall is very unlikely, clearly say so.

🌡️ ఉష్ణోగ్రత

Explain:

- When temperatures are lowest.
- When temperatures are highest.
- Whether the day is relatively cool, warm, or hot
  based only on the provided data.

💨 గాలి పరిస్థితి

Analyze the hourly wind speeds.

Explain whether the wind is generally low,
moderate, or relatively strong.

🌾 రైతుకు సూచన

Give practical farming advice based ONLY
on the weather information provided.

🧪 మందులు పిచికారీ

Explain whether today's weather appears suitable
for pesticide spraying.

Consider:

- Rain probability
- Rainfall
- Wind speed

Explain the reason simply.

IMPORTANT RULES:

- Answer ONLY about today.
- Do NOT mention tomorrow.
- Do NOT mention future days.
- Do NOT invent weather information.
- Do NOT invent crop-specific information.
- Do NOT simply list all 24 hours.
- Identify useful time periods from the hourly data.
- Mention specific times when useful.
- Do not claim rain will definitely happen.
- Use probability-based language.
- Keep the answer concise.
- Make the answer practical for a farmer.
"""


    # =========================
    # GEMINI
    # =========================

    try:

        response = model.invoke(prompt)

        # Convert Gemini response into plain text
        summary = extract_text(response)

    except Exception as e:

        return {
            "error": f"AI weather analysis failed: {str(e)}"
        }


    # =========================
    # FINAL JSON
    # =========================

    return {

        "today": today,

        "hourly": hourly,

        "summary": summary

    }