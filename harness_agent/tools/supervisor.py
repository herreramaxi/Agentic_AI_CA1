import logging

from langchain.tools import ToolRuntime, tool
from harness_agent.state import AgentContext

@tool
def request_supervisor(user_query: str, runtime: ToolRuntime[AgentContext]):
    """Return the supervisor example only when no available skill description matches the customer query.
    Do not call this tool when a skill matches; call `load_skill` instead.

    Args:
        user_query (str): The exact user query to get an example response for
    """
    
    reference_answer = f"Example response: {runtime.context.reference_answer}"
    logging.info(f"Supervisor called")
    logging.debug(f"reference_answer: {reference_answer}")
    
    return reference_answer   