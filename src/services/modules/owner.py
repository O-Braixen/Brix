import discord,os,requests,json,aiohttp,datetime,pytz,asyncio ,random
from discord.ext import commands , tasks
from discord import app_commands
from os import listdir
from typing import List
from src.services.connection.database import BancoUsuarios,BancoServidores,BancoBot,BancoLoja , BancoFinanceiro , BancoLogs , BancoCodigosResgate
from src.services.essential.respostas import Res
from src.services.essential.funcoes_usuario import userpremiumcheck , verificar_cooldown
from src.services.modules.premium import liberarpremium
from src.services.essential.host import informação,status,restart 
from src.services.essential.gasmii import generate_response_with_text
from src.services.essential.diversos import Paginador_Global
from src.services.essential.pokemon_module import inicializar_caches_se_preciso
from src.services.essential.shardsname import NOME_DOS_SHARDS
from src.services.essential.Criador_embed import CriadorDeEmbed
from dotenv import load_dotenv









#CARREGA E LE O ARQUIVO .env na raiz
load_dotenv(os.path.join(os.path.dirname(__file__), '.env')) #load .env da raiz
donoid = int(os.getenv("DONO_ID")) #acessa e define o id do dono



















#Função status
async def botstatus(self,interaction):
  if await Res.print_brix(comando="botstatus",interaction=interaction):
    return
  await interaction.response.defer()  # Defer normal
  fuso = pytz.timezone('America/Sao_Paulo')
  now = datetime.datetime.now().astimezone(fuso).replace(hour=0, minute=0, second=0, microsecond=0)
  try:
    logs_hoje = BancoLogs.contar_comandos({"timestamp": {"$gte": now}})
    dadosbot = BancoBot.insert_document()
    if self.client.user.id == 983000989894336592:
      ambiente = "Produção"
    else:
      ambiente = "Beta Teste"
    try:
      res_information , host = await informação(self.client.user.name)
      res_status, host = await status(self.client.user.name)

        #DADOS PELA SQUARECLOUD      
      if host == "squarecloud":
        resposta = discord.Embed(
            colour=discord.Color.yellow(),
            title=f"🦊┃Informações do {res_information['response']['name']}",
            description=f"{res_information['response']['desc']}"
        )
        resposta.set_thumbnail(url=f"{self.client.user.avatar.url}")
        resposta.add_field(name="🖥️⠂Square Cloud", value=f"```{res_information['response']['cluster']}```", inline=True)
        resposta.add_field(name="📊⠂Ram", value=f"```{(res_status['response']['ram'])} / {res_information['response']['ram']} MB```", inline=True)
        resposta.add_field(name="🌡⠂CPU", value=f"```{res_status['response']['cpu']}```", inline=True)
        resposta.add_field(name="👨‍💻⠂Linguagem", value=f"```{res_information['response']['language']}```", inline=True)
        resposta.add_field(name="🕐⠂Uptime", value=f"<t:{round(res_status['response']['uptime']/1000)}:R>", inline=True)
        resposta.add_field(name="🌐⠂Rede", value=f"```{res_status['response']['network']['total']}```", inline=True)
        resposta.add_field(name="🏓⠂Ping", value=f"```{round(self.client.latency * 1000)}ms```", inline=True)
        resposta.add_field(name="🔮⠂Menção", value=f"<@{self.client.user.id}>", inline=True)
        resposta.add_field(name="🗄️⠂Servidores", value=f"```{len(self.client.guilds) :,.0f} Comunidades```", inline=True)
        resposta.add_field(name="👥⠂Usuários", value=f"```{len(self.client.users) :,.0f} Usuários```", inline=True)
        resposta.add_field(name="🤖⠂Usados hoje", value=f"```{logs_hoje :,.0f} Comandos```", inline=True)
        resposta.add_field(name="✨⠂Shards", value=len(self.client.latencies), inline=True)
        resposta.set_footer(text=f"Rodando versão: {dadosbot['version']} - Mais detalhes use /brix version",icon_url="https://cdn.discordapp.com/emojis/976096456513552406.png")

        #DADOS PELA DISCLOUD
      if host == "discloud":
        resposta = discord.Embed(
            colour=discord.Color.yellow(),
            title=f"🦊┃Informações do {self.client.user.name}",
            description=f"🖥️⠂Discloud - CLUSTER {res_information['apps']['clusterName']}"
        )
        resposta.set_thumbnail(url=f"{self.client.user.avatar.url}")
        resposta.set_thumbnail(url=f"{self.client.user.avatar.url}")
        resposta.add_field(name="👨‍💻⠂Linguagem", value=f"```{res_information['apps']['lang']}```", inline=True)
        resposta.add_field(name="📊⠂Ram", value=f"```{(res_status['apps']['memory'])}```", inline=True)
        resposta.add_field(name="🗄️⠂Armazenamento", value=f"```{res_status['apps']['ssd']}```", inline=True)
        resposta.add_field(name="🌡⠂CPU", value=f"```{res_status['apps']['cpu']}```", inline=True)
        resposta.add_field(name="🕐⠂Uptime", value=f"{res_status['apps']['last_restart']}", inline=True)
        resposta.add_field(name="🌐⠂Rede", value=f"```⬇️ {res_status['apps']['netIO']['down']}/⬆️ {res_status['apps']['netIO']['up']}```", inline=True)
        resposta.add_field(name="🏓⠂Ping", value=f"```{round(self.client.latency * 1000)}ms```", inline=True)
        resposta.add_field(name="🔮⠂Menção", value=f"<@{self.client.user.id}>", inline=True)
        resposta.add_field(name="🗄️⠂Servidores", value=f"```{len(self.client.guilds) :,.0f} Comunidades```", inline=True)
        resposta.add_field(name="👥⠂Usuários", value=f"```{len(self.client.users) :,.0f} Usuários```", inline=True)
        resposta.add_field(name="🤖⠂Usados hoje", value=f"```{logs_hoje :,.0f} Comandos```", inline=True)
        resposta.add_field(name="✨⠂Shards", value=len(self.client.latencies), inline=True)
        resposta.set_footer(text=f"Rodando versão: {dadosbot['version']} - Mais detalhes use /brix version",icon_url="https://cdn.discordapp.com/emojis/976096456513552406.png")


      view = discord.ui.View()
      button = discord.ui.Button(style=discord.ButtonStyle.blurple,label=Res.trad(interaction=interaction,str="botão_abrir_site_brix"),url="https://brixbot.xyz/")
      view.add_item(item=button)
      buttonsquare = discord.ui.Button(style=discord.ButtonStyle.blurple,label=Res.trad(interaction=interaction,str="botão_abrir_site_square"),url="https://squarecloud.app/")
      view.add_item(item=buttonsquare)

      await interaction.followup.send(embed=resposta, view=view)

    except Exception as e:
      print(e)
      resposta = discord.Embed(
              colour=discord.Color.yellow(),
              title=f"🦊┃Informações do {self.client.user.name}",
              description=f"O melhor Braixen Bot, sem dados de hospedagem."
          )
      resposta.set_thumbnail(url=f"{self.client.user.avatar.url}")
      resposta.add_field(name="🍀⠂Ambiente", value=f"```{ambiente}```", inline=True)
      resposta.set_footer(text=f"Rodando versão: {dadosbot['version']} - Mais detalhes use /brix version",icon_url="https://cdn.discordapp.com/emojis/976096456513552406.png")

      view = discord.ui.View()
      button = discord.ui.Button(style=discord.ButtonStyle.blurple,label=Res.trad(interaction=interaction,str="botão_abrir_site_brix"),url="https://brixbot.xyz/")
      view.add_item(item=button)
      buttonsquare = discord.ui.Button(style=discord.ButtonStyle.blurple,label=Res.trad(interaction=interaction,str="botão_abrir_site_square"),url="https://squarecloud.app/")
      view.add_item(item=buttonsquare)
      
      await interaction.followup.send(embed=resposta, view=view)
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

    def __init__(self, client: discord.Client):
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
          BancoFinanceiro.registrar_transacao(user_id=membro.id,tipo="ganho",origem="Deus Raposa",valor=quantidade,moeda=self.moeda,descricao=f"Esse valor entrou misteriosamente em sua conta.")

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
        BancoFinanceiro.registrar_transacao(user_id=membro.id,tipo="gasto",origem="Deus Raposa",valor=quantidade,moeda=self.moeda,descricao=f"Esse valor saiu misteriosamente em sua conta.")

        await interaction.followup.send(Res.trad(interaction=interaction,str="message_financeiro_pagamento_take").format(membro.mention,saldo,self.emoji)) 
      except: await interaction.followup.send(Res.trad(interaction=interaction,str='message_erro_mongodb').format(interaction.user.id),ephemeral=True)  























