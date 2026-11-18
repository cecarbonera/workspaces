from rag_agent import searchVetorResults
from graph_agent import searchGraphResults

# Function to create contexts by combining results from both the vector database and the graph database based on a query string
def createContexts(query):
    try:
        # Perform searches in both the vector database and the graph database
        vectorResults = searchVetorResults(query)
        graphResults = searchGraphResults(query)

        # Combine the results from both searches into a single context string
        combinedContext = f"{vectorResults}\n{graphResults}"

        # Return the combined context
        return combinedContext
    except Exception as e:
        return f"[ERROR] Failed to create contexts: {str(e)}"