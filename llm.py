
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_deepseek import ChatDeepSeek
from langchain_openai import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel

load_dotenv(override=True)

models: dict[str, BaseChatModel] = {
    # Groq - Open-weight models
    "openai/gpt-oss-20b": ChatGroq(
        model="openai/gpt-oss-20b",
        temperature=0,
    ),
    "openai/gpt-oss-120b": ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0,
    ),
    "qwen/qwen3.8-27b": ChatGroq(
        model="qwen/qwen3.8-27b",
        temperature=0,
    ),  
    # Agent: OpenAI model
    "gpt-5-nano": ChatOpenAI(
        model="gpt-5-nano",
        reasoning_effort="low",
        max_retries=3,
        timeout=60,
    ),
    #expensive
    "gpt-5.5": ChatOpenAI(
        model="gpt-5.5",
        reasoning_effort="low",
        max_retries=3,
        timeout=60,
    ),
    "gpt-6-luna-none": ChatOpenAI(
        model="gpt-6-luna",
        reasoning_effort="none",
        max_retries=3,
        timeout=60,
    ),
    "gpt-6-luna-low": ChatOpenAI(
        model="gpt-6-luna",
        reasoning_effort="low",
        max_retries=3,
        timeout=60,
    ),
    "gpt-6-luna-medium": ChatOpenAI(
            model="gpt-6-luna",
            reasoning_effort="medium",
            max_retries=3,
            timeout=60,
    ),
    "gpt-6-astra": ChatOpenAI(
        model="gpt-6-astra",
        reasoning_effort="low",
        max_retries=3,
        timeout=60,
    ),
    # Agent: fast DeepSeek model
     "deepseek-flash": ChatDeepSeek(
            model="deepseek-flash",
            temperature=0,
            max_retries=3,
            timeout=60,
        ),
    "deepseek-flash-low": ChatDeepSeek(
        model="deepseek-flash",
        reasoning_effort="low",
        temperature=0,
        max_retries=3,
        timeout=60,
    ),   
    # Fixed evaluation judge
    "deepseek-v4-pro": ChatDeepSeek(
        model="deepseek-v4-pro",
        temperature=0,
        max_retries=3,
        timeout=60,
        #https://github.com/deepseek-ai/DeepSeek-V3/issues/1376
        extra_body={"thinking": {"type": "disabled"}},
    ),
}


def get_llm(model_name: str) -> BaseChatModel:
    return models[model_name]