#Classe do MODAL USER CONSULTAR EXTRATO
class ModalUserextrato(discord.ui.Modal,title = "Consulte o extrato de alguém!"):
    userid = discord.ui.TextInput(label="ID do Usuario",style=discord.TextStyle.short,min_length=1,placeholder="0123456789")

    def __init__(self, client):
        super().__init__()
        self.client = client

    async def on_submit(self, interaction: discord.Interaction):
      membro = await self.client.fetch_user(self.userid.value)
      await interaction.response.defer(ephemeral=True)
      try:
        transacoes = BancoFinanceiro.buscar_historico(membro.id, limite=1000,moeda=None)
        lista = []
        for t in transacoes:
            timestamp = int(t["timestamp"].timestamp())
            tipo = "🟢 +" if t["tipo"] == "ganho" else "🔴 -"
            origem = t.get("origem", "desconhecido")
            moeda = "<:BraixenCoin:1272655353108103220>" if t["moeda"] == "braixencoin" else "<:Graveto:1318962131567378432>"
            descricao = t.get("descricao", "desconhecido")
            linha = f"**{tipo} {t['valor']:,.0f}** {moeda} <t:{timestamp}:R> - {origem}\n*{descricao}*"
            lista.append(linha)

        if not lista:
          lista =[f"{Res.trad(interaction= interaction, str='message_financeiro_sem_transções')}"]
        
        blocos = [lista[i:i + 10] for i in range(0, len(lista), 10)] 
        descrição = Res.trad(interaction= interaction, str="message_financeiro_extrato").format(membro.name)
        await Paginador_Global(self, interaction, blocos, pagina=0, originaluser=interaction.user,descrição=descrição, thumbnail_url=None)

 
      except: await interaction.edit_original_response(content=Res.trad(interaction=interaction,str='message_erro_mongodb').format(interaction.user.id))  

















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




















class ModalDeletarCodigo(discord.ui.Modal, title="Deletar Código"):
    codigo = discord.ui.TextInput(label="Código", placeholder="Digite o código exato", max_length=50)

    async def on_submit(self, interaction: discord.Interaction):
        codigo = self.codigo.value.strip()
        doc = BancoCodigosResgate.get_codigo( codigo )

        if not doc:
            return await interaction.response.send_message(    f"<:Braix_Shocked:1272663500115935264>┃ Kyu~! O código **{codigo}** não existe ou já foi usado. Dá uma olhadinha certinho antes de tentar de novo!",    ephemeral=True)

        BancoCodigosResgate.delete_codigo( codigo )
        await interaction.response.send_message(    f"<:Braix_uwu:1287443559074500691>┃ Código **{codigo}** deletado com sucesso, kyu~! Tudo limpo e organizado do jeitinho que eu gosto!",ephemeral=True)
















class ModalAddCodigo(discord.ui.Modal):
    def __init__(self, client, tipo_selecionado: str):
        super().__init__(title="Cadastrar Código de Resgate")
        self.client = client
        self.tipo = tipo_selecionado  # recebido do dropdown
        self.codigo = discord.ui.TextInput(label="Código", placeholder="Ex: BraixenDay", max_length=50)
        self.add_item(self.codigo)

        self.valor = discord.ui.TextInput(label=f"Valor ({self.tipo})", placeholder="Ex: valor / dias ou nome da arte", max_length=250)
        self.add_item(self.valor)

        self.max_usos = discord.ui.TextInput(label="Máx. usos (0 = ilimitado)", placeholder="Ex: 10 ou 0", required=False, max_length=10)
        self.add_item(self.max_usos)

        self.dias_validade = discord.ui.TextInput(label="Dias de validade", placeholder="Ex: 7", required=False, max_length=5)
        self.add_item(self.dias_validade)

        self.dia_ativacao = discord.ui.TextInput(label="Dia de ativação (YYYY-MM-DD)", placeholder="Ex: 2025-10-07", required=False, max_length=10)
        self.add_item(self.dia_ativacao)

    async def on_submit(self, interaction: discord.Interaction):
        codigo = self.codigo.value.strip()
        valor = int(self.valor.value) if self.tipo in ["braixencoin", "gravetos", "premium"] else self.valor.value.strip()
        max_usos = int(self.max_usos.value) if self.max_usos.value else None
        dias_validade = int(self.dias_validade.value) if self.dias_validade.value else None
        dia_ativacao = self.dia_ativacao.value if self.dia_ativacao.value else None

        # validações
        if BancoCodigosResgate.get_codigo(codigo):
          return  await interaction.response.send_message(    f"<:Braix_Shocked:1272663500115935264>┃ Kyu~! O código **{codigo}** já existe. Tente usar um diferente, tá bem?",    ephemeral=True)
  

        # datas
        ativa_em_iso = None
        if dia_ativacao:
            try:
                ativa_em_iso = datetime.datetime.fromisoformat(dia_ativacao).isoformat()
            except:
              return await interaction.response.send_message(    "<:Braix_Shocked:1272663500115935264>┃ Data de ativação inválida, kyu~! Use o formato correto: **YYYY-MM-DD** (ano-mês-dia).",    ephemeral=True)

        expira_em = None
        if dias_validade:
            if ativa_em_iso:
                expira_em = (datetime.datetime.fromisoformat(dia_ativacao) + datetime.timedelta(days=dias_validade)).isoformat()
            else:
                expira_em = (datetime.datetime.now() + datetime.timedelta(days=dias_validade)).isoformat()

        BancoCodigosResgate.insert_document( codigo=codigo, recompensa={"tipo": self.tipo, "valor": valor}, max_usos=max_usos if max_usos != 0 else None, expira_em=expira_em, ativa_em=ativa_em_iso )
        await interaction.response.send_message(    f"### <:Braix_uwu:1287443559074500691>┃ Código registrado com sucesso, kyu~!\n"    f"**Código:** `{codigo}`\n"    f"**Tipo:** `{self.tipo}`\n"    f"**Valor:** `{valor}`\n"    f"**Máx. usos:** `{max_usos or 'ilimitado'}`\n"    f"**Ativo a partir de:** `{ativa_em_iso or 'imediatamente'}`\n"    f"**Expira em:** `{expira_em or 'sem prazo'}`\n\n"    f"<:Braix_Tongue:1272662386590879795>┃ Agora é só usar direitinho, tá pronto pra funcionar, kyuuu~!",    ephemeral=True)










