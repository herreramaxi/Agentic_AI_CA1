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