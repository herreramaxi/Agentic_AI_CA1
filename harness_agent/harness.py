from dataclasses import dataclass
from typing import Any

from langchain.agents import create_agent
from langchain.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage

from harness_agent.middleware.skill_middleware import SkillMiddleware
from harness_agent.state import AgentContext, TrainingState
from harness_agent.tools.supervisor import request_supervisor
from harness_agent.skills.tools import create_skill
from llm import get_llm

SKILL_CREATOR_PROMPT = """
You are a skill creation agent responsible for improving
a customer service assistant.

You will receive:
- A customer query
- A reference answer provided by a supervisor

Your only action is to call the tool named create_skill.
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

Create exactly one focused, reusable skill via create_skill.
"""

@dataclass
class AgentHarness:
    model: BaseChatModel
    training_dataset : Any |None = None
    training_mode: bool = False
    agent: Any | None = None 
    system_prompt: str | None = None
        
    def __post_init__(self):
        if not self.system_prompt:            
            self.system_prompt = "You are a helpful assistant."

        tools = []
        if self.training_mode:
            tools.append(request_supervisor)
            self.skills_creator_agent = create_agent(
                model=self.model,
                tools=[create_skill],
                system_prompt=SKILL_CREATOR_PROMPT,
            )
        self.agent = create_agent(
            model=self.model,        
            context_schema=AgentContext,
            state_schema=TrainingState,
            # tools= [sm.load_skill, self.request_supervisor],
            tools= tools,
            middleware=[SkillMiddleware(training_mode =self.training_mode)],
            system_prompt=self.system_prompt,
        )

    def get_reference_answer(self, query):
        matches = self.training_dataset.loc[self.training_dataset["instruction"].eq(query), "response"]
        reference_answer = matches.iloc[0] if not matches.empty else "N/A"
        return reference_answer

    def invoke(self, query: str):
        reference_answer = self.get_reference_answer(query) if self.training_mode else ""
        context = AgentContext(reference_answer)
        humman_message = HumanMessage(query)
        messages = [humman_message]
        response = self.agent.invoke(
            {   
                'messages': messages, 
                'supervisor_used': False
            }, 
            context= context
        )
        if response.get("supervisor_used", False):                    
            response_skill_creator = self.skills_creator_agent.invoke({
                "messages": [{
                    "role": "user",
                    "content": f"""Customer query:
                        {query}

                        Supervisor reference answer:
                        {reference_answer}
                        """
                            }]
             })
            print("response_skill_creator:")
            print(response_skill_creator)
                        

        return response
