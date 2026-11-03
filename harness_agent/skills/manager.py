import logging
import os
from pathlib import Path
import re
import yaml

#ref: https://github.com/langchain-ai/deepagents/blob/e80fd67dfaf5ef19f11a64c5d039f18b8b0c7b27/libs/deepagents/deepagents/middleware/skills.py#L168
#Regex to parse the skills header
_FRONTMATTER_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

#based on: https://github.com/langchain-ai/deepagents/blob/e80fd67dfaf5ef19f11a64c5d039f18b8b0c7b27/libs/deepagents/deepagents/middleware/skills.py#L873
SKILLS_SYSTEM_PROMPT = """## Skills System

You have access to a skills library that provides specialized capabilities and domain knowledge.

**Available Skills:**
{skills_list}

**How to Use Skills (Progressive Disclosure):**

Skills follow a progressive disclosure pattern: you see each skill's name and description above, but you read its full instructions only when needed.

1. **Recognize when a skill applies**: compare the user's request with the available skill descriptions.
2. **Load the full instructions**: call 'load_skill' with the exact skill name from the 'Available Skills' list.
3. **Follow the skill**: use the returned instructions to answer the request.

**When to Use Skills:**

- Only when the Available Skills list contains a skill
- The user's request matches one of those descriptions
- A skill matches only when both the situation and the kind of reply in its description fit the customer

Important:
- Call load_skill only with a name copied from the Available Skills list.
- If the list says no skills are available, or none of the descriptions match, do not call load_skill and do not invent a name.
- Do not try to open a skill file yourself.
"""

NO_SKILL_PROMPT_TRAINING = """
If no skill in the list matches, call request_supervisor before you answer.
Answer in your own words from that example. Do not copy it line by line.
"""

NO_SKILL_PROMPT_INFERENCE = """
If no skill in the list matches, answer the customer as well as you can.
"""

class SkillsManager: 
    skills_location:str = ""

    def __init__(self, skills_location= "./skills"):
        self.skills_location = skills_location        
    
    def load_skills(self):
        skills = []
        
        # folders= os.walk(self.skills_folder)
        if(not os.path.isdir(self.skills_location)):
            logging.warning(f"There is not skills folder on: {self.skills_location}")
            return skills

        base_dir = Path(self.skills_location)    
   
        for item in base_dir.iterdir():                       
            if not item.is_dir():
                logging.warning(f"Skill not found on: {skill_path}")
                continue
            skill_file_name = item.name  
            skill_file_content = "N/A"
            skill_path = item / "SKILL.md"
            
            if not skill_path.is_file():
                logging.warning(f"Skill not found on: {skill_path}")
                continue
            skill_file_content = skill_path.read_text(encoding="utf-8")
          
            match = _FRONTMATTER_PATTERN.match(skill_file_content )
            if not match:
                logging.warning(f"Skill does not complies with standard SKILL header format: {skill_path}")
                continue

            skill_header = match.group(1)
            data = yaml.safe_load(skill_header)
            skill_header_name = data.get("name", "").strip()
            skill_header_description = data.get("description", "").strip()

            if(not skill_header_name or not skill_header_description):
                logging.warning(f"Skill name and description fileds are mandatory: {skill_path}")
                continue

            if skill_header_name != skill_file_name:
                logging.warning(f"There is a mistmatch between skill folder name and skill header name: {skill_path}")
                continue

            skills.append({
                "name": skill_header_name,
                 "description":   skill_header_description,
                 "skill_path": skill_path,
                 "file_content": skill_file_content
                })

        return skills
            
    def get_skill_first_level_descriptions(self):        
        skills_first_level = self.load_skills()
        any_skill = len(skills_first_level) > 0

        if(not any_skill):
            skills_list= f"(No skills available yet)"
        else:
            skills_list = ""

        for skill in skills_first_level:
            formatted_skill = f"- **{skill["name"]}**: {skill["description"]}\n"            
            skills_list +=formatted_skill

        return skills_list
    
    def generate_system_prompt(self, training_mode: bool = False):
        skills_list = self.get_skill_first_level_descriptions()
        fallback = NO_SKILL_PROMPT_TRAINING if training_mode else NO_SKILL_PROMPT_INFERENCE
        return SKILLS_SYSTEM_PROMPT.format(skills_list=skills_list) + fallback

    def GetSkillContent(self, skill_name: str) -> str:
        skill_path = Path(self.skills_location) / skill_name / "SKILL.md"
        if not skill_path.is_file():
            return f"No skill named {skill_name}. Use a name from the Available Skills list."
        return skill_path.read_text(encoding="utf-8")

    #Ref: Based on agent_skills_utils.py
    def create_skill(self,
        name: str,
        description: str,
        content: str
    ) -> Path:
        """
        Create an agent skill directory with a SKILL.md file.
        
        Args:
            name: The skill name (used for directory name and YAML frontmatter)
            description: Brief description of the skill's purpose (appears in YAML frontmatter)
            content: The markdown content of the skill
            
        Returns:
            Path to the created SKILL.md file
            
        Example:
            >>> create_skill(
            ...     name="python-testing",
            ...     description="Write and run Python unit tests with pytest",
            ...     content="# Python Testing\\n\\nUse pytest for unit testing..."
            ... )
        """

        base_dir = Path(self.skills_location)
        skill_dir = base_dir / name
        skill_dir.mkdir(parents=True, exist_ok=True)
        
        # Escape description if it contains special YAML characters
        escaped_description = description
        if ':' in description or '"' in description or "'" in description:
            # Quote and escape the description
            escaped_description = description.replace('"', '\\"')
            escaped_description = f'"{escaped_description}"'
        
        # Create SKILL.md content with YAML frontmatter
        skill_content = f"""---\nname: {name}\ndescription: {escaped_description}\n---\n\n{content}"""
        
        # Write SKILL.md file
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text(skill_content, encoding='utf-8')
        
        return skill_file 