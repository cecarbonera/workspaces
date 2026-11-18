import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import sys, time, subprocess, pathlib
from pathlib import Path

# 2. Prepare as variáveis de ambiente
env = os.environ.copy()
env["KMP_DUPLICATE_LIB_OK"] = "TRUE"

def initializeMCPsModules():
    # 1st Step - Composing Docker configurations and start the containers
    print("Process of Initialization Started...")
    BASE_DIR = Path(__file__).resolve().parent.parent

    #print("1st Step - Composing Docker configurations and start the containers...")        
    #DOCKER_COMPOSE_PATH = BASE_DIR / "docker" / "docker-compose.yaml"
    #subprocess.call(f'docker-compose -f "{DOCKER_COMPOSE_PATH}" up -d', shell = True)
    #print("1st Step - Finished.")        
    #time.sleep(2)
    
    # 2nd Step - Initializing the API
    print("1st Step - Initializing the API...")       
    root_path = str(pathlib.Path(__file__).parent.parent)
    project_path = root_path + "\\mcp-client"
    
    # Initialization of variables
    env["PYTHONPATH"] = root_path
    if "PYTHONPATH" in env:
        env["PYTHONPATH"] = f"{root_path};{env['PYTHONPATH']}"

    #Load the API
    subprocess.Popen(["uvicorn", "promerge_api:app", "--host", "0.0.0.0", "--port", "8000"], cwd = project_path,  env = env)
    print("1st Step - Finished.")        
    time.sleep(2)
    
    # Start the file watcher to monitor the Documentos folder for new files and process them
    print("2nd Step - Initializing the watcher and processing the data sources...")
    WATCHER_PATH = BASE_DIR / "mcp-resource" / "watcher.py"    
    #subprocess.Popen(["python", str(WATCHER_PATH)], env=env)
    subprocess.run([sys.executable, str(WATCHER_PATH)], check=True)   

if __name__ == "__main__":
    # Start the initialization process
    initializeMCPsModules()