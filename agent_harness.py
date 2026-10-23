from dataclasses import dataclass
from typing import Any
from langchain.agents import create_agent
from langchain.chat_models import BaseChatModel
from langchain_core.messages import (
    AIMessage,
    AnyMessage,
    HumanMessage,
    SystemMessage,
)
from langchain.tools import tool

from skill_middleware import SkillMiddleware
from skills_manager import SkillsManager

@dataclass
class AgentHarness:
    model: BaseChatModel
    training_mode: bool = False
    agent: Any | None = None #CompiledStateGraph[AgentState[Any], ContextT, InputAgentState, OutputAgentState[Any]]: ...
    tools: Any | None = None
    system_prompt: str | None = None

    @tool
    def request_supervisor(user_query: str) -> str:
        """REQUIRED fallback: get an example response when no available skill matches the user query.
        Call this for orders, payments, tickets, account data, or any domain question with no matching skill.
        Do not answer those questions yourself without calling this tool first.

        Args:
            user_query (str): The exact user query to get an example response for
        """
        print(f"request_supervisor: {user_query}")
        # response = train_df.loc[train_df["instruction"] == user_query, "response"].iloc[0]
        # return response
        return "N/A"

    def __post_init__(self):
        sm=SkillsManager()

        if not self.system_prompt:            
            self.system_prompt = "You are a helpful assistant."

        tools = []
        if self.training_mode:
            tools.append(self.request_supervisor)
            
        self.agent = create_agent(
        model=self.model,        
        # tools= [sm.load_skill, self.request_supervisor],
        tools= tools,
        middleware=[SkillMiddleware(training_mode =self.training_mode )],
        system_prompt=self.system_prompt,
        )


    def invoke(self, message: str):
        humman_message = HumanMessage(message)
        messages = [humman_message]
        response = self.agent.invoke({'messages': messages})
        return response
