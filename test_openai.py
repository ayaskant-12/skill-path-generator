# test_openai.py
import openai
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')

try:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Say 'Hello World'"}],
        max_tokens=5
    )
    print("API Key is working!")
    print(response.choices[0].message.content)
except Exception as e:
    print(f"API Key error: {e}")
