#
# https://build.nvidia.com/settings/api-keys  -- Criar conta ANTES
#
# Por exemplo: KEY_VAL_LHAMA_PROMERGE (Setar a opção "Never Expires") 
#
# Import
import os

# Define a key de acesso da NVidia
nvidia_key = "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"

# Define o endereço base da url da NVidia
baseNvidia_url = "https://integrate.api.nvidia.com/v1"

# Define o endereço do Qdrant
qdrantUrl = "http://localhost:6333"

# Define o nome do modelo (tokenizador - Realiza o Chunking)
model_name = "sentence-transformers/msmarco-bert-base-dot-v5"

# Define o nome do modelo LLM
model_nameLLM = "meta/llama-3.3-70b-instruct"

# Define a quantidade de respostas
numberOfAnswers = 10

# Define o usuário e senha do Neo4j (padrão)
neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
neo4j_user = os.getenv("NEO4J_USER", "neo4j")
neo4j_password = os.getenv("NEO4J_PASSWORD", "promerge") 

# Define o número máximo de tokens para a resposta do LLM
max_tokens = 8000

# Define a temperatura para a resposta do LLM (quanto mais próximo de 0, mais exata é a resposta)
temperature = 0.5

# Define a quantidade de respostas a serem retornadas pelo LLM (top_p = 1 retorna apenas a resposta mais provável)
top_p = 1

# Modelos de Prompts
promptModel1 = "Responda à pergunta do usuário utilizando prioritariamente as informações fornecidas no contexto. "\
               "Instruções: "\
               "1. Analise a pergunta do usuário. "\
               "2. Utilize as informações do contexto como principal fonte para construir a resposta. "\
               "3. Caso o contexto seja insuficiente, complemente a resposta com conhecimento geral da inteligência artificial. "\
               "4. Não invente informações que não estejam no contexto ou que não possam ser inferidas com segurança. "\
               "5. Forneça uma resposta clara, objetiva e bem estruturada. "\
               "6. Quando apropriado, organize a resposta em tópicos ou passos para facilitar o entendimento. "\
               "Objetivo: Gerar uma resposta correta, completa e fácil de entender para o usuário. "        

# Modelos de Prompts (Usando RAG)
promptDefault = "Você é um assistente especializado em responder perguntas utilizando um contexto fornecido. "\
                "Objetivo: "\
                "Responder à pergunta do usuário utilizando prioritariamente as informações presentes no contexto. "\
                "Regras: "\
                "1. Prioridade do contexto "\
                "- Utilize primeiro as informações presentes no contexto fornecido. "\
                "- Se o contexto contiver a resposta completa, baseie sua resposta apenas nele. "\
                "2. Contexto parcial "\
                "- Se o contexto contiver apenas parte da resposta, utilize essas informações e complemente com conhecimento geral confiável. "\
                "3. Contexto insuficiente "\
                "- Se o contexto não contiver informações suficientes para responder à pergunta, informe claramente que o contexto é insuficiente e responda utilizando conhecimento geral. "\
                "4. Conflito de informações "\
                "- Se houver conflito entre o contexto e o conhecimento geral, priorize o contexto fornecido. "\
                "5. Contexto irrelevante "\
                "- Ignore partes do contexto que não estejam relacionadas à pergunta. "\
                "6. Evitar alucinações "\
                "- Não invente fatos. "\
                "- Utilize apenas informações presentes no contexto ou conhecimento geral confiável. "\
                "Formato da resposta: "\
                "- Resposta clara e objetiva "\
                "- Utilize listas ou passos quando apropriado "\
                "- Destaque informações importantes "