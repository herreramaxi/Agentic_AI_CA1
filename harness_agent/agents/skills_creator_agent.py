from dataclasses import dataclass
import logging
from typing import Any
from langchain.chat_models import BaseChatModel
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from general import get_tools_info
from harness_agent.skills.tools import create_skill

SYSTEM_PROMPT = """You create one skill from a supervisor example for the customer service assistant.

Call create_skill once. Do not answer with plain text. Do not look for an existing skill and do not update one.

name: a short kebab-case name
description: one sentence that says the situation and the kind of reply, such as "Use when the customer wants to cancel an order and the reply should give the portal steps."
content: only the steps from this example. Keep placeholders such as {{Order Number}} as they are. Do not add anything that is not in the example, and do not copy the customer's exact words.
"""

@dataclass
class SkillsCreatorAgent:
    model: BaseChatModel
    agent: Any | None = None 
    
    def __post_init__(self)-> None:
        self.agent = create_agent(
                model=self.model,
                tools=[create_skill],
                system_prompt=SYSTEM_PROMPT,
        )

    def invoke(self, query: str, reference_answer: str):
        message = HumanMessage(f"""Customer query:
{query}

Supervisor reference answer:
{reference_answer}""")
        
        response = self.agent.invoke(
             {
                 "messages": [message]
             }
        )
        
        response['tools_info'] = get_tools_info(response, 'create_skill')

        logging.debug(f"response: {response}")  
        logging.info(f"SkillsCreatorAgent executed {'successfully' if response['tools_info']['last_tool_status'] else "with errors"}, number of tool calls: {response['tools_info']['tool_calls']}")
                
        return response
