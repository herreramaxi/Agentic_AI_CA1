from langchain.tools import ToolRuntime, tool
from langchain_core.messages import ToolMessage
from langgraph.types import Command

from harness_agent.state import AgentContext, TrainingState

@tool
def request_supervisor(user_query: str, runtime: ToolRuntime[AgentContext, TrainingState]) -> Command:
    """REQUIRED fallback: get an example response when no available skill matches the user query.
    Call this for orders, payments, tickets, account data, or any domain question with no matching skill.
    Do not answer those questions yourself without calling this tool first.

    Args:
        user_query (str): The exact user query to get an example response for
    """
    
    reference_answer = f"Example response: {runtime.context.reference_answer}"
    print(f"request_supervisor: {user_query}, refeerence: {reference_answer}")
    # return reference_answer
    return Command(
        update={
            "supervisor_used": True,
            "messages": [
                ToolMessage(
                    content=reference_answer,
                    tool_call_id=runtime.tool_call_id
                )
            ]
        })
