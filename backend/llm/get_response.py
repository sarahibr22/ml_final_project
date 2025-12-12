import json
from tools.duckduckgo_tool import web_search_tool
from tools.email_tool import send_email
from tools.templated_query_tool import templated_query_tool
from tools.rag_tool import rag_tool

def get_response(prompt: str) -> str:
    # Call LLM (simulate for now)
    # In real use, this would call cohere_chat or similar
    try:
        response = json.loads(prompt) if prompt.strip().startswith('{') else None
    except Exception:
        response = None

    if response and 'action' in response and response['action']:
        tool_name = response['action']
        tool_input = response.get('input', {})
        if tool_name == 'web_search_tool':
            obs = web_search_tool(**tool_input)
        elif tool_name == 'send_email':
            obs = send_email(**tool_input)
        elif tool_name == 'templated_query_tool':
            obs = templated_query_tool(**tool_input)
        elif tool_name == 'rag_tool':
            obs = rag_tool(**tool_input)
        else:
            obs = f"Unknown tool: {tool_name}"
        response['observation'] = obs
        return json.dumps(response)
    return f"Echo: {prompt}"
