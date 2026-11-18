# Importa o módulo os
import os

# Importa o módulo promerge_env_var com a API para o LLM
import promerge_env_var

# Importa a classe FastAPI do módulo fastapi para criar a API
from fastapi import FastAPI

# Importa a classe QdrantClient do módulo qdrant_client para conectar no banco de dados vetorial
from qdrant_client import QdrantClient    

# Importa a classe Qdrant do módulo langchain_qdrant para instanciar o banco de dados vetorial
from langchain_qdrant import Qdrant

# Importa a classe BaseModel do módulo pydantic para validar os dados que forem enviados para a API
from pydantic import BaseModel

# Importa a classe HuggingFaceEmbeddings do módulo langchain_huggingface para gerar as embeddings
from langchain_huggingface import HuggingFaceEmbeddings

# Importa a classe SentenceTransformer do módulo sentence_transformers para importar os tranformadores (vetoriais)
from sentence_transformers import SentenceTransformer

# Importa Neo4j (grafo)
from neo4j import GraphDatabase

# Importar demais funcionalidades necessárias para o funcionamento da API
import yaml, time, docker

# Filtra warnings
import warnings
warnings.filterwarnings('ignore')

# -----------------------------------
# Configurações do LLM e embeddings
# -----------------------------------
class Item(BaseModel):
    query: str    

# Define o formador de sentença
model = SentenceTransformer(promerge_env_var.model_name)

# Cria uma instância de HuggingFaceEmbeddings
embeddings = HuggingFaceEmbeddings(model_name = promerge_env_var.model_name)

# Define a variável use_nvidia_api como False
use_nvidia_api = False

# Verifica se a chave da Nvidia está disponível
if promerge_env_var.nvidia_key != "":
    # Importa a classe OpenAI do módulo openai
    from openai import OpenAI
    
    # Cria uma instância OpenAI com a URL base e a chave da API
    clientOpenAi = OpenAI(base_url = promerge_env_var.baseNvidia_url, 
                          api_key = promerge_env_var.nvidia_key)

    # Define use_nvidia_api como verdadeiro
    use_nvidia_api = True

else:
    # Imprime uma mensagem indicando que não é possível usar um LLM
    print("Não é possível acessar o LLM - ApiKey inválida .")

# ---------------------------------------------------
# Conexão Qdrant (vetorial)
# ---------------------------------------------------
client = QdrantClient(url = promerge_env_var.qdrantUrl)

# Define o nome da coleção
collection_name = "ProMergeVectorDB"

# Cria uma instância de Qdrant para a consulta dos dados do banco vetorial
#
# Modelo de Armazenamento do Qdrant
# {
#   "id": 1,
#   "vector": [0.123, 0.532, 0.998, ...],
#   "payload": 
#	{
#		"page_content": "Texto original do documento",
#		"source": "arquivo.pdf"
#	}
# }       
#
qdrant = Qdrant(client = client, 
                collection_name = collection_name, 
                embeddings = embeddings)

# ---------------------------------------------------
# Conexão Neo4j (grafo)
# ---------------------------------------------------
neo4j_driver = GraphDatabase.driver(promerge_env_var.neo4j_uri, 
                                    auth = (promerge_env_var.neo4j_user, 
                                            promerge_env_var.neo4j_password))

# Define a função query_graph que recebe uma string de consulta e um limite de resultados (padrão é 10)    
def query_graph(query: str, limit = promerge_env_var.numberOfAnswers):    
    with neo4j_driver.session() as session:
        # Define a consulta Cypher para buscar nós cujo conteúdo contém a query, limitando a 10 resultados
        cypher = f"""
                  MATCH (n)
                  WHERE n.content CONTAINS $query
                  RETURN n.content AS content
                  LIMIT $limit
                  """
        # Executa a consulta e obtém os resultados
        result = session.run(cypher, parameters = {"query": query, "limit": limit})
        
        #definir o retorno da consulta
        return [record["content"] for record in result]

