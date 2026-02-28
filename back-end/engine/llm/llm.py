import logging
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from engine.config import MODEL
from engine.llm.tools import FUNCTION_DECLARATIONS

load_dotenv()

logger = logging.getLogger("llm")


class LLMInterface:
    def __init__(self):
        self.client = genai.Client()
        self.chat_history = []
        self.model = MODEL
        self.tools = types.Tool(function_declarations=FUNCTION_DECLARATIONS)

        prompt_path = os.path.join(os.path.dirname(__file__), "system_prompt.txt")
        with open(prompt_path, "r") as f:
            self.system_prompt = f.read()

        self.config = types.GenerateContentConfig(
            tools=[self.tools],
            system_instruction=self.system_prompt
        )
    def translate_to_query(self, user_input):
        try:
            logger.info("Sending query to Gemini...")
            self.chat_history.append(
                types.Content(
                    role="user", parts=[types.Part(text=user_input)]
                )
            )
            response = self.client.models.generate_content(
                model=self.model,
                config=self.config,
                contents=self.chat_history,
            )
            if response.candidates:
                self.chat_history.append(response.candidates[0].content)
                first_candidate = response.candidates[0]

                for part in first_candidate.content.parts:
                    if part.function_call:
                        function_name = part.function_call.name
                        arguments = dict(part.function_call.args)
                        args_str = ", ".join(f"{k}={v!r}" for k, v in arguments.items())
                        logger.info("Gemini returned function call: %s(%s)", function_name, args_str)
                        return (function_name, arguments)

            logger.info("Gemini returned no function call")
            return None
        except Exception as e:
            logger.error("Error during model generation: %s", e)
            return None

    def format_prolog_result(self, function_name: str, result: dict):
        function_response_part = types.Part.from_function_response(
            name=function_name,
            response={"result": result}
        )
        self.chat_history.append(types.Content(role="user", parts=[function_response_part]))

        response = self.client.models.generate_content(
            model=self.model,
            config=self.config,
            contents=self.chat_history,
        )
        result["data"]["answer"] = response.text
        return result