class SelectTipo(discord.ui.Select):
    def __init__(self, client):
        options = [
            discord.SelectOption(label="Braixencoin", value="braixencoin", emoji= "<:BraixenCoin:1272655353108103220>"),
            discord.SelectOption(label="Graveto", value="graveto", emoji= "<:Graveto:1318962131567378432>"),
            discord.SelectOption(label="Premium", value="premium", emoji= "💎"),
            discord.SelectOption(label="Arte", value="arte", emoji= "🎨")
        ]
        super().__init__(placeholder="Selecione o tipo de recompensa", min_values=1, max_values=1, options=options)
        self.client = client

    async def callback(self, interaction: discord.Interaction):
        tipo = self.values[0]
        await interaction.response.send_modal(ModalAddCodigo(self.client, tipo_selecionado=tipo))








class ViewSelectTipo(discord.ui.View):
    def __init__(self, client):
        super().__init__()
        self.add_item(SelectTipo(client))




































#Botões dashboard
class Botoesdash(discord.ui.View):
    def __init__(self,client):
        super().__init__(timeout=300)
        self.client = client
        self.value=None

    @discord.ui.button(label="Server",style=discord.ButtonStyle.red,emoji="📄",row=0)
    async def listservers (self,interaction: discord.Interaction, button: discord.ui.Button):
      if interaction.user.id == donoid: # Verifica se o usuário é o dono do bot
        await interaction.response.defer(ephemeral=True) # Envia uma resposta de interação para indicar que o comando está sendo processado
        servers = self.client.guilds
        lista = "## 🦊┃ Lista de Servidores\n"  # Cria uma variável para armazenar a lista de servidores
        
        partes = []
        parte_atual = lista

        for i, server in enumerate(servers, start=1):  # contador automático
            entrada = f"`{i}` - **Nome:** `{server.name}` - **id:** `{server.id}`\n"

            if len(parte_atual) + len(entrada) > 2000:
                partes.append(parte_atual)
                parte_atual = ""
            parte_atual += entrada
        
        partes.append(parte_atual)  # Adiciona a última parte
        for parte in partes:
            await interaction.followup.send(content=parte, ephemeral=True)
      else:
        await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyowner"),delete_after=10, ephemeral=True) # Envia uma resposta de interação que só é visível para o usuário

    @discord.ui.button(label="Server",style=discord.ButtonStyle.red,emoji="🔚",row=0)
    async def leave (self,interaction: discord.Interaction, button: discord.ui.Button):
      if interaction.user.id == donoid:
          await interaction.response.send_modal(ModalSairServidor(self.client))
      else:
          await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyowner"),delete_after=10)
    

    @discord.ui.button(label="Logs",style=discord.ButtonStyle.red,emoji="📓",row=0)
    async def logsbrix (self,interaction: discord.Interaction, button: discord.ui.Button):
      if interaction.user.id == donoid:
        await interaction.response.defer(ephemeral=True)
        logs = BancoLogs.listar_logs(limite=1000)  # pega últimos 1000 comandos
        lista = []
        for log in logs:
            timestamp = int(log["timestamp"].timestamp())
            guild = f"{log['guild_name']}" if log.get("guild_name") else "DM"
            linha = f"`/{log['comando']}` por **{log['user_name']}** {log['user_id']} (<t:{timestamp}:R>) no servidor: *{guild}*"
            lista.append(linha)

        if not lista:
            lista = ["Nenhum comando registrado."]

        blocos = [lista[i:i + 10] for i in range(0, len(lista), 10)]
        descrição = f"<:Braix_Jay:1272669280932069437> **Histórico dos últimos comandos usados** (total: {len(lista)})\n\n"
        await Paginador_Global(self, interaction, blocos, pagina=0, originaluser=interaction.user,descrição=descrição, thumbnail_url=None)
      else:
          await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyowner"),delete_after=10)


    
    @discord.ui.button(label="Nome",style=discord.ButtonStyle.green,emoji="🤖",row=0)
    async def botname (self,interaction: discord.Interaction, button: discord.ui.Button):
      if interaction.user.id == donoid:
          await interaction.response.send_modal(ModalNomeBot(self.client))
      else:
          await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyowner"),delete_after=10)
    
    @discord.ui.button(label="Avatar",style=discord.ButtonStyle.green,emoji="🖼️",row=0)
    async def botavatar (self,interaction: discord.Interaction, button: discord.ui.Button):
      if interaction.user.id == donoid:
          await interaction.response.send_modal(ModalavatarBot(self.client))
      else:
          await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyowner"),delete_after=10)
    
    @discord.ui.button(label="site dash",style=discord.ButtonStyle.green,emoji="🗄️",row=1)
    async def dashboardsite (self,interaction: discord.Interaction, button: discord.ui.Button):
      if interaction.user.id == donoid:
        dadosbot = BancoBot.insert_document()
        if dadosbot['status_dashboard']:
          item = {"status_dashboard": False}
        else:
          item = {"status_dashboard": True}
        update = BancoBot.update_one(item)
        await interaction.response.send_message(f"<:Braix_Hmph:1272666561244561429>┃ Dashboard do site: {item['status_dashboard']}",delete_after=20)
      else:
          await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyowner"),delete_after=10)
    
    @discord.ui.button(label="+",style=discord.ButtonStyle.green,emoji="<:BraixenCoin:1272655353108103220>",row=1)
    async def awardcoin (self,interaction: discord.Interaction, button: discord.ui.Button):
      if interaction.user.id == donoid:
          await interaction.response.send_modal(ModalUserAward(self.client,moeda='braixencoin',emoji="<:BraixenCoin:1272655353108103220>"))
      else:
          await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyowner"),delete_after=10,ephemeral=True)
    
    @discord.ui.button(label="-",style=discord.ButtonStyle.green,emoji="<:BraixenCoin:1272655353108103220>",row=1) #row=0
    async def takecoin (self,interaction: discord.Interaction, button: discord.ui.Button):
      if interaction.user.id == donoid:
          await interaction.response.send_modal(ModalUserTake(self.client,moeda='braixencoin',emoji='<:BH_BraixenCoin:1182695452731265126>'))
      else:
          await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyowner"),delete_after=10,ephemeral=True)
    
    @discord.ui.button(label="+",style=discord.ButtonStyle.green,emoji="<:Graveto:1318962131567378432>",row=1)
    async def awardstick (self,interaction: discord.Interaction, button: discord.ui.Button):
      if interaction.user.id == donoid:
          await interaction.response.send_modal(ModalUserAward(self.client,moeda='graveto',emoji='<:Graveto:1318962131567378432>'))
      else:
          await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyowner"),delete_after=10,ephemeral=True)
    
    @discord.ui.button(label="-",style=discord.ButtonStyle.green,emoji="<:Graveto:1318962131567378432>",row=1) #row=0
    async def takestick (self,interaction: discord.Interaction, button: discord.ui.Button):
      if interaction.user.id == donoid:
          await interaction.response.send_modal(ModalUserTake(self.client,moeda='graveto',emoji='<:Graveto:1318962131567378432>'))
      else:
          await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyowner"),delete_after=10,ephemeral=True)
    
    @discord.ui.button(label="",style=discord.ButtonStyle.green,emoji="📃",row=2) #row=0
    async def extrato (self,interaction: discord.Interaction, button: discord.ui.Button):
      if interaction.user.id == donoid:
          await interaction.response.send_modal(ModalUserextrato(self.client))
      else:
          await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyowner"),delete_after=10,ephemeral=True)
    
    @discord.ui.button(label="bio user",style=discord.ButtonStyle.green,emoji="🙍",row=2) #row=0
    async def chargedescricao (self,interaction: discord.Interaction, button: discord.ui.Button):
      if interaction.user.id == donoid:
          await interaction.response.send_modal(ModalUserdescricao(self.client))
      else:
          await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyowner"),delete_after=10,ephemeral=True)
    
    @discord.ui.button(label="Loja D",style=discord.ButtonStyle.grey,emoji="⬇️",row=2) #row=0
    async def lojadonwload (self,interaction: discord.Interaction, button: discord.ui.Button):
      if interaction.user.id == donoid:
          await interaction.response.send_message("<:Braix_Hmph:1272666561244561429>┃ Okay Kyuu, vou atualizar os arquivos locais")
          await baixaritensloja(baixe_tudo=True)
      else:
          await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyowner",),delete_after=10,ephemeral=True)

    @discord.ui.button(label="Loja R",style=discord.ButtonStyle.grey,emoji="🔀",row=2) #row=0
    async def lojarotação (self,interaction: discord.Interaction, button: discord.ui.Button):
      if interaction.user.id == donoid:
        dadosbot = BancoBot.insert_document()
        if dadosbot['rotacaoloja']:
          item = {"rotacaoloja": False}
        else:
          item = {"rotacaoloja": True}
        update = BancoBot.update_one(item)
        await interaction.response.send_message(f"<:Braix_Hmph:1272666561244561429>┃ Rotação da loja: {item['rotacaoloja']}",delete_after=20)
      else:
        await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyowner"),delete_after=10)
      

    @discord.ui.button(label="Reiniciar Bot",style=discord.ButtonStyle.red,emoji="⚡",row=2) #row=0
    async def buttonshutdown (self,interaction: discord.Interaction, button: discord.ui.Button):
      if interaction.user.id == donoid:
          await interaction.response.send_message(f"<:Braix_Shocked:1272663500115935264>┃ Enviando solicitação a Host...",delete_after=10)
          await restart(self.client.user.name)
      else:
          await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyowner"),delete_after=10,ephemeral=True)

    
    @discord.ui.button(label="Banir",style=discord.ButtonStyle.red,emoji="🔨",row=3) #row=0
    async def buttonbanuser(self,interaction: discord.Interaction, button: discord.ui.Button):
      if interaction.user.id == donoid:
        await interaction.response.send_modal(ModalBanUSER(self.client))
      else:
          await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyowner"),delete_after=10,ephemeral=True)
    
    @discord.ui.button(label="Desbanir",style=discord.ButtonStyle.red,emoji="🔨",row=3) #row=0
    async def buttonUnbanuser(self,interaction: discord.Interaction, button: discord.ui.Button):
      if interaction.user.id == donoid:
        await interaction.response.send_modal(ModalUnBanUSER(self.client))
      else:
          await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyowner"),delete_after=10,ephemeral=True)
    
    @discord.ui.button(label="listar Banidos",style=discord.ButtonStyle.red,emoji="📃",row=3) #row=0
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


    @discord.ui.button(label="Cadastrar Código", style=discord.ButtonStyle.green, emoji="📝", row=3)
    async def addcodigo_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != donoid:
            await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyowner"),delete_after=10,ephemeral=True)
            return
        await interaction.response.send_message(view=ViewSelectTipo(self) ,ephemeral =True)


    @discord.ui.button(label="Códigos", style=discord.ButtonStyle.green, emoji="🎟️", row=3)
    async def listar_codigos(self, interaction: discord.Interaction, button: discord.ui.Button):
      if interaction.user.id != donoid:
          return await interaction.response.send_message( Res.trad(interaction=interaction, str="message_erro_onlyowner"), delete_after=10 )
      await interaction.response.defer(ephemeral=True)

      codigos = list(BancoCodigosResgate.get_all_codigo().sort("criado_em", -1))  # ordena por criação
      lista = []

      for doc in codigos:
          criado_em = doc.get("criado_em")
          expira_em = doc.get("expira_em")
          ativa_em = doc.get("ativa_em")
          recompensa = doc.get("recompensa", {})

          linha = (
              f"**{doc['_id']}** | {recompensa.get('tipo')} → {recompensa.get('valor')}\n"
              f"Usos: {len(doc.get('usados_por', []))}/{doc.get('max_usos') or '∞'} | \n"
              f"Ativa em: {ativa_em or 'imediato'} | Expira em: {expira_em or 'sem prazo'} | \n"
              f"{'✅ ativo' if doc.get('ativo', True) else '❌ inativo'}"
          )
          lista.append(linha)

      if not lista:
          lista = ["Nenhum código registrado."]

      blocos = [lista[i:i + 5] for i in range(0, len(lista), 5)]
      descrição = f"## 🎟️ Lista de Códigos de Resgate (total: {len(lista)})\n\n"

      await Paginador_Global( self, interaction, blocos, pagina=0, originaluser=interaction.user, descrição=descrição, thumbnail_url=None      )


    @discord.ui.button(label="Deletar Código", style=discord.ButtonStyle.danger, emoji="🗑️", row=4)
    async def deletar_codigo(self, interaction: discord.Interaction, button: discord.ui.Button):
      if interaction.user.id != donoid:
        return await interaction.response.send_message( Res.trad(interaction=interaction, str="message_erro_onlyowner"), delete_after=10 )

      await interaction.response.send_modal(ModalDeletarCodigo())




















