from dataclasses import dataclass
import logging
from typing import Any
from langchain.chat_models import BaseChatModel
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from general import get_tools_info
from harness_agent.skills.manager import SkillsManager
from harness_agent.skills.tools import create_skill, load_skill

SYSTEM_PROMPT_old = """You create one skill from a supervisor example for the customer service assistant.

Call create_skill once. Do not answer with plain text.

name: a short kebab-case name
description: one sentence saying when to use the skill
content: the steps from the example, so they can be reused later. Keep placeholders such as {{Order Number}} as they are. Do not add anything that is not in the example, and do not copy the customer's exact words.
"""

SYSTEM_PROMPT_o1 = """You create or update one skill from a supervisor example for the customer service assistant.

Before creating a skill, check whether an existing skill can be improved or reused.

## Inputs
The user message contains:
- the existing skills, as name and description only
- the customer query
- the supervisor example

## What to do
- Compare the query and the example with those descriptions.
- If one skill might apply, call load_skill with that exact name and read its steps.
- If the existing skill already covers the example, do not modify it.
- If they are close but incomplete, call create_skill with the same name and the improved steps.
- If none apply, call create_skill once with a new skill.

## Skill fields
- name: a short kebab-case name
- description: one sentence saying when to use the skill
- content: the steps from the example, so they can be reused later. Keep placeholders such as {{Order Number}} as they are. Do not add anything that is not in the example, and do not copy the customer's exact words.

Call load_skill only for a name from the list. Call create_skill once. Do not answer with plain text.
"""

SYSTEM_PROMPT = """You create or update one skill from a supervisor example for the customer service assistant.
Before creating a skill, check whether an existing skill can be improved or reused.

## Inputs
The user message contains:
- the existing skills, as name and description only
- the customer query
- the supervisor example

## What to do
- Compare the query and the example with those descriptions.
- If one skill might apply, call load_skill with that exact name and read its steps.
- If those steps already cover the example, stop. Do not call create_skill.
- If they are close but incomplete, call create_skill once with the same name. Keep the existing steps and add only what this example is missing.
- If none apply, call create_skill once with a new name.

## Skill fields
- name: a short kebab-case name. Reuse the existing name when improving a skill.
- description: one sentence saying when to use the skill
- content: reusable steps. Keep placeholders such as {{Order Number}} as they are. Do not copy the customer's exact words.

Call load_skill only for a name from the list. Do not answer with plain text."""

@dataclass
class SkillsCreatorAgent:
    model: BaseChatModel
    agent: Any | None = None 
    
    def __post_init__(self)-> None:
        self.agent = create_agent(
                model=self.model,
                tools=[load_skill, create_skill],
                system_prompt=SYSTEM_PROMPT,
        )

    def invoke(self, query: str, reference_answer: str):
        existing_skills = SkillsManager().get_skill_first_level_descriptions()
        message = HumanMessage(f"""Existing skills:
{existing_skills}
                               
Customer query:
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

