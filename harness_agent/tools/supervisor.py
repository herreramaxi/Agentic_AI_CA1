import logging

from langchain.tools import ToolRuntime, tool
from harness_agent.state import AgentContext

@tool
def request_supervisor(user_query: str, runtime: ToolRuntime[AgentContext]):
    """Ask the supervisor for an example response to this customer query.

    Args:
        user_query (str): The customer query
    """
    
    reference_answer = f"Example response: {runtime.context.reference_answer}"
    logging.info(f"Supervisor called")
    logging.debug(f"reference_answer: {reference_answer}")
    
    return reference_answer   