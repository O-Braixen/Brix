import discord,os,requests,json,random,datetime,pytz,asyncio
from discord.ext import commands , tasks
from discord import app_commands
from os import listdir
from typing import List
from modulos.connection.database import BancoUsuarios,BancoServidores,BancoBot,BancoLoja
from modulos.essential.respostas import Res
from modulos.essential.usuario import userpremiumcheck
from modulos.essential.host import informação,status,restart
from modulos.essential.gasmii import generate_response_with_text
from dotenv import load_dotenv



#CARREGA E LE O ARQUIVO .env na raiz
load_dotenv(os.path.join(os.path.dirname(__file__), '.env')) #load .env da raiz
donoid = int(os.getenv("DONO_ID")) #acessa e define o id do dono






#Função status
async def botstatus(self,interaction):
    if await Res.print_brix(comando="botstatus",interaction=interaction):
      return
    #bot_esta_na_guilda = interaction.guild and interaction.guild.id in [guild.id for guild in self.client.guilds]
    #if bot_esta_na_guilda:  # Bot está na guilda
    await interaction.response.defer()  # Defer normal
    #else:  # Bot não está na guilda
        # interaction.response.defer(ephemeral=True)  # Defer com ephemeral
    fuso = pytz.timezone('America/Sao_Paulo')
    now = datetime.datetime.now().astimezone(fuso)
    try:
      dadosbot = BancoBot.insert_document()
      if self.client.user.id == 983000989894336592:
        ambiente = "Produção"
      else:
        ambiente = "Beta Teste"
      try:
        res_information = await informação(self.client.user.name)
        res_status = await status(self.client.user.name)
        resposta = discord.Embed(
                colour=discord.Color.yellow(),
                title=f"🦊┃Informações do {res_information['response']['name']}",
                description=f"{res_information['response']['desc']}"
            )
        resposta.set_thumbnail(url=f"{self.client.user.avatar.url}")
        resposta.add_field(name="🖥️⠂squarecloud", value=f"```{res_information['response']['cluster']}```", inline=True)
        resposta.add_field(name="👨‍💻⠂Linguagem", value=f"```{res_information['response']['language']}```", inline=True)
        resposta.add_field(name="🦊⠂Dono", value=f"<@{donoid}>", inline=True)
        resposta.add_field(name="📊⠂Ram", value=f"```{(res_status['response']['ram'])} / {res_information['response']['ram']} MB```", inline=True)
        resposta.add_field(name="🌡⠂CPU", value=f"```{res_status['response']['cpu']}```", inline=True)
        resposta.add_field(name="🕐⠂Uptime", value=f"<t:{round(res_status['response']['uptime']/1000)}:R>", inline=True)
        resposta.add_field(name="🌐⠂Rede", value=f"```{res_status['response']['network']['total']}```", inline=True)
        resposta.add_field(name="🏓⠂Ping", value=f"```{round(self.client.latency * 1000)}ms```", inline=True)
        resposta.add_field(name="🔮⠂Menção", value=f"<@{self.client.user.id}>", inline=True)
        resposta.add_field(name="🕐⠂Hora Sistema", value=f"```{now.strftime('%d/%m/%y - %H:%M')}```", inline=True)
        resposta.add_field(name="🆔⠂Bot ID", value=f"```{self.client.user.id}```", inline=True)
        resposta.add_field(name="🍀⠂Ambiente", value=f"```{ambiente}```", inline=True)

        resposta.set_footer(text=f"Rodando versão: {dadosbot['version']} - Mais detalhes use /brix version",icon_url="https://cdn.discordapp.com/emojis/976096456513552406.png")

        await interaction.followup.send(embed=resposta)
      except Exception as e:
        resposta = discord.Embed(
                colour=discord.Color.yellow(),
                title=f"🦊┃Informações do {self.client.user.name}",
                description=f"O melhor Braixen Bot, sem dados de hospedagem."
            )
        resposta.set_thumbnail(url=f"{self.client.user.avatar.url}")
        resposta.add_field(name="🍀⠂Ambiente", value=f"```{ambiente}```", inline=True)
        resposta.set_footer(text=f"Rodando versão: {dadosbot['version']} - Mais detalhes use /brix version",icon_url="https://cdn.discordapp.com/emojis/976096456513552406.png")

        await interaction.followup.send(embed=resposta)
    except Exception as e:
      await Res.erro_brix_embed(interaction,str="message_erro_getsquare",e=e,comando="botstatus")









#Função Bot Version
async def botversion(self,interaction):
    if await Res.print_brix(comando="botversion",interaction=interaction):
      return
    await interaction.response.defer()  # Defer normal
    try:
      dadosbot = BancoBot.insert_document()
      if self.client.user.id == 983000989894336592:
        ambiente = "Produção"
      else:
        ambiente = "Beta Teste"
      resposta = discord.Embed(
                colour=discord.Color.yellow(),
                title=f"Versão Atual de {self.client.user.name}",
                description=f"Versão do codigo: **{dadosbot['version']}**\nRotação da Loja Ativo?: **{dadosbot['rotacaoloja']}**\nSistema Premium Ativo?: **{dadosbot['premiumsys']}**\nAmbiente: **{ambiente}**\n\nNotas de atualização: **{dadosbot['notasupdate']}**"
            )
      resposta.set_thumbnail(url=f"{self.client.user.avatar.url}")
      
      await interaction.followup.send(embed=resposta)
    except Exception as e:
      await Res.erro_brix_embed(interaction,str="message_erro_brixsystem",e=e,comando="botversion")












#------------------------------------------------MODAIS--------------------------------------------

