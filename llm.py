from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

class LLMInterface:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", 0))
        with open("system_prompt.txt", "r") as f:
            self.system_prompt = f.read()
    
    def translate_to_query(self, user_input):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_input}
                ]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error during LLM call: {e}")
            return None