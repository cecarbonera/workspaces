import os
from dotenv import load_dotenv

# load environment variables from .env file
load_dotenv()

#Variables for the application
WHISPER_MODEL = "base"
MAX_CONNECTION_LIFETIME = 300
MAX_CONNECTION_POOL_SIZE = 50
CONNECTION_TIMEOUT = 60
LIVENESS_CHECK_TIMEOUT = 30
MAX_RETRIES = 3
RESPONSE_LIMIT = 5

# LLMs and parameters configurations
# Options: 1) meta/llama-3.3-70b-instruct  - Much requested model for LLM tasks, CAN APPEAR PROBLEMS WITH MEMORY USAGE, REQUIRES HIGH RESOURCES
#          2) meta/llama-3.1-70b-instruct
#          3) meta/llama-3.2-11b-vision-instruct 
NVIDIAMODEL_NAME_LLM = "meta/llama-3.2-11b-vision-instruct"  # LLM model for generating answers   
NVIDIAMODEL_NAME_LLM_AUDIO = "nvidia/riva-whisper"  
MODEL_SENTENCETRANS_NAME = "sentence-transformers/msmarco-bert-base-dot-v5"

# Acess configurations for NVIDIA API (NVIDIA_API_KEY.txt configuration file)
BASE_NVIDIA_URL = "https://integrate.api.nvidia.com/v1"
NVIDIACHUNKSIZE = 1500
NVIDIACHUNKOVERLAP = 150
NVIDIATEMPERATURE = 0.2
NVIDIAMAXTOKENS = 4096 #8192
NVIDIAREASONINGEFFORT = "none"
NVIDIATIMEOUT = 180
NVIDIAMAXRETRIES = 2

#Groq LLM configurations
GROQMODEL_NAME_LLM = "openai/gpt-oss-120b"  # LLM model for generating answers
GROQMODEL_NAME_AUDIO = "whisper-large-v3-turbo"
GROQTEMPERATURE = 0.2
GROQMAXTOKENS = 8192    

# Databases configurations (Docker Version)
#NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
#NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
#NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "promerge")

#Qdrant Configurations (Docker Version)
#QDRANT_URL = "http://localhost:6333"

# Databases configurations (Remote Version)
NEO4J_URI = os.getenv("NEO4J_URI", "neo4j+s://d7482491.databases.neo4j.io")
NEO4J_USER = os.getenv("NEO4J_USER", "d7482491")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "1rx3UZBCa5kDSWdTi_zUdggS6RwmC1dWoCKM74Q0yy4")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "d7482491")
AURA_INSTANCEID = os.getenv("AURA_INSTANCEID", "d7482491")
AURA_INSTANCENAME = os.getenv("AURA_INSTANCENAME", "Free instance")

NEO4J_CONSTRAINTDOCUMENTS = "CREATE CONSTRAINT doc_path_unique IF NOT EXISTS FOR (d:Document) REQUIRE d.path IS UNIQUE;"
NEO4J_CONSTRAINTCHUNKS = "CREATE CONSTRAINT chunk_id_unique IF NOT EXISTS FOR (c:Chunk) REQUIRE c.id IS UNIQUE;"
NEO4J_CONSTRAINTENTITIES = "CREATE CONSTRAINT entity_name_unique IF NOT EXISTS FOR (e:Entity) REQUIRE e.name IS UNIQUE;"
NEO4J_INDEXENTITY = "CREATE FULLTEXT INDEX chunk_fulltext_index IF NOT EXISTS FOR (c:Chunk) ON EACH [c.page_content];"
NEO4J_INDEXCHUNK = "CREATE FULLTEXT INDEX entity_fulltext_index IF NOT EXISTS FOR (e:Entity) ON EACH [e.name];"

# Qdrant WebRespository (QdrantProMergeVectorDBApiKey.txt configuration file)
QDRANT_URL = "https://64d72ea3-df92-4899-b5f1-a14e9b14206c.sa-east-1-0.aws.cloud.qdrant.io:6333"
QDRANT_COLLECTION_NAME = "ProMergeVectorDB"

