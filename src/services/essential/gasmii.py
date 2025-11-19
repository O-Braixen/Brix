import os, io ,asyncio , tempfile, base64 , traceback
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image





load_dotenv()
GOOGLE_AI_KEY = os.getenv("GOOGLE_AI_KEY")

MAX_RETRIES = 3  # Número máximo de tentativas
RETRY_DELAY = 2  # Atraso entre as tentativas (em segundos)


try:
    if not GOOGLE_AI_KEY:
        raise ValueError("API KEY ausente.")
    genaiclient = genai.Client(api_key=GOOGLE_AI_KEY)
    print("✔️   -  Conectado a api do Gemini com sucesso.")
except Exception as e:
    print(f"❌  -  Erro ao inicializar Gemini AI: {e}")

modelo_linguagem = "gemini-2.0-flash"
imagem_modelo = "gemini-2.0-flash-preview-image-generation"


configurações_de_segurança = [
    types.SafetySetting(category='HARM_CATEGORY_HARASSMENT', threshold='BLOCK_NONE'),
    types.SafetySetting(category='HARM_CATEGORY_HATE_SPEECH', threshold='BLOCK_NONE'),
    types.SafetySetting(category='HARM_CATEGORY_SEXUALLY_EXPLICIT', threshold='BLOCK_NONE'),
    types.SafetySetting(category='HARM_CATEGORY_DANGEROUS_CONTENT', threshold='BLOCK_NONE')
]


"""
text_generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 1024,
}
image_generation_config = {
    "temperature": 0.4,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 1024,
}

"""

#RESPONDE A TUDO DE TEXTO VIA TEXTO
async def generate_response_with_text(message_text):
    prompt_parts = [message_text]
    for attempt in range(MAX_RETRIES):
        try:
            response = genaiclient.models.generate_content(model=modelo_linguagem , contents=prompt_parts , config= types.GenerateContentConfig(safety_settings=configurações_de_segurança))
            return response.text
        except Exception as e:
            print(f"[Gemini ERRO] Tentativa {attempt+1}/{MAX_RETRIES} → {e}")

            # Se ainda tem tentativas, tenta de novo
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(RETRY_DELAY)
                continue
            # Acabaram as tentativas → ESTOURA o erro
            raise



    
#RESPONDE A TUDO DE IMAGEM VIA TEXTO
async def generate_response_with_image_and_text(image_data, text):
    image = Image.open(io.BytesIO(image_data))
    for attempt in range(MAX_RETRIES):
        try:
            response = genaiclient.models.generate_content(model=modelo_linguagem , contents= [image , text], config= types.GenerateContentConfig(safety_settings=configurações_de_segurança))
            return response.text
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                # Atraso fixo entre as tentativas
                await asyncio.sleep(RETRY_DELAY)
            else:
                return f"❌ Erro na tentativa de consulta com a API do gemini, veja o erro indicado {e}"

#RESPONDE A TUDO DE AUDIO VIA TEXTO
async def generate_response_with_transcribe_audio(audio_data, text):
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_audio:
        temp_audio.write(audio_data)  # Escreve os bytes no arquivo
        temp_audio_path = temp_audio.name  # Pega o caminho do arquivo
        
    myfile = genaiclient.files.upload(file=temp_audio_path )
    for attempt in range(MAX_RETRIES):
        try:
            response = genaiclient.models.generate_content(model=modelo_linguagem , contents= [myfile , text], config= types.GenerateContentConfig(safety_settings=configurações_de_segurança))
            return response.text
        except:
            if attempt < MAX_RETRIES - 1:
                # Atraso fixo entre as tentativas
                await asyncio.sleep(RETRY_DELAY)
            else:
                return f"❌ Erro na tentativa de consulta com a API do gemini, tente mais tarde"



#RESPONDE A TUDO DE VIDEO VIA TEXTO
async def generate_response_with_video_and_text(video_data, text):
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_video:
        temp_video.write(video_data)  # Escreve os bytes no arquivo
        temp_video_path = temp_video.name  # Pega o caminho do arquivo
    
    try:
        myfile = genaiclient.files.upload(file=temp_video_path )
    except: return f"❌ Erro na tentativa de consulta com a API do gemini, tente mais tarde"
    for attempt in range(MAX_RETRIES):
        try:
            print(f"🔮  -  tentativa: {attempt}")
            await asyncio.sleep(0.3)
            response = genaiclient.models.generate_content(model=modelo_linguagem , contents= [myfile , text], config= types.GenerateContentConfig(safety_settings=configurações_de_segurança))
            return response.text
        except:
            if attempt < MAX_RETRIES - 1:
                # Atraso fixo entre as tentativas
                await asyncio.sleep(RETRY_DELAY)
            else:
                return f"❌ Erro na tentativa de consulta com a API do gemini, tente mais tarde"




# AINDA NÂO DISPONIVEL
#RESPONDE A TUDO DE TEXTO VIA IMAGEM
async def generate_image_by_text( text):
    response = genaiclient.models.generate_content(model=imagem_modelo,contents=text,config=types.GenerateContentConfig( response_modalities=['IMAGE','TEXT'],safety_settings=configurações_de_segurança))
    buffer = None
    for part in response.candidates[0].content.parts:
        print(part)
        if part.text is not None:
            text = part.text
            print(text)
        
        if hasattr(part, "inline_data") and hasattr(part.inline_data, "data"):
            print("imagem")
            print(f"Tamanho do base64: {len(part.inline_data.data)} bytes")

            try:
                image_data = base64.b64decode(part.inline_data.data)
                
                # Verificação rápida: dados suficientes pra imagem?
                if len(image_data) < 100:
                    print("Aviso: imagem com poucos bytes, pode estar corrompida ou muito pequena, mas vou tentar abrir assim mesmo.")
                
                image = Image.open(io.BytesIO(image_data))
                buffer = io.BytesIO()
                image.save(buffer, format="PNG")
                buffer.seek(0)
            
            except Exception as e:
                print(f"erro na imagem: {e}")
    
    return buffer , text

