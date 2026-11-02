from langchain.tools import tool
from harness_agent.guidelines.manager import GuidelinesManager

@tool
def update_guidelines(new_guidelines: str) -> str:
    """Replace AGENT.md with the full guideline list.
    At most 10 lines, like: 1. instruction - short reason

    Args:
        new_guidelines: The full list to save.
    """  
    gm = GuidelinesManager()        
    return gm.update_guidelines(new_guidelines)    