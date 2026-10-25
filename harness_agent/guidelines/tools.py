from langchain.tools import tool
from harness_agent.guidelines.manager import GuidelinesManager

@tool
def update_guidelines(new_guidelines: str) -> str:
    """Update content of guidelines
    Args:
        new_guidelines (str): The new content of guidelines
    """     
    gm = GuidelinesManager()        
    return gm.update_guidelines(new_guidelines)    