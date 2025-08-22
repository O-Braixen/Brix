import discord,os,random,asyncio,re,requests , aiohttp
from discord.ext import commands, tasks
from discord import app_commands
from datetime import datetime, timedelta
from src.services.essential.respostas import Res
from src.services.connection.database import BancoServidores,BancoUsuarios,BancoLoja , BancoFinanceiro
from src.services.modules.premium import liberarpremium
from dotenv import load_dotenv


load_dotenv()
botlist_token = os.getenv("botlist_token")
topgg_api = os.getenv("topgg_token")
canal_vote_topgg = os.getenv("canal_vote_topgg")









#          CLASSE DE BOTÔES DE INFORMAÇÔES DO SERVIDOR
class BotoesBuscarServidor(discord.ui.View):
    def __init__(self,interaction ,menu, client,server):
        super().__init__(timeout=300)
        self.interaction = interaction
        self.menu = menu
        self.client = client
        self.servidor = server
        self.value=None

        self.sicone = discord.ui.Button(label=Res.trad(interaction=self.interaction,str="botão_ver_icone"),style=discord.ButtonStyle.blurple,emoji="🎨")
        self.add_item(item=self.sicone)
        self.sicone.callback = self.botaoiconeservidor

        self.sbanner = discord.ui.Button(label=Res.trad(interaction=self.interaction,str="botão_ver_banner"),style=discord.ButtonStyle.blurple,emoji="🖼️")
        self.add_item(item=self.sbanner)
        self.sbanner.callback = self.botaobannerservidor

        self.splash = discord.ui.Button(label=Res.trad(interaction=self.interaction,str="botão_ver_splash"),style=discord.ButtonStyle.blurple,emoji="🎪")
        self.add_item(item=self.splash)
        self.splash.callback = self.botaosplashservidor

    def __call__(self):
        return self

    #@discord.ui.button(label="Ver icone",style=discord.ButtonStyle.blurple,emoji="🎨")
    async def botaoiconeservidor(self,interaction: discord.Interaction):
      self.value = True
      await iconeserver(self,interaction)

    
    #@discord.ui.button(label="Ver Banner",style=discord.ButtonStyle.blurple,emoji="🖼️")
    async def botaobannerservidor(self,interaction: discord.Interaction):
      self.value = True
      await bannerserver(self,interaction)

    #@discord.ui.button(label="Ver Splash",style=discord.ButtonStyle.blurple,emoji="🎪")
    async def botaosplashservidor(self,interaction: discord.Interaction):
      self.value = True
      await splashserver(self,interaction)
      






# FUNÇÂO CONSULTAR ICONE DO SERVIDOR
async def iconeserver(self,interaction):
    #await interaction.response.defer()
    if await Res.print_brix(comando="iconeserver",interaction=interaction):
        return
    servidor = self.servidor
    icone_url = servidor.icon.url if servidor.icon else None
    if icone_url:
      resposta = discord.Embed(
        title=Res.trad(interaction=interaction,str="icone_guild"),
        description=Res.trad(interaction=interaction,str="icone_guild_description").format(servidor.name),
        colour=discord.Color.yellow()
      )
      resposta.set_image(url=icone_url)
      view = discord.ui.View()
      item = discord.ui.Button(style=discord.ButtonStyle.blurple, label=Res.trad(interaction=interaction,str="botão_abrir_navegador"), url=icone_url)
      view.add_item(item=item)
      await interaction.response.send_message(embed=resposta, view=view, delete_after=60)
    else:
      await interaction.response.send_message(Res.trad(interaction= interaction, str="message_erro_server_icon"),ephemeral = True)







# FUNÇÂO CONSULTAR BANNER DO SERVIDOR
async def bannerserver(self,interaction):
    #await interaction.response.defer()
    if await Res.print_brix(comando="bannerserver",interaction=interaction):
        return
    servidor = self.servidor
    banner_url = servidor.banner.url if servidor.banner else None
    if banner_url:
      resposta = discord.Embed(
        title=Res.trad(interaction=interaction,str="banner_guild"),
        description=Res.trad(interaction=interaction,str="banner_guild_description").format(servidor.name),
        colour=discord.Color.yellow()
      )
      resposta.set_image(url=banner_url)
      view = discord.ui.View()
      item = discord.ui.Button(style=discord.ButtonStyle.blurple, label=Res.trad(interaction=interaction,str="botão_abrir_navegador"), url=banner_url)
      view.add_item(item=item)
      await interaction.response.send_message(embed=resposta, view=view , delete_after = 60 )
    else:
      await interaction.response.send_message(Res.trad(interaction= interaction, str="message_erro_server_banner"),ephemeral = True)







