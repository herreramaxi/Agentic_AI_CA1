from dataclasses import dataclass
from typing import Any
from langchain.chat_models import BaseChatModel
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from harness_agent.skills.tools import create_skill

SYSTEM_PROMPT = """
You are a skill creation agent responsible for improving a customer service assistant.
You will receive:
- A customer query
- A reference answer provided by a supervisor

You MUST call the tool named 'create_skill'.
Do not invent other tool names. Do not answer in plain text.

Tool arguments:
- name: short kebab-case skill id (e.g. payment-options-inquiry)
- description: one-line summary of when to use the skill
- content: Markdown instructions for handling similar queries

Instructions for the skill content:
1. Identify the general task demonstrated by the example.
2. Write clear, actionable Markdown the assistant can follow later.
3. Preserve important facts, rules, and constraints from the reference.
4. Do not invent policies not supported by the example.
5. Do not include customer-specific details unless needed for a general procedure.

Create exactly one focused, reusable skill via 'create_skill' tool.
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
        response = self.agent.invoke(
             {
                 "messages": [
                     HumanMessage(f"""Customer query: {query}
                     Supervisor reference answer:
                     {reference_answer}""")
                     ]
             }
        )
        return response
      
