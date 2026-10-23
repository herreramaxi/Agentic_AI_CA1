from langchain.agents.middleware import AgentState, ModelRequest, ModelResponse, AgentMiddleware, Runtime
from langchain.messages import SystemMessage
from typing import Any, Callable
from langchain.tools import tool
from skills_manager import SkillsManager
from dataclasses import dataclass

#ref: Based on https://docs.langchain.com/oss/python/langchain/multi-agent/skills-sql-assistant#view-complete-skill-definitions
@dataclass
class SkillMiddleware(AgentMiddleware):
    """Middleware that injects skill descriptions into the system prompt."""

    training_mode: bool = False

    #This does not look that belong to this class
    @tool
    def load_skill(skill_name: str) -> str:
        """Get the content of a skill given the skill name.
        Args:
            skill_name (str): The name of the skill to get the content of.
        """     
        sm = SkillsManager()        
        return sm.GetSkillContent(skill_name)    
        
    def before_agent(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        print(f"before_agent {len(state['messages'])} messages")        
        return
    
    # Register the load_skill tool as a class variable
    tools = [load_skill]

    # def __init__(self):
    #     """Initialize and generate the skills prompt from SKILLS."""
    #     # Build skills prompt from the SKILLS list
    #     skills_list = []
    #     for skill in SKILLS:
    #         skills_list.append(
    #             f"- **{skill['name']}**: {skill['description']}"
    #         )
    #     self.skills_prompt = "\n".join(skills_list)

    
    def wrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        """Sync: Inject skill descriptions into system prompt."""
        # Build the skills addendum
        # skills_addendum = (
        #     f"\n\n## Available Skills\n\n{self.skills_prompt}\n\n"
        #     "Use the load_skill tool when you need detailed information "
        #     "about handling a specific type of request."
        # )

        sm= SkillsManager()
        _, skills_addendum = sm.generate_first_level_prompt(self.training_mode)
        # Append to system message content blocks
        new_content = list(request.system_message.content_blocks) + [
            {"type": "text", "text": skills_addendum}
        ]
        new_system_message = SystemMessage(content=new_content)
        modified_request = request.override(system_message=new_system_message)
        return handler(modified_request)