QDRANT_INDEXDOCUMENTS = """
CREATE VECTOR INDEX chunk_vector_index IF NOT EXISTS
FOR (c:Chunk) ON (c.embedding)
OPTIONS {
  indexConfig: {
    `vector.dimensions`: 768,
    `vector.similarity_function`: 'cosine'
  }
};""".strip()

# Create constraints and indexes in Neo4j if they do not exist
QUERIESNEO4J = ["CREATE CONSTRAINT doc_path_unique IF NOT EXISTS FOR (d:Document) REQUIRE d.path IS UNIQUE;",
                "CREATE CONSTRAINT chunk_id_unique IF NOT EXISTS FOR (c:Chunk) REQUIRE c.id IS UNIQUE;",
                "CREATE CONSTRAINT entity_name_unique IF NOT EXISTS FOR (e:Entity) REQUIRE e.name IS UNIQUE;",
                "CREATE FULLTEXT INDEX chunk_fulltext_index IF NOT EXISTS FOR (c:Chunk) ON EACH [c.page_content];",
                "CREATE FULLTEXT INDEX entity_fulltext_index IF NOT EXISTS FOR (e:Entity) ON EACH [e.name];"]

GRAPH_QUERY_INGESTION_MODEL_2 = """
    MERGE (d:Document {path: $path})
    
    WITH d, $chunks AS list_chunks
    UNWIND range(0, size(list_chunks) - 1) AS i
    WITH d, list_chunks[i] AS c_data
    
    MERGE (c:Chunk {id: c_data.id})
    SET c.page_content = c_data.text,
        c.chunk_index = c_data.chunk_index
        
    MERGE (d)-[:HAS_CHUNK]->(c)
    
    WITH d, c, c_data
    FOREACH (e_info IN [e IN coalesce(c_data.entities, []) WHERE e.name IS NOT NULL AND trim(e.name) <> ''] |
        MERGE (e:Entity {name: trim(e_info.name)})
        ON CREATE SET e.type = coalesce(e_info.type, 'Entity')
        MERGE (c)-[:MENTIONS]->(e)
    )
    
    WITH d, c, c_data ORDER BY c_data.chunk_index ASC
    WITH collect(c) AS chunk_nodes
    
    FOREACH (idx IN range(0, size(chunk_nodes) - 2) |
        FOREACH (curr IN [chunk_nodes[idx]] |
            FOREACH (next IN [chunk_nodes[idx + 1]] |
                MERGE (curr)-[:NEXT_CHUNK]->(next)
            )
        )
    )""".strip()

GRAPH_QUERY_INGESTION = """
    MERGE (d:Document {path: $path})
    
    WITH d
    UNWIND $chunks AS c_data
    
    MERGE (c:Chunk {id: c_data.id})
    SET c.page_content = c_data.text,
        c.chunk_index = c_data.chunk_index
        
    MERGE (d)-[:HAS_CHUNK]->(c)
    
    FOREACH (e_info IN [e IN coalesce(c_data.entities, []) WHERE e.name IS NOT NULL AND trim(e.name) <> ''] |
        MERGE (e:Entity {name: trim(e_info.name)})
        ON CREATE SET e.type = coalesce(e_info.type, 'Entity')
        MERGE (c)-[:MENTIONS]->(e)
    )
    
    WITH d, c ORDER BY c.chunk_index ASC
    WITH d, collect(c) AS chunk_nodes
    
    CALL apoc.nodes.link(chunk_nodes, 'NEXT_CHUNK')
    
    RETURN count(chunk_nodes) AS total_chunks""".strip()

