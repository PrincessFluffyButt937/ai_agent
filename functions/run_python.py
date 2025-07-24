import os
import subprocess

api_key = os.environ.get("GEMINI_API_KEY")

from google import genai
from google.genai import types

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Executes Python files with optional arguments, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The location of python file we want to execute, relative to the working directory.",
            ),
        },
    ),
)

def run_python_file(working_directory, file_path, args=[]):
    full_path = os.path.join(working_directory, file_path)

    abs_working_dir = os.path.abspath(working_directory)
    abs_full_path = os.path.abspath(full_path)

    if not abs_full_path.startswith(abs_working_dir):
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
    
    if not os.path.exists(abs_full_path):
        return f'Error: File "{file_path}" not found.'
    
    if not file_path.endswith('.py'):
        return f'Error: "{file_path}" is not a Python file.'
    
    try:
        completed_process = subprocess.run(args=["python3", file_path] + args, timeout=30, capture_output=True, text=True, cwd=working_directory)
        out = completed_process.stdout
        err = completed_process.stderr
        exit_code = completed_process.returncode
        
        if not out and not err:
            return "No output produced"

        if exit_code != 0:
            return f'Process exited with code {exit_code}\nSTDOUT:\n{out}\nSTDERR:\n{err}'
        
        return f'STDOUT:\n{out}\nSTDERR:\n{err}'
    
    except Exception as e:
        return f"Error: executing Python file: {e}"