from dataclasses import dataclass, field
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
    message_history: list[str] = field(default_factory=list)
    
    def __post_init__(self) -> None:
        logging.info(f"Initializing AgentHarness - training_mode: {self.training_mode}, agentic_memory_disabled: {self.agentic_memory_disabled}")

        if not self.system_prompt:            
            self.system_prompt = "You are a helpful customer service assistant."

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

    def invoke(self, input :str):
        reference_answer = self.get_reference_answer(input) if self.training_mode else ""
        context = AgentContext(reference_answer)
        humman_message = HumanMessage(input)
         
        if self.training_mode:
            messages = [humman_message]
        else:
            self.message_history.append(humman_message)
            messages = self.message_history
               
        response = self.agent.invoke({ 'messages': messages}, context= context)
        ai_response = response["messages"][-1]
        ai_response_text = ai_response.text           
        
        if self.training_mode:            
            if was_tool_called(response, "request_supervisor"):
                self.skills_creator.invoke(input, reference_answer)
            self.guidelines_optimizer.invoke(input, ai_response_text, reference_answer)
        else:
            self.message_history.append(ai_response)
                        
        response['content'] = response['text'] = ai_response_text
        logging.info(f"Harness Response: {response['text']}")

        return response
