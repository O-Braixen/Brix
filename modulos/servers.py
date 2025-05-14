import discord,os,random,asyncio,re,requests
from discord.ext import commands, tasks
from discord import app_commands
from datetime import datetime
from modulos.essential.respostas import Res
from modulos.connection.database import BancoServidores,BancoUsuarios,BancoLoja
from modulos.premium import liberarpremium
from modulos.web.webserver import atualizar_status_cache, atualizar_loja_cache
from dotenv import load_dotenv


load_dotenv()
discoverd_api = os.getenv("discorverd_token")
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
    if not self.update_api_servidores.is_running():
      self.update_api_servidores.start()

 





  @commands.Cog.listener()
  async def on_message(self,message):
    await asyncio.sleep(1)  # Delay para evitar spam
    # RETORNO DE AVISO DE BUMP
    if message.author.bot and message.embeds:
      if message.embeds and message.embeds[0].description and "Bump done!" in message.embeds[0].description and message.author and message.author.id == 302050872383242240:
          await message.add_reaction('<:BH_Braix_Me:1154340918757949501>')
          msgenviada = await message.channel.send(Res.trad(guild=message.guild.id, str="message_bump_notification"))
          await asyncio.sleep(15)
          await msgenviada.delete()
          await asyncio.sleep(7190)
          print(f"mandando lembrete de bump para {message.guild.name}!")
          consulta = BancoServidores.insert_document(message.guild.id)
          if "bump-message" in consulta:
            mensagem = consulta['bump-message'].replace(r"\q", "\n")
            await message.channel.send(Res.trad(guild=message.guild.id, str="message_bump_lembrete_ping").format(mensagem))
          else: 
            await message.channel.send(Res.trad(guild=message.guild.id, str="message_bump_lembrete_noping"))


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

        try:
          resposta = discord.Embed(colour=discord.Color.yellow(),description=Res.trad(user=usuario, str='message_votetopgg_dm').format(total_votos, recompensa))
          resposta.set_thumbnail(url="https://cdn.discordapp.com/emojis/1154338634011521054.png")
          await usuario.send( embed = resposta)
          contagem = True
        except: 
          print(f"falha ao enviar DM ao usuario {usuario.name} - {usuario.id}")
          contagem = False
          await message.add_reaction('❌')
        
        if total_votos % 20 == 0: # a cada 20 votos libera 5 dias de premium
          await liberarpremium(self,None,usuario,7,False)
          print(f"liberado premium para {usuario.name} - {usuario.id}")

        if contagem: # se eu acho o usuario dentro do discord entro na logica e mando mensagem a ele 
          await asyncio.sleep(43200) # tempo de espera de aviso voto ( 43200 )
          resposta = discord.Embed(colour=discord.Color.yellow(),description=Res.trad(user=usuario, str='message_votetopgg_lembrete_dm'))
          resposta.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/8957/8957077.png")
          view = discord.ui.View()
          item = discord.ui.Button(style=discord.ButtonStyle.blurple,label=Res.trad(user=usuario,str="botão_abrir_navegador"),url="https://top.gg/bot/983000989894336592/vote")
          view.add_item(item=item)
          await usuario.send( embed = resposta , view=view)

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







  #FUNÇÂO DE ATUALIZAÇÂO DO TOTAL DE SERVIDORES NO TOP.GG
  @tasks.loop(minutes=10) # hours=5
  async def update_api_servidores(self): 
    try:
      atualizar_status_cache()
      filtro = {"braixencoin": {"$exists": True}}
      dados = BancoLoja.select_many_document(filtro)
      atualizar_loja_cache(dados)
      servidores = len(self.client.guilds)

      requests.post(f"https://api.discoverd.net/bots/status",headers={"Authorization": discoverd_api},json={"servers": servidores})
      requests.post(f"https://top.gg/api/bots/{self.client.user.id}/stats",headers={"Authorization": topgg_api},json={"server_count": servidores})
    except:
      print("falha ao atualizar algum lugar")


  
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

    if servidor.owner: resposta.add_field(name=Res.trad(interaction=interaction,str="servidor_owner_name"), value=f"{servidor.owner.mention}\n```{servidor.owner.id}```")
    if servidor.id: resposta.add_field(name=":id: ID", value=f"```{servidor.id}```")
    if servidor.created_at: resposta.add_field(name=Res.trad(interaction=interaction,str="servidor_criadoem_name"), value=f"```{servidor.created_at.strftime(Res.trad(interaction=interaction, str='padrao_data')+' - %H:%M:%S')}```")
    if servidor.emojis: resposta.add_field(name=Res.trad(interaction=interaction,str="servidor_emoji_name"), value=f"```Total: {len(servidor.emojis)}```")

    await interaction.response.send_message(embed=resposta , view=BotoesBuscarServidor(client=self,interaction=interaction,menu=False,server=servidor))






async def setup(client:commands.Bot) -> None:
  await client.add_cog(servers(client))