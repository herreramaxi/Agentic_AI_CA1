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
        print(f"Initializing AgentHarness - training_mode: {self.training_mode}, agentic_memory_disabled: {self.agentic_memory_disabled}")
        if not self.system_prompt:            
            self.system_prompt = "You are a helpful assistant."

        tools = []
        if self.training_mode:
            tools.append(request_supervisor)
            self.skills_creator = SkillsCreatorAgent(model=self.model)
            self.guidelines_optimizer = GuidelinesOptimizerAgent(model=self.model)

        middlewares = [SkillMiddleware(training_mode =self.training_mode), GuidelinesMiddleware()] if not self.agentic_memory_disabled else[]
        print(f"middlewares: {len(middlewares)}")
        self.agent = create_agent(
            model=self.model,        
            context_schema=AgentContext,
            state_schema=TrainingState,
            # tools= [sm.load_skill, self.request_supervisor],
            tools= tools,
            middleware=middlewares,
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
        agent_response =  response["messages"][-1].content

        if self.training_mode and response.get("supervisor_used", False):                    
#TODO: Check this later
#             After the agent has responded your application will analyse the conversation to see if the agent
# needed help i.e. looked at the example response), and it will ingest the response as a skill to be
# used for similar queries in the future.
            response_skill_creator = self.skills_creator.invoke(query,reference_answer)        

        if self.training_mode:
            self.guidelines_optimizer.invoke(query, agent_response, reference_answer)
       
        print(f"------harness: {agent_response}")
        return {
            'agent_response': agent_response
        }