#--------------- COMANDO PARA BAIXAR ITENS DA LOJA PARA OS ARQUIVOS LOCAIS -----------
"""async def baixaritensloja():
  filtro = {"_id": {"$ne": "diaria"}}
  itens = BancoLoja.select_many_document(filtro)
  IMAGE_SAVE_PATH = r"src/assets/imagens/backgroud/all-itens"
  if not os.path.exists(IMAGE_SAVE_PATH):
    os.makedirs(IMAGE_SAVE_PATH)
  print('🦊 - Iniciando Download dos itens da loja...')
  async with aiohttp.ClientSession() as session:
    async def baixar_imagem(item, idx):
      file_name = f"{item['_id']}.png"
      file_path = os.path.join(IMAGE_SAVE_PATH, file_name)
      try:
        async with session.get(item['url']) as response:
          if response.status == 200:
            with open(file_path, 'wb') as f:
              f.write(await response.read())
            print(f"🖼️ - Imagem Salva {idx:02d} - {file_name}")
          else:
            print(f'❌ - Falha ao baixar: {item["url"]}')
      except Exception as e:
        print(f'❌ - Erro ao baixar {item["url"]}: {e}')

    tarefas = [baixar_imagem(item, idx + 1) for idx, item in enumerate(itens)]
    await asyncio.gather(*tarefas)

  print('✅ - Todos os itens foram baixados...')"""

