#Classe do MODAL SAIR SERVIDOR
class ModalSairServidor(discord.ui.Modal,title = "Saindo de um Servidor!"):
    serverid = discord.ui.TextInput(label="ID do servidor",style=discord.TextStyle.short,min_length=1,placeholder="0123456789")

    def __init__(self, client):
        super().__init__()
        self.client = client

    async def on_submit(self, interaction: discord.Interaction):
      guild = self.client.get_guild (int (self.serverid.value)) # Obtém o objeto guilda pelo ID
      await guild.leave () # Faz o bot sair da guilda
      await interaction.response.send_message(Res.trad(interaction=interaction,str="message_servidor_sair").format(guild.name),delete_after=10)






#Classe do MODAL ALTERAR NOME DO BOT
class ModalNomeBot(discord.ui.Modal,title = "Renomeando o bot!"):
    newname = discord.ui.TextInput(label="Qual o novo Nome?",style=discord.TextStyle.short,min_length=1,placeholder="brix")

    def __init__(self, client):
        super().__init__()
        self.client = client

    async def on_submit(self, interaction: discord.Interaction):
      await self.client.user.edit(username=self.newname.value)
      await interaction.response.send_message(Res.trad(interaction=interaction,str="message_botname").format(self.newname.value),delete_after=10, ephemeral=True)






#Classe do MODAL ALTERAR AVATAR DO BOT
class ModalavatarBot(discord.ui.Modal,title = "Alterar Avatar do Bot!"):
    newavatar = discord.ui.TextInput(label="Indique o Link da imagem?",style=discord.TextStyle.long,min_length=1,placeholder="http:algumacoisalinkdireto")

    def __init__(self, client):
        super().__init__()
        self.client = client

    async def on_submit(self, interaction: discord.Interaction):
      avatar = requests.get(self.newavatar.value).content
      await self.client.user.edit(avatar=avatar)
      await interaction.response.send_message(Res.trad(interaction=interaction,str="message_botavatar"),delete_after=10, ephemeral=True)








#Classe do MODAL USER AWARD
class ModalUserAward(discord.ui.Modal,title = "Premie um Membro!"):
    userid = discord.ui.TextInput(label="ID do Usuario",style=discord.TextStyle.short,min_length=1,placeholder="0123456789")
    valordado = discord.ui.TextInput(label="Valor a Entregar",style=discord.TextStyle.short,min_length=1,placeholder="1000")

    def __init__(self, client,moeda,emoji):
        super().__init__()
        self.client = client
        self.moeda = moeda
        self.emoji = emoji


    async def on_submit(self, interaction: discord.Interaction):
      membro = await self.client.fetch_user(self.userid.value)
      quantidade = self.valordado.value
      await interaction.response.defer()
      print(f"Comando award - User: {interaction.user.name}")
      datahoje = datetime.datetime.now().astimezone(pytz.timezone('America/Sao_Paulo')) - datetime.timedelta(days=1)
      if quantidade.endswith('k'): # verifica se passaram K na variavel
          if ',' in quantidade  or '.' in quantidade: # verifica pontuação
            quantidade = quantidade.replace(',','').replace('.','')
            quantidade = int(quantidade[:-1]) * 100
          else:
            quantidade = int(quantidade[:-1]) * 1000
      else: quantidade = int(quantidade)
      try:
          usuario = BancoUsuarios.insert_document(membro)
          saldo = usuario[self.moeda]
          saldo = saldo + quantidade
          BancoUsuarios.update_document(membro,{self.moeda: saldo,"date-daily": datahoje.strftime("%d/%m/%Y")})
      except:await interaction.followup.send(Res.trad(interaction=interaction,str='message_erro_mongodb').format(interaction.user.id),ephemeral=True)
      await interaction.followup.send(Res.trad(interaction=interaction,str="message_financeiro_pagamento_owner").format(membro.mention,quantidade,self.emoji))
      try:
          dm_notification = usuario['dm-notification']
      except:
          dm_notification = True
          item = {"dm-notification": dm_notification}
          BancoUsuarios.update_document(membro,item)
      if dm_notification is True:
          try:
            await membro.send(Res.trad(interaction=interaction,str="message_financeiro_pagamento_owner_dm").format(quantidade,self.emoji))
          except:
            print("erro no envio de dm para informar pagamento")
            return
      else:
          print("membro não recebe notificações via DM")
          return







#Classe do MODAL USER TAKE
class ModalUserTake(discord.ui.Modal,title = "Tirar Moeda de Membro!"):
    userid = discord.ui.TextInput(label="ID do Usuario",style=discord.TextStyle.short,min_length=1,placeholder="0123456789")
    valordado = discord.ui.TextInput(label="Valor a ser Removido",style=discord.TextStyle.short,placeholder="1000")

    def __init__(self, client,moeda,emoji):
        super().__init__()
        self.client = client
        self.moeda = moeda
        self.emoji = emoji

    async def on_submit(self, interaction: discord.Interaction):
      membro = await self.client.fetch_user(self.userid.value)
      quantidade = int(self.valordado.value)
      print(f"Comando take - User: {interaction.user.name}")
      await interaction.response.defer(ephemeral=True)
      try:
        usuario = BancoUsuarios.insert_document(membro)
        saldo = usuario[self.moeda]
        if quantidade == 0:
              saldo = 0
        else:
              saldo = saldo - int(quantidade)
        BancoUsuarios.update_document(membro,{self.moeda: saldo})
        await interaction.followup.send(Res.trad(interaction=interaction,str="message_financeiro_pagamento_take").format(membro.mention,saldo,self.emoji)) 
      except: await interaction.followup.send(Res.trad(interaction=interaction,str='message_erro_mongodb').format(interaction.user.id),ephemeral=True)  







