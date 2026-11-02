def get_tools_info(response, tool_name):
    tools_called = get_tool_Calls(response, tool_name)
    last_tool = tools_called[-1] if tools_called else None
    last_tool_status = last_tool.status if last_tool else 'N/A'
    tool_calls = len(tools_called)

    tools_info = {
        'tool_calls': tool_calls,
        'last_tool_status': last_tool_status
    }      

    return tools_info

def was_tool_called(response, tool_name):
    tools_called = get_tool_Calls(response, tool_name)
    return any(tools_called)
    
def get_tool_Calls(response, tool_name):
    tool_calls =[m for m in response['messages'] if getattr(m, 'type') == 'tool' and m.name == tool_name]

    return tool_calls

import os
from pathlib import Path
import shutil
def clean_agentic_memory():
    logging.info("Cleaning agentic memory...")
    logging.info(" * rmtree Skills...")
    if(os.path.exists("./skills")):
        shutil.rmtree("./skills")
    else:
        logging.warning(f"path not exist ./skills, skipping...")
       
    Path('.skills').mkdir(parents=True, exist_ok=True)        
    logging.info(" * .skills folder created...")
   
    
    if os.path.exists("./AGENT.md"):
        os.remove("./AGENT.md")
        logging.info(" * Deleted AGENT.md...")
    else:
        print(f"path not exist ./AGENT.md, skipping...")
    
    Path("./AGENT.md").touch(exist_ok=True)
    print(" * ./AGENT.md file created...")
import logging

def initialize_logging(level):
    #https://docs.python.org/3/howto/logging.html
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(filename)s - %(funcName)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        force=True
    )        