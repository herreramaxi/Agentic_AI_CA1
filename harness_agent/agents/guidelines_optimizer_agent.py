from dataclasses import dataclass
import logging
from typing import Any
from langchain.chat_models import BaseChatModel
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from general import get_tools_info
from harness_agent.guidelines.manager import GuidelinesManager
from harness_agent.guidelines.tools import update_guidelines

SYSTEM_PROMPT = """You maintain a top 10 procedural guidelines. You must follow below workflow:
Workflow:
1. For a user query, compare the agent's response to the supervisor reference answer (style, tone, response type — what to keep / improve / avoid).
2. Reason about how to improve the Current Top 10 Guidelines.
3. Call update_guidelines once with a full replacement list (max 10).
Format each line as:
[#]. [Instruction] - [Brief rationale]
Do not invent other tools. Prefer improving the existing top 10 guidelines over growing the list.
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
        
        response = self.agent.invoke(
             {
                 "messages": [
                     HumanMessage(f"""User query: {query}
                     Agent Response: {agent_response}
                     Supervisor Reference Answer: {reference_answer}
                     Current Top 10 Guidelines: \n{current_guidelines}""")
                     ]
             }
        )

        response['tools_info'] = get_tools_info(response, 'update_guidelines')

        logging.debug(f"response: {response}")  
        logging.info(f"GuidelinesOptimizerAgent executed {'successfully' if response['tools_info']['last_tool_status'] else "with errors"}, number of tool calls: {response['tools_info']['tool_calls']}")
       
        return response
