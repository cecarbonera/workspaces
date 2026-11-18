import uvicorn, re
from fastapi import FastAPI
from pydantic import BaseModel
from context_agent import createContexts
from llm_agent import generateAnswers

app = FastAPI()

class Item(BaseModel):
    query: str

@app.post("/promerge_api")
async def promerge_api(item: Item):
    # Add a '\' before special character
    _query = re.sub(r'([+\-!(){}\[\]^"~*?:\\/])', r'\\\1', item.query)
    
    # Create contexts based on the query and generate answers using the LLM agent
    context = createContexts(_query)
    
    # Call the LLM to get the answer
    answer = generateAnswers(context, _query)

    #Return the answer as a JSON response
    return answer

#
#  ********* IMPORTANT *********
#  
#  For local debugging, run the script directly using "python debbuger: debbug using Launch.json" option
#
#  Must appear in console to executes correctly the uvicorn server ****
#  INFO:     Started server process [8180]
#  INFO:     Waiting for application startup.
#  INFO:     Application startup complete.
#
# Inicializes the FastAPI server using uvicorn, listening on all interfaces
if __name__=="__main__":
    uvicorn.run("promerge_api:app", host = '0.0.0.0', port = 8000, reload = True)    