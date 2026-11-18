import os
import sys
import time
import shutil
import warnings
import numpy as np
import cv2
import docx
import whisper
import easyocr
import torch

from pathlib import Path
from pptx import Presentation
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import Qdrant
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PayloadSchemaType, VectorParams
from neo4j import GraphDatabase
from PyPDF2 import PdfReader
from groq import Groq

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import constants

warnings.filterwarnings('ignore')

# Configuration for logging
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

# Configuration for the NVIDIA LLM and Parser
entityPrompt = ChatPromptTemplate.from_template(constants.NVIDIAPROMPTDEFAULT)
llm = ChatNVIDIA(model = constants.NVIDIAMODEL_NAME_LLM,
                 api_key = constants.NVIDIA_API_KEY,                                                  
                 temperature = constants.NVIDIATEMPERATURE,
                 base_url = constants.BASE_NVIDIA_URL,
                 max_tokens = constants.NVIDIAMAXTOKENS,
                 timeout = constants.NVIDIATIMEOUT,
                 max_retries = constants.NVIDIAMAXRETRIES)
parser = JsonOutputParser()

#Concatenation of the entity prompt, LLM, and parser to form a processing chain for extracting entities from text
entity_chain = entityPrompt | llm | parser

# OCR and Whisper model initialization
ocr_reader = easyocr.Reader(['pt'], gpu = torch.cuda.is_available())
whisper_model = whisper.load_model(constants.WHISPER_MODEL, device = DEVICE)

# Embedding model initialization using HuggingFace
embeddingModel = HuggingFaceEmbeddings(model_name = constants.MODEL_SENTENCETRANS_NAME,
                                       model_kwargs = {'device': DEVICE},
                                       encode_kwargs = {'normalize_embeddings': True})

#Qdrant Client and Qdrant Wrapper configuration
qdrantClient = QdrantClient(url = constants.QDRANT_URL, api_key = constants.QDRANT_API_KEY)
qdrant = Qdrant(qdrantClient, constants.QDRANT_COLLECTION_NAME, embeddingModel)

# Driver do Neo4j (With configurable parameters for connection pooling and timeouts)
neo4j_driver = GraphDatabase.driver(constants.NEO4J_URI, 
                                    auth = (constants.NEO4J_USER, constants.NEO4J_PASSWORD),
                                    max_connection_lifetime = constants.MAX_CONNECTION_LIFETIME,
                                    max_connection_pool_size = constants.MAX_CONNECTION_POOL_SIZE,
                                    connection_acquisition_timeout = constants.CONNECTION_TIMEOUT,
                                    liveness_check_timeout = constants.LIVENESS_CHECK_TIMEOUT)
class DocumentHandler(FileSystemEventHandler):
    def __init__(self, qdrant_client, neo4j_driver):
        self.qdrant_client = qdrant_client
        self.neo4j_driver = neo4j_driver

    def on_created(self, event):
        if not event.is_directory:
            file_path = event.src_path
            print(f"Processing a new file detected: {file_path}")
            
            try:
                # Process the newly created file and index its content into Qdrant and Neo4j
                promerge_process_files(file_path, self.neo4j_driver)

                destination = "./Processed"
                os.makedirs(destination, exist_ok=True)

                # Wait a moment (1 second) to ensure the file is fully written before moving it
                time.sleep(1)

                # Move the processed file to the "Processed" folder
                shutil.move(file_path, os.path.join(destination, os.path.basename(file_path)))

            except Exception as e:
                print(f"Error in Watchdog event for {file_path}: {e}")

def promerge_load_text_from_image(file_path: str) -> str:
    imagens = cv2.imread(file_path)
    
    if imagens is None:
        return ""

    imagens = cv2.resize(imagens, None, fx = 2, fy = 2, interpolation = cv2.INTER_CUBIC)
    gray = cv2.cvtColor(imagens, cv2.COLOR_BGR2GRAY)
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    img_nitida = cv2.filter2D(gray, -1, kernel)    
    text = ocr_reader.readtext(img_nitida, detail=0)

    return '\n'.join(text)

def promerge_load_text_from_video(file_path: str) -> str:
    result = whisper_model.transcribe(file_path, language="pt")
    return result.get("text", "")

def promerge_load_text_from_audio(file_path: str) -> str:    
    try:
        client = Groq(api_key = constants.GROQ_API_KEY)

        with open(file_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                file = audio_file,
                model = constants.GROQMODEL_NAME_AUDIO,
                language = "pt",
                response_format="text")

        return transcription

    except Exception as e:
        print(f"Error transcribing audio: {e}")
        return ""

def promerge_load_text_from_word(file_path: str) -> str:
    doc = docx.Document(file_path)
    return '\n'.join([para.text for para in doc.paragraphs if para.text])

def promerge_load_text_from_ppt(file_path: str) -> str:
    ppt = Presentation(file_path)
    text = []
    for slide in ppt.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text") and shape.text:
                text.append(shape.text)

    return '\n'.join(text)

