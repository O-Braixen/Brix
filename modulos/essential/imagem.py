import aiohttp
from PIL import Image
import io,discord

async def pegar_imagem(interaction: discord.Interaction, imagem: discord.Attachment = None, url_imagem: str = None, avatar_usuario: discord.User = None, posicao_imagem: int = 0):
    """
    Função para obter a imagem a partir de diferentes fontes:
    - Imagem anexada
    - URL de uma imagem
    - Avatar de um usuário
    - Última imagem no chat, se nenhuma das anteriores for fornecida

    Retorna:
    - PIL.Image object se a imagem for encontrada
    - None se não for possível obter uma imagem
    """
    imagem_pil = None
    
    # Verifica se a imagem foi anexada
    if imagem:
        arquivo = await imagem.read()
        imagem_pil = Image.open(io.BytesIO(arquivo))
    
    # Verifica se foi passada uma URL de imagem
    elif url_imagem:
        async with aiohttp.ClientSession() as session:
            async with session.get(url_imagem) as resp:
                if resp.status == 200:
                    dados_imagem = await resp.read()
                    imagem_pil = Image.open(io.BytesIO(dados_imagem))
                else:
                    raise Exception("Não foi possível carregar a imagem a partir da URL.")
    
    # Verifica se foi selecionado o avatar de um usuário
    elif avatar_usuario:
        async with aiohttp.ClientSession() as session:
            avatar_url = avatar_usuario.display_avatar.url
            async with session.get(avatar_url) as resp:
                if resp.status == 200:
                    dados_avatar = await resp.read()
                    imagem_pil = Image.open(io.BytesIO(dados_avatar))
                else:
                    raise Exception("Não foi possível carregar o avatar do usuário.")
    
    # Caso nenhuma opção seja fornecida, busca a última imagem no histórico do chat
    else:
        imagens_encontradas = []
        messages = interaction.channel.history(limit=50)
        async for message in messages:
            if message.attachments:
                for attachment in message.attachments:
                    if attachment.content_type and "image" in attachment.content_type:
                        arquivo = await attachment.read()
                        #imagem_pil = Image.open(io.BytesIO(arquivo))
                        imagens_encontradas.append(Image.open(io.BytesIO(arquivo)))
                        #break
            if len(imagens_encontradas) > posicao_imagem:
                break
        if len(imagens_encontradas) > posicao_imagem:
            imagem_pil = imagens_encontradas[posicao_imagem]
        else:
            return None
    
    # Retorna a imagem ou None se não encontrar nenhuma
    return imagem_pil