#--------------- COMANDO PARA BAIXAR ITENS DA LOJA PARA OS ARQUIVOS LOCAIS -----------
async def baixaritensloja(baixe_tudo: bool = False):
    filtro = {"_id": {"$ne": "diaria"}}
    itens = BancoLoja.select_many_document(filtro)
    IMAGE_SAVE_PATH = r"src/assets/imagens/backgroud/all-itens"

    if not os.path.exists(IMAGE_SAVE_PATH):
      os.makedirs(IMAGE_SAVE_PATH)

    print('🦊 - Iniciando Download dos itens da loja...')

    async with aiohttp.ClientSession() as session:
      async def baixar_imagem(item, idx):
        file_name = f"{item['_id']}.png"
        file_path = os.path.join(IMAGE_SAVE_PATH, file_name)

        # Checagem individual por arquivo
        if os.path.exists(file_path) and not baixe_tudo:
          if os.path.getsize(file_path) > 0:
            return
          else:
            print(f"⚠️ - Rebaixando {idx:02d} - {file_name} (arquivo vazio/corrompido)")

        try:
          async with session.get(item['url']) as response:
            if response.status == 200:
              content = await response.read()
              if content:  # só salva se realmente veio algo
                with open(file_path, 'wb') as f:
                  f.write(content)
                print(f"🖼️ - Imagem Salva {idx:02d} - {file_name}")
              else:
                print(f"⚠️ - Resposta vazia para {item['url']}")
            else:
              print(f'❌ - Falha ao baixar: {item["url"]} ({response.status})')
        except Exception as e:
          print(f'❌ - Erro ao baixar {item["url"]}: {e}')

      tarefas = [baixar_imagem(item, idx + 1) for idx, item in enumerate(itens)]
      await asyncio.gather(*tarefas)

    print('✅ - Download concluído!')
































class owner(commands.Cog):
  def __init__(self, client: commands.AutoShardedBot):
    self.client = client




    # no __init__ da classe (ou onde você inicializa os menus)
    self.menu_exportar_embed = app_commands.ContextMenu( name="Copiar JSON do Embed", callback=self.exportar_embed_json, type=discord.AppCommandType.message, allowed_installs=app_commands.AppInstallationType(guild=True, user=True), allowed_contexts=app_commands.AppCommandContext(guild=True, dm_channel=True, private_channel=True) )
    self.client.tree.add_command(self.menu_exportar_embed)
























  @commands.Cog.listener()
  async def on_ready(self):
    print("🦊  -  Modúlo Owner carregado.")

    
    if not self.verificar_guilds.is_running():
      self.verificar_guilds.start()
      await asyncio.sleep(20)
      await inicializar_caches_se_preciso()
      await asyncio.sleep(300)
      await baixaritensloja()





















# ======================================================================
#  TRATAMENTO DE ERRO CONTRA ERRO 429 DO DISCORD
  @commands.Cog.listener()
  async def on_command_error(self,ctx, error):
    if isinstance(error, discord.errors.HTTPException) and error.status == 429:
        print(f"Rate limit detectado no comando: {ctx.command}")
        await restart(self.client.user.name)












