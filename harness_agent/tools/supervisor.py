import logging

from langchain.tools import ToolRuntime, tool
from harness_agent.state import AgentContext

@tool
def request_supervisor(user_query: str, runtime: ToolRuntime[AgentContext]):
    """REQUIRED fallback: get an example response when no available skill matches the user query.
    Call this for orders, payments, tickets, account data, or any domain question with no matching skill.
    Do not answer those questions yourself without calling this tool first.

    Args:
        user_query (str): The exact user query to get an example response for
    """
    
    reference_answer = f"Example response: {runtime.context.reference_answer}"
    logging.info(f"Supervisor called")
    logging.debug(f"reference_answer: {reference_answer}")
    
    return reference_answer   