# FUNÇÂO CONSULTAR SPLASH DO SERVIDOR
async def splashserver(self,interaction):
    #await interaction.response.defer()
    if await Res.print_brix(comando="splashserver",interaction=interaction):
        return
    servidor = self.servidor
    splash_id = servidor.splash
    if splash_id:
        splash_url = f"{splash_id}"
        resposta = discord.Embed(
            title=Res.trad(interaction=interaction,str="splash_guild"),
            description=Res.trad(interaction=interaction,str="splash_guild_description").format(servidor.name),
            colour=discord.Color.yellow()
        )
        resposta.set_image(url=splash_url)
        view = discord.ui.View()
        item = discord.ui.Button(style=discord.ButtonStyle.blurple, label=Res.trad(interaction=interaction,str="botão_abrir_navegador"), url=splash_url)
        view.add_item(item=item)
        await interaction.response.send_message(embed=resposta, view=view )
    else:
        await interaction.response.send_message(Res.trad(interaction= interaction, str="message_erro_server_splash"),ephemeral = True)











#INICIO DA CLASSE
class servers(commands.Cog):
  def __init__(self, client: commands.Bot) -> None:
    self.client = client
        





  @commands.Cog.listener()
  async def on_ready(self):
    print("🗄️  -  Modúlo Servers carregado.")
    await self.client.wait_until_ready() #Aguardando o bot ficar pronto
    #LIGANDO TASKS
    if not self.update_api_servidores.is_running():
      await asyncio.sleep(20)
      self.update_api_servidores.start()

    if not self.loop_bumps.is_running():
      await asyncio.sleep(20)
      self.loop_bumps.start()
    
    if not self.lembretes_topgg.is_running():
      await asyncio.sleep(20)
      self.lembretes_topgg.start()

 





  @commands.Cog.listener()
  async def on_message(self,message):
    #await asyncio.sleep(1)  # Delay para evitar spam
    # RETORNO DE AVISO DE BUMP
    if message.author.bot and message.embeds:
      if message.embeds and message.embeds[0].description and "Bump done!" in message.embeds[0].description and message.author and message.author.id == 302050872383242240:
        try:
          await message.add_reaction('<:BH_Braix_Me:1154340918757949501>')
        except:
          print(f"falha ao colocar reação em {message.guild.id}")
        msgenviada = await message.channel.send(Res.trad(guild=message.guild.id, str="message_bump_notification"))
        proximo_bump = datetime.now().replace(tzinfo=None) + timedelta(seconds=7200)
        item = { "bump.proximo_aviso": proximo_bump , "bump.canal_id": message.channel.id}
        BancoServidores.update_document(message.guild.id,item )
        await asyncio.sleep(15)
        await msgenviada.delete()
        



     # RETORNO DE VOTO do TOP.GG
    elif int(message.channel.id) == int(canal_vote_topgg):
      await message.add_reaction('<:BH_Braix_Me:1154340918757949501>')
      # Expressão regular para capturar a ID do usuário
      padrao = r"TOP\.GG - (\d+) - \d+"
      resultado = re.search(padrao, message.content)

      if resultado:
        user_id = resultado.group(1)  # Captura a ID do usuário
        usuario = await self.client.fetch_user(int(user_id)) # Procuro pelo usuario
        recompensa = 2000  # Defino a recompensa por cada voto
        dados_do_membro = BancoUsuarios.insert_document(usuario)  # Procuro pelo usuario no banco de dados
        total_votos = dados_do_membro.get('topgg-vote' , 0) + 1  # pego o total de votos é já acrescento + 1 
        BancoUsuarios.update_inc(usuario, {"topgg-vote": 1 , "braixencoin" : recompensa }) # Incremento o valor de moeda e do voto
        BancoFinanceiro.registrar_transacao(user_id=usuario.id,tipo="ganho",origem="Top.gg Voto",valor=recompensa,moeda="braixencoin",descricao=f"Recompensa por votar em mim no top.gg")


        try:
          resposta = discord.Embed(colour=discord.Color.yellow(),description=Res.trad(user=usuario, str='message_votetopgg_dm').format(total_votos, recompensa))
          resposta.set_thumbnail(url="https://cdn.discordapp.com/emojis/1154338634011521054.png")
          if dados_do_membro["dm-notification"] is True:
            await usuario.send( embed = resposta)
            contagem = True
        except: 
          print(f"falha ao enviar DM ao usuario {usuario.name} - {usuario.id}")
          contagem = False
          await message.add_reaction('❌')
        
        if total_votos % 20 == 0: # a cada 20 votos libera 5 dias de premium
          await liberarpremium(self,None,usuario,5,False)
          print(f"liberado premium para {usuario.name} - {usuario.id}")

        if contagem: # se eu acho o usuario dentro do discord entro na logica e mando mensagem a ele 
          proximo_lembrete = datetime.now().replace(tzinfo=None) + timedelta(hours=12)
          BancoUsuarios.update_document( usuario.id,{"topgg_lembrete": proximo_lembrete})

    return






  #Comando AutoPhox 
  @app_commands.command(name="vote", description="🦊⠂Vote no melhor Braixen bot.")
  async def votebrix(self, interaction: discord.Interaction):
    if await Res.print_brix(comando="votebrix",interaction=interaction):
      return
    resposta = discord.Embed(       colour=discord.Color.yellow(),      description=Res.trad(interaction=interaction,str="message_votetopgg")  )
    resposta.set_thumbnail(url=f"https://cdn.discordapp.com/emojis/1154338634011521054.png")
    view = discord.ui.View()
    item = discord.ui.Button(style=discord.ButtonStyle.blurple,label=Res.trad(interaction=interaction,str="botão_abrir_navegador"),url="https://top.gg/bot/983000989894336592/vote")
    view.add_item(item=item)
    await interaction.response.send_message(embed=resposta , view=view)







  @commands.Cog.listener()
  async def on_guild_join(self,guild):
    print(f'Fui adicionado ao servidor: {guild.name} (ID: {guild.id})')








  @commands.Cog.listener()
  async def on_guild_remove(self,guild):
    print(f'Fui removido do servidor: {guild.name} (ID: {guild.id})')







  # FUNÇÃO DE ATUALIZAÇÃO DO TOTAL DE SERVIDORES NO TOP.GG E BOTLIST
  @tasks.loop(hours=5)
  async def update_api_servidores(self):
    try:
      servidores = len(self.client.guilds)
      usuarios = len(self.client.users)

      async with aiohttp.ClientSession() as session:
        # DiscordBotList
        await session.post( f"https://discordbotlist.com/api/v1/bots/{self.client.user.id}/stats", headers={"Authorization": botlist_token}, json={"guilds": servidores, "users": usuarios} )

        # Top.gg
        await session.post( f"https://top.gg/api/bots/{self.client.user.id}/stats", headers={"Authorization": topgg_api}, json={"server_count": servidores} )

    except Exception as e:
      print(f"Falha ao atualizar algum lugar: {e}")












  #TASK DE LOOP DA VERIFICAÇÂO DE BUMPS
  @tasks.loop(minutes=15)
  async def loop_bumps(self):
    while True:
      agora = datetime.now().replace(tzinfo=None)
      # Pega todos os servidores com bump configurado
      servidores = BancoServidores.select_many_document({"bump": {"$exists": True}})
      if not servidores:
        await asyncio.sleep(300)  # sem nada? espera 5 min
        continue
      # Filtra os com campo válido e calcula o mais próximo
      proximos = []
      for s in servidores:
        try:
          ts = s["bump"].get("proximo_aviso")
          if ts and isinstance(ts, datetime):
            proximos.append((ts.timestamp(), s))
        except:
          continue
      if not proximos:
        await asyncio.sleep(300) #300
        continue
      # Encontra o menor timestamp
      proximos.sort()
      ts_proximo, _ = proximos[0]
      espera = max(ts_proximo - agora.timestamp(), 5)
      print(f"[bump] Próximo aviso em {espera:.0f}s")
      await asyncio.sleep(espera)
      # Verifica os que passaram do horário
      agora = datetime.now().replace(tzinfo=None).timestamp()
      for ts, servidor in proximos:
        if ts > agora:
          continue  # ainda não
        guild_id = servidor["_id"]
        canal_id = servidor["bump"].get("canal_id")
        msg_ping = servidor.get("bump-message")
        # Remove o campo do aviso
        BancoServidores.delete_field(guild_id, {"bump": 0})
        
        guild = self.client.get_guild(guild_id)
        if not guild or not canal_id:
          continue
        canal = guild.get_channel(canal_id)
        if not canal:
          continue
        if msg_ping:
          await canal.send(Res.trad(guild=guild_id, str="message_bump_lembrete_ping").format( msg_ping.replace(r"\q", "\n")))
        else:
          await canal.send(Res.trad(guild=guild_id, str="message_bump_lembrete_noping"))
        
        






  @tasks.loop(minutes=10)
  async def lembretes_topgg(self):
    await asyncio.sleep(5)  # Delay para evitar spam
    agora = datetime.now().replace(tzinfo=None)
    usuarios = BancoUsuarios.select_many_document({"topgg_lembrete": {"$lte": agora}})

    for u in usuarios:
      try:
        user = await self.client.fetch_user(u["_id"])
        resposta = discord.Embed(
          colour=discord.Color.yellow(),
          description=Res.trad(user=user, str='message_votetopgg_lembrete_dm')
        )
        resposta.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/8957/8957077.png")
        view = discord.ui.View()
        item = discord.ui.Button(
          style=discord.ButtonStyle.blurple,
          label=Res.trad(user=user, str="botão_abrir_navegador"),
          url="https://top.gg/bot/983000989894336592/vote"
        )
        view.add_item(item)
        await user.send(embed=resposta, view=view)
      except:
        print(f"[voto] Falha ao enviar lembrete para {u['_id']}")

        # Remove o campo pra evitar repetir
      BancoUsuarios.delete_field(u["_id"], {"topgg_lembrete": 0})






  
