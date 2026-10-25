from langchain.agents.middleware import AgentState, ModelRequest, ModelResponse, AgentMiddleware, Runtime
from langchain.messages import SystemMessage
from typing import Any, Callable
from dataclasses import dataclass
from harness_agent.guidelines.manager import GuidelinesManager

@dataclass
class GuidelinesMiddleware(AgentMiddleware):
    """Middleware that injects Guidelines into the system prompt."""
    
    # # Register the load_skill tool as a class variable
    # tools = [load_skill]            

    def before_agent(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        print(f"before_agent {len(state['messages'])} messages")        

        return
    
    def wrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        """Sync: Inject Guidelines into system prompt."""
        manager = GuidelinesManager()
        guidelines_addendum = manager.generate_system_prompt()
        # Append to system message content blocks
        new_content = list(request.system_message.content_blocks) + [
            {"type": "text", "text": guidelines_addendum}
        ]
        new_system_message = SystemMessage(content=new_content)
        modified_request = request.override(system_message=new_system_message)
        return handler(modified_request)
