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
    """Create a skill directory with a SKILL.md file.

    Args:
        name: Skill id (directory name and YAML frontmatter name), kebab-case.
        description: Brief description of when to use the skill.
        content: Markdown body with instructions for the assistant.
    """
    sm = SkillsManager()
    return str(sm.create_skill(name, description, content))