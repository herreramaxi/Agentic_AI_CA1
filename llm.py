import os
from langchain_groq import ChatGroq
from langchain_deepseek import ChatDeepSeek
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel

load_dotenv(override=True)
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
    "gpt-6-luna" :ChatOpenAI(
        model="gpt-6-luna",
        api_key=os.getenv("OPENAI_API_KEY", "n/a")     
    ),
    "openai/gpt-oss-20b": ChatGroq(
        model="openai/gpt-oss-20b",
        temperature=0) ,
    "openai/gpt-oss-120b": ChatGroq(
        model="openai/gpt-oss-120b",
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

def get_llm(model_name) -> BaseChatModel:
    return models.get(model_name)