#Classe do MODAL USER DESCRICAO
class ModalUserdescricao(discord.ui.Modal,title = "Mude a descrição de alguém!"):
    userid = discord.ui.TextInput(label="ID do Usuario",style=discord.TextStyle.short,min_length=1,placeholder="0123456789")
    descricao = discord.ui.TextInput(label="Nova descrição",style=discord.TextStyle.long,max_length=150,placeholder="texto legal aqui")

    def __init__(self, client):
        super().__init__()
        self.client = client

    async def on_submit(self, interaction: discord.Interaction):
      membro = await self.client.fetch_user(self.userid.value)
      await interaction.response.defer(ephemeral=True)
      try:
        BancoUsuarios.update_document(membro,{'descricao': self.descricao.value})
        await interaction.followup.send(Res.trad(interaction=interaction,str="message_sobremim").format(self.descricao.value)) 
      except: await interaction.followup.send(Res.trad(interaction=interaction,str='message_erro_mongodb').format(interaction.user.id),ephemeral=True)  








#Classe do MODAL BAN USER
class ModalBanUSER(discord.ui.Modal,title = "Banir um Usuario no meu sistema Brix!"):
    userid = discord.ui.TextInput(label="ID do Usuario",style=discord.TextStyle.short,min_length=1,placeholder="0123456789")
    motivo = discord.ui.TextInput(label="Motivo do Banimento",style=discord.TextStyle.long,placeholder="Informe aqui o motivo pelo qual esse usuario ta sendo banido.")

    def __init__(self, client):
        super().__init__()
        self.client = client

    async def on_submit(self, interaction: discord.Interaction):
      membro = await self.client.fetch_user(self.userid.value)
      await interaction.response.defer(ephemeral=True)
      try:
        item = {"ban.data": datetime.datetime.now(),"ban.motivo": self.motivo.value , "ban.autor" : interaction.user.name}
        BancoUsuarios.update_document(membro,item)
        resposta = discord.Embed(color=discord.Color.yellow(),description=f"## 🦊 - Usuario Banido do sistema brix\n**Usuario:** {membro.mention}\n**Motivo:** {self.motivo.value}")
        await interaction.followup.send(embed=resposta) 
      except: await interaction.followup.send(Res.trad(interaction=interaction,str='message_erro_mongodb').format(interaction.user.id),ephemeral=True)  







#Classe do MODAL UNBAN USER
class ModalUnBanUSER(discord.ui.Modal,title = "Desbanir um Usuario no meu sistema Brix!"):
    userid = discord.ui.TextInput(label="ID do Usuario",style=discord.TextStyle.short,min_length=1,placeholder="0123456789")

    def __init__(self, client):
        super().__init__()
        self.client = client

    async def on_submit(self, interaction: discord.Interaction):
      membro = await self.client.fetch_user(self.userid.value)
      await interaction.response.defer(ephemeral=True)
      try:
        item = {"ban": 0}
        BancoUsuarios.delete_field(membro,item)
        resposta = discord.Embed(color=discord.Color.yellow(),description=f"## 🦊 - Usuario Desbanido do sistema brix\n**Usuario:** {membro.mention}")
        await interaction.followup.send(embed=resposta) 
      except: await interaction.followup.send(Res.trad(interaction=interaction,str='message_erro_mongodb').format(interaction.user.id),ephemeral=True)  






