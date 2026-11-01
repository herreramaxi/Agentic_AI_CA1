from dataclasses import dataclass
from pathlib import Path

@dataclass
class GuidelinesManager:    
    guidelines_file_path: str = "./AGENT.md"
    
    def read_guidelines(self):     
        #if file agent.md does not exist just create an empty one 
        Path(self.guidelines_file_path).touch(exist_ok=True)

        with open(self.guidelines_file_path, "r",encoding="utf-8") as content:          
            guidelines = content.read()
            
        return guidelines.strip() or "N/A"
    
    def update_guidelines(self, new_guidelines: str):      
        with open(self.guidelines_file_path, "w",encoding="utf-8") as content:
            num_characters= content.write(new_guidelines)
        
        return f"Guidelines successfully updated, number of characters written: {num_characters}" 

    def generate_system_prompt(self):
        guidelines = self.read_guidelines()
        guidelines_prompt = f"Additionally, here you have a top 10 Guidelines for interactions with the user: \n{guidelines}"
     
        return guidelines_prompt