def promerge_load_text_from_pdf(path: str) -> str:
    texts = []
    reader = PdfReader(path)
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            texts.append(extracted)

    return "\n".join(texts)

def promerge_extract_file_content(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    
    audios = (".mp3", ".wav", ".m4a", ".flac", ".aac", ".ogg")
    videos = (".mp4", ".mov", ".mkv", ".avi", ".webm")
    images = (".png", ".jpg", ".jpeg")
    docs = (".doc", ".docx")
    ppts = (".ppt", ".pptx")
    
    if ext == ".pdf":
        return promerge_load_text_from_pdf(file_path)
    
    elif ext == ".txt":
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    elif ext in docs:
        return promerge_load_text_from_word(file_path)

    elif ext in ppts:
        return promerge_load_text_from_ppt(file_path)

    elif ext in audios:
        return promerge_load_text_from_audio(file_path)

    elif ext in videos:
        return promerge_load_text_from_video(file_path)

    elif ext in images:
        return promerge_load_text_from_image(file_path)
    
    return ""

# Extract entities from the given text.
def promerge_extract_entities_batch(chunk_text: str) -> dict:
    try:
        response = entity_chain.invoke({"text": chunk_text})

        return response if isinstance(response, dict) else {}
    
    except Exception as e:
        print(f"Error extracting entities using LLM: {e}")
        return {}

#Setup Neo4j database by creating constraints and indexes.
def promerge_setup_databases(neo4j_driver):
    #Execute queries to create constraints and indexes in Neo4j
    with neo4j_driver.session() as session:        
        # Execute each query in the QUERIESNEO4J list to set up constraints and indexes
        for q in constants.QUERIESNEO4J:
            # Execute the query to create constraints and indexes in Neo4j
            session.run(q)

    # Message to indicate that the constraints and indexes have been created
    print("Neo4j constraints and indexes configured successfully!")

def promerge_save_graph_batch(driver, file_path: str, chunks_data: list[dict], batch_size: int = 50):
    # Validate if chunks_data is empty
    if not chunks_data:
        return

    # Processs the chunks in batches to avoid memory issues and optimize performance
    total_chunks = len(chunks_data)
    for i in range(0, total_chunks, batch_size):
        # Create a sub-batch of chunks to be processed in this iteration
        sub_batch = chunks_data[i : i + batch_size]
        max_retries = constants.MAX_RETRIES

        # Retry mechanism to handle transient errors during database writes
        for attempt in range(max_retries):
            try:
                with driver.session() as session:
                    # Execute the write operation in a transaction to ensure atomicity and consistency
                    session.execute_write(save_batch_graph_commands, file_path, sub_batch)                    
                break

            except Exception as e:
                # Log the error and retry if the maximum number of retries has not been reached
                print(f"Error saving batch {i // batch_size + 1} (Attempt: {attempt +1} / {max_retries}): {e}")

                # Exponential backoff strategy to avoid overwhelming the database with retries
                time.sleep(2 * (attempt + 1))

                # If the maximum number of retries is reached, raise the exception to be handled by the calling function
                if attempt == max_retries - 1:
                    raise e

def save_batch_graph_commands(comm, file_path: str, chunks_data: list[dict]):
    # Queries to ingest the chunks and their relationships into the Neo4j graph database
    comm.run(constants.GRAPH_QUERY_INGESTION, path = file_path, chunks = chunks_data)

    # If any of the chunks have relationships, execute the query to save those relationships in the graph
    if any(c.get("relationships") for c in chunks_data):
        comm.run(constants.GRAPH_QUERY_RELATIONSHIPS, chunks = chunks_data)

def promerge_process_files(file_path: str, neo4j_driver):
    # 1. Print a message indicating that the file is being indexed
    print(f"Indexing file: {file_path}")

    # 2. Extract the content of the file based on its type (PDF, Word, PPT, audio, video, image, etc.)
    contents = promerge_extract_file_content(file_path)

    # 3. Check if the extracted content is empty or consists only of whitespace, and print a warning message if so
    if not contents.strip():
        print(f"Warning: Empty content for {file_path}")
        return

    # 4. Divide the content into chunks using the RecursiveCharacterTextSplitter
    textSplitter = RecursiveCharacterTextSplitter(chunk_size = constants.NVIDIACHUNKSIZE, 
                                                  chunk_overlap = constants.NVIDIACHUNKOVERLAP,
                                                  separators = ["\n\n", "\n", ".", ","])
    texts = textSplitter.split_text(contents)

    # 5. Create metadata for each chunk, including the file path, chunk index, source file name, and file extension
    metadatas = [{"path": file_path,
                  "chunk": idx,
                  "source": os.path.basename(file_path),
                  "extension": os.path.splitext(file_path)[1]
                 } for idx, _ in enumerate(texts)]

    # For efficiency, we can add texts in batches to Qdrant
    for i in range(0, len(texts), 128):
        #Save a batch of texts and their corresponding metadata to Qdrant
        qdrant.add_texts(texts[i: i + 128], metadatas[i: i + 128])

    # 6. Extract entities and relationships from each chunk using the LLM
    print(f"Extracting entities from {len(texts)} chunks via LLM...")
    chunks_batch = []

    # 7. Loop through each chunk of text to extract entities and relationships using the LLM
    for idx, chunk in enumerate(texts):
        # Variable to uniquely identify each chunk in the context of the file
        chunk_id = f"{file_path}:{idx}"        
        result_llm = promerge_extract_entities_batch(chunk)
        raw_entities = result_llm.get("entities", [])
        raw_relationships = result_llm.get("relationships", [])

        # Remove entities with null or empty names and ensure they are in the correct format
        clean_entities = []

        # If the raw_entities is a list, loop through each entity to validate and clean the data
        if isinstance(raw_entities, list):
            # Loop through each entity to validate and clean the data
            for e in raw_entities:
                # Check if the entity is a dictionary and has a valid name
                if isinstance(e, dict):
                    # Get the name of the entity, checking for both "name" and "nome" keys to support different languages
                    name = e.get("name") or e.get("nome")

                    # Only add entities that have a valid name
                    if name and str(name).strip():
                        # Append the cleaned entity to the clean_entities list, ensuring that the name and type are stripped of whitespace
                        clean_entities.append({ "name": str(name).strip(), "type": str(e.get("type", "Entity")).strip()})

        # Remove relationships with null or empty source/target and ensure they are in the correct format
        clean_relationships = []

        if isinstance(raw_relationships, list):
            # Loop through each relationship to validate and clean the data
            for r in raw_relationships:
                # Check if the relationship is a dictionary and has valid source and target
                if isinstance(r, dict):
                    source = r.get("source") or r.get("origem")
                    target = r.get("target") or r.get("destino")
                    rel_type = r.get("type") or r.get("tipo") or "RELATED_TO"

                    # Only add relationships that have valid source and target names
                    if source and target and str(source).strip() and str(target).strip():
                        clean_relationships.append({ "source": str(source).strip(),
                                                     "target": str(target).strip(),
                                                     "type": str(rel_type).strip()})
                        
        # Append the cleaned entities and relationships to the chunks_batch for later persistence in Neo4j
        chunks_batch.append({"id": chunk_id, 
                             "text": chunk, 
                             "chunk_index": idx,
                             "entities": clean_entities,
                             "relationships": clean_relationships})

    # Message to indicate that the graph structure is being saved in Neo4j
    print("Saving graph structure in Neo4j...")

    # 8. Save the structured graph data into Neo4j in batches to optimize performance and avoid memory issues    
    promerge_save_graph_batch(neo4j_driver, file_path, chunks_batch, batch_size=50)

    # Message to indicate that the file has been processed and saved successfully
    print(f"File {file_path} processed and saved successfully!")

def promerge_files_indexes(caminho: str):
    # Check if the Qdrant collection exists, if not, create it with the specified vector configuration
    if not qdrantClient.collection_exists(collection_name=constants.QDRANT_COLLECTION_NAME):
        # Create the Qdrant collection with the specified vector size and distance metric (CONSINE)
        qdrantClient.create_collection(constants.QDRANT_COLLECTION_NAME, 
                                       vectors_config=VectorParams(size = 768, distance = Distance.COSINE))

        # Create a payload index for the "metadata.source" field to optimize search queries
        qdrantClient.create_payload_index(collection_name = constants.QDRANT_COLLECTION_NAME,
                                          field_name = "metadata.source",
                                          field_schema = PayloadSchemaType.KEYWORD)
    
    # Initialize the Neo4j database by creating necessary constraints and indexes
    promerge_setup_databases(neo4j_driver)

    # Get a list of all files in the specified directory and its subdirectories
    filesToProcess = [str(p) for p in Path(caminho).rglob('*') if p.is_file()]

    #Loop through each file and process it, handling any exceptions that may occur during processing
    for file_path in filesToProcess:
        try:
            # Process the file and index its content into Qdrant and Neo4j
            promerge_process_files(file_path, neo4j_driver)

        except Exception as e:
            print(f"Failure to process file {file_path} - Error: {e}")

    #Message to indicate that the indexing of all files in the specified directory has been completed
    print("\nIndexing finished!\n")

def promerge_initializes_mcp_processments():
    path = "./Documents"
    os.makedirs(path, exist_ok=True)
    
    # Processes all existing files in the "Documents" folder and indexes them into Qdrant and Neo4j
    promerge_files_indexes(path)

    # Initialize the Watchdog observer to monitor the "Documents" folder for new files and process them as they are added
    event_handler = DocumentHandler(qdrantClient, neo4j_driver)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()

    # Message to indicate that the Watchdog observer has been started and is monitoring the "Documents" folder for new files
    print("Monitoring activated. Press Ctrl + C to finish.")

    try:
        while True:
            time.sleep(2)

    except KeyboardInterrupt:
        observer.stop()

if __name__ == "__main__":
    promerge_initializes_mcp_processments()