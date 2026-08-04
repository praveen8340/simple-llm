
from urllib.request import Request

from google import genai
from google.genai import types
from starlette.responses import JSONResponse

client = genai.Client(api_key="YOUR_API_KEY")  # Replace with your actual API key

personalities = {
  "Friendly": """You are a friendly, enthusiastic, and highly encouraging Study Assistant.
  Your goal is to break down complex concepts into simple, beginner-friendly explanations.
  Use analogies and real-world examples that beginners can relate to. Always ask a follow-up
  question to check understanding.""",

  "Academic": """You are a strictly academic, highly detailed, and professional university
   Professor. Use precise, formal terminology, cite key concepts and structure your response.
   Your goal is to break down complex concepts into simple, beginner-friendly explanations.
   Use analogies and real-world examples that beginners can relate to. Always ask a follow-up question
    to check understanding."""
}

def study_assistant(question,persona):
  system_prompt = personalities[persona]
  response = client.models.generate_content(
    model="gemini-2.5-flash",
    config = types.GenerateContentConfig(
        temperature=0.4,
        max_output_tokens=5000,
    ),
    contents= question
  )
  return response




async def study_llm(request:Request) -> JSONResponse:
  input = await request.json()
  question = input.get("question")
  personality = input.get("personality")
  output = study_assistant(question,personality)
  return JSONResponse({"response": output.text})


#question="HI, Can you explain about Machine learning algorithm"
#personality = "Friendly"
#output = study_assistant(question,personality)
#print(output.text)