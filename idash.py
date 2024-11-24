import boto3, json, requests
from ipdb import set_trace
import tools, rag, llm

# url = "http://localhost:11434/api/v1/completions"

def parse_query_with_tool_selection(llm, user_query, tools):
    """Parse user query and select the appropriate tool using Mistral."""
    tools_description = "\n".join(
        f"- Tool: {tool['name']}\n  Description: {tool['description']}\n  Parameters: {tool['parameters']}"
        for tool in tools
    )

    prompt = f"""
You are an intelligent assistant for AWS cloud management. Your task is to interpret the user's query and select the most appropriate tool from the following list:

{tools_description}

User Query: "{user_query}"

Return a JSON object with:
- tool: The name of the tool to use.
- parameters: The parameters required for the selected tool.
    """
    return llm.call(prompt)

def summarize_data(llm, data, resource_type):
    """Summarize resource data using Mistral."""
    prompt = f"Summarize the following {resource_type} data: {data}"
    return llm.call(prompt)

def main():
    available_tools = tools.generate_tool_definitions()
    l = llm.LLM()
    vs = rag.VectorStore()
    vs.add_tools(available_tools)
    def parse_query_with_rag(user_query):
        prompt = vs.prompt_for_query_with_tools(user_query)
        print("RAG Prompt: ", prompt)
        return l.call(prompt)

    print("Welcome to the Cloud Inventory Dashboard! Ask me about your AWS resources.")
    while True:
        # User Input
        user_query = input("\nYou: ")
        if user_query.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        # Parse Query
        try:
            # parsed_query = parse_query_with_tool_selection(llm, user_query, available_tools)
            parsed_query = parse_query_with_rag(user_query)
            print(f"\nParsed Query: {parsed_query}")
            try:
                parsed_result = json.loads(parsed_query)
            except Exception as e:
                print("Query is not json: ", e)
                set_trace()
                continue

            tool_name = parsed_result.get("tool")
            parameters = parsed_result.get("parameters", {})


            print(f"\nAgent: Using tool '{tool_name}' with parameters {parameters}")

            # Call the appropriate tool
            tool_output = tools.call_tool_dyn(tool_name, parameters)
            summary = summarize_data(tool_output, tool_name)
            print(f"\nAgent: {summary}")
        except Exception as e:
            print(f"\nAgent: Sorry, something went wrong. {str(e)}")
            raise e
