from dataclasses import dataclass
from typing import Any

from langchain.agents import create_agent
from langchain.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage

from harness_agent.agents.guidelines_optimizer_agent import GuidelinesOptimizerAgent
from harness_agent.agents.skills_creator_agent import SkillsCreatorAgent
from harness_agent.middleware.guidelines_middleware import GuidelinesMiddleware
from harness_agent.middleware.skill_middleware import SkillMiddleware
from harness_agent.state import AgentContext, TrainingState
from harness_agent.tools.supervisor import request_supervisor
from harness_agent.skills.tools import create_skill
from llm import get_llm


@dataclass
class AgentHarness:
    model: BaseChatModel
    training_dataset : Any |None = None
    training_mode: bool = False
    agent: Any | None = None 
    skills_creator: SkillsCreatorAgent | None = None 
    guidelines_optimizer: GuidelinesOptimizerAgent | None = None 
    system_prompt: str | None = None
        
    def __post_init__(self) -> None:
        if not self.system_prompt:            
            self.system_prompt = "You are a helpful assistant."

        tools = []
        if self.training_mode:
            tools.append(request_supervisor)
            self.skills_creator = SkillsCreatorAgent(model=self.model)
            self.guidelines_optimizer = GuidelinesOptimizerAgent(model=self.model)

        self.agent = create_agent(
            model=self.model,        
            context_schema=AgentContext,
            state_schema=TrainingState,
            # tools= [sm.load_skill, self.request_supervisor],
            tools= tools,
            middleware=[SkillMiddleware(training_mode =self.training_mode), GuidelinesMiddleware()],
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

        print(response)
        if self.training_mode and response.get("supervisor_used", False):                    
            response_skill_creator = self.skills_creator.invoke(query,reference_answer)
            print("response_skill_creator:")
            print(response_skill_creator)

        if self.training_mode:
            agent_response = response["messages"][-1].content
            self.guidelines_optimizer.invoke(query, agent_response, reference_answer)

        return response
