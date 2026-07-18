from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

res = client.chat.completions.create(
    model="meta-llama/llama-3.1-8b-instruct",
    messages=[
        {"role": "user", "content": "Say hello"}
    ]
)

print(res.choices[0].message.content)