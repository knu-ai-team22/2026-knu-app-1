from langchain_groq import ChatGroq
from dotenv import load_dotenv
load_dotenv()

# from langchain_openai import ChatOpenAI 
# llm = ChatOpenAI(model="gpt-5", temperature=0.7) 

_llm = ChatGroq(model="openai/gpt-oss-20b")

def get_llm():
    return _llm