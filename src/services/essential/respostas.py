import discord,os,asyncio,time,json,datetime,pytz
from discord.ext import commands
from discord import app_commands , SyncWebhook
from src.services.connection.database import BancoServidores,BancoUsuarios , BancoLogs
from discord import HTTPException, Forbidden, NotFound , ClientException
from dotenv import load_dotenv


#load_dotenv(os.path.join(os.path.dirname(__file__), '.env')) #load .env da raiz
#DISCORD_LOGS_WEBHOOK = os.getenv("DISCORD_LOGS_WEBHOOK")



# Parte do primeiro de abril
listapegadinha = [] # Lista com todos que cairam na pegadinha


respostas = {}
# Listar arquivos na pasta
for arquivo in os.listdir("src/core/responses"):
    caminho_arquivo = os.path.join("src/core/responses", arquivo)

    # Verificar se é um arquivo JSON
    if os.path.isfile(caminho_arquivo) and arquivo.endswith(".json"):
        # Extrair o idioma do nome do arquivo (assumindo que os nomes têm um padrão)
        idioma = arquivo.split(".")[0]

        # Carregar o arquivo JSON no dicionário respostas
        with open(caminho_arquivo, "r", encoding="utf-8") as file:
            respostas[idioma] = json.load(file)


class Res:
    # Cache local para armazenar o idioma já verificado
  idioma_cache = {}

  @staticmethod
  def trad(str, interaction=None, guild=None, user=None):
        try:
            # Verificação de idioma já armazenado no cache
            if interaction is not None:
                user_id = interaction.user.id
                guild_id = interaction.guild.id if interaction.guild else None
                
                # Cache para o idioma do usuário
                if user_id in Res.idioma_cache:
                  if interaction.locale.value == Res.idioma_cache[user_id]:
                    idioma = Res.idioma_cache[user_id]
                  else:
                    idioma = interaction.locale.value
                    Res.idioma_cache[user_id] = idioma
                    BancoUsuarios.update_document(user_id, {"language": idioma})
                else:
                    # Detecta idioma do usuário no interaction
                    if interaction.locale.value in respostas:
                        idioma = interaction.locale.value
                        Res.idioma_cache[user_id] = idioma
                        BancoUsuarios.update_document(user_id, {"language": idioma})
                    elif interaction.guild_locale.value in respostas:
                        idioma = interaction.guild_locale.value
                        Res.idioma_cache[guild_id] = idioma
                        BancoServidores.update_document(guild_id, {"language": idioma})
                    else:
                        idioma = 'pt-BR'
                        Res.idioma_cache[user_id] = idioma

            elif user:
                # Verificação no cache para o idioma do usuário
                user_id = user

                if user_id in Res.idioma_cache:
                    idioma = Res.idioma_cache[user_id]
                else:
                    try:
                        retorno = BancoUsuarios.insert_document(user)
                        idioma = retorno.get("language", 'pt-BR')
                        Res.idioma_cache[user_id] = idioma
                    except:
                        idioma = 'pt-BR'
                        Res.idioma_cache[user_id] = idioma

            elif guild:
                # Verificação no cache para o idioma do servidor
                guild_id = guild
                if guild_id in Res.idioma_cache:
                    idioma = Res.idioma_cache[guild_id]
                else:
                    try:
                        retorno = BancoServidores.insert_document(guild)
                        idioma = retorno.get("language", 'pt-BR')
                        Res.idioma_cache[guild_id] = idioma
                    except:
                        idioma = 'pt-BR'
                        Res.idioma_cache[guild_id] = idioma
            else:
                idioma = 'pt-BR'

        except Exception as e:
            # Fallback caso ocorra algum erro
            print(f"Erro ao detectar idioma: {e}")
            idioma = 'pt-BR'

        # Busca a resposta no idioma correto
        res = respostas.get(idioma, {}).get(str)
        return res



  async def erro_brix_embed(interaction,str,e,comando):
    erro_formatado = f"{e}"  # Evita chamar str() diretamente

    # Tratamento de erros específicos
    if "Maximum number of emojis reached" in erro_formatado:
        mensagem_erro = "O servidor já atingiu o limite de emojis. kyuuu"
    elif isinstance(e, ClientException):
        mensagem_erro = "Não consegui executar a ação que você pediu. kyuuu"
    elif isinstance(e, Forbidden) or "Missing Permissions" in erro_formatado:
        mensagem_erro = Res.trad(interaction=interaction, str="message_erro_permissao_general")
    elif isinstance(e, HTTPException):
        mensagem_erro = f"Erro HTTP: {e.text} (Código {e.status})"
    elif isinstance(e, NotFound):
        mensagem_erro = "O recurso solicitado não foi encontrado."
    else:
        mensagem_erro = f"Ocorreu um erro desconhecido, confira ele ai: {erro_formatado}"

    resposta = discord.Embed( 
            colour=discord.Color.red(),
            description=Res.trad(interaction=interaction, str=str).format(mensagem_erro)
            )
    print(f"error: {e}\n{interaction.user} - comando:{comando}")
    try:
        await interaction.response.send_message(embed=resposta,delete_after=30, ephemeral= True)
    except:
        try:
            await interaction.followup.send(embed=resposta)
        except:
            await interaction.followup.send(Res.trad(interaction=interaction, str=str).format(mensagem_erro))


        






  async def print_brix(comando,interaction,condicao=None):
    usuario_banco = BancoUsuarios.insert_document(interaction.user)
    now = datetime.datetime.now().astimezone(pytz.timezone('America/Sao_Paulo'))
    primeiroabril = datetime.date(now.year , 4 , 1 )
    if 'ban' in usuario_banco:  # Verifica se 'servidor' não é None ou vazio
        print(f"Usuario {interaction.user.id} na lista de banidos, comando negado")
        await interaction.response.send_message(Res.trad(interaction=interaction,str="message_banido").format(int(usuario_banco['ban']['data'].timestamp()),usuario_banco['ban']['motivo'],usuario_banco['ban']['autor']),delete_after=60)
        return True
    
    elif now.date() == primeiroabril:
        if interaction.user.id not in listapegadinha:
            listapegadinha.append(interaction.user.id)
            await interaction.response.send_message(Res.trad(interaction=interaction,str="message_banido").format(int(now.timestamp()),"Porque eu quis","Brix The Braixen") )
            await asyncio.sleep(10)
            await interaction.followup.send(Res.trad(interaction=interaction,str="message_1abril"))
            print(f"Usuario {interaction.user.id} Caiu na pegadinha de primeiro de abril")
            return True

    else:
        BancoLogs.registrar_comando(interaction, comando, condicao)
  

