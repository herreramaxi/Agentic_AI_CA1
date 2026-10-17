import os
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
2. **Read the skill's full instructions**: Use `load_skill` tool passing as parameter the path shown in the skill list above.
    Pass `limit=1000` since the default of 100 lines is too small for most skill files.
3. **Follow the skill's instructions**: SKILL.md contains step-by-step workflows, best practices, and examples

**When to Use Skills:**

- User's request matches a skill's domain (e.g., "research X" -> web-research skill)
- You need specialized knowledge or structured workflows
- A skill provides proven patterns for complex tasks

**Example Workflow:**

User: "Can you research the latest developments in quantum computing?"

1. Check available skills -> See "web-research" skill with its path
2. Read the full skill file: `load_skill(file_path="...", limit=1000)`
3. Follow the skill's research workflow (search -> organize -> synthesize)

Remember: Skills make you more capable and consistent. When in doubt, check if a skill exists for the task!"""


class SkillsManager:
    skills_location: str = ""

    def __init__(self, skills_location="skills"):
        self.skills_location = skills_location

    def load_first_level(self):
        # folders= os.walk(self.skills_folder)
        folders = os.listdir(self.skills_location)
        skills_first_level = []

        for folder in folders:
            skill_file_name = folder
            skill_file_content = "N/A"
            skill_path = os.path.join(self.skills_location, skill_file_name, "SKILL.md")

            if not os.path.isfile(skill_path):
                print(f"Skill not found on: {skill_path}")
                continue

            with open(skill_path) as file:
                skill_file_content = file.read()

            match = _FRONTMATTER_PATTERN.match(skill_file_content)
            if not match:
                print(f"Skill does not complies with standard SKILL header format: {skill_path}")
                continue

            skill_header = match.group(1)
            data = yaml.safe_load(skill_header)
            skill_header_name = data.get("name", "").strip()
            skill_header_description = data.get("description", "").strip()

            if not skill_header_name or not skill_header_description:
                print(f"Skill name and description fileds are mandatory: {skill_path}")
                continue

            if skill_header_name != skill_file_name:
                print(f"There is a mistmatch between skill folder name and skill header name: {skill_path}")
                continue

            skills_first_level.append({
                "name": skill_header_name,
                "description": skill_header_description,
                "skill_path": skill_path,
                "file_content": skill_file_content,
            })

        return skills_first_level

    def generate_first_level_prompt(self):       
        skills_first_level = self.load_first_level()
        skills_list = ""

        for skill in skills_first_level:
            formatted_skill = (
                f"- **{skill['name']}**: {skill['description']}\n"
                f"  -> Read `{skill['skill_path']}` for full instructions\n"
            )
            skills_list += formatted_skill

        return SKILLS_SYSTEM_PROMPT.format(
            skills_location=self.skills_location,
            skills_list=skills_list,
        )
