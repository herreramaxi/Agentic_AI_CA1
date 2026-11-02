from langchain.tools import tool
from harness_agent.skills.manager import SkillsManager

@tool
def load_skill(skill_name: str) -> str:
    """Get the content of a skill given the skill name.
    The name must be copied from the Available Skills list.
    Args:
        skill_name (str): The name of the skill to get the content of.
    """     
    sm = SkillsManager()        
    return sm.GetSkillContent(skill_name)    

@tool
def create_skill(name: str, description: str, content: str) -> str:
    """Create a skill, or replace the skill with this name if it already exists.
    Args:
        name: kebab-case name
        description: when the assistant should load this skill
        content: markdown steps taken from the supervisor example
    """
    sm = SkillsManager()
    skill_path_created = str(sm.create_skill(name, description, content))

    return f"Skill successfully created on path: {skill_path_created}"