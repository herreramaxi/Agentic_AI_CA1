import logging
import os
from pathlib import Path
import re
import yaml

##ref: https://github.com/langchain-ai/deepagents/blob/e80fd67dfaf5ef19f11a64c5d039f18b8b0c7b27/libs/deepagents/deepagents/middleware/skills.py#L168
#Regex to parse the skills header
_FRONTMATTER_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

SKILLS_SYSTEM_PROMPT = """## Skills System

You have access to a skills library that provides specialized capabilities and domain knowledge.

Skills Location: {skills_location}

**Available Skills:**

{skills_list}

**How to Use Skills (Progressive Disclosure):**

Skills follow a **progressive disclosure** pattern - you see their name and description above, but only read full instructions when needed:

1. **Recognize when a skill applies**: Check if the user's task matches a skill's description
2. **Read the skill's full instructions**: Use `load_skill` tool passing as parameter the name shown in the skill list above.
3. **Follow the skill's instructions**: SKILL.md contains step-by-step workflows, best practices, and examples

**When to Use Skills:**

- Only when there are Skills available
- User's request matches a skill's domain (e.g., "research X" -> web-research skill)
- You need specialized knowledge or structured workflows
- A skill provides proven patterns for complex tasks

**Example Workflow (skill match):**

User: "Can you research the latest developments in quantum computing?"

1. Check available skills -> See a matching research skill
2. Read the full skill file: `load_skill(skill_name="...")`
3. Follow the skill's research workflow

Remember: Skills make you more capable and consistent. When in doubt, check if a skill exists for the task!
"""

NO_SKILL_PROMPT_TRAINING ="""
**When No Relevant Skill Exists or no Skills are available (MANDATORY):**

You MUST call the `request_supervisor` tool with the user's query BEFORE answering.
Do NOT answer from your own knowledge, guess, or say you lack access — call the tool first, then base your reply on its result.

**Example Workflow (no skill match):**
User: "do you have info about order 1234?"

1. Check available skills -> none match orders/tickets
2. MUST call: `request_supervisor(user_query="do you have info about order 1234?")`
3. Answer using the supervisor example — do not skip this step

Remember: When in doubt whether a skill applies, call `request_supervisor`. Never skip it for domain questions with no matching skill.
"""

NO_SKILL_PROMPT_INFERENCE ="""
**When No Relevant Skill Exists or no Skills are available:**
1. Respond to the user the best as you can with your knowledge.
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
            
    def generate_system_prompt(self, training_mode: bool = False):
        skills_first_level = self.load_skills()
        any_skill = len(skills_first_level) > 0

        if(not any_skill):
            skills_list= f"(No skills available yet. You can create skills in '{self.skills_location}' folder)"
        else:
            skills_list = ""

        for skill in skills_first_level:
            formatted_skill = f"- **{skill["name"]}**: {skill["description"]}\n  -> Read `{skill["skill_path"]}` for full instructions\n"
            # print(formatted_skill)
            skills_list +=formatted_skill

        system_prompt =  SKILLS_SYSTEM_PROMPT.format(
            skills_location = self.skills_location,
            skills_list = skills_list
        )

        skill_not_found_prompt = NO_SKILL_PROMPT_TRAINING if training_mode else NO_SKILL_PROMPT_INFERENCE
        system_prompt+=skill_not_found_prompt
        
        return system_prompt

    def GetSkillContent(self, skill_name: str) -> str:        
        base_dir = Path(self.skills_location)    
        skill_path = base_dir / skill_name / 'SKILL.md'
        skill_content = skill_path.read_text(encoding="utf-8")

        return skill_content

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