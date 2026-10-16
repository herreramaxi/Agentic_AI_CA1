from langchain_groq import ChatGroq
from langchain_deepseek import ChatDeepSeek
from dotenv import load_dotenv

load_dotenv()

models = {
    "qwen/qwen3.8-27b": ChatGroq(
        model=    "qwen/qwen3.8-27b",
        temperature=0
    ),
    "qwen/qwen3-32b": ChatGroq(
        model="qwen/qwen3-32b",
        temperature=0
    ),
     "qwen/qwen3-32b/fast": ChatGroq(
        model="qwen/qwen3-32b",
        temperature=0,
        reasoning_effort="none"
    ),
    "llama-3.1-8b-instant": ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0
    ),
    "openai/gpt-oss-20b": ChatGroq(
        model="openai/gpt-oss-20b",
        temperature=0) ,
    "deepseek":  ChatDeepSeek(
         model=  "deepseek-chat",
         temperature=0),
     "DeepSeek-R1-Distill-Qwen-32B": ChatDeepSeek(
         model= "DeepSeek-R1-Distill-Qwen-32B",
         temperature=0),
          "deepseek-v4-flash": ChatDeepSeek(
         model= "deepseek-v4-flash",
            temperature=0),
    "deepseek-v4-pro": ChatDeepSeek(
         model= "deepseek-v4-pro",
            temperature=0)
}

def get_llm(model_name):
    return models.get(model_name)