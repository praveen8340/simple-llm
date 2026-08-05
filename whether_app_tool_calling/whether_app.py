import json
import os
from typing import Any

import requests
from dotenv import load_dotenv
from groq import Groq
from starlette.requests import Request
from starlette.responses import JSONResponse


load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None


def get_weather(location: str) -> dict[str, Any]:
    if not WEATHER_API_KEY:
        return {"error": "Missing WEATHER_API_KEY"}

    url = (
        "http://api.openweathermap.org/data/2.5/weather"
        f"?q={location}&units=metric&appid={WEATHER_API_KEY}"
    )

    response = requests.get(url, timeout=10)
    data = response.json()

    if data.get("cod") == 200:
        return {
            "location": location,
            "temperature": data["main"]["temp"],
            "description": data["weather"][0]["description"],
        }

    return {"error": "City not found"}


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name like Mumbai, London",
                    }
                },
                "required": ["location"],
            },
        },
    }
]

messages = [
    {
        "role": "system",
        "content": "You are a weather assistant. Use get_weather function whenever weather information is requested.",
    }
]


async def whether(request: Request) -> JSONResponse:
    try:
        payload = await request.json()
    except Exception:
        payload = {"text": ""}

    user_input = payload if isinstance(payload, str) else json.dumps(payload)

    messages.append({"role": "user", "content": user_input})

    if client is None:
        return JSONResponse({"error": "Missing GROQ_API_KEY"})

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )

    response_message = response.choices[0].message

    if response_message.tool_calls:
        tool_call = response_message.tool_calls[0]
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)

        result: Any = {}
        if function_name == "get_weather":
            result = get_weather(arguments["location"])

        messages.append(
            {
                "role": "assistant",
                "tool_calls": response_message.tool_calls,
            }
        )

        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": function_name,
                "content": json.dumps(result),
            }
        )

        final_response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
        )
        assistant_reply = final_response.choices[0].message.content or ""
    else:
        assistant_reply = response_message.content or ""

    messages.append({"role": "assistant", "content": assistant_reply})

    return JSONResponse({"reply": assistant_reply})