#  TRATAMENTO DE ERRO CONTRA ERRO 429 DO DISCORD
  @commands.Cog.listener()
  async def on_app_command_error(self, interaction: discord.Interaction, error):
    if isinstance(error, discord.errors.HTTPException) and error.status == 429:
        print(f"Rate limit detectado no comando slash: {interaction.command}")
        await restart(self.client.user.name)






















  #PAINEL DASHBOARD OWNER
  @commands.command(name="dashboard", description='Dashboard de operação administrativa.')
  async def dashboard(self,ctx):
    await ctx.message.delete()
    if ctx.author.id == donoid:
      async with ctx.typing():
        msg = await ctx.send(file = discord.File("src/assets/imagens/Brixdashboardbanner.png"), view = Botoesdash(self.client))
      await asyncio.sleep(60)
      await msg.delete()

    else:
      msg = await ctx.send(Res.trad(user=ctx.author,str="message_erro_onlyowner"))
      await asyncio.sleep(20)
      await msg.delete()
      return



















  #DBGUILD COMANDO DEBUG
  @commands.command(name="debugguild", description='Exibe todos os dados da comunidade presente no banco de dados.')
  async def debugguild(self,ctx, guild:int = None):
    #await ctx.message.delete()
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
      try:
        for emb in embeds:
          msg = await ctx.send(embed=emb)
          mensagens.append(msg)  # Adiciona a mensagem à lista
        await asyncio.sleep(120)  # Espera 120 segundos
        for msg in mensagens:
            await msg.delete()  # Deleta cada mensagem enviada
      except: await ctx.send("Falha ao enviar os Embeds ~kyuuu")
         
    else:
      msg = await ctx.send(Res.trad(user=ctx.author,str="message_erro_onlyowner"))
      await asyncio.sleep(20)
      await msg.delete()
      return























  #DBGUILD COMANDO DEBUG
  @commands.command(name="debuguser", description='Exibe todos os dados de um usuário presente no banco de dados.')
  async def debuguser(self,ctx,user:discord.User = None):
    #await ctx.message.delete()
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
        try:
          for emb in embeds:
            msg = await ctx.send(embed=emb)
            mensagens.append(msg)  # Adiciona a mensagem à lista
          await asyncio.sleep(120)  # Espera 120 segundos
          for msg in mensagens:
              await msg.delete()  # Deleta cada mensagem enviada
        except: await ctx.send("Falha ao enviar os Embeds ~kyuuu")


          
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















    # COMANDO PARA REGISTRAR PARCEIROS
  @commands.command(name="addparceiro", description="Registra um servidor como parceiro no banco de dados.")
  async def registrarparceiro(self, ctx, guild: int = None):
    if ctx.author.id != donoid:
      msg = await ctx.send(Res.trad(user=ctx.author, str="message_erro_onlyowner"))
      await asyncio.sleep(20)
      await msg.delete()
      return

    async with ctx.typing():
      try:
        # Usa o ID passado ou o do servidor atual
        guild_id = guild if guild is not None else ctx.guild.id

        # Atualiza o campo partner para True
        BancoServidores.update_document(guild_id, {"partner": True})

        # Monta mensagem de confirmação
        embed = discord.Embed(
          title="🤝┃Servidor Registrado como Parceiro",
          description=f"O servidor **{ctx.guild.name if guild is None else guild_id}** foi registrado como parceiro com sucesso!",
          color=discord.Color.yellow()
        )
        embed.set_thumbnail(url="https://brixbot.xyz/cdn/path_to_braixen_image.png")
        await ctx.send(embed=embed)

      except Exception as e:
        print(f"[ERRO] Falha ao registrar parceiro: {e}")
        await ctx.send(f"<:Braix_Cry2:1272667164637401250>┃ Ocorreu um erro ao registrar o parceiro: `{e}`")











    # COMANDO PARA LISTAR SERVIDORES PARCEIROS
  @commands.command(name="lsparceiro", description="Lista todos os servidores parceiros registrados no banco de dados.")
  async def listaparceiros(self, ctx):
    if ctx.author.id != donoid:
      msg = await ctx.send(Res.trad(user=ctx.author, str="message_erro_onlyowner"))
      await asyncio.sleep(20)
      await msg.delete()
      return

    async with ctx.typing():
      try:
        parceiros = BancoServidores.select_many_document({"partner": True})
        if not parceiros:
          await ctx.send("<:Braix_Cry2:1272667164637401250>┃ Nenhum servidor parceiro encontrado.")
          return

        embed = discord.Embed(
          title="🤝┃Servidores Parceiros Registrados",
          color=discord.Color.yellow()
        )

        for srv in parceiros[:25]:  # limite pra não estourar embed
          servidor = self.client.get_guild(int(srv['_id']))
          nome = servidor.name if servidor else srv['_id']
          embed.add_field(name=nome, value=f"ID: `{srv['_id']}`", inline=False)

        await ctx.send(embed=embed)

      except Exception as e:
        print(f"[ERRO] Falha ao listar parceiros: {e}")
        await ctx.send(f"<:Braix_Cry2:1272667164637401250>┃ Erro ao listar parceiros: `{e}`")
  # ======================================================================

  # COMANDO PARA REMOVER UM SERVIDOR PARCEIRO
  @commands.command(name="remparceiro", description="Remove o status de parceiro de um servidor.")
  async def removerparceiro(self, ctx, guild: int = None):
    if ctx.author.id != donoid:
      msg = await ctx.send(Res.trad(user=ctx.author, str="message_erro_onlyowner"))
      await asyncio.sleep(20)
      await msg.delete()
      return

    async with ctx.typing():
      try:
        guild_id = guild if guild is not None else ctx.guild.id

        # Remove o campo partner
        BancoServidores.delete_field(guild_id, {"partner": True})

        embed = discord.Embed(
          title="🗑️┃Servidor Removido da Lista de Parceiros",
          description=f"O servidor **{ctx.guild.name if guild is None else guild_id}** foi removido da lista de parceiros.",
          color=discord.Color.red()
        )
        embed.set_thumbnail(url="https://brixbot.xyz/cdn/braixen%20deitado.png")
        await ctx.send(embed=embed)

      except Exception as e:
        print(f"[ERRO] Falha ao remover parceiro: {e}")
        await ctx.send(f"<:Braix_Cry2:1272667164637401250>┃ Erro ao remover parceiro: `{e}`")












  #TAREFA PARA VERIFICAR EM QUAIS GUILDAS BRIX ESTÁ, E SE NÃO TIVER DELETA OS DADOS DO BANCO DE DADOS
  @tasks.loop(time=datetime.time(hour=2, minute=0, tzinfo=datetime.timezone(datetime.timedelta(hours=-3))))
  async def verificar_guilds(self): 
    print(f"🦊 - Iniciando Verificação de Servidores onde o bot está")

    # PASSO EXTRA: Adicionar os servidores que o bot está mas não estão no banco
    # ---------------------------
    dados = list(BancoServidores.select_many_document({}))
    ids_no_banco = {str(server["_id"]) for server in dados}
    for guild in self.client.guilds:
      if str(guild.id) not in ids_no_banco:
        print(f"➕ Registrando novo servidor no banco: {guild.name} ({guild.id})")
        await asyncio.to_thread( BancoServidores.bot_in_guild , guild.id , True)
    
    # Função normal de verificação
    # ---------------------------
    async def verificar(server, i):
      servidor = self.client.get_guild(int(server['_id']))
      if servidor is None:
        falhas = server.get("check_falhas", 0) + 1
        if falhas >= 30:
          print(f"{i}: ⚠️ Falhou 30 vezes. Deletando registro do ID {server['_id']}")
          await asyncio.to_thread(BancoServidores.delete_document, server['_id'])
        else:
          print(f"{i}: 🚨 Incrementando falhas ({falhas}/30) para o ID {server['_id']}")
          await asyncio.to_thread(BancoServidores.update_document, server['_id'], {"check_falhas": falhas, "bot_in_guild": False})
      else:
        #print(f"{i}: ✔️ Servidor válido: {servidor.name} (ID: {servidor.id})")
        if "check_falhas" in server:
          await asyncio.to_thread(BancoServidores.delete_field, server['_id'], {"check_falhas": 0})
        await asyncio.to_thread( BancoServidores.update_document, server['_id'], {"bot_in_guild": True} )

    # PROCESSAMENTO EM LOTES
    # ---------------------------
    async def processar_em_lotes(dados, tamanho_lote=50):
      for i in range(0, len(dados), tamanho_lote):
        lote = dados[i:i + tamanho_lote]
        await asyncio.gather(*(verificar(server, i + j + 1) for j, server in enumerate(lote)))
        await asyncio.sleep(0.2)  # Alivia a carga, opcional

    await processar_em_lotes(dados)
    print(f"🦊 - Verificação de Servidores Concluída")






  
  """   #VERIFICANDO USUARIOS DO BANCO DE DADOS
  @commands.command(name="clearusuarios", description='limpeza de usuarios excluidos do banco de dados.')
  async def clearuser(self,ctx):
    await ctx.message.delete()
    if ctx.author.id == donoid:
      print("Iniciando verificação de usuários do banco de dados...")
      dados = BancoUsuarios.select_many_document({})
      sem = asyncio.Semaphore(5)
      async def verificar(membro, i):
        async with sem:
          await asyncio.sleep(1)  # evita rate limit
          try:
            user = await self.client.fetch_user(int(membro['_id']))
            if user and "deleted_user" in user.name:
              print(f"{i}: 🗑️ Usuário deletado: {user.name} (ID: {user.id}), deletando registro")
              await asyncio.to_thread(BancoUsuarios.delete_document, membro['_id'])
            else:
              print(f"{i}: ✔️ Usuário válido: {user.name} (ID: {user.id})")
              if "verificacoes_falhas" in membro:
                await asyncio.to_thread(BancoUsuarios.delete_field, membro['_id'], {"verificacoes_falhas": 0})

          except discord.NotFound:
            print(f"{i}: ❓ Usuário {membro['_id']} não encontrado.")
            falhas = membro.get("verificacoes_falhas", 0) + 1

            if falhas >= 30:
              print(f"{i}: ⚠️ Falhou 30 vezes. Deletando registro do ID {membro['_id']}")
              await asyncio.to_thread(BancoUsuarios.delete_document, membro['_id'])
            else:
              print(f"{i}: 🚨 Incrementando falhas ({falhas}/30) para o ID {membro['_id']}")
              await asyncio.to_thread(BancoUsuarios.update_document, membro['_id'], {"verificacoes_falhas": falhas})

          except Exception as e:
            print(f"{i}: Erro ao verificar usuário {membro['_id']}: {e}")

      tarefas = [verificar(membro, i+1) for i, membro in enumerate(dados)]
      await asyncio.gather(*tarefas)

      
    else:
      msg = await ctx.send(Res.trad_nada(str="message_erro_onlyowner"))
      await asyncio.sleep(20)
      await msg.delete()
      return"""
  















                  #GRUPO BOT 
  bot=app_commands.Group(name="brix",description="Comandos de gestão do sistema Brix.",allowed_installs=app_commands.AppInstallationType(guild=True,user=True),allowed_contexts=app_commands.AppCommandContext(guild=True, dm_channel=True, private_channel=True))


















                  # COMANDO SAY
  @bot.command(name="say", description="🦊⠂Diga alguma coisa como Brix.")
  @app_commands.describe(mensagem="Qual é a mensagem? use \q para quebrar linha.", ia="Peça algo gerado por Inteligencia artificial.")
  @commands.has_permissions(manage_messages=True)
  async def say(self, interaction: discord.Interaction, mensagem: str = None, ia: str = None):
    if await Res.print_brix(comando="say",interaction=interaction,condicao=f"mensagem:{mensagem} - pedido ia: {ia}"):
      return  
    if mensagem is None and ia is None:
      await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_notargument").format("Escreva uma mensagem ou peça algo pelo Brix IA."), delete_after=20,ephemeral=True)
      return
    
    if interaction.permissions.manage_messages is False:
      await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro"), delete_after=20,ephemeral=True)
      return
    
    await interaction.response.defer()

    if mensagem:
      try:
        mensagem_formatada = mensagem.replace(r"\q", "\n")
        if interaction.user.id == donoid:
          await interaction.followup.send(Res.trad(interaction=interaction, str="message_say"), ephemeral=True)
          envio = interaction.channel.send
        else:
          envio = interaction.followup.send
        await envio(mensagem_formatada)
      except:
        await interaction.followup.send(Res.trad(interaction=interaction, str="message_erro_say"))
      return
    

    if ia:
      Check = await userpremiumcheck(interaction)
      if Check == False:
        permitido, tempo_restantante = await verificar_cooldown(interaction, "say", 600)
        if not permitido:
          await interaction.followup.send(Res.trad(interaction=interaction, str='message_ia_cooldown_premium'))
          return
      gerado = (await generate_response_with_text(f"{ia} Limite 1800 Caracteres"))
      try:
        await interaction.followup.send(gerado)
        #await interaction.followup.send(Res.trad(interaction=interaction, str="message_say"))
      except:
        await interaction.followup.send(Res.trad(interaction=interaction, str="message_erro_say"))
      return























  @bot.command(name="embed", description="🦊⠂Envie um embed como Brix.")
  async def embed(self, interaction: discord.Interaction):
    """Embed Generator With Default Embed"""
    if interaction.permissions.manage_messages is False:
      await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro"), delete_after=20,ephemeral=True)
      return
    # Creates a instance of EmbedCreator class
    view = CriadorDeEmbed(interacao= interaction)
    await interaction.response.send_message(embed=view.get_default_embed, view=view)





   #COMANDO EXPORTAR EMBED JSON MENU
  async def exportar_embed_json(self,interaction: discord.Interaction, mensagem: discord.Message):
    if await Res.print_brix(comando="exportar_embed_json",interaction=interaction):
      return
    await CriadorDeEmbed.context_exportar_embed(self,interaction,mensagem)


























                #COMANDO PING
  @bot.command(name="ping", description='🦊⠂Exibe o ping do Brix.')
  async def ping(self, interaction: discord.Interaction):
    if await Res.print_brix(comando="ping", interaction=interaction):
        return

    bot_latency = round(self.client.latency * 1000)
    start_time = discord.utils.utcnow()
    await interaction.response.defer()
    end_time = discord.utils.utcnow()

    api_latency = round((end_time - start_time).total_seconds() * 1000)
    shard_atual = interaction.guild.shard_id if interaction.guild else "Desconhecido"

    resposta = discord.Embed( colour=discord.Color.yellow(), title="🏓┃Pong ~kyu", description=Res.trad( interaction=interaction, str="owner_ping" ).format(bot_latency, bot_latency / 1000, api_latency, api_latency / 1000 , NOME_DOS_SHARDS.get(shard_atual, 'Desconhecido'))    )

    # Adiciona latência de cada shard
    for shard_id, latency in self.client.latencies:
        qtd_guilds = sum(1 for g in self.client.guilds if g.shard_id == shard_id)
        resposta.add_field(
            name=f"{NOME_DOS_SHARDS.get(shard_id, 'Desconhecido')} ({shard_id})",
            value=f"🏓┃ {round(latency * 1000)}ms\n🌐┃ {qtd_guilds} servidores",
            inline=True
        )

    resposta.set_thumbnail(url="https://static.wikia.nocookie.net/pokemon-opalo-por-ericlostie/images/5/53/654.png/revision/latest?cb=20220313124241&path-prefix=es")
    await interaction.followup.send(embed=resposta)























                  #COMANDO STATUS BOT
  @bot.command(name="status",description='🦊⠂Exibe informações sobre o status de Brix.')
  async def botstatusslash(self, interaction: discord.Interaction):
    await botstatus(self,interaction)

















                  #COMANDO VERSION BOT
  @bot.command(name="version",description='🦊⠂Exibe a versão atual do bot.')
  async def botversionslash(self, interaction: discord.Interaction):
    await botversion(self,interaction)




















                  #COMANDO DE AJUDA SOBRE O BOT
  @bot.command(name="ajuda",description='🦊⠂Ajuda sobre o Brix.')
  async def help(self,interaction: discord.Interaction):
    if await Res.print_brix(comando="help",interaction=interaction):
      return
    resposta = discord.Embed( 
      colour=discord.Color.yellow(),
      title=Res.trad(interaction=interaction,str="onwer_help_title"),
      description=Res.trad(interaction=interaction,str="onwer_help_description")
    )
    resposta.set_thumbnail(url=f"{self.client.user.avatar.url}")
    view = discord.ui.View()
    button = discord.ui.Button(style=discord.ButtonStyle.blurple,label=Res.trad(interaction=interaction,str="botão_abrir_site_brix"),url="https://brixbot.xyz/")
    view.add_item(item=button)
    buttonsquare = discord.ui.Button(style=discord.ButtonStyle.blurple,label=Res.trad(interaction=interaction,str="botão_abrir_site_square"),url="https://squarecloud.app/")
    view.add_item(item=buttonsquare)
    await interaction.response.send_message(embed=resposta , view= view)
























 
   #COMANDO DE INFORMAÇÕES DO BOT
  @bot.command(name="info",description='🦊⠂saiba sobre o Brix.')
  async def botinfo(self,interaction: discord.Interaction):
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
    button = discord.ui.Button(style=discord.ButtonStyle.blurple,label=Res.trad(interaction=interaction,str="botão_abrir_site_brix"),url="https://brixbot.xyz/")
    view.add_item(item=button)
    buttonsquare = discord.ui.Button(style=discord.ButtonStyle.blurple,label=Res.trad(interaction=interaction,str="botão_abrir_site_square"),url="https://squarecloud.app/")
    view.add_item(item=buttonsquare)
    await interaction.response.send_message(embed=resposta , view= view)
























  #COMANDO PARA LIMPAR A DM DO USUARIO DELETANDO TUDO QUE O BRIX ENVIOU
  @bot.command(name="limpar-dm",description='🦊⠂Limpe todas as mensagens de brix em sua DM.')
  async def cleardm(self,interaction: discord.Interaction):
    if await Res.print_brix(comando="cleardm",interaction=interaction):
      return
    await interaction.response.send_message(content=Res.trad(interaction=interaction,str='message_clear_dm'),delete_after=20,ephemeral=True)
    async for message in interaction.user.history():
      if message.author == self.client.user:
        await asyncio.sleep(1)
        await message.delete()
        

























  #LINGUAGEM BOT SERVIDOR
  @bot.command(name="idioma-servidor",description='🦊⠂altere o idioma de brix na comunidade.')
  @app_commands.describe(idioma="Selecione um idioma padrão para sua comunidade...")
  @app_commands.choices(idioma=[app_commands.Choice(name="Portugues", value="pt-BR"),app_commands.Choice(name="English", value="en-US"),app_commands.Choice(name="polish", value="pl")])# ,app_commands.Choice(name="Spanish", value="es-ES")])
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
  








  #LINGUAGEM BOT SERVIDOR
  @bot.command(name="idioma-usuario",description='🦊⠂altere o idioma de brix com você.')
  @app_commands.describe(idioma="Selecione um idioma padrão para sua comunidade...")
  @app_commands.choices(idioma=[app_commands.Choice(name="Portugues", value="pt-BR"),app_commands.Choice(name="English", value="en-US"),app_commands.Choice(name="polish", value="pl")])# ,app_commands.Choice(name="Spanish", value="es-ES")])
  async def chargelanguageuser(self,interaction: discord.Interaction,idioma:app_commands.Choice[str]):
    if await Res.print_brix(comando="chargelanguageuser",interaction=interaction):
      return
    await interaction.response.defer(ephemeral=False)
    item = {"language": idioma.value}
    BancoUsuarios.update_document(interaction.user,item)
    await interaction.followup.send(Res.trad(interaction=interaction,str="message_language", force_refresh = True).format(idioma.name))
    
  























  
  #Comando Ativar/Desativar Notificação em DM
  @bot.command(name="notificacao",description='🦊⠂Ative ou Desative as notificações em DM.')
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
  @bot.command(name="bump",description='🦊⠂Personalize a mensagem de bump de brix.')
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


























  
#COMANDO DE INVITE PARA CONVIDAR O BOT PARA SUA COMUNIDADE
  @bot.command(name="invite",description='🦊⠂Receba meu link de convite.')
  async def invitebot(self,interaction:discord.Interaction ):
    if await Res.print_brix(comando="invitebot",interaction=interaction):
      return
    resposta = discord.Embed( 
      colour=discord.Color.yellow(),
      description= Res.trad(interaction=interaction,str="onwer_botinvite_description")
    )

    resposta.set_thumbnail(url=self.client.user.avatar.url)
    view = discord.ui.View()
    button = discord.ui.Button(style=discord.ButtonStyle.blurple,label=Res.trad(interaction=interaction,str="botão_abrir_navegador"),url="https://brixbot.xyz/invite")
    view.add_item(item=button)
    await interaction.response.send_message(embed=resposta , view= view)
























  
