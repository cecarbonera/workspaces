import sys, os

# Add root path of project to Python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import constants
import logging

# Configure o logger da sua aplicação
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

# Variable to store the Qdrant client instance and the SentenceTransformer model (WebRepository)
#For Local Version
#qdrant_client = QdrantClient(constants.QDRANT_URL)  

#Remote Repository
qdrantClient = QdrantClient(url = constants.QDRANT_URL, api_key = constants.QDRANT_API_KEY)
modelName = SentenceTransformer(constants.MODEL_SENTENCETRANS_NAME)

#Log definition
logger = logging.getLogger(__name__)

# Function to search for results in the vector database based on a query string
def searchVetorResults(query):
    try:
        # 1. Generate the vector representation of the query using the SentenceTransformer model
        vector_result = modelName.encode(query).tolist()

        # 2. Search for similar points in the Qdrant collection using the generated vector
        results = qdrantClient.query_points(collection_name = constants.QDRANT_COLLECTION_NAME,
                                            query = vector_result,
                                            limit = constants.RESPONSE_LIMIT,
                                            with_payload = ["page_content"])

        # 3. Process the results to extract the "page_content" from the payload of each point
        contents = [payload["page_content"] for point in results.points if (payload := point.payload) and "page_content" in payload]

        # 4. Return the list of contents as a single string, or None if no results were found
        return "\n".join(contents) if contents else None

    except Exception as e:
        # Log the error with detailed information and return None to indicate failure
        logger.error(f"Error querying Qdrant: {e}", exc_info = True)
        return None