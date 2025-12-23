import os
from google.adk.models.lite_llm import LiteLlm
from dotenv import load_dotenv
load_dotenv()

LLM_MODEL = os.getenv('LLM_MODEL', 'gemini-2.5-pro')
BASE_URL = os.getenv('BASE_URL', 'http://ailab.flashhold.com:13001/v1')
API_KEY = os.getenv('API_KEY')

model_config = LiteLlm(model=LLM_MODEL, api_base=BASE_URL, api_key=API_KEY)