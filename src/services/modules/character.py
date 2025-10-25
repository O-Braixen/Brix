import discord,os,asyncio,random,uuid
from discord.ext import commands
from discord import app_commands
from src.services.essential.funcoes_usuario import userpremiumcheck 
from src.services.connection.database import BancoUsuarios,BancoBot
from src.services.essential.respostas import Res
from dotenv import load_dotenv

from PyCharacterAI import Client






# ======================================================================

load_dotenv(os.path.join(os.path.dirname(__file__), '.env')) #load .env da raiz
donoid = int(os.getenv("DONO_ID")) #acessa e define o id do dono
char_id = os.getenv('char_id')
char_token = os.getenv('char_token')
id_chatBH =  int(os.getenv('id_chatBH'))


clientcai = Client()






# ======================================================================
  





# Fila global para processar mensagens
fila_global_brix = asyncio.Queue()


# Worker que processa mensagens uma a uma
async def worker_brix(self):
  while True:
    message = await fila_global_brix.get()  # pega a próxima mensagem da fila
    try:
      async with message.channel.typing():
        if not await userpremiumcheck(message.author):
            await message.reply(Res.trad(user=message.author, str="message_cai_only_premium"))
            continue

        try:
            await message.add_reaction('<:BH_Badge_PequenoMago:1154180154076176466>')
        except:
            await message.reply(Res.trad(user=message.author, str='message_cai_erro_reacao'))

        response = await enviar_mensagem_para_character_ai(self, message.author, message.content)
        print(f"🦊 - brix respondeu para {message.author.name} {message.author.id}: {response}")

        if random.randint(1, 100) <= 20:
            response += f"\n{Res.trad(user=message.author, str='message_cai_footer')}"

        await message.reply(response, allowed_mentions=discord.AllowedMentions(everyone=False))
    except Exception as e:
      print(e)
      await message.channel.send(Res.trad(user=message.author, str="message_cai_erro"))
    finally:
      fila_global_brix.task_done()  # marca como processada










# COMANDO PARA CONECTAR O BOT AO CHARACTER.AI
async def enviar_mensagem_para_character_ai(self, membro, mensagem):
  tentativas = 5
  message = ( mensagem.replace(f"<@{self.client.user.id}>", "") .replace("@everyone", "todo mundo") .replace("@here", "todo mundo online")    )
  mensagem_formatada = f"author: {membro}\n{message}"

  try:
    # Puxa ou cria documento do usuário
    dado = BancoUsuarios.insert_document(membro)
    chat_id = str(dado.get("cai-idchat"))

    # Se não existir histórico, reseta antes
    if not chat_id or chat_id == "None":
      await reset_character_ai(membro)
      await asyncio.sleep(0.2)
      dado = BancoUsuarios.insert_document(membro)
      chat_id = str(dado.get("cai-idchat"))

    # Loop de tentativas só para o envio da mensagem
    for tentativa in range(tentativas):
      try:
        data = await clientcai.chat.send_message(char_id, str(dado['cai-idchat']), mensagem_formatada)
        return data.get_primary_candidate().text
      except Exception as e:
        print(f"Tentativa {tentativa+1}/{tentativas} falhou: {e}")
        await clientcai.close_session()
        await asyncio.sleep(1)
        await clientcai.authenticate(char_token)

    # Se todas as tentativas falharem
    return f"{Res.trad(user=membro, str='message_cai_erro')}"

  except Exception as e:
      print(f"CHARACTER.AI ERROR: {e}")
      return f"{Res.trad(user=membro, str='message_cai_erro')}"












# ======================================================================

#FUNÇAO PARA CRIAR UMA NOVA CONVERSA INDIVIDUAL
async def reset_character_ai(membro):
  try:
    #client = await PyCharacterAI.get_client(char_token)
    print("🔄️ - reset conversa")
    # AUTENTICANDO CLIENTECAI PARA ACESSAR AS COISAS NO CAI
    chat, greeting_message = await clientcai.chat.create_chat(char_id)
    item = {"cai-idchat": str(chat.chat_id)}
    BancoUsuarios.update_document(membro,item)
    text = greeting_message.get_primary_candidate().text

    return f"{text}"
  except Exception as e:
    return f"{Res.trad(user=membro,str='message_cai_erro')}"
  











# ======================================================================

