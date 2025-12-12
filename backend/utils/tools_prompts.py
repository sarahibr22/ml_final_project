tools_prompts = {
    "web_search_tool": (
        "Use this tool to search the web (DuckDuckGo backend) for external information, optionally filtered by date. "
        "Tool Call Format:\n"
        "{\n"
        "  'tool': 'web_search_tool',\n"
        "  'input': {\n"
        "    'query': '<search query>',\n"
        "    'num_results': <number>,\n"
        "    'from_date': '<YYYY_MM_DD>',\n"
        "    'to_date': '<YYYY_MM_DD>'\n"
        "  }\n"
        "}"
    ),
    "send_email": (
        "Use this tool to send an email via SMTP. You must provide recipient, subject, and body. SMTP configuration is hardcoded in the tool. "
        "Tool Call Format:\n"
        "{\n"
        "  'tool': 'send_email',\n"
        "  'input': {\n"
        "    'to_email': '<recipient>',\n"
        "    'subject': '<subject>',\n"
        "    'body': '<email body>'\n"
        "  }\n"
        "}"
    ),
    "templated_query_tool": (
        "Use this tool to run a named SQL query and get a results overview and chart. "
        "Tool Call Format:\n"
        "{\n"
        "  'tool': 'templated_query_tool',\n"
        "  'input': {\n"
        "    'query_name': '<name>',\n"
        "    'params': {<param_dict>}\n"
        "  }\n"
        "}"
    ),
    "rag_tool": (
        "Use this tool to semantically search and fetch relevant patient data. It generates an embedding for your query using the Qwen model and retrieves the most similar patient cases from the database. "
        "Tool Call Format:\n"
        "{\n"
        "  'tool': 'rag_tool',\n"
        "  'input': {\n"
        "    'query': '<your text>'\n"
        "  }\n"
        "}"
    ),
}