#GRUPO SERVIDOR 
  servidor=app_commands.Group(name="servidor",description="Comandos de servidores do bot.",allowed_installs=app_commands.AppInstallationType(guild=True,user=False),allowed_contexts=app_commands.AppCommandContext(guild=True, dm_channel=False, private_channel=False))

#COMANDO ICONE DE SERVIDOR
  @servidor.command(name="icone", description='🗄️⠂Exibe o ícone do servidor.')
  async def icone(self, interaction: discord.Interaction):
    self.servidor = interaction.guild
    await iconeserver(self,interaction)
   
#COMANDO BANNER DE SERVIDOR
  @servidor.command(name="banner", description='🗄️⠂Exibe o banner do servidor.')
  async def banner(self, interaction: discord.Interaction):
    self.servidor = interaction.guild
    await bannerserver(self,interaction)
        
#COMANDO SPLASH DE SERVIDOR
  @servidor.command(name="splash", description='🗄️⠂Exibe a splash do servidor.')
  async def splash(self, interaction: discord.Interaction):
    self.servidor = interaction.guild
    await splashserver(self,interaction)
   
#COMANDO INFORMAÇÂO DE SERVIDOR
  @servidor.command(name="info", description='🗄️⠂Exibe informações sobre o servidor.')
  @app_commands.describe(id="informe uma id de um servidor")
  async def infoservidor(self, interaction: discord.Interaction, id: str=None):
    #await interaction.response.defer()
    if await Res.print_brix(comando="infoservidor",interaction=interaction):
        return
    if id is None:
      servidor = interaction.guild
    else:
      servidor = self.client.get_guild(int(id))
      if servidor is None:
        await interaction.response.send_message(Res.trad(interaction= interaction, str="message_erro_server_notfound"),ephemeral=True , delete_after=30)
        return
    icone_url = servidor.icon.url if servidor.icon else None
    resposta = discord.Embed(
        title=Res.trad(interaction=interaction,str="servidor_info").format(servidor.name),
        description=servidor.description,
        colour=discord.Color.yellow()
    )

    if icone_url: resposta.set_thumbnail(url=icone_url)
    if servidor.members: resposta.add_field(name=Res.trad(interaction=interaction,str="servidor_usuario_name"), value=f"```Total: {servidor.member_count}\nPessoas: {sum(1 for member in servidor.members if not member.bot)}\nBots: {sum(1 for member in servidor.members if member.bot)}```")
    if servidor.channels:
      voz = sum(1 for canal in servidor.channels if isinstance(canal, discord.VoiceChannel))
      texto = sum(1 for canal in servidor.channels if isinstance(canal, discord.TextChannel))
      resposta.add_field(name=Res.trad(interaction=interaction,str="servidor_canais_name"), value=f"```Total: {voz+texto}\nTexto: {texto}\nVoz: {voz}```")

    if servidor.owner: resposta.add_field(name=Res.trad(interaction=interaction,str="servidor_owner_name"), value=servidor.owner.mention)
    if servidor.id: resposta.add_field(name="🆔 ⠂ID", value=f"```{servidor.id}```")                                      
    if servidor.emojis: resposta.add_field(name=Res.trad(interaction=interaction,str="servidor_emoji_name"), value=f"```Total: {len(servidor.emojis)}```")
    if servidor.created_at: resposta.add_field(name=Res.trad(interaction=interaction,str="servidor_criadoem_name"), value=f"**<t:{int(servidor.created_at.timestamp())}:d>-<t:{int(servidor.created_at.timestamp())}:R>**")

    await interaction.response.send_message(embed=resposta , view=BotoesBuscarServidor(client=self,interaction=interaction,menu=False,server=servidor))






async def setup(client:commands.Bot) -> None:
  await client.add_cog(servers(client))