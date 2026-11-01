from langchain.agents.middleware import AgentState, ModelRequest, ModelResponse, AgentMiddleware, Runtime
from langchain.messages import SystemMessage
from typing import Any, Callable
from dataclasses import dataclass, field

from harness_agent.skills.manager import SkillsManager
from harness_agent.skills.tools import load_skill

#ref: Based on https://docs.langchain.com/oss/python/langchain/multi-agent/skills-sql-assistant#view-complete-skill-definitions
@dataclass
class SkillMiddleware(AgentMiddleware):
    """Middleware that injects skill descriptions into the system prompt."""
    
    skills_location:str = "./skills"
    training_mode: bool = False          
    skills: list[Any] = field(default_factory=list)
    
    # Register the load_skill tool as a class variable
    tools = [load_skill]            

    # def before_agent(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    #     print(f"before_agent {len(state['messages'])} messages")        

    #     # self.skills = self.load_skills_from_folder()
    #     return
    
    def wrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        """Sync: Inject skill descriptions into system prompt."""
        sm = SkillsManager(self.skills_location)
        skills_addendum = sm.generate_system_prompt(self.training_mode)
        # Append to system message content blocks
        new_content = list(request.system_message.content_blocks) + [
            {"type": "text", "text": skills_addendum}
        ]
        new_system_message = SystemMessage(content=new_content)
        modified_request = request.override(system_message=new_system_message)
        return handler(modified_request)