#FUNÇAO PARA CRIAR UMA NOVA CONVERSA INDIVIDUAL NA BRAIXEN'S HOUSE
async def reset_character_ai_BH():
  try:
    print("🔄️ - reset conversa")
    # AUTENTICANDO CLIENTECAI PARA ACESSAR AS COISAS NO CAI
    chat, greeting_message = await clientcai.chat.create_chat(char_id)
    item = {"cai-idchat": str(chat.chat_id)}
    BancoBot.update_one(item)
    text = greeting_message.get_primary_candidate().text
    return f"{text}"
  except Exception as e:
    return f"{Res.trad(str='message_cai_erro')}"












# ======================================================================

class caracterai(commands.Cog):
  def __init__(self, client: commands.Bot):
    self.client = client
    
    






# ======================================================================

  @commands.Cog.listener()
  async def on_ready(self):
    print("🤖  -  Modúlo Characterai carregado.")
    # Autentica só uma vez
    await asyncio.sleep(10)
    await clientcai.authenticate(char_token)
    self.client.loop.create_task(worker_brix(self))

    
  






# ======================================================================

  @commands.Cog.listener()
  async def on_message(self,message):
    





    
    # RETORNO DO CAI NO CANAL BRIX AI NA BH 
    if message.channel.id == id_chatBH and message.author != self.client.user and not message.author.bot and message.content != "-resetchatbrix":
      async with message.channel.typing():
        # AUTENTICANDO CLIENTECAI PARA ACESSAR AS COISAS NO CAI
        #await clientcai.authenticate(char_token)
        tentativas = 10
        for tentativa in range(tentativas):
          try:
            texto = message.content
            texto = texto.replace(f"<@{self.client.user.id}>", "").replace("@everyone", "todo mundo").replace("@here", "todo mundo online")
            mensagem = f"author: {message.author}\n{texto}"
            #client = await PyCharacterAI.get_client(char_token)
            dado = BancoBot.insert_document()
            # Validação de historico de usuario
            if 'cai-idchat' in dado:
              data = await clientcai.chat.send_message(char_id, str(dado['cai-idchat']), mensagem) 
            else:
              await reset_character_ai_BH()
              await asyncio.sleep(0.2)
              dado = BancoBot.insert_document()
              data = await clientcai.chat.send_message(char_id, str(dado['cai-idchat']), mensagem) 
            # Retorno da variavel
            return await message.reply(data.get_primary_candidate().text, allowed_mentions=discord.AllowedMentions(everyone=False))
          except Exception as e:
            if tentativa == tentativas - 1:
                # última tentativa, manda msg de erro
              try:
                return await message.channel.send(Res.trad(user=message.author, str="message_cai_erro"))
              except:return
            else:
              await asyncio.sleep(0.2)  # espera antes de tentar de novo
              



    # RETORNO DO BRIX AI CAI EM QUALQUER MENSAGEM QUE ELE SEJA MENCIONADO
    elif message.guild and message.author != self.client.user and not message.author.bot and message.content.startswith(f"<@{self.client.user.id}> "):
      await fila_global_brix.put(message)
      







    # RETORNO DO BRIX CASO ALGUEM MENCIONE ELE SEM MAIS NENHUMA PALAVRA ADICIONAL
    elif f"<@{self.client.user.id}>" in message.content and not message.author.bot and message.author != self.client.user:
      try:
        resposta = discord.Embed( 
          colour=discord.Color.yellow(),
            description= Res.trad(user=message.author,str="onwer_botinfo_description").format(len(self.client.guilds),len(self.client.users))
          )
        
        resposta.set_author(name= Res.trad(user=message.author,str="onwer_botinfo_author").format(self.client.user.name) ,icon_url=self.client.user.avatar.url)
        resposta.set_thumbnail(url=self.client.user.avatar.url)
        resposta.set_footer(text=Res.trad(user=message.author,str="onwer_botinfo_footer"),icon_url="https://cdn.discordapp.com/emojis/976096456513552406.png")
        view = discord.ui.View()
        button = discord.ui.Button(style=discord.ButtonStyle.blurple,label=Res.trad(user=message.author,str="botão_abrir_site_brix"),url="https://brixbot.xyz/")
        view.add_item(item=button)
        try:
          msgenviada = await message.reply(embed=resposta, view=view)
        except discord.errors.Forbidden:
          msgenviada = await message.channel.send(embed=resposta, view=view)

        await asyncio.sleep(30)
        try:
          await msgenviada.delete()
        except discord.errors.Forbidden:
          pass  # Não tem permissão pra deletar, ignora
      except Exception as e:
        print(e)
        return


    