GRAPH_QUERY_RELATIONSHIPS_MODEL2 = """
    UNWIND $chunks AS c_data
    UNWIND [r IN coalesce(c_data.relationships, []) WHERE r.source IS NOT NULL AND r.target IS NOT NULL AND trim(r.source) <> '' AND trim(r.target) <> ''] AS rel
    
    MERGE (source:Entity {name: trim(rel.source)})
    MERGE (target:Entity {name: trim(rel.target)})
    
    WITH source, target, rel
    CALL apoc.merge.relationship(
         source,
         toUpper(replace(coalesce(rel.type, 'RELATED_TO'), ' ', '_')),
         {},
         {},
         target,
         {}
    ) YIELD rel AS r
    RETURN count(r)""".strip()

GRAPH_QUERY_RELATIONSHIPS = """
    UNWIND $chunks AS c_data
    UNWIND [r IN coalesce(c_data.relationships, []) 
            WHERE r.source IS NOT NULL AND r.target IS NOT NULL 
            AND trim(r.source) <> '' AND trim(r.target) <> ''
            AND trim(r.source) <> trim(r.target)] AS rel
    
    MERGE (source:Entity {name: trim(rel.source)})
    MERGE (target:Entity {name: trim(rel.target)})
    
    WITH source, target, rel
    CALL apoc.merge.relationship(
        source,
        toUpper(replace(trim(coalesce(rel.type, 'RELATED_TO')), ' ', '_')),
        {},
        {},
        target,
        {}
    ) YIELD rel AS r
    RETURN count(r) AS total_relationships""".strip()

# NVIDIA Prompt for extracting entities from text, with specific rules and response format
NVIDIAPROMPTDEFAULT = """
You are an expert in knowledge extraction.
Extract all relevant entities from the text.

Allowed entity types:
- Person
- Organization
- Location
- Technology
- Programming language
- Framework
- Library
- Database
- Project
- Concept

Rules:
1. Return EXCLUSIVELY a valid JSON object, without code markers like ```json.
2. Do not include any explanatory text before or after the JSON.
3. Do not include generic or ambiguous entities.
4. Remove duplicates.

Text:
{text}

Required response format:
{{
  "entities": [ {{
                "name": "entity name",
                "type": "entity type"
                }}
              ]
}}""".strip()


# Queries Cypher (Alinhadas para evitar espaços desnecessários)
CYPHER_MODEL2 = """
MATCH (n:Document)
WHERE n.page_content IS NOT NULL
AND n.page_content CONTAINS $query
RETURN n.page_content AS content
LIMIT $limit""".strip()

CYPHER_MODEL3 = """
MATCH (e:Entity)<-[:MENTIONS]-(d:Document)
WHERE e.name CONTAINS $query
RETURN d.content 
LIMIT $limit""".strip()

CYPHER_DEFAULT = """
CALL db.index.fulltext.queryNodes("chunk_fulltext_index", $query) YIELD node AS c, score
MATCH (d:Document)-[:HAS_CHUNK]->(c)
RETURN c.page_content AS content, d.path AS source, score
ORDER BY score DESC
LIMIT $limit""".strip()

PROMPT_MODEL1 = """
Answer the user's question primarily using the information provided in the context.
Instructions:
1. Analyze the user's question.
2. Use the information from the context as the main source for constructing the answer.
3. If the context is insufficient, supplement the answer with general AI knowledge.
4. Do not invent information that is not in the context or cannot be safely inferred.
5. Provide a clear, objective, and well-structured answer.
6. When appropriate, organize the answer into bullet points or steps to facilitate understanding.
Objective: Generate a correct, complete, and easy-to-understand answer for the user.""".strip()

TEXTCOMPL = """
Embora os campos perBonificacao e perComissao estejam como FLOAT(5) no  modelo ER para a tabela Employees, os dois campos deverão ser em formato INT (Inteiro). Isso se justifica devido a reunião com a diretório que decidiu tratar esses dois campos na condição de inteiros. Observando as regas normais do arredondamento."""

