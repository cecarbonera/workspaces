import sys, os

# Add the root path from python to the system path to allow for module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import constants
from neo4j import GraphDatabase

# Driver do Neo4j (With configurable parameters for connection pooling and timeouts)
neo4j_driver = GraphDatabase.driver(uri = constants.NEO4J_URI, 
                                    auth = (constants.NEO4J_USER, constants.NEO4J_PASSWORD),
                                    max_connection_lifetime = constants.MAX_CONNECTION_LIFETIME,
                                    max_connection_pool_size = constants.MAX_CONNECTION_POOL_SIZE,
                                    connection_acquisition_timeout = constants.CONNECTION_TIMEOUT,
                                    liveness_check_timeout = constants.LIVENESS_CHECK_TIMEOUT)

# Function to search for results in the Neo4j graph database based on a query string
def searchGraphResults(query):
    try:
        # Verify connectivity to the Neo4j database
        neo4j_driver.verify_connectivity()

        with neo4j_driver.session() as session:
            # Executes the query and retrieves the results to 
            results = session.run(constants.CYPHER_DEFAULT,
                                  parameters = {"query": query, "limit": constants.RESPONSE_LIMIT})

            # gets the content from the query results, filtering out any records that do not have a "content" field
            contents = [record["content"] for record in results if record.get("content") is not None]

            #Returns a list of content from the query results
            #return contents if contents else None
            return contents if contents else constants.TEXTCOMPL  #Temporrario
                
    except Exception as e:
        return None     