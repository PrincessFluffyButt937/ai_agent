import os

api_key = os.environ.get("GEMINI_API_KEY")

from google import genai
from google.genai import types

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            ),
        },
    ),
)

def get_files_info(working_directory, directory="."):
    full_path = os.path.join(working_directory, directory)

    abs_working_dir = os.path.abspath(working_directory)
    abs_full_path = os.path.abspath(full_path)

    if not abs_full_path.startswith(abs_working_dir):
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
    
    if not os.path.isdir(abs_full_path):
        return f'Error: "{directory}" is not a directory'
    
    
    files = os.listdir(full_path)
    content = ""
    for file in files:
        path = os.path.join(full_path, file)
        size = os.path.getsize(path)
        if os.path.isdir(path):
            content = content + f'- {file}: file_size={size} bytes, is_dir=True\n'
        else:
            content = content + f'- {file}: file_size={size} bytes, is_dir=False\n'
    return content