"""
  async def print_brix(comando,interaction,condicao=None):
    usuario_banco = BancoUsuarios.insert_document(interaction.user)
    now = datetime.datetime.now().astimezone(pytz.timezone('America/Sao_Paulo'))
    primeiroabril = datetime.date(now.year , 4 , 1 )
    if 'ban' in usuario_banco:  # Verifica se 'servidor' não é None ou vazio
        print(f"Usuario {interaction.user.id} na lista de banidos, comando negado")
        await interaction.response.send_message(Res.trad(interaction=interaction,str="message_banido").format(int(usuario_banco['ban']['data'].timestamp()),usuario_banco['ban']['motivo'],usuario_banco['ban']['autor']),delete_after=60)
        return True
    
    elif now.date() == primeiroabril:
        if interaction.user.id not in listapegadinha:
            listapegadinha.append(interaction.user.id)
            await interaction.response.send_message(Res.trad(interaction=interaction,str="message_banido").format(int(now.timestamp()),"Porque eu quis","Brix The Braixen") )
            await asyncio.sleep(10)
            await interaction.followup.send(Res.trad(interaction=interaction,str="message_1abril"))
            print(f"Usuario {interaction.user.id} Caiu na pegadinha de primeiro de abril")
            return True

    else:
        mensagem = f"Usuario: {interaction.user.name} - {interaction.user.id} usou comando /{comando}"
        if condicao:
            mensagem = mensagem + f"\ncondição: {condicao}"
        if interaction.guild:
            mensagem = mensagem + f"\nServidor: {interaction.guild.id}-{interaction.guild.name}\n\n"
        try:
            # URL do webhook
            webhook = discord.SyncWebhook.from_url(DISCORD_LOGS_WEBHOOK)
            webhook.send(mensagem)

        except:
            print(mensagem)"""
  


