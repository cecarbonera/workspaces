# Importa o módulo sys para acessar os argumentos da linha de comando
import sys

# Importa o módulo docx para manipulação de arquivos Word
import docx

# Importa o módulo PyPDF2 para manipulação de arquivos PDF
import PyPDF2

# Importa o módulo whisper para processamento de aúdio E vídeo
import whisper

# Importa os módulos easyocr e cv2
import easyocr, cv2

# Importa o módulo Presentation do pacote pptx para manipulação de arquivos PowerPoint
from pptx import Presentation

# Importa as funções listdir, isfile, join e isdir dos módulos os e os.path para manipulação de pastas e arquivos
from os import listdir
from os.path import isfile, join, isdir

# Importa a classe TokenTextSplitter do pacote langchain_text_splitters para a divisão do texto em tokens
from langchain_text_splitters import TokenTextSplitter

# Importa a classe HuggingFaceEmbeddings do pacote langchain_huggingface para criar as embeddings
from langchain_huggingface import HuggingFaceEmbeddings

# Importa as classes QdrantClient, Distance e VectorParams do pacote qdrant_client
from qdrant_client import QdrantClient

# Criaremos o cliente de acesso ao Qdrant, definindo os parâmetros de armazenamento no banco vetorial
from qdrant_client.models import Distance, VectorParams

# Importa a classe Qdrant do pacote langchain_qdrant para criar uma instância do Qdrant e enviar os dados para o banco vetorial
from langchain_qdrant import Qdrant

# Filtra warnings
import warnings
warnings.filterwarnings('ignore')

# Define a função que carrega o texto de uma imagem
def promerge_carrega_texto_imagem(arquivo):        
    #Carregar o arquivo
    img = cv2.imread(arquivo)

    # Aumentar a escala da imagem ajuda o OCR a ler letras pequenas
    img = cv2.resize(img, None, fx = 2, fy = 2, interpolation = cv2.INTER_CUBIC)

    # Converter para tons de cinza
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Aplicar um filtro de nitidez (Sharpening)
    kernel = [[0, -1, 0], [-1, 5, -1], [0, -1, 0]]
    
    # Importa o numpy
    import numpy as np
    
    kernel = np.array(kernel)
    img_nítida = cv2.filter2D(gray, -1, kernel)

    # Envia a imagem processada para o EasyOCR
    reader = easyocr.Reader(['pt'])
    text = reader.readtext(img_nítida, detail=0)
    
    # Definir o retorno
    return '\n'.join(text)

# Define a função que carrega o texto de um arquivo de vídeo
def promerge_carrega_texto_video(arquivo):        
    # 1. Escolha o modelo (tiny, base, small, medium, large)
    # O 'small' é excelente para o português e roda bem em CPUs comuns.
    modelo = whisper.load_model("small")

    # 2. Transcrever o vídeo diretamente
    result = modelo.transcribe(arquivo, language="pt", verbose=True)

    # Definir o retorno
    return '\n'.join(result["text"])
    
# Define a função que carrega o texto de um arquivo de áudio
def promerge_carrega_texto_audio(arquivo):        
    # Carrega o modelo (o 'base' é rápido, o 'large' é super preciso)
    model = whisper.load_model("base")

    # Transcreve o áudio (aceita quase qualquer formato: mp3, m4a, wav)
    result = model.transcribe(arquivo)
    
    #definir o retorno
    return '\n'.join(result["text"])

# Define a função que carrega o texto de um arquivo Word
def promerge_carrega_texto_word(arquivo):    
    # Abre o arquivo Word
    doc = docx.Document(arquivo)   
    
    # Extrai o texto de cada parágrafo e adiciona à lista
    fullText = [para.text for para in doc.paragraphs]
    
    # Junta todos os textos em uma única string separada por quebras de linha
    return '\n'.join(fullText)

# Define a função que carrega o texto de um arquivo PowerPoint
def promerge_carrega_texto_ppt(arquivo):    
    # Abre o arquivo PowerPoint
    ppt = Presentation(arquivo)
    
    # Inicializa uma lista vazia para armazenar os textos
    fullText = []
    
    # Itera sobre todos os slides
    for slide in ppt.slides:        
        # Itera sobre todas as formas no slide
        for shape in slide.shapes:            
            # Se a forma tiver o atributo "text", adiciona o texto à lista
            if hasattr(shape, "text"):
                fullText.append(shape.text)
    
    # Junta todos os textos em uma única string separada por quebras de linha
    return '\n'.join(fullText)

