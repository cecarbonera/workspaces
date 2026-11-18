# -------------------------------------------------------------------------------
# MCP-CLIENT - LLM AGENT
# Responsible by:
# - Receives context + query
# - Create the NLP prompt
# - Call LLM using an API
# - Return the answer
# -------------------------------------------------------------------------------
import sys, os

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.messages import SystemMessage, HumanMessage

# Add root path of projecto to Python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import constants

# Main function to generate response from LLM
def generateAnswers(context: str, query: str) -> str:
    try:               
        # 1. Instanciates the LLM model using the NVIDIA API with the specified parameters
        # 2. Formats the prompt with the provided context and query, and creates the messages for the LLM
        # 3. Invcokes the LLM with the formatted messages and retrieves the response
        # 4. If the response is valid and contains content, return the content; otherwise, return an error message
        llm = ChatNVIDIA(model = constants.NVIDIAMODEL_NAME_LLM,
                         api_key = constants.NVIDIA_API_KEY,                                                  
                         temperature = constants.NVIDIATEMPERATURE,
                         base_url = constants.BASE_NVIDIA_URL,
                         max_tokens = constants.NVIDIAMAXTOKENS,
                         timeout = constants.NVIDIATIMEOUT,
                         max_retries = constants.NVIDIAMAXRETRIES)
        
        messages = [SystemMessage(content = constants.PROMPTDEFAULT),
                    HumanMessage(content = f"Context:\n{context}\n\nQuestion: {query}")]
        
        response = llm.invoke(messages)
       
        if response and response.content:
            return response.content

        return "[ERROR] No response from the LLM."

    except Exception as e:
        # Exception handling: Return an error message with the exception details
        return f"[ERROR LLM] {str(e)}"

"""        
# Main function to generate response from LLM
def generateAnswers(context: str, query: str) -> str:
    try:
        # 1. Instantiate the LLM model using the Groq API
        llm = ChatGroq(model = constants.GROQMODEL_NAME_LLM,
                       api_key = constants.GROQ_API_KEY,
                       temperature = constants.GROQTEMPERATURE,
                       max_tokens = constants.GROQMAXTOKENS)

        # 2. Formats the prompt with the provided context and query
        #    and creates the messages for the LLM
        messages = [SystemMessage(content=constants.PROMPTDEFAULT),
                    HumanMessage(content=f"Context:\n{context}\n\nQuestion: {query}")]

        # 3. Invokes the LLM with the formatted messages
        response = llm.invoke(messages)

        # 4. Validates and returns the response
        if response and response.content:
            return response.content

        return "[ERROR] No response from the LLM."

    except Exception as e:

        # Exception handling
        return f"[ERROR LLM] {str(e)}"
"""