PROMPTDEFAULT_2 = """
You are an assistant specialized in answering questions based on the provided context.
Objective:
Answer the user's question, prioritizing information found in the context.
Rules:
1. Context priority
- Use information from the provided context first.
- If the context contains the complete answer, base your response solely on it.
2. Partial context
- If the context contains only part of the answer, use that information and supplement it with reliable general knowledge.
3. Insufficient context
- If the context does not contain enough information to answer the question, clearly state that the context is insufficient and answer based on general knowledge.
4. Conflicting information
- If there is a conflict between the context and general knowledge, prioritize the provided context.
5. Irrelevant context
- Ignore parts of the context that are unrelated to the question.
6. Avoid hallucinations
- Do not invent facts.
- Use only information from the context or reliable general knowledge.
Response format:
- Clear and concise answer.
- Organize the response to include: 1 - problem details, 2 - versions modified by developers, 3 - problem definition, 4 - proposed solution, 5 - steps to resolve the problem, 6 - conclusion.
- Highlight important information.
- The response must be in English.""".strip()


PROMPTDEFAULT = """ 
You are an expert AI software engineering assistant specializing in source-code analysis, concurrent modification reasoning, and source-code conflict resolution.

OBJECTIVE:
Analyze provided conflicting source code fragments along with context-aware information. Your goal is to determine the intention of each divergent branch, synthesize a syntactically and semantically correct unified implementation, and provide a clear technical breakdown for the developer.

CORE PRINCIPLES & EXECUTION CONSTRAINTS:

1. Contextual Superiority and  Hallucination Policy:
- The provided source snippets and context-aware information are the unique source of business rules and domain or information types.
- Strict Invariance: NEVER invent source-code suggestions; use ONLY the source-code fragments provided.

- Ambiguity Protocol: If conflicting changes represent mutually exclusive business choices where intent cannot be inferred from code or context-aware information, DO NOT arbitrarily favor one branch. Instead, present a recommendation for source-code conflict resolution, explicitly outline the trade-offs, and flag the ambiguities for human review.

2. Deep Semantic & Structural Analysis:
- Differentiate between structural refactoring (e.g., renaming variables, extracting methods, altering signatures) and behavioral modifications (e.g., bug fixes, logic additions, security patches).

- Preserve side effects, exception handling boundaries, micro-optimizations, and architectural constraints present in both branches unless they are directly mutually exclusive.

3. Source-Code Rigor:
- The proposed resolved code MUST be syntactically valid, properly formatted, and ready for production deployment or direct integration into source-code  conflict resolution tools.
- Retain all necessary annotations, docstrings, typing constructs, and visibility modifiers.

4. Context priority
- Use information from the provided context first.
- If the context-aware information contains the complete answer, base your response solely on it.

4.1. Partial context
- If the context contains only part of the answer, use these information and supplement it with reliable general knowledge.

4.2. Insufficient context
- If the context does not contain enough information to answer the question, clearly state that the context is insufficient and answer based on general knowledge.

7. Conflicting information
- If there is a conflicts between the context-aware information and general knowledge, prioritize the context-aware information.

8. Irrelevant context
- Ignore parts of the context that are unrelated to the source code conflicts.

RESPONSE FORMAT REQUIREMENTS:

9. Executive Conflict Summary
   - Concise technical diagnosis identifying the root cause of the conflict (e.g., concurrent signature alteration, conflicting state mutation, incompatible refactoring vs. hotfix).

10. Proposed Resolved Code
   - Ensure all imports, annotations, and logic paths are correctly harmonized without missing code snippets or placeholder comments.

11.  Final response layout (MANDATORY) - THAT MUST BE FOLLOWED STRICTLY:
        1 - Problem Details
        2 - Versions modified by developers (Fragment A and  B)
              [ Version Fragment A ]
              
              [ Version Fragment B]

        3 - Problem Definition
        4 - Context-aware information analisys
        5 - Proposed source code version with conflict resolution based on context-aware information
              [ Proposed Source-Code Version]

        6 - Step-by-step to source-conde conflicts resolution               
        7 - Final appointments""".strip()