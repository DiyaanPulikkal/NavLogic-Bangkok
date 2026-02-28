import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from config import MODEL
from llms.tools import FUNCTION_DECLARATIONS

load_dotenv()

class LLMInterface:
    def __init__(self):
        self.client = genai.Client()
        self.model = MODEL
        self.tools = types.Tool(function_declarations=FUNCTION_DECLARATIONS)
        self.config = types.GenerateContentConfig(
            tools=self.tools,
        )

        with open("system_prompt.txt", "r") as f:
            self.system_prompt = f.read()
    
    def translate_to_query(self, user_input):
        try:
            response = self.client.models.generate_content(
                model=self.model,
                config=self.config,
                contents=user_input,
            )
            if response.candidates:
                first_candidate = response.candidates[0]

                for part in first_candidate.content.parts:
                    if part.function_call:
                        function_name = part.function_call.name
                        arguments = dict(part.function_call.args)
                        return (function_name, arguments)

            return None
        except Exception as e:
            print(f"Error during model generation: {e}")
            return None