# ======================================================================
  #COMANDO PARA DAR RESET NA CONVERSA DO BRIX NA BRAIXEN'S HOUSE
  @commands.command(name="resetchatbrix", description='reseta a conversa do brix na BH...')
  async def resetchatbrixbh(self,ctx):
    if ctx.author.id == donoid:
      await ctx.message.delete()
      brix = await reset_character_ai_BH()
      await ctx.send(brix)
    else:
      await ctx.send(Res.trad(guild=ctx.guild.id,str="message_erro_onlyowner"))
      return

















# ======================================================================
#GRUPO DE COMANDOS DE IMAGENS BOT 
  cai=app_commands.Group(name="cai",description="Comandos de character.ai integrados no Brix.",allowed_installs=app_commands.AppInstallationType(guild=True,user=True),allowed_contexts=app_commands.AppCommandContext(guild=True, dm_channel=True, private_channel=True))












# ======================================================================
#COMANDO CHARACTER AI RESET
  @cai.command(name="resetar",description='🤖⠂Resete sua conversa com Brix.')
  async def resetcharacter(self,interaction: discord.Interaction):
    if await Res.print_brix(comando="resetcharacter",interaction=interaction):
      return
    if interaction.guild is None:
      await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyservers"),delete_after=20,ephemeral=True)
      return
    await interaction.response.defer(ephemeral=True)
    Check = await userpremiumcheck(interaction)
    if Check == False:
      await interaction.followup.send(Res.trad(interaction=interaction,str="message_cai_only_premium"))
      return
    brix = await reset_character_ai(interaction.user)
    await interaction.followup.send(Res.trad(interaction=interaction,str="message_cai_reset_conversa"))
    await interaction.followup.send(f"{brix}")















# ======================================================================
#COMANDO CHARACTER AI AJUDA
  @cai.command(name="ajuda",description='🤖⠂Receba ajuda sobre CharacterAi.')
  async def helpcharacter(self,interaction: discord.Interaction):
    if await Res.print_brix(comando="helpcharacter",interaction=interaction):
      return
    resposta = discord.Embed(
      colour=discord.Color.yellow(),
      title="🦊┃ Brix AI",
      description="Eai, bem-vindo(a) a parte de ajuda sobre o **Character.ai**, eu faço uso da **api deles** para tentar ficar um **pouquinho mais inteligente** e **você pode conversar comigo agora mesmo**, basta me **marcar nas mensagem direcionadas** a mim ou usar o comando **/cai conversar** e eu tentarei te responder kyuuu\n\n**Obs:** Caso queira há qualquer momento pode resetar minha conversa com **/cai resetar** e eu volto ao padrão pré definido. kyuuu"
    )
    resposta.set_thumbnail(url="https://play-lh.googleusercontent.com/fTNuw4Wv-JbIvq3yONyqU2aGQ0eB6vTgHYrjmq6MlMtngeR75Qp_at5kiYUs7P6LnqU")
    resposta.set_footer(text=Res.trad(interaction=interaction,str="message_cai_footer_api"))
    await interaction.response.send_message(embed=resposta)


  @cai.command(name="conversar",description='🤖⠂Converse com Brix usando CharacterAi.')
  @app_commands.describe(mensagem ="Escreva uma mensagem para enviar ao Brix")
  async def conversarcharacter(self,interaction: discord.Interaction,mensagem:str):
    if await Res.print_brix(comando="conversacharacter",interaction=interaction):
      return
    if interaction.guild is None:
      await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyservers"),delete_after=20,ephemeral=True)
      return
    await interaction.response.defer()
    Check = await userpremiumcheck(interaction)
    if Check == False:
      await interaction.followup.send(Res.trad(interaction=interaction,str="message_cai_only_premium"))
      return
    
    response = await enviar_mensagem_para_character_ai(self,interaction.user,mensagem)
    print(f"🦊 - brix respondeu para {interaction.user.name} : {response}")
    await interaction.followup.send(response)
    

























# ======================================================================

async def setup(client:commands.Bot) -> None:
  await client.add_cog(caracterai(client))