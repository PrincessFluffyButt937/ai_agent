import os
import sys
from functions.get_files_info import schema_get_files_info, get_files_info
from functions.get_file_content import schema_get_file_content, get_file_content
from functions.run_python import schema_run_python_file, run_python_file
from functions.write_file import schema_write_file, write_file
from dotenv import load_dotenv


load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

from google import genai
from google.genai import types

model_name = 'gemini-2.0-flash-001'
system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""


available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_run_python_file,
        schema_write_file
    ]
)

function_map = {
    "get_files_info": get_files_info,
    "get_file_content": get_file_content,
    "run_python_file": run_python_file,
    "write_file": write_file
}

def call_function(function_call_part, verbose=False):
    if verbose:
        print(f"Calling function: {function_call_part.name}({function_call_part.args})")
    else:
        print(f" - Calling function: {function_call_part.name}")

    function_call_part.args["working_directory"] = "./calculator"

    if function_call_part.name in function_map:
        function_call = function_map[function_call_part.name]
        call_content = function_call(**function_call_part.args)
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_call_part.name,
                    response={"result": call_content},
                )
            ],
        )
    else:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_call_part.name,
                    response={"error": f"Unknown function: {function_call_part.name}"},
                )
            ],
        )


def main():
    verbose = False
    arguments = sys.argv
    question = sys.argv[1]
    if len(arguments) > 2:
        flag = sys.argv[2]
        if flag == "--verbose":
            verbose = True

    messages = [
        types.Content(role="user", parts=[types.Part(text=question)]),
]
    #messages = list

    client = genai.Client(api_key=api_key)

    for i in range(0,20):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=messages,
                config=types.GenerateContentConfig(
                    tools=[available_functions], 
                    system_instruction=system_prompt
                ),
        )

            function_call_parts = response.function_calls

            if verbose:
                print(sys.argv)
                print(f"User prompt: {question}")
                print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
                print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
                
            candidates = response.candidates
            for candidate in candidates:
                messages.append(candidate.content)
                #candidate.content has role='model' by default

            if function_call_parts:
                for function_call_part in function_call_parts:
                    function_call_result = call_function(function_call_part, verbose)

                    if not function_call_result.parts[0].function_response.response:
                        raise Exception(f"Fatal error! Function call result has no \".parts[0].function_response.response\" property.")
                    elif verbose:
                        print(f"-> {function_call_result.parts[0].function_response.response}")

                    messages.append(function_call_result)            

            else:
                print(response.text)
                return
        except:
            print(f'Error, function call {messages[-1]} failed to produce desired output.')
    print(f'Error, maximum iteration limnit has been reached!')


if __name__ == "__main__":
    main()
