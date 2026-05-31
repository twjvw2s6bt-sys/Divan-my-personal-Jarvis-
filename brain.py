from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))



def get_response(conversation_history):
    response = client.chat.completions.create(
        model = "llama-3.3-70b-versatile",
        messages=conversation_history
    )
    return response.choices[0].message.content

def get_session_review(conversation_history):
    review_prompt = conversation_history + [{
        "role": "user",
        "content": "Review this conversation. Rate my performance 1-10, identify my main weakness, and suggest one adjustment for next time. Reply in JSON like: {\"score\": 7, \"weakness\": \"...\", \"adjustment\": \"...\"}"
    }]
    response = client.chat.completions.create(
        model = "llama-3.3-70b-versatile",
        messages=review_prompt
    )
    return response.choices[0].message.content