# Inicializa todos os containers definidos no arquivo YAML.
def Inicializacao_Containers() -> None:
    # Conecta ao Docker local
    client = docker.from_env()

    # Lê o arquivo YAML
    with open("containers_config.yaml", "r") as f:
        config = yaml.safe_load(f)

    # Encontra a seção "containers" no arquivo YAML e obtém a lista de containers (ou uma lista vazia se não houver containers definidos)
    containers = config.get("containers", [])

    # Itera sobre os containers definidos no arquivo YAML e os inicia (ou reinicia se já existirem)
    for container_info in containers:
        # Obtém o nome do container a partir do arquivo YAML
        name = container_info.get("name")

        # Tenta obter o container pelo nome. Se existir, reinicia. Caso contrário, cria um novo container.
        try:
            # Verifica se o container já existe
            existing = client.containers.get(name)

            # Se o container já existir, reinicia o container e imprime uma mensagem indicando que o container já existe e está sendo reiniciado
            print(f"Container '{name}' sendo inicializado...")

            # Reinicia o container existente
            existing.restart()

        except docker.errors.NotFound:
            # Se o container não existir, cria um novo container com as configurações do arquivo YAML
            print(f"Criando container '{name}'...")
            client.containers.run(**container_info)

# Cria uma instância do FastAPI
api = FastAPI()

# ---------------------------------------------------
#Inicializa os containers definidos no arquivo YAML
# ---------------------------------------------------
Inicializacao_Containers()

# Define a rota /promerge_api (POST)
@api.post("/promerge_api")
async def promerge_api(item: Item):
    # Obtém a query a partir do item
    query = item.query       

    # Gerar embedding (Tranformar a pergunta do usuário em um vetor de valores numéricos para realizar a busca no banco vetorial)
    query_vector = model.encode(query).tolist()

    # Definir os parâmetros de pesquisa (E retornar até 10 resultados próximos - com os maiores scores de proximidade com o tema pesquisado)
    search_result = client.query_points(collection_name = collection_name,
                                        query = query_vector,
                                        limit = promerge_env_var.numberOfAnswers)    
        
    # Constrói o contexto e a lista de resultados -  res.payload (Dados salvos) e res.score (Valor da similaridade)
    context_vectorDb = "\n".join([res.payload.get("page_content", "") for res in search_result.points])

    # --- Recupera resultados do Neo4j ---
    context_graph = "\n".join(query_graph(query))

    # --- Concatena contextos ---
    full_context = f"VectorDB Results:\n{context_vectorDb}\n\nGraphDB Results:\n{context_graph}"

    # Define as regras do prompt que será passado ao LLM
    rolemsg = {"role": "system", "content": promerge_env_var.promptDefault}
    
    # Define as mensagens (contexto) passado ao LLM
    messages = [rolemsg, {"role": "user", "content": f"{full_context}\n\nQuestion: {query}"}]

    # Verifica se a API da Nvidia está sendo usada
    if use_nvidia_api:
            # Faz a chamada do LLM usando a API da Nvidia (LLM hospedado e suportado pelo site da NVidia)
        resposta = clientOpenAi.chat.completions.create(model = promerge_env_var. model_nameLLM,    # Modelo de LLM utilizado
                                                        messages = messages,                        # Menssagens passada ao LLM (Contexto)
                                                        temperature = promerge_env_var.temperature, # Quanto mais próximo de 0 mais exata é a resposta
                                                        top_p = promerge_env_var.top_p,             # Retorno apenas a 1a resposta
                                                        max_tokens = promerge_env_var.max_tokens,   # Limita a resposta ao tamanho de 128000 caracteres 
                                                        stream = False)
    
        # Obtém a resposta do LLM
        response = resposta.choices[0].message.content

    else:
        # Imprime uma mensagem indicando que não é possível usar um LLM
        print("Não é possível chamar o LLM - chamador via API.")
    
    #definir o retorno
    return response 