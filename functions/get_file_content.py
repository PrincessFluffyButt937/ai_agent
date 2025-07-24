import os
from functions.config import MAX_CHARS

api_key = os.environ.get("GEMINI_API_KEY")

from google import genai
from google.genai import types

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Reads files contents up to a hadrcoded character limit, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Location of the read file is, relative to the working directory.",
            ),
        },
    ),
)

def get_file_content(working_directory, file_path):
    full_path = os.path.join(working_directory, file_path)

    abs_working_file = os.path.abspath(working_directory)
    abs_full_path = os.path.abspath(full_path)

    if not abs_full_path.startswith(abs_working_file):
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
    if not os.path.isfile(abs_full_path):
        return f'Error: File not found or is not a regular file: "{file_path}"'

    with open(abs_full_path, "r") as f:
        file_content = f.read(MAX_CHARS + 100)
        if len(file_content) <= MAX_CHARS:
            return file_content
        else:
            return f'{file_content[:MAX_CHARS]}[...File "{file_path}" truncated at {MAX_CHARS} characters]'
