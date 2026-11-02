from langchain.tools import tool
from harness_agent.skills.manager import SkillsManager

@tool
def load_skill(skill_name: str) -> str:
    """Get the content of a skill given the skill name.
    Args:
        skill_name (str): The name of the skill to get the content of.
    """     
    sm = SkillsManager()        
    return sm.GetSkillContent(skill_name)    

@tool
def create_skill(name: str, description: str, content: str) -> str:
    """Create or replace one customer-service skill. This tool's exact name is `create_skill`
    Args:
        name: Concise kebab-case name for the demonstrated task. Reuse the existing name when refining that skill.
        description: One sentence explaining when the service agent should load the skill.
        content: Reusable Markdown instructions based only on the reference; retain its abstract fields and exclude unsupported facts.
    """
    sm = SkillsManager()
    skill_path_created = str(sm.create_skill(name, description, content))

    return f"Skill successfully created on path: {skill_path_created}"