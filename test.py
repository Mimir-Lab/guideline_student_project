import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("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"),        # ✅ Groq key
    base_url="https://api.groq.com/openai/v1"  # ✅ Groq endpoint
)
response = client.chat.completions.create(
    model="llama3.1-8b-instant",  # ✅ FREE Groq model
    messages=[{"role": "user", "content": "Hi"}]
)
print(response.choices[0].message.content)