#Botões dashboard
class Botoesdash(discord.ui.View):
    def __init__(self,client):
        super().__init__(timeout=300)
        self.client = client
        self.value=None

    @discord.ui.button(label="Listar Server",style=discord.ButtonStyle.red,emoji="📄",row=0)
    async def listservers (self,interaction: discord.Interaction, button: discord.ui.Button):
      if await Res.print_brix(comando="listservers",interaction=interaction):
        return
      if interaction.user.id == donoid: # Verifica se o usuário é o dono do bot
        await interaction.response.defer(ephemeral=True) # Envia uma resposta de interação para indicar que o comando está sendo processado
        servers = self.client.guilds
        lista = "## 🦊┃ Lista de Servidores\n"  # Cria uma variável para armazenar a lista de servidores
        
        partes = []
        parte_atual = lista
        
        for server in servers:
            entrada = f"**Nome:** `{server.name}` - **id:** `{server.id}`\n"
            if len(parte_atual) + len(entrada) > 2000:
                partes.append(parte_atual)
                parte_atual = ""
            parte_atual += entrada
        
        partes.append(parte_atual)  # Adiciona a última parte
        for parte in partes:
            await interaction.followup.send(content=parte, ephemeral=True)
      else:
        await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyowner"),delete_after=10, ephemeral=True) # Envia uma resposta de interação que só é visível para o usuário

    @discord.ui.button(label="Sair Server",style=discord.ButtonStyle.red,emoji="🔚",row=0)
    async def leave (self,interaction: discord.Interaction, button: discord.ui.Button):
      if await Res.print_brix(comando="leave",interaction=interaction):
        return
      if interaction.user.id == donoid:
          await interaction.response.send_modal(ModalSairServidor(self.client))
      else:
          await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyowner"),delete_after=10)
    
    @discord.ui.button(label="Nome Bot",style=discord.ButtonStyle.green,emoji="🤖",row=1)
    async def botname (self,interaction: discord.Interaction, button: discord.ui.Button):
      if interaction.user.id == donoid:
          await interaction.response.send_modal(ModalNomeBot(self.client))
      else:
          await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyowner"),delete_after=10)
    
    @discord.ui.button(label="Avatar Bot",style=discord.ButtonStyle.green,emoji="🖼️",row=1)
    async def botavatar (self,interaction: discord.Interaction, button: discord.ui.Button):
      if interaction.user.id == donoid:
          await interaction.response.send_modal(ModalavatarBot(self.client))
      else:
          await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyowner"),delete_after=10)
    
    @discord.ui.button(label="+",style=discord.ButtonStyle.green,emoji="<:BraixenCoin:1272655353108103220>",row=2)
    async def awardcoin (self,interaction: discord.Interaction, button: discord.ui.Button):
      if interaction.user.id == donoid:
          await interaction.response.send_modal(ModalUserAward(self.client,moeda='braixencoin',emoji="<:BraixenCoin:1272655353108103220>"))
      else:
          await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyowner"),delete_after=10,ephemeral=True)
    
    @discord.ui.button(label="-",style=discord.ButtonStyle.green,emoji="<:BraixenCoin:1272655353108103220>",row=2) #row=0
    async def takecoin (self,interaction: discord.Interaction, button: discord.ui.Button):
      if interaction.user.id == donoid:
          await interaction.response.send_modal(ModalUserTake(self.client,moeda='braixencoin',emoji='<:BH_BraixenCoin:1182695452731265126>'))
      else:
          await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyowner"),delete_after=10,ephemeral=True)
    
    @discord.ui.button(label="+",style=discord.ButtonStyle.green,emoji="<:Graveto:1318962131567378432>",row=2)
    async def awardstick (self,interaction: discord.Interaction, button: discord.ui.Button):
      if interaction.user.id == donoid:
          await interaction.response.send_modal(ModalUserAward(self.client,moeda='graveto',emoji='<:Graveto:1318962131567378432>'))
      else:
          await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyowner"),delete_after=10,ephemeral=True)
    
    @discord.ui.button(label="-",style=discord.ButtonStyle.green,emoji="<:Graveto:1318962131567378432>",row=2) #row=0
    async def takestick (self,interaction: discord.Interaction, button: discord.ui.Button):
      if interaction.user.id == donoid:
          await interaction.response.send_modal(ModalUserTake(self.client,moeda='graveto',emoji='<:Graveto:1318962131567378432>'))
      else:
          await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyowner"),delete_after=10,ephemeral=True)
    
    @discord.ui.button(label="bio user",style=discord.ButtonStyle.green,emoji="🙍",row=2) #row=0
    async def chargedescricao (self,interaction: discord.Interaction, button: discord.ui.Button):
      if interaction.user.id == donoid:
          await interaction.response.send_modal(ModalUserdescricao(self.client))
      else:
          await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyowner"),delete_after=10,ephemeral=True)
    
    @discord.ui.button(label="Loja Download Local",style=discord.ButtonStyle.grey,emoji="⬇️",row=3) #row=0
    async def lojadonwload (self,interaction: discord.Interaction, button: discord.ui.Button):
      if interaction.user.id == donoid:
          await interaction.response.send_message("<:Braix_Hmph:1272666561244561429>┃ Okay Kyuu, vou atualizar os arquivos locais")
          await baixaritensloja()
      else:
          await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyowner",),delete_after=10,ephemeral=True)

    @discord.ui.button(label="Loja rotação",style=discord.ButtonStyle.grey,emoji="🔀",row=3) #row=0
    async def lojarotação (self,interaction: discord.Interaction, button: discord.ui.Button):
      dadosbot = BancoBot.insert_document()
      if dadosbot['rotacaoloja']:
        item = {"rotacaoloja": False}
      else:
        item = {"rotacaoloja": True}
      update = BancoBot.update_one(item)
      await interaction.response.send_message(f"<:Braix_Hmph:1272666561244561429>┃ Rotação da loja: {item['rotacaoloja']}")

    @discord.ui.button(label="Reiniciar Bot",style=discord.ButtonStyle.red,emoji="⚡",row=4) #row=0
    async def buttonshutdown (self,interaction: discord.Interaction, button: discord.ui.Button):
      if interaction.user.id == donoid:
          await interaction.response.send_message(f"<:Braix_Shocked:1272663500115935264>┃ Enviando solicitação a Squarecloud...",delete_after=10)
          await restart(self.client.user.name)
      else:
          await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyowner"),delete_after=10,ephemeral=True)

    @discord.ui.button(label="Reload cogs",style=discord.ButtonStyle.red,emoji="🦊",row=4) #row=0
    async def buttonreload(self,interaction: discord.Interaction, button: discord.ui.Button):
      if interaction.user.id == donoid:
        await interaction.response.defer(ephemeral=True)
        resposta = discord.Embed( 
                colour=discord.Color.yellow(),
                description="Sistema Brix recarregou as seguintes cogs"
        )
        resposta.set_thumbnail(url=f"{self.client.user.avatar.url}")
        for cog in listdir("modulos"):
          if cog.endswith(".py"):
            try:
              cog = os.path.splitext(cog)[0]
              await self.client.unload_extension('modulos.' + cog)
              await self.client.load_extension('modulos.' + cog)
              resposta.add_field(name=f"Carregado: {cog}",value='\uFEFF',inline=True)
            except Exception as e:
              resposta.add_field(name=f"Falha ao carregar: {cog}",value=e,inline=True)
        await interaction.followup.send(embed=resposta)
      else:
          await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyowner"),delete_after=10,ephemeral=True)
    
    @discord.ui.button(label="Banir",style=discord.ButtonStyle.red,emoji="🔨",row=4) #row=0
    async def buttonbanuser(self,interaction: discord.Interaction, button: discord.ui.Button):
      if interaction.user.id == donoid:
        await interaction.response.send_modal(ModalBanUSER(self.client))
      else:
          await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyowner"),delete_after=10,ephemeral=True)
    
    @discord.ui.button(label="Desbanir",style=discord.ButtonStyle.red,emoji="🔨",row=4) #row=0
    async def buttonUnbanuser(self,interaction: discord.Interaction, button: discord.ui.Button):
      if interaction.user.id == donoid:
        await interaction.response.send_modal(ModalUnBanUSER(self.client))
      else:
          await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyowner"),delete_after=10,ephemeral=True)
    
    @discord.ui.button(label="listar Banidos",style=discord.ButtonStyle.red,emoji="📃",row=4) #row=0
    async def buttonlistbanuser(self,interaction: discord.Interaction, button: discord.ui.Button):
      if interaction.user.id == donoid:
        await interaction.response.defer(ephemeral=True)
        # Busque aniversariantes e servidores uma vez
        filtro_banidos = {"ban": {"$exists": True} }
        banidos = BancoUsuarios.select_many_document(filtro_banidos)
        # Criar as mensagens formatadas
        partes = []
        parte_atual = "## <:BH_Braix_FuckUp:1321297765627859075>┃ Lista de banidos Brix System\n"
        for doc in banidos:
            entrada = f"**ID:** `{doc['_id']}` - <@{doc['_id']}> - <t:{int(doc['ban']['data'].timestamp())}:f>\n"
            if len(parte_atual) + len(entrada) > 2000:
                partes.append(parte_atual)
                parte_atual = ""
            parte_atual += entrada
        
        # Adicionar a última parte
        if parte_atual:
            partes.append(parte_atual)
        
        # Enviar cada parte como uma mensagem separada
        for parte in partes:
            await interaction.followup.send(content=parte, ephemeral=True)
        
      else:
          await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyowner"),delete_after=10,ephemeral=True)