#COMANDO PARA ACESSAR A DASHBOARD DO BOT NO SITE
  @bot.command(name="dashboard",description='🦊⠂Acesse minha dashboard e personalize tudo.')
  async def dashboardsite(self,interaction:discord.Interaction ):
    if await Res.print_brix(comando="dashboardsite",interaction=interaction):
      return
    resposta = discord.Embed( 
      colour=discord.Color.yellow(),
      description= Res.trad(interaction=interaction,str="onwer_dashboard_description")
    )

    resposta.set_thumbnail(url=self.client.user.avatar.url)
    view = discord.ui.View()
    button = discord.ui.Button(style=discord.ButtonStyle.blurple,label=Res.trad(interaction=interaction,str="botão_abrir_navegador"),url="https://brixbot.xyz/dashboard")
    view.add_item(item=button)
    await interaction.response.send_message(embed=resposta , view= view)

























#COMANDO PARA ACESSAR A DASHBOARD DO BOT NO SITE
  @bot.command(name="kyu",description='🦊⠂Mande um kyu.')
  async def brixkyu(self,interaction:discord.Interaction ):
    if await Res.print_brix(comando="kyu",interaction=interaction):
      return
    await interaction.response.send_message(random.choice(Res.trad(interaction=interaction,str='responsekyu')))
























  @bot.command(name="resgatar", description="🦊⠂Resgate um código de recompensa do Brix.")
  @app_commands.describe(codigo="O código de resgate que você recebeu.")
  async def resgatar(self, interaction: discord.Interaction, codigo: str):
    await interaction.response.defer(ephemeral=False)

    codigo_doc = BancoCodigosResgate.get_codigo(codigo)

    if not codigo_doc:
      return await interaction.followup.send(Res.trad(interaction=interaction,str="message_erro_codigo_invalido"), ephemeral=True)

    # Verifica se está ativo
    if not codigo_doc.get("ativo", True):
      return await interaction.followup.send( Res.trad(interaction=interaction,str="message_erro_codigo_desativado") , ephemeral=True)

    # Verifica validade por data (se tiver expiração)
    expira_em = codigo_doc.get("expira_em")
    if expira_em:
      try:
        data_expira = datetime.datetime.fromisoformat(expira_em)
        if datetime.datetime.now() > data_expira:
          return await interaction.followup.send(Res.trad(interaction=interaction,str="message_erro_codigo_expirado"), ephemeral=True)
      except Exception:
          pass  # se expira_em não estiver em ISO válido
    
    ativa_em = codigo_doc.get("ativa_em")
    if ativa_em:
        data_ativa = datetime.datetime.fromisoformat(ativa_em)
        if datetime.datetime.now() < data_ativa:
            return await interaction.followup.send( Res.trad(interaction=interaction,str="message_erro_codigo_indisponivel").format(data_ativa.strftime(Res.trad(interaction=interaction,str="padrao_data"))) , ephemeral=True )

    # Verifica se usuário já usou esse código
    if interaction.user.id in codigo_doc.get("usados_por", []):
        return await interaction.followup.send(Res.trad(interaction=interaction,str="message_erro_codigo_ja_resgatado"), ephemeral=True)

    # Verifica limite de usos
    max_usos = codigo_doc.get("max_usos")
    if max_usos is not None and len(codigo_doc.get("usados_por", [])) >= max_usos:
        return await interaction.followup.send(Res.trad(interaction=interaction,str="message_erro_codigo_limite_uso"), ephemeral=True)

    recompensa = codigo_doc.get("recompensa", {})
    recompensa_msg = "nenhuma recompensa encontrada"

    # --- entrega da recompensa ---
    if recompensa.get("tipo") == "premium":
      dias = int(recompensa.get("valor", 7))
      await liberarpremium(self,interaction,interaction.user,dias,False)
      recompensa_msg = f"**{dias} dias de Premium**"

    elif recompensa.get("tipo") == "braixencoin":
      valor = int(recompensa.get("valor", 0))
      BancoUsuarios.update_inc(interaction.user, {"braixencoin": valor})
      BancoFinanceiro.registrar_transacao( user_id=interaction.user.id, tipo="ganho", origem="resgate de código", valor=valor, moeda="braixencoin", descricao=f"resgate do código {codigo}" )
      recompensa_msg = f"**{valor} Braixencoin**"

    elif recompensa.get("tipo") == "graveto":
      valor = int(recompensa.get("valor", 0))
      BancoUsuarios.update_inc(interaction.user, {"graveto": valor})
      BancoFinanceiro.registrar_transacao( user_id=interaction.user.id, tipo="ganho", origem="resgate de código", valor=valor, moeda="graveto", descricao=f"resgate do código {codigo}" )
      recompensa_msg = f"**{valor} Gravetos**"

    elif recompensa.get("tipo") == "arte":
      banner_name = recompensa.get("valor", "")
      if banner_name:
        insert = {"backgroud": banner_name, f"backgrouds.{banner_name}": banner_name}
        BancoUsuarios.update_document(interaction.user, insert)
        recompensa_msg = Res.trad(interaction=interaction,str="message_erro_codigo_msg_arte").format(banner_name) 

    # --- atualizar usos ---
    BancoCodigosResgate.add_uso(codigo, interaction.user.id)

    await interaction.followup.send( Res.trad(interaction=interaction,str="message_erro_codigo_msg_aviso").format(interaction.user.mention , codigo , recompensa_msg) , ephemeral=True)





























async def setup(client:commands.Bot) -> None:
  await client.add_cog(owner(client))




      
 
      
      