import discord,os,asyncio,random,uuid
from discord.ext import commands
from discord import app_commands
from modulos.connection.database import BancoUsuarios,BancoBot
from modulos.essential.respostas import Res
from characterai import PyAsyncCAI
from dotenv import load_dotenv



load_dotenv(os.path.join(os.path.dirname(__file__), '.env')) #load .env da raiz
donoid = int(os.getenv("DONO_ID")) #acessa e define o id do dono
char_id = os.getenv('char_id')
char_token = os.getenv('char_token')
id_chatBH =  int(os.getenv('id_chatBH'))



chats = []







#COMANDO PARA CONECTAR O BOT AO CHARACTER.AI
async def enviar_mensagem_para_character_ai(self,membro,mensagem):
  try:
    message = mensagem.replace(f"<@{self.client.user.id}>", "").replace("@everyone", "todo mundo").replace("@here", "todo mundo online")
    mensagem = f"author: {membro}\n{message}"
    client = PyAsyncCAI(char_token)
    async with client.connect() as chat2:
  
      chat = await client.chat2.get_chat(char_id)
      author = {'author_id':chat['chats'][0]['creator_id'], 'is_human': True, 'name': membro.name}
      dado = BancoUsuarios.insert_document(membro)
      #Validação de historico de usuario
      if 'cai-idchat' in dado:
          data = await chat2.send_message(char_id,str(dado['cai-idchat']),mensagem, author) 
          #break
      else:
        await reset_character_ai(membro)
        await asyncio.sleep(1)
        dado = BancoUsuarios.insert_document(membro)
        data = await chat2.send_message(char_id,str(dado['cai-idchat']),mensagem, author) 

      #Retorno da variavel
      text = data['turn']['candidates'][0]['raw_content']
      return text
    
  except Exception as e:
    return f"{Res.trad(user=membro,str='message_cai_erro').format(e)}"
  



#FUNÇAO PARA CRIAR UMA NOVA CONVERSA INDIVIDUAL
async def reset_character_ai(membro):
  try:
    client = PyAsyncCAI(char_token)
    idchat = uuid.uuid4()

    print("🔄️ - reset conversa")
    item = {"cai-idchat": str(idchat)}
    BancoUsuarios.update_document(membro,item)
    chat = await client.chat2.get_chat(char_id)
    async with client.connect() as chat2:
      data = await chat2.new_chat(char_id,str(idchat),chat['chats'][0]['creator_id'])
    text = data[1]['turn']['candidates'][0]['raw_content']

    return f"{text}"
  except Exception as e:
    return f"{Res.trad(user=membro,str='message_cai_erro').format(e)}"
  






#FUNÇAO PARA CRIAR UMA NOVA CONVERSA INDIVIDUAL NA BRAIXEN'S HOUSE
async def reset_character_ai_BH():
  try:
    client = PyAsyncCAI(char_token)
    idchat = uuid.uuid4()

    print("🔄️ - reset conversa")
    item = {"cai-idchat": str(idchat)}
    BancoBot.update_one(item)
    chat = await client.chat2.get_chat(char_id)
    async with client.connect() as chat2:
      data = await chat2.new_chat(char_id,str(idchat),chat['chats'][0]['creator_id'])
    text = data[1]['turn']['candidates'][0]['raw_content']

    return f"{text}"
  except Exception as e:
    return f"{Res.trad(str='message_cai_erro').format(e)}"








