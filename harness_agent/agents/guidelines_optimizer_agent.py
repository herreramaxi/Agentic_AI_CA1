from dataclasses import dataclass
import logging
from typing import Any
from langchain.chat_models import BaseChatModel
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from general import get_tools_info
from harness_agent.guidelines.manager import GuidelinesManager
from harness_agent.guidelines.tools import update_guidelines

SYSTEM_PROMPT = """You keep AGENT.md, a list of at most 10 guidelines for how the assistant should respond.

Your task is to refine that list from the latest turn while keeping the most valuable existing guidelines.

## Inputs
The user message contains:
- the current guidelines
- the customer query
- the assistant reply
- the supervisor example

## What to judge
Compare the assistant reply with the supervisor example on:
- tone
- kind of reply: ask a question, answer directly, or pass it on

Leave concrete steps and intent-specific procedures to the skills.

## How to update
- Keep a guideline that is still useful.
- Revise or add a guideline only when this turn shows it would improve future replies.
- If nothing should change, return the current list unchanged.

## Output
Return only the list. One guideline per line, at most 10:

[#]. [Imperative instruction] - [short reason]

Call update_guidelines once with that full list.
"""

@dataclass
class GuidelinesOptimizerAgent:
    model: BaseChatModel
    agent: Any | None = None 
    
    def __post_init__(self)-> None:
        self.agent = create_agent(
                model=self.model,
                tools=[update_guidelines],                
                system_prompt=SYSTEM_PROMPT
        )

    def invoke(self, query: str, agent_response: str, reference_answer: str):    
        current_guidelines = GuidelinesManager().read_guidelines()
        message = HumanMessage(f"""User query: {query}

Agent response:
{agent_response}

Supervisor reference answer:
{reference_answer}

Current guidelines:
{current_guidelines}""")
        
        response = self.agent.invoke(
             {
                 "messages": [message]
             }
        )

        response['tools_info'] = get_tools_info(response, 'update_guidelines')

        logging.debug(f"response: {response}")  
        logging.info(f"GuidelinesOptimizerAgent executed {'successfully' if response['tools_info']['last_tool_status'] else "with errors"}, number of tool calls: {response['tools_info']['tool_calls']}")
       
        return response
