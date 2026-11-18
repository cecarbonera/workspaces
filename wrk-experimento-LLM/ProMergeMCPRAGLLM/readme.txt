#
# 1) Create a username and password on the NVIDIA website
#
# 2) Create the token for access to LLM (which can be accessed directly from the NVIDIA website) - https://build.nvidia.com/settings/api-keys
#
# Navigate to the folder containing the source files and in the "promerge_env_var.py" file, place the token in the "nvidia_key" variable
#
# Open the Anaconda command prompt as administrator and go to the directory where the source files are located
#
# Never run the `conda create` command... as it references the files in the Anaconda installation folder (and doesn't work correctly)
#
# - 5G Wi-Fi is working better for debugging
# - Stop the antivirus
# - Open the FOLDER where the data sources are located
# - Select the "FastApi" compiler/debugger
#
# Create a virtual environment (anaconda command prompt as administrator) `python -m venv` promergeenv

# 
# Create a virtual environment (open an anaconda prompt as administrator OR in the terminal move to directory ProMerge-MCP)
python -m venv promergeenv

# Activate the environment - Windows (must set the path, for example.. "cd C:\workspaces\wrk-experimento-LLM\ProMergeMCPRAGLLM")
promergeenv\scripts\activate

# IMPORTANT:
#
#
# **** To execute the endpoint by Postman - desactivate the proxy go to "Settings" -> Proxy (Aba) -> option "Use the system proxy" must be unchecked
# **** To execute the promerge_api in debugger mode -> the main method must be commented AND choose option "python debugger: Debbug using launch.json" -> choose fastAPI
#
#
# Open the "requirements.txt" file and run each of the commands contained within separately
#
# After installing the packages -> open Visual Studio Code and in the execution environment you should locate
# the Python interpreter for the environment located in "...env\scripts\python.exe"
#
#
# Open Docker Desktop
# 
# Initialize the API OR RUN in debugger mode
double click in Start.bat or debug .\mcp-server\main.py

# Deactivate the virtual environment when the work is complete
deactivate

#
# Use Postman for testing and validation
# 1st) Create a POST request -> http://localhost:8000/promerge_api
# 2nd) Headers -> Content-Type -> application/json
# 3rd) Body -> { "query": "Here do the question......" }