class caracterai(commands.Cog):
  def __init__(self, client: commands.Bot):
    self.client = client
    
    




  @commands.Cog.listener()
  async def on_ready(self):
    print("🤖  -  Modúlo Characterai carregado.")
  





  @commands.Cog.listener()
  async def on_message(self,message):

    #  RETORNO DO CAI NO CANAL BRIX AI NA BH 
    if message.channel.id == id_chatBH and message.author != self.client.user and not message.author.bot and message.content != "-resetchatbrix":
      async with message.channel.typing():
        try:
          texto = message.content
          texto = texto.replace(f"<@{self.client.user.id}>", "").replace("@everyone", "todo mundo").replace("@here", "todo mundo online")
          mensagem = f"author: {message.author}\n{texto}"
          client = PyAsyncCAI(char_token)
          async with client.connect() as chat2:
            chat = await client.chat2.get_chat(char_id)
            author = {'author_id':chat['chats'][0]['creator_id'], 'is_human': True, 'name': message.author.name}
            dado = BancoBot.insert_document()
            #Validação de historico de usuario
            if 'cai-idchat' in dado:
              data = await chat2.send_message(char_id,str(dado['cai-idchat']),mensagem, author) 
              #break
            else:
              await reset_character_ai_BH()
              await asyncio.sleep(2)
              dado = BancoBot.insert_document()
              data = await chat2.send_message(char_id,str(dado['cai-idchat']),mensagem, author) 

          #Retorno da variavel
          await message.reply( data['turn']['candidates'][0]['raw_content'] ,allowed_mentions = discord.AllowedMentions(everyone=False))
        except Exception as e:
          await message.channel.send( Res.trad(user=message.author,str="message_cai_erro").format(e) )




    # RETORNO DO BRIX AI CAI EM QUALQUER MENSAGEM QUE ELE SEJA MENCIONADO
    elif f"<@{self.client.user.id}> " in message.content and message.author != self.client.user:
      async with message.channel.typing():
        if message.guild is None:
            await message.reply(Res.trad(user=message.author,str="message_erro_onlyservers"))
        else:
          try:
            dado = BancoUsuarios.insert_document(message.author)
            premiumativo = BancoBot.insert_document()
            if premiumativo['premiumsys'] is False:
              print("sistema premium desativado, comando liberado")
              premium = True
            else:
              try:
                premium = dado['premium']
              except:
                premium = False
              
            if premium != False:
              await message.add_reaction('<:BH_Badge_PequenoMago:1154180154076176466>')
              response = await enviar_mensagem_para_character_ai(self,message.author,message.content)
              print(f"brix respondeu para {message.author.name} : {response}")
              chance_de_aparecer = 20
              if random.randint(1, 100) <= chance_de_aparecer:
                  response += f"\n{Res.trad(user=message.author,str='message_cai_footer')}"
              await message.reply(response,allowed_mentions = discord.AllowedMentions(everyone=False))
            else:
              await message.reply(Res.trad(user=message.author,str="message_cai_only_premium"))
          except Exception as e:
            await message.channel.send( Res.trad(user=message.author,str="message_cai_erro").format(e) )




    # RETORNO DO BRIX CASO ALGUEM MENCIONE ELE SEM MAIS NENHUMA PALAVRA ADICIONAL
    elif f"<@{self.client.user.id}>" in message.content and message.author != self.client.user:
      resposta = discord.Embed( 
        colour=discord.Color.yellow(),
          description= Res.trad(user=message.author,str="onwer_botinfo_description").format(len(self.client.guilds),len(self.client.users))
        )
      
      resposta.set_author(name= Res.trad(user=message.author,str="onwer_botinfo_author").format(self.client.user.name) ,icon_url=self.client.user.avatar.url)
      resposta.set_thumbnail(url=self.client.user.avatar.url)
      resposta.set_footer(text=Res.trad(user=message.author,str="onwer_botinfo_footer"),icon_url="https://cdn.discordapp.com/emojis/976096456513552406.png")
      view = discord.ui.View()
      button = discord.ui.Button(style=discord.ButtonStyle.blurple,label=Res.trad(user=message.author,str="botão_abrir_site_brix"),url="https://brix.squareweb.app/")
      view.add_item(item=button)
      msgenviada = await message.reply(embed=resposta , view = view)
      await asyncio.sleep(30)
      await msgenviada.delete()









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

















#GRUPO DE COMANDOS DE IMAGENS BOT 
  cai=app_commands.Group(name="cai",description="Comandos de character.ai integrados no Brix.",allowed_installs=app_commands.AppInstallationType(guild=True,user=True),allowed_contexts=app_commands.AppCommandContext(guild=True, dm_channel=True, private_channel=True))

#COMANDO CHARACTER AI RESET
  @cai.command(name="resetar",description='🤖⠂Resete sua conversa com Brix.')
  async def resetcharacter(self,interaction: discord.Interaction):
    if await Res.print_brix(comando="resetcharacter",interaction=interaction):
      return
    if interaction.guild is None:
      await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyservers"),delete_after=20,ephemeral=True)
      return
    else:
      await interaction.response.defer(ephemeral=True)
      dado = BancoUsuarios.insert_document(interaction.user)
      premiumativo = BancoBot.insert_document()
      if premiumativo['premiumsys'] is False:
        print("sistema premium desativado, comando liberado")
        premium = True
      else:
        try:
          premium = dado['premium']
        except:
          premium = False   
      if premium != False:
        brix = await reset_character_ai(interaction.user)
        await interaction.followup.send(Res.trad(interaction=interaction,str="message_cai_reset_conversa"))
        await interaction.followup.send(f"{brix}")
      else:
        await interaction.followup.send(Res.trad(interaction=interaction,str="message_cai_only_premium"))

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
    else:
      await interaction.response.defer()
      dado = BancoUsuarios.insert_document(interaction.user)
    premiumativo = BancoBot.insert_document()
    if premiumativo['premiumsys'] is False:
        print("sistema premium desativado, comando liberado")
        premium = True
    else: 
      try:
        premium = dado['premium']
      except:
        premium = False
    if premium != False:
      response = await enviar_mensagem_para_character_ai(self,interaction.user,mensagem)
      print(f"brix respondeu para {interaction.user.name} : {response}")
      await interaction.followup.send(response)
    else:
      await interaction.followup.send(Res.trad(interaction=interaction,str="message_cai_only_premium"))














async def setup(client:commands.Bot) -> None:
  await client.add_cog(caracterai(client))