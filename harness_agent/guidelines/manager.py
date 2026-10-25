from dataclasses import dataclass

@dataclass
class GuidelinesManager:    
    guidelines_file_path: str = "./AGENT.md"
    
    def read_guidelines(self):      
        with open(self.guidelines_file_path, "r",encoding="utf-8") as content:          
            guidelines = content.read()
            
        return guidelines
    
    def update_guidelines(self, new_guidelines: str):      
        with open(self.guidelines_file_path, "w",encoding="utf-8") as content:
            content.write(new_guidelines)
        
        return "Guidelines successfully updated" 

    def generate_system_prompt(self):
        guidelines = self.read_guidelines().strip() or "N/A"
        guidelines_prompt = f"Additionally, here you have a top 10 Guidelines for interactions with the user: \n{guidelines}"
     
        return guidelines_prompt