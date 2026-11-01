from dataclasses import dataclass
from typing import Any
from langchain.agents import create_agent
from langchain.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage
from general import was_tool_called
from harness_agent.agents.guidelines_optimizer_agent import GuidelinesOptimizerAgent
from harness_agent.agents.skills_creator_agent import SkillsCreatorAgent
from harness_agent.middleware.guidelines_middleware import GuidelinesMiddleware
from harness_agent.middleware.skill_middleware import SkillMiddleware
from harness_agent.state import AgentContext
from harness_agent.tools.supervisor import request_supervisor
import logging

@dataclass
class AgentHarness:
    model: BaseChatModel
    training_dataset : Any |None = None
    training_mode: bool = False
    agentic_memory_disabled: bool = False
    agent: Any | None = None 
    skills_creator: SkillsCreatorAgent | None = None 
    guidelines_optimizer: GuidelinesOptimizerAgent | None = None 
    system_prompt: str | None = None
        
    def __post_init__(self) -> None:
        logging.info(f"Initializing AgentHarness - training_mode: {self.training_mode}, agentic_memory_disabled: {self.agentic_memory_disabled}")

        if not self.system_prompt:            
            self.system_prompt = "You are a helpful assistant."

        tools = []
        if self.training_mode:
            tools.append(request_supervisor)
            self.skills_creator = SkillsCreatorAgent(model=self.model)
            self.guidelines_optimizer = GuidelinesOptimizerAgent(model=self.model)

        middlewares = [SkillMiddleware(training_mode=self.training_mode), GuidelinesMiddleware()] if not self.agentic_memory_disabled else[]
       
        logging.debug(f"Tools: {", ".join( [tool.name for tool in tools]) if tools else "N/A"}")
        logging.debug(f"Middlewares: {", ".join( [m.name for m in middlewares]) if middlewares else "N/A"}")

        self.agent = create_agent(
            model=self.model,        
            context_schema=AgentContext,
            # state_schema=TrainingState,
            # tools= [sm.load_skill, self.request_supervisor],
            tools= tools,
            middleware=middlewares,
            system_prompt=self.system_prompt,
        )

    def get_reference_answer(self, query):
        matches = self.training_dataset.loc[self.training_dataset["instruction"].eq(query), "response"]
        reference_answer = matches.iloc[0] if not matches.empty else "N/A"

        logging.debug(f"reference_answer: {reference_answer}")  

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
        final_message = response["messages"][-1]
        agent_response = final_message.text           
        
        if self.training_mode and was_tool_called(response, 'request_supervisor'):     
            self.skills_creator.invoke(query,reference_answer)  

        if self.training_mode:
            self.guidelines_optimizer.invoke(query, agent_response, reference_answer)
            
        response['content'] = response['text'] = agent_response
        logging.info(f"Harness Response: {response['text']}")

        return response
