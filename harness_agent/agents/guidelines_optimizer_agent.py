from dataclasses import dataclass
import logging
from typing import Any
from langchain.chat_models import BaseChatModel
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from general import get_tools_info
from harness_agent.guidelines.manager import GuidelinesManager
from harness_agent.guidelines.tools import update_guidelines

SYSTEM_PROMPT = """You maintain a top 10 list of customer-service guidelines.

Workflow:
1. For a user query, compare the agent's response with the supervisor reference answer. Review the response type, tone, clarity, and level of detail. Identify what should be kept, improved, or avoided.
2. Give the response a style score from 1 to 10 with a short reason.
3. Use the comparison to improve the Current Top 10 Guidelines.
4. Call `update_guidelines` once with the full replacement list.

Recommendations:
* Keep the guidelines short and general. 
* Include lessons about the wrong kind of response or unsuitable tone when relevant. 
* Keep task-specific procedures in skills.

IMPORTANT: 
* Use no more than 10 lines in this format: [#]. [Instruction] - [Brief rationale]
* Do not put the style score in the guidelines.
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