#--------------- COMANDO PARA BAIXAR ITENS DA LOJA PARA OS ARQUIVOS LOCAIS -----------
async def baixaritensloja(): 
  filtro = {"_id": {"$ne": "diaria"}}
  itens = BancoLoja.select_many_document(filtro)
  IMAGE_SAVE_PATH = r"imagens/backgroud/all-itens"

  if not os.path.exists(IMAGE_SAVE_PATH):
        os.makedirs(IMAGE_SAVE_PATH)
  print('🦊 - Iniciando Donwload dos itens da loja...')
  for item in itens:
        file_name = f"{item['_id']}.png"
        file_path = os.path.join(IMAGE_SAVE_PATH, file_name)
        await asyncio.sleep(0,5)
        response = requests.get(item['url'])
        if response.status_code == 200:
          with open(file_path, 'wb') as f:
            f.write(response.content)
          print(f'Imagem salva: {file_path}')
        else:
          print(f'Falha ao baixar a imagem: {item["url"]}')
  print('Todos os itens foram baixados...')









class owner(commands.Cog):
  def __init__(self, client: commands.Bot):
    self.client = client






  @commands.Cog.listener()
  async def on_ready(self):
    print("🦊  -  Modúlo Owner carregado.")
    if not self.verificar_guilds.is_running():
      self.verificar_guilds.start()
      await asyncio.sleep(900)
      await baixaritensloja()








  #PAINEL DASHBOARD OWNER
  @commands.command(name="dashboard", description='Dashboard de operação administrativa.')
  async def dashboard(self,ctx):
    await ctx.message.delete()
    if ctx.author.id == donoid:
      async with ctx.typing():
        msg = await ctx.send(file = discord.File("imagens/Brixdashboardbanner.png"), view = Botoesdash(self.client))
      await asyncio.sleep(60)
      await msg.delete()

    else:
      msg = await ctx.send(Res.trad(user=ctx.author,str="message_erro_onlyowner"))
      await asyncio.sleep(20)
      await msg.delete()
      return







  #DBGUILD COMANDO DEBUG
  @commands.command(name="debugguild", description='Exibe todos os dados da comunidade presente no banco de dados.')
  async def debugguild(self,ctx , guild:int = None):
    await ctx.message.delete()
    if ctx.author.id == donoid:
      async with ctx.typing():
        if guild is not None:
           consulta = BancoServidores.insert_document(guild)
        else:
          consulta = BancoServidores.insert_document(ctx.message.guild.id)
        embeds = []
        embed = discord.Embed( title="<:Braix_Tongue:1272662386590879795>┃ Brix Debug",  description="Segue tudo que encontrei no banco de dados desta comunidade.",  color=discord.Color.yellow()   )
        embed.set_thumbnail(url=f"{self.client.user.avatar.url}")
        
        total_chars = 0
        for chave, valor in consulta.items():
            campo = f"**{chave}:** {valor}"
            if total_chars + len(campo) > 5500:  # Aproximação para não ultrapassar 6000
                embeds.append(embed)
                embed = discord.Embed(
                    title="<:Braix_Tongue:1272662386590879795>┃ Brix Debug (cont.)",
                    color=discord.Color.yellow()
                )
                total_chars = 0  # Reinicia contagem
            
            valor_str = str(valor)  # Converte para string
            if len(valor_str) > 1000:
                valor_str = valor_str[:1000] + "..."  # Corta para 1021 caracteres e adiciona "..."

            embed.add_field(name=str(chave), value=f"```{valor_str}```", inline=False)
            total_chars += len(campo)

      embeds.append(embed)  # Adiciona o último embed
      mensagens = []  # Lista para armazenar as mensagens enviadas
      for emb in embeds:
        msg = await ctx.send(embed=emb)
        mensagens.append(msg)  # Adiciona a mensagem à lista
      await asyncio.sleep(60)  # Espera 60 segundos
      for msg in mensagens:
          await msg.delete()  # Deleta cada mensagem enviada

    else:
      msg = await ctx.send(Res.trad(user=ctx.author,str="message_erro_onlyowner"))
      await asyncio.sleep(20)
      await msg.delete()
      return







  #DBGUILD COMANDO DEBUG
  @commands.command(name="debuguser", description='Exibe todos os dados de um usuário presente no banco de dados.')
  async def debuguser(self,ctx,user:discord.User = None):
    await ctx.message.delete()
    if ctx.author.id == donoid:
      if user is None:
        msg = await ctx.send("Passe um usuário para que eu possa procurar ~kyuu")
      else:
        async with ctx.typing():
          consulta = BancoUsuarios.insert_document(user)
          embeds = []
          embed = discord.Embed( title="<:Braix_Tongue:1272662386590879795>┃ Brix Debug",  description="Segue tudo que encontrei no banco desse usuário.",  color=discord.Color.yellow()   )
          embed.set_thumbnail(url=f"{user.avatar.url}")
          total_chars = 0
          for chave, valor in consulta.items():
              campo = f"**{chave}:** {valor}"
              if total_chars + len(campo) > 5500:  # Aproximação para não ultrapassar 6000
                  embeds.append(embed)
                  embed = discord.Embed(
                      title="<:Braix_Tongue:1272662386590879795>┃ Brix Debug (cont.)",
                      color=discord.Color.yellow()
                  )
                  total_chars = 0  # Reinicia contagem
              
              valor_str = str(valor)  # Converte para string
              if len(valor_str) > 1000:
                  valor_str = valor_str[:1000] + "..."  # Corta para 1021 caracteres e adiciona "..."

              embed.add_field(name=str(chave), value=f"```{valor_str}```", inline=False)
              total_chars += len(campo)

        embeds.append(embed)  # Adiciona o último embed
        mensagens = []  # Lista para armazenar as mensagens enviadas
        for emb in embeds:
          msg = await ctx.send(embed=emb)
          mensagens.append(msg)  # Adiciona a mensagem à lista
        await asyncio.sleep(60)  # Espera 60 segundos
        for msg in mensagens:
            await msg.delete()  # Deleta cada mensagem enviada

          
    else:
      msg = await ctx.send(Res.trad(user=ctx.author,str="message_erro_onlyowner"))
      await asyncio.sleep(20)
      await msg.delete()
      return









  #BUMP TEST COMANDO DEBUG
  @commands.command(name="bumptest", description='Envia uma mensagem de teste de bump.')
  async def bumptest(self,ctx):
    await ctx.message.delete()
    if ctx.author.id == donoid:
      async with ctx.typing():
        consulta = BancoServidores.insert_document(ctx.message.guild.id)
        if "bump-message" in consulta:
          mensagem = consulta['bump-message'].replace(r"\q", "\n")
        msg = await ctx.send(Res.trad(guild=ctx.message.guild.id, str="message_bump_lembrete_ping").format(mensagem))
      await asyncio.sleep(30)
      await msg.delete()

    else:
      msg = await ctx.send(Res.trad(user=ctx.author,str="message_erro_onlyowner"))
      await asyncio.sleep(20)
      await msg.delete()
      return






