from langchain_core.language_models import BaseChatModel
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

_llm = ChatGroq(
    model='openai/gpt-oss-20b'
)

def get_llm()->BaseChatModel:
    return _llm