# Define a função principal para indexação dos documentos
def promerge_indexacao_arquivos(caminho):    
    # Define o nome do modelo a ser usado para criar as embeddings
    model_name = "sentence-transformers/msmarco-bert-base-dot-v5"
    
    # Define as configurações do modelo
    model_kwargs = {'device': 'cpu'}
    
    # Define as configurações de codificação
    encode_kwargs = {'normalize_embeddings': True}

    # Inicializa a classe de embeddings do HuggingFace
    embedding = HuggingFaceEmbeddings(model_name = model_name,
                                      model_kwargs = model_kwargs,
                                      encode_kwargs = encode_kwargs)

    # Inicializa o cliente Qdrant
    client = QdrantClient("http://localhost:6333")
    
    # Define o nome da coleção de embeddings
    collection_name = "ProMergeVectorDB"

    # Se a coleção existir
    if client.collection_exists(collection_name):
        # Exclusão da coleção
        client.delete_collection(collection_name)

    # Cria uma nova coleção com parâmetros especificados
    client.create_collection(collection_name, 
                             vectors_config = VectorParams(size = 768, distance = Distance.DOT))

    # Inicializa a instância Qdrant
    qdrant = Qdrant(client, collection_name, embedding)

    # Imprime mensagem informando que a indexação dos documentos está iniciando
    print("\nIndexando os documentos...\n")

    # Obtém a lista de todos os arquivos no diretório especificado
    lista_arquivos = promerge_lista_arquivos(caminho)

    # Sufixos
    audios_suffixes = (".mp3", ".wav", ".m4a", ".flac", ".aac", ".ogg")
    videos_suffixes = (".mp4",".mov",".mkv",".avi",".webm")
    images_suffixes = (".png", ".jpg", ".jpeg")
    docs_suffixes = (".doc", ".docx")
    ppts_suffixes = (".ppt", ".pptx")
    
    # Itera sobre cada arquivo na lista
    for arquivo in lista_arquivos:
        # try / catch
        try:            
            # Inicializa uma string vazia para armazenar o conteúdo do arquivo processado
            conteudo = ""
            
            # Verifica se o arquivo é um PDF
            if arquivo.endswith(".pdf"):
                # Mensagem de controle do usuário                
                print("Indexando: " + arquivo)
                
                # Ler o arquivo PDF
                arquivoPDF = PyPDF2.PdfReader(arquivo)
                
                for page in arquivoPDF.pages:
                    conteudo += " " + page.extract_text()
            
            # Verifica se o arquivo é um texto simples
            elif arquivo.endswith(".txt"):
                # Mensagem de controle do usuário
                print("Indexando: " + arquivo)
                
                # Abertura do arquivo
                with open(arquivo, 'r') as f:
                    # Leitura do arquivo
                    conteudo = f.read()
            
            # Arquivos do tipo Word
            elif arquivo.endswith(docs_suffixes):
                # Mensagem de controle do usuário                
                print("Indexando: " + arquivo)
                
                # Processar o arquivo do tipo "doc" ou "docx"
                conteudo = promerge_carrega_texto_word(arquivo)
            
            # Arquivos do tipo Power Point
            elif arquivo.endswith(ppts_suffixes):
                # Mensagem de controle do usuário                
                print("Indexando: " + arquivo)
                
                # Processar o arquivo do tipo "ppt" ou "pptx"
                conteudo = promerge_carrega_texto_ppt(arquivo)            

            # Arquivos de Áudio
            elif arquivo.endswith(audios_suffixes):
                # Mensagem de controle do usuário                
                print("Indexando: " + arquivo)

                # Processar o arquivos do áudio
                conteudo = promerge_carrega_texto_audio(arquivo)

            # Arquivos de Vídeo
            elif arquivo.endswith(videos_suffixes):
                # Mensagem de controle do usuário                
                print("Indexando: " + arquivo)

                # Processar o arquivos de video
                conteudo = promerge_carrega_texto_video(arquivo)

            # Arquivos de Imagens
            elif arquivo.endswith(images_suffixes):
                # Mensagem de controle do usuário                
                print("Indexando: " + arquivo)

                # Processar o arquivos de imagem
                conteudo = promerge_carrega_texto_imagem(arquivo)

            else:                
                # Se o arquivo não for de um formato suportado continua para o próximo arquivo
                continue

            # Inicializa o chuck de texto com tamanho e sobreposição especificados (A sobreposição é para manter o vínculo entre os paràgrafos)
            texto_splitter = TokenTextSplitter(chunk_size = 500, chunk_overlap = 50)
            
            # Divide o conteúdo do arquivo em chunks de texto
            textos = texto_splitter.split_text(conteudo)
            
            # Cria metadados para cada chunk de texto
            metadata = [{"path": arquivo} for _ in textos]
            
            # Adiciona os textos e seus metadatas ao Qdrant
            qdrant.add_texts(textos, metadatas = metadata)

        except Exception as e:
            # Se ocorrer um erro, imprime uma mensagem de erro
            print(f"O processo falhou para o arquivo {arquivo} - Erro: {e}")

    # Imprime mensagem informando que a indexação foi concluída
    print("\nIndexação dos Arquivos Concluída com Sucesso!\n")

# Define a função que lista todos os arquivos em um diretório, incluindo os de subdiretórios
def promerge_lista_arquivos(diretorio):    
    # Inicializa uma lista vazia para armazenar os caminhos dos arquivos
    arquivos = []
    
    # Percorre todos os arquivos e sub-diretórios (com os arquivos) do diretório especificado
    for arquivo in listdir(diretorio):        
        # Se for um arquivo, adiciona à lista
        if isfile(join(diretorio, arquivo)):
            arquivos.append(join(diretorio, arquivo))
        
        # Se for um diretório chama a função recursivamente e adiciona os resultados à lista
        elif isdir(join(diretorio, arquivo)):
            arquivos += promerge_lista_arquivos(join(diretorio, arquivo))
    
    # Retorna a lista de arquivos
    return arquivos

# Main principal
if __name__ == "__main__":
    # Argumentos da linha de comando
    arguments = sys.argv
    
    # Se foi fornecido um caminho de diretório
    if len(arguments) > 1:
        #Realiza o processamento dos arquivos
        promerge_indexacao_arquivos(arguments[1])

    else:
        #Imprime uma mensagem de erro
        print("Caminho da pasta com documentos para indexação inválido.") 