#TAREFA PARA VERIFICAR EM QUAIS GUILDAS BRIX ESTÁ, E SE NÃO TIVER DELETA OS DADOS DO BANCO DE DADOS
  @tasks.loop(time=datetime.time(hour=2, minute= 0, tzinfo=datetime.timezone(datetime.timedelta(hours=-3))))
  async def verificar_guilds(self): 
    print(f"Iniciando Verificação de Servidores onde o bot está")
    dados = BancoServidores.select_many_document({})
    contador = 0
    for server in dados:
      await asyncio.sleep(0.2)
      contador += 1
      servidor = self.client.get_guild(int(server['_id']))
      if servidor is None:
        falhas = server.get("check_falhas", 0) + 1
        if falhas >= 30:
          print(f"{contador}: ⚠️ Falhou 30 vezes. Deletando registro do ID {server['_id']}")
          BancoServidores.delete_document(server['_id'])
        else:
          print(f"{contador}: 🚨 Incrementando falhas ({falhas}/10) para o ID {server['_id']}")
          BancoServidores.update_document(server['_id'], {"check_falhas": falhas})
      
      else:
        print(f"{contador}: ✔️ Servidor válido: {servidor.name} (ID: {servidor.id})")
        BancoServidores.delete_field(server['_id'], {"check_falhas": 0})

    print(f"Verificação de Servidores Concluida ")



  """
     #VERIFICANDO USUARIOS DO BANCO DE DADOS
  @commands.command(name="clearusuarios", description='limpeza de usuarios excluidos do banco de dados.')
  async def clearuser(self,ctx):
    await ctx.message.delete()
    if ctx.author.id == donoid:
      filtro = {}  # Pega todos os registros do banco de dados
      dados = BancoUsuarios.select_many_document(filtro)
      await ctx.send("Iniciando verificação de usuários...\nConfirá os detalhes no terminal...")
      usuario = 0
      
      for membro in dados:
        await asyncio.sleep(1)
        usuario += 1
        try:
          user = await self.client.fetch_user(membro['_id'])

          if user and "deleted_user" in user.name:
              print(f"{usuario}: 🗑️ Usuário deletado: {user.name} (ID: {user.id}), deletando registro")
              BancoUsuarios.delete_document(user)
          else:
              print(f"{usuario}: ✔️ Usuário válido: {user.name} (ID: {user.id})")
              BancoUsuarios.delete_field(user, {"verificacoes_falhas": 0})

        except discord.NotFound:
          print(f"{usuario}: ❓ Usuário {membro['_id']} não encontrado.")
          falhas = membro.get("verificacoes_falhas", 0) + 1

          if falhas >= 3:
              print(f"{usuario}: ⚠️ Falhou 3 vezes. Deletando registro do ID {user}")
              BancoUsuarios.delete_document(user)
          else:
              print(f"{usuario}: 🚨 Incrementando falhas ({falhas}/3) para o ID {user}")
              BancoUsuarios.update_document(user, {"verificacoes_falhas": falhas})

        except Exception as e:
            print(f"{usuario}: Erro ao verificar usuário {membro['_id']}: {e}")

      
    else:
      msg = await ctx.send(Res.trad_nada(str="message_erro_onlyowner"))
      await asyncio.sleep(20)
      await msg.delete()
      return
  """






                  #GRUPO BOT 
  bot=app_commands.Group(name="brix",description="Comandos de gestão do sistema Brix.",allowed_installs=app_commands.AppInstallationType(guild=True,user=True),allowed_contexts=app_commands.AppCommandContext(guild=True, dm_channel=True, private_channel=True))







                  # COMANDO SAY
  @bot.command(name="say", description="🦊⠂Diga alguma coisa como Brix.")
  @app_commands.describe(mensagem=r"Qual é a mensagem? use \q para quebrar linha.", ia="Peça algo gerado por Inteligencia artificial.")
  @commands.has_permissions(manage_messages=True)
  async def say(self, interaction: discord.Interaction, mensagem: str = None, ia: str = None):
    if await Res.print_brix(comando="say",interaction=interaction,condicao=f"mensagem:{mensagem} - pedido ia: {ia}"):
      return  
    if mensagem is None and ia is None:
      await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_notargument").format("Escreva uma mensagem ou peça algo pelo Brix IA."), delete_after=20,ephemeral=True)
      return
    await interaction.response.defer(ephemeral=True)
    if mensagem:
      try:
        mensagem_formatada = mensagem.replace(r"\q", "\n")
        await interaction.channel.send(mensagem_formatada)
        await interaction.followup.send(Res.trad(interaction=interaction, str="message_say"))
      except:
        await interaction.followup.send(Res.trad(interaction=interaction, str="message_erro_permissao"))
      return
    if ia:
      Check = await userpremiumcheck(interaction)
      if Check == True:
        gerado = (await generate_response_with_text(f"{ia} Limite 1800 Caracteres"))
        try:
          await interaction.channel.send(gerado)
          await interaction.followup.send(Res.trad(interaction=interaction, str="message_say"))
        except:
          await interaction.followup.send(Res.trad(interaction=interaction, str="message_erro_permissao"))
        return
      else:
        await interaction.followup.send(Res.trad(interaction=interaction, str='message_ia_only_premium'))
        return










                  # COMANDO EMBED
  @bot.command(name="embed", description="🦊⠂Envie um embed como Brix.")
  @app_commands.describe(embed="Crie o Json no site eb.nadeko.bot")
  @commands.has_permissions(manage_messages=True)
  async def embed(self, interaction: discord.Interaction, embed: str):
    if await Res.print_brix(comando="say",interaction=interaction,condicao=f"json:{embed}"):
      return
    if interaction.user.id == donoid:
      await interaction.response.send_message(Res.trad(interaction=interaction, str="message_say"), delete_after=2, ephemeral=True)
      envio = interaction.channel.send
    else:
      envio = interaction.response.send_message
    try:
      data = json.loads(embed)
      content = data.get("content", None)
      embeds = data.get("embeds", [])
      embedpronto = []
      for embed_data in embeds:
        if "color" in embed_data:
          color_str = embed_data["color"].lstrip('#')
          embed_data["color"] = int(color_str, 16)
        if "thumbnail" in embed_data and isinstance(embed_data["thumbnail"], str):
          embed_data["thumbnail"] = {"url": embed_data["thumbnail"]}
        if "image" in embed_data and isinstance(embed_data["image"], str):
          embed_data["image"] = {"url": embed_data["image"]}
        if "fields" in embed_data and isinstance(embed_data["fields"], str):
          fields = embed_data.get("fields", [])
          for field in fields:
            embed_data[field]
        embedpronto.append(discord.Embed.from_dict(embed_data))
      await envio(content=content, embeds=embedpronto)
    except Exception as e:
      await envio(content=Res.trad(interaction=interaction, str="message_erro_embed"))
      # Res.erro_brix_embed(interaction,str="message_erro_brixsystem",e=e,comando="embed")











                  #COMANDO PING
  @bot.command(name="ping",description='🤖⠂Exibe o ping do Brix.')
  async def ping(self,interaction: discord.Interaction):
    if await Res.print_brix(comando="ping",interaction=interaction):
      return
    bot_latency = round(self.client.latency * 1000)  # Convertendo de segundos para milissegundos
    start_time = discord.utils.utcnow()
    await interaction.response.defer()
    end_time = discord.utils.utcnow()

    api_latency = round((end_time - start_time).total_seconds() * 1000)
    resposta = discord.Embed( colour=discord.Color.yellow(), title="🏓┃Pong ~kyu", description=Res.trad(interaction=interaction,str="owner_ping").format(bot_latency,bot_latency/1000,api_latency,api_latency/1000))
    resposta.set_thumbnail(url="https://static.wikia.nocookie.net/pokemon-opalo-por-ericlostie/images/5/53/654.png/revision/latest?cb=20220313124241&path-prefix=es")
    await interaction.followup.send(embed=resposta)









                  #COMANDO STATUS BOT
  @bot.command(name="status",description='🤖⠂Exibe informações sobre o status de Brix.')
  async def botstatusslash(self, interaction: discord.Interaction):
    await botstatus(self,interaction)









                  #COMANDO VERSION BOT
  @bot.command(name="version",description='🤖⠂Exibe a versão atual do bot.')
  async def botversionslash(self, interaction: discord.Interaction):
    await botversion(self,interaction)









                  #COMANDO DE AJUDA SOBRE O BOT
  @bot.command(name="ajuda",description='🤖⠂Ajuda sobre o Brix.')
  async def help(self,interaction: discord.Integration):
    if await Res.print_brix(comando="help",interaction=interaction):
      return
    resposta = discord.Embed( 
      colour=discord.Color.yellow(),
      title=Res.trad(interaction=interaction,str="onwer_help_title"),
      description=Res.trad(interaction=interaction,str="onwer_help_description")
    )
    resposta.set_thumbnail(url=f"{self.client.user.avatar.url}")
    await interaction.response.send_message(embed=resposta)








 
   #COMANDO DE INFORMAÇÕES DO BOT
  @bot.command(name="info",description='🤖⠂saiba sobre o Brix.')
  async def botinfo(self,interaction: discord.Integration):
    if await Res.print_brix(comando="botinfo",interaction=interaction):
      return
    resposta = discord.Embed( 
      colour=discord.Color.yellow(),
      description= Res.trad(interaction=interaction,str="onwer_botinfo_description").format(len(self.client.guilds),len(self.client.users))
    )

    resposta.set_author(name= Res.trad(interaction=interaction,str="onwer_botinfo_author").format(self.client.user.name),icon_url=self.client.user.avatar.url)
    resposta.set_thumbnail(url=self.client.user.avatar.url)
    resposta.set_footer(text= Res.trad(interaction=interaction,str="onwer_botinfo_footer") ,icon_url="https://cdn.discordapp.com/emojis/976096456513552406.png")
    view = discord.ui.View()
    button = discord.ui.Button(style=discord.ButtonStyle.blurple,label=Res.trad(interaction=interaction,str="botão_abrir_site_brix"),url="https://brix.squareweb.app/")
    view.add_item(item=button)
    await interaction.response.send_message(embed=resposta , view= view)









  #COMANDO PARA LIMPAR A DM DO USUARIO DELETANDO TUDO QUE O BRIX ENVIOU
  @bot.command(name="limpar-dm",description='🤖⠂Limpe todas as mensagens de brix em sua DM.')
  async def cleardm(self,interaction: discord.Interaction):
    if await Res.print_brix(comando="cleardm",interaction=interaction):
      return
    await interaction.response.send_message(content=Res.trad(interaction=interaction,str='message_clear_dm'),delete_after=20,ephemeral=True)
    async for message in interaction.user.history():
      if message.author == self.client.user:
        await asyncio.sleep(1)
        await message.delete()
        








  #LINGUAGEM BOT
  @bot.command(name="idioma",description='🤖⠂altere o idioma de brix na comunidade.')
  @app_commands.describe(idioma="Selecione um idioma padrão para sua comunidade...")
  @app_commands.choices(idioma=[app_commands.Choice(name="Portugues", value="pt-BR"),app_commands.Choice(name="English", value="en-US")])
  async def chargelanguage(self,interaction: discord.Interaction,idioma:app_commands.Choice[str]):
    if await Res.print_brix(comando="chargelanguage",interaction=interaction):
      return
    await interaction.response.defer(ephemeral=False)
    if interaction.guild is None:
      await interaction.followup.send(Res.trad(interaction=interaction,str="message_erro_onlyservers"))
      return
    elif interaction.permissions.manage_guild or interaction.user.id == donoid:
      item = {"language": idioma.value}
      BancoServidores.update_document(interaction.guild.id,item)
      await interaction.followup.send(Res.trad(interaction=interaction,str="message_language").format(idioma.name))
    else:
      await interaction.followup.send(Res.trad(interaction=interaction,str="message_erro"),ephemeral=False)
  








  
  #Comando Ativar/Desativar Notificação em DM
  @bot.command(name="notificacao",description='🤖⠂Ative ou Desative as notificações em DM.')
  @app_commands.describe(notificacao="Selecione uma opção...")
  async def dmnotificacao(self,interaction:discord.Interaction,notificacao:bool):
    if await Res.print_brix(comando="dmnotificacao",interaction=interaction):
      return
    await interaction.response.defer()
    if notificacao:
        msgstatus = "Ativou"
    else:msgstatus = "desativou"
    item = {"dm-notification": notificacao}
    try:
      BancoUsuarios.update_document(interaction.user,item)
      await interaction.followup.send(Res.trad( interaction=interaction, str="message_bot_notificacao").format(msgstatus))
    except:
      await interaction.followup.send(Res.trad( interaction=interaction, str='message_erro_mongodb').format(interaction.user.id),ephemeral=True)
    









#Comando Ativar/Desativar Notificação em DM
  @bot.command(name="bump",description='🤖⠂Personalize a mensagem de bump de brix.')
  @app_commands.describe(mensagem="Escreva como deve ser a mensagem de aviso de bump, use \q para quebrar a linha.")
  async def msgbump(self,interaction:discord.Interaction , mensagem: str):
    if await Res.print_brix(comando="msgbump",interaction=interaction):
      return
    await interaction.response.defer()
    mensagem = mensagem.replace(r"\q", "\n")
    item = {"bump-message": mensagem}
    if interaction.permissions.manage_guild:
      try:
        BancoServidores.update_document(interaction.guild.id,item)
        await interaction.followup.send(Res.trad( interaction=interaction, str="message_bump_message_confirmacao").format(mensagem))
      except:
        await interaction.followup.send(Res.trad( interaction=interaction, str='message_erro_mongodb').format(interaction.user.id),ephemeral=True)
    
    else:
      await interaction.followup.send(Res.trad(interaction=interaction,str="message_erro"),ephemeral=False)








async def setup(client:commands.Bot) -> None:
  await client.add_cog(owner(client))




      
 
      
      