from langchain.tools import tool
from harness_agent.guidelines.manager import GuidelinesManager

@tool
def update_guidelines(new_guidelines: str) -> str:
    """Replace AGENT.md with the complete guideline list.
    Use at most 10 short, general points in this format: [#]. [Instruction] - [Brief rationale]
    
    Args:
        new_guidelines: The complete list to save.
    """  
    gm = GuidelinesManager()        
    return gm.update_guidelines(new_guidelines)    