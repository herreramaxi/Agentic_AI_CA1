from dataclasses import dataclass
import logging
from typing import Any
from langchain.chat_models import BaseChatModel
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from general import get_tools_info
from harness_agent.skills.manager import SkillsManager
from harness_agent.skills.tools import create_skill, load_skill

SYSTEM_PROMPT = """You create or refine one reusable customer-service skill from a supervisor example.

You MUST finish by calling `create_skill` exactly once.
The only valid tools are `load_skill` and `create_skill`.
Use `load_skill` only to inspect one existing skill that covers the same task.
Do not call `set_skill` or invent another tool name.
Do not return only a plain-text answer.

You will receive the customer query, supervisor reference answer, and the names and descriptions of existing skills.

If an existing description covers the same task:
1. Call `load_skill` with that exact name.
2. Merge the reusable procedure from the existing skill and the new reference.
3. Prefer the richer procedure: if this reference adds ordered steps, placeholders, or support channels missing from the existing skill, add them.
4. Call `create_skill` with the same name to replace the skill with the improved version.

If no existing description covers the task, call `create_skill` with a new name.

Tool arguments:
- name: concise kebab-case name for the demonstrated task; reuse the existing name when refining
- description: one sentence defining when the service agent should load it
- content: Markdown procedure card for handling similar future queries

Content rules:
1. Extract the reusable procedure from the supervisor reference. If the reference has ordered steps, keep them as ordered steps in the skill.
2. Keep placeholders exactly as in the reference (for example {{Order Number}}, {{Online Company Portal Info}}, {{Online Order Interaction}}, {{Customer Support Hours}}, {{Customer Support Phone Number}}, {{Website URL}}).
3. Preserve the reference response type (give self-serve steps vs ask for a clarifying detail vs escalate).
4. Generalize from the example; do not include the customer's exact wording as a special case.
5. Include only facts, steps, channels, and constraints supported by the reference. Do not invent merchants, policies, deadlines, eligibility rules, or contact details that are not in the reference.
6. Do NOT replace a detailed reference with only "acknowledge the request" or "do not provide unsupported steps". If the reference gives a procedure, the skill must teach that procedure.
7. Prefer this short structure: when to use → steps → optional support/escalation taken from the reference.
8. Keep tone guidance brief; general interaction style belongs in AGENT.md.
"""

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
        skill_descriptions = SkillsManager().get_skill_first_level_descriptions()
        
        message = HumanMessage(f"""Existing skills:
        {skill_descriptions}

        Customer query:
        {query}

        Supervisor reference answer:
        {reference_answer}

        Use `load_skill` only if an existing description covers the same task.
        If refining an existing skill, merge in any steps, placeholders, or support channels from this reference that are missing.
        Finish by calling `create_skill` exactly once.
        Do not use other tool names.""")
        
        response = self.agent.invoke(
             {
                 "messages": [message]
             }
        )
        
        response['tools_info'] = get_tools_info(response, 'create_skill')

        logging.debug(f"response: {response}")  
        logging.info(f"SkillsCreatorAgent executed {'successfully' if response['tools_info']['last_tool_status'] else "with errors"}, number of tool calls: {response['tools_info']['tool_calls']}")
                
        return response

