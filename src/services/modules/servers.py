import discord,os, pytz ,asyncio,re,requests , aiohttp
from discord import ui
from discord.ext import commands, tasks
from discord import app_commands
from datetime import datetime, timedelta
from src.services.essential.respostas import Res
from src.services.connection.database import BancoServidores,BancoUsuarios,BancoLogs , BancoFinanceiro
from src.services.modules.premium import liberarpremium
from src.services.essential.diversos import Paginador_Global , container_media_button_url
from functools import partial
from dotenv import load_dotenv







load_dotenv()
botlist_token = os.getenv("botlist_token")
topgg_api = os.getenv("topgg_token")
canal_vote_topgg = os.getenv("canal_vote_topgg")




FUSOHORARIO = pytz.timezone('America/Sao_Paulo')




















# FUNÇÂO CONSULTAR ICONE DO SERVIDOR
async def iconeserver(self,interaction : discord.Interaction ,servidor):
    if await Res.print_brix(comando="iconeserver",interaction=interaction):
        return
    icone_url = servidor.icon.url if servidor.icon else None
    if icone_url:
      view = container_media_button_url(titulo=Res.trad(interaction=interaction,str="icone_guild"),descricao=Res.trad(interaction=interaction,str="icone_guild_description").format(servidor.name) ,buttonLABEL=Res.trad(interaction=interaction,str="botão_abrir_navegador"),buttonURL = icone_url, galeria = icone_url)
      await interaction.response.send_message(view=view, delete_after=60)
    else:
      await interaction.response.send_message(Res.trad(interaction= interaction, str="message_erro_server_icon"),ephemeral = True)


















# FUNÇÂO CONSULTAR BANNER DO SERVIDOR
async def bannerserver(self,interaction: discord.Interaction ,servidor):
    if await Res.print_brix(comando="bannerserver",interaction=interaction):
        return
    banner_url = servidor.banner.url if servidor.banner else None
    if banner_url:
      view = container_media_button_url(titulo=Res.trad(interaction=interaction,str="banner_guild"),descricao=Res.trad(interaction=interaction,str="banner_guild_description").format(servidor.name) ,buttonLABEL=Res.trad(interaction=interaction,str="botão_abrir_navegador"),buttonURL = banner_url, galeria = banner_url)
      await interaction.response.send_message( view=view , delete_after = 60 )
    else:
      await interaction.response.send_message(Res.trad(interaction= interaction, str="message_erro_server_banner"),ephemeral = True)




















# FUNÇÂO CONSULTAR SPLASH DO SERVIDOR
async def splashserver(self,interaction: discord.Interaction ,servidor):
    if await Res.print_brix(comando="splashserver",interaction=interaction):
        return
    splash_url = f"{servidor.splash}" if servidor.splash else None
    if splash_url:        
        view = container_media_button_url(titulo=Res.trad(interaction=interaction,str="splash_guild"),descricao=Res.trad(interaction=interaction,str="splash_guild_description").format(servidor.name) ,buttonLABEL=Res.trad(interaction=interaction,str="botão_abrir_navegador"),buttonURL = splash_url, galeria = splash_url)
        await interaction.response.send_message(view=view, delete_after = 60 )
    else:
        await interaction.response.send_message(Res.trad(interaction= interaction, str="message_erro_server_splash"),ephemeral = True)



























#INICIO DA CLASSE
class servers(commands.Cog):
  def __init__(self, client: commands.Bot) -> None:
    self.client = client
    # Cache para contar erros de cada registro: chave = ID do servidor, valor = contador
    self.tag_error_count =[]
        













  @commands.Cog.listener()
  async def on_bot_ready(self):
    print("💚  -  Modúlo Servers carregado.")
    #LIGANDO TASKS
    #await asyncio.sleep(240)
    if not self.update_api_servidores.is_running():
      print("🍕  -  Iniciando update de dados dos servidores em API's externas")
      self.update_api_servidores.start()

    if not self.loop_bumps.is_running():
      print("🍕  -  Iniciando Verificação de bumps nas comunidades")
      self.loop_bumps.start()
    
    if not self.lembretes_topgg.is_running():
      print("🍕  -  Iniciando Verificação de lembretes do top.gg")
      self.lembretes_topgg.start()
    
    if not self.verificar_tags.is_running():
      print("🍕  -  Iniciando verificação de tags nas comunidades")
      self.verificar_tags.start()

 



















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
        await message.channel.send(Res.trad(guild=message.guild.id, str="message_bump_notification") , delete_after = 20)
        proximo_bump = datetime.now().replace(tzinfo=None).astimezone(FUSOHORARIO) + timedelta(seconds=7200)
        item = { "bump.proximo_aviso": proximo_bump , "bump.canal_id": message.channel.id}
        BancoServidores.update_document(message.guild.id,item )
        
        



















     # RETORNO DE VOTO do TOP.GG
    elif int(message.channel.id) == int(canal_vote_topgg):
      await message.add_reaction('<:BH_Braix_Me:1154340918757949501>') 
      # Expressão regular para capturar a ID do usuário
      padrao = r"TOP\.GG - (\d+)"  #TOP.GG - <user> - <mentionuser> votou no Brix / <count> votos / <streak> sequencias!
      resultado = re.search(padrao, message.content)
      print(message.content)
      print(resultado)

      if resultado:
        user_id = resultado.group(1)  # Captura a ID do usuário
        usuario = await self.client.fetch_user(int(user_id)) # Procuro pelo usuario
        recompensa = 5000  # Defino a recompensa por cada voto
        dados_do_membro = BancoUsuarios.insert_document(usuario)  # Procuro pelo usuario no banco de dados
        total_votos = dados_do_membro.get('topgg-vote' , 0) + 1  # pego o total de votos é já acrescento + 1 
        BancoUsuarios.update_inc(usuario, {"topgg-vote": 1 , "braixencoin" : recompensa }) # Incremento o valor de moeda e do voto
        BancoFinanceiro.registrar_transacao(user_id=usuario.id,tipo="ganho",origem="Top.gg Voto",valor=recompensa,moeda="braixencoin",descricao=f"Recompensa por votar em mim no top.gg")
        contagem = False

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
          await liberarpremium(self,None,usuario,7,False)
          print(f"liberado premium para {usuario.name} - {usuario.id}")

        if contagem: # se eu acho o usuario dentro do discord entro na logica e mando mensagem a ele 
          proximo_lembrete = datetime.now().replace(tzinfo=None).astimezone(FUSOHORARIO) + timedelta(hours=12)
          BancoUsuarios.update_document( usuario.id,{"topgg_lembrete": proximo_lembrete})

    return























  #Comando VOTE TOP.GG 
  @app_commands.command(name="vote", description="🦊⠂Vote no melhor Braixen bot.")
  @app_commands.allowed_installs(guilds=True, users=True)
  @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
  async def votebrix(self, interaction: discord.Interaction):
    if await Res.print_brix(comando="votebrix",interaction=interaction):
      return
    view = container_media_button_url(descricao=Res.trad(interaction=interaction,str="message_votetopgg") , descricao_thumbnail= "https://cdn.discordapp.com/emojis/1154338634011521054.png" ,buttonLABEL=Res.trad(interaction=interaction,str="botão_abrir_navegador"),buttonURL = "https://brixbot.xyz/vote" )

    await interaction.response.send_message(view=view)

















  @commands.Cog.listener()
  async def on_guild_join(self, guild: discord.Guild):
    print(f'🍕🍕🍕 - Fui adicionado ao servidor: {guild.name} (ID: {guild.id})')
    BancoServidores.bot_in_guild(guild.id, True)
    BancoLogs.registrar_guild_evento(guild, tipo_entrada=True)

    # tenta achar o primeiro canal onde o bot pode mandar mensagem
    channel = None
    for c in guild.text_channels:
      if c.permissions_for(guild.me).send_messages:
        channel = c
        break

    if channel:
      try:
        await channel.send( Res.trad(guild=guild.id, str="message_bot_join_guild").format (guild.name) , delete_after = 120 , suppress_embeds = True)
      except Exception as e:
        print(f"❌ Erro ao enviar mensagem de boas-vindas em {guild.name}: {e}")



  


















  @commands.Cog.listener()
  async def on_guild_remove(self,guild):
    print(f'❌❌❌ - Fui removido do servidor: {guild.name} (ID: {guild.id})')
    BancoServidores.bot_in_guild(guild.id,False)
    BancoLogs.registrar_guild_evento(guild, tipo_entrada=False)




















  # FUNÇÃO DE ATUALIZAÇÃO DO TOTAL DE SERVIDORES NO TOP.GG E BOTLIST
  @tasks.loop(hours=1)
  async def update_api_servidores(self):
    await self.client.member_cache_ready_event.wait() 
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
      agora = datetime.now().replace(tzinfo=None).astimezone(FUSOHORARIO)
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
      print(f"⏰ - [bump] Próximo aviso em {espera:.0f}s")
      await asyncio.sleep(espera)
      # Verifica os que passaram do horário
      agora = datetime.now().replace(tzinfo=None).astimezone(FUSOHORARIO).timestamp()
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
    try:
      agora = datetime.now().replace(tzinfo=None).astimezone(FUSOHORARIO)
      usuarios = BancoUsuarios.select_many_document({"topgg_lembrete": {"$lte": agora}})

      for u in usuarios:
        await asyncio.sleep(5)  # Delay para evitar spam
        try:
          
          if u["dm-notification"] is True:
            user = await self.client.fetch_user(u["_id"])
            view = container_media_button_url(descricao= Res.trad(user=user, str='message_votetopgg_lembrete_dm') ,descricao_thumbnail= "https://brixbot.xyz/cdn/sino_notificacao.png" ,buttonLABEL=Res.trad(user=user, str="botão_abrir_navegador"),buttonURL = "https://brixbot.xyz/vote" )
            await user.send(view=view)
          else:
            print("🦊 - membro não recebe notificações via DM")
            
        except:
          print(f"[voto] Falha ao enviar lembrete para {u['_id']}")

          # Remove o campo pra evitar repetir
        BancoUsuarios.delete_field(u["_id"], {"topgg_lembrete": 0})
    except Exception as e:
      print(f"🔴 - LEMBRETE_TOP.GG ERROR: falha na tarefa pelo erro {e}, verificará mais tarde")





















  # ======================================================================
  # TASK DE VERIFICAÇÃO DE TAGS DE SERVIDOR
  @tasks.loop(minutes=2)  # roda a cada 2 min
  async def verificar_tags(self):
    try:
      await asyncio.sleep(300) #300
      filtro = {"tag_server": {"$exists": True}}
      servidores = BancoServidores.select_many_document(filtro)

      for servidor in servidores:
        
        guild_id = servidor["_id"]
        cargo_id = servidor["tag_server"]["cargo"]
        notificar = servidor["tag_server"]["aviso_dm"]
        owner_dm_aviso = False

        guild = self.client.get_guild(guild_id)
        if not guild:
          continue

        cargo = guild.get_role(cargo_id)
        if not cargo:
          # incrementa contador de erros
            contador = self.tag_error_count.get(guild_id, 0) + 1
            self.tag_error_count[guild_id] = contador

            print(f"Cargo {cargo_id} não encontrado em {guild.name}. Erro {contador}/40")

            # se passar de 40, remove do banco e reseta contador
            if contador >= 40:
                print(f"Removendo configuração de tag do servidor {guild.name} ({guild_id}) após 40 falhas.")
                BancoServidores.delete_field(guild_id, {"tag_server": servidor["tag_server"]})
                del self.tag_error_count[guild_id]

            continue  # pula para o próximo servidor

        # se achou o cargo, reseta contador de erro (se existir)
        if guild_id in self.tag_error_count:
            del self.tag_error_count[guild_id]

        # ================================
        # ETAPA 1: Adicionar cargo a quem tem a tag
        # ================================
        for member in guild.members:
          if ( member.primary_guild and member.primary_guild.id == guild.id and member.primary_guild.identity_enabled ):
            if cargo not in member.roles:
              try:
                await member.add_roles(cargo, reason="Usa a tag do servidor")
                await asyncio.sleep(0.2) #Evitar abuso de api do discord
                print(f"🦊 {member} recebeu o cargo {cargo.name} em {guild.name} ({guild_id})")

                if notificar:
                  dados_do_membro = BancoUsuarios.insert_document(member)
                  if dados_do_membro["dm-notification"] is True:
                    try:
                      await member.send(view= container_media_button_url(descricao= Res.trad(user=member, str='servidor_tag_ativado_dm_aviso').format(member.mention,cargo.name, guild.name)  ,descricao_thumbnail= "https://brixbot.xyz/cdn/sino_notificacao.png" ))
                    except:
                      print(f"📪 Falha ao enviar DM para {member}")
              except Exception as e:
                print(f"❌ Erro ao adicionar cargo em {member} em {guild_id}: {e}")
                try:
                  if not owner_dm_aviso:
                    owner_dm_aviso = True
                    aviso_expira_em = servidor.get("owner_aviso",None)
                    agora = datetime.now()
                    # Só avisa se não houver aviso válido
                    if not aviso_expira_em or agora >= aviso_expira_em:
                        await guild.owner.send( Res.trad(user=guild.owner, str='servidor_tag_erro_owner_aviso').format(guild.name) )
                        print(f"🦊 - Dono do servidor {guild.name} avisado do problema de permissão")
                        # Atualiza no banco a data de expiração do aviso (15 dias à frente)
                        item = { "owner_aviso": agora + timedelta(days=15) }
                        BancoServidores.update_document(guild_id, item)

                except Exception as aviso_erro:
                    print(f"📪 Falha ao avisar o dono do servidor: {aviso_erro}")

        # ================================
        # ETAPA 2: Remover cargo de quem deixou de usar a tag
        # ================================
        for member in guild.members:
          if cargo in member.roles:
            if not ( member.primary_guild and member.primary_guild.id == guild.id and member.primary_guild.identity_enabled ):
              try:
                await member.remove_roles(cargo, reason="Parou de usar a tag do servidor")
                await asyncio.sleep(0.2) #Evitar abuso de api do discord
                print(f"😿 {member} perdeu o cargo {cargo.name} em {guild.name} ({guild_id})")

                if notificar:
                  dados_do_membro = BancoUsuarios.insert_document(member)
                  if dados_do_membro["dm-notification"] is True:
                    try:
                      await member.send(view= container_media_button_url(descricao= Res.trad(user=member, str='servidor_tag_desativado_dm_aviso').format(cargo.name, guild.name)  ,descricao_thumbnail= "https://brixbot.xyz/cdn/sino_notificacao.png" ))
                    except:
                      print(f"📪 Falha ao enviar DM para {member}")
              except Exception as e:
                print(f"❌ Erro ao remover cargo de {member} em {guild_id}: {e}")
                try:
                  if not owner_dm_aviso:
                    owner_dm_aviso = True
                    aviso_expira_em = servidor.get("owner_aviso",None)
                    agora = datetime.now()
                    # Só avisa se não houver aviso válido
                    if not aviso_expira_em or agora >= aviso_expira_em:
                      await guild.owner.send( Res.trad(user=guild.owner, str='servidor_tag_erro_owner_aviso').format(guild.name) )
                      print(f"🦊 - Dono do servidor {guild.name} avisado do problema de permissão")
                      # Atualiza no banco a data de expiração do aviso (15 dias à frente)
                      item = { "owner_aviso": agora + timedelta(days=15) }
                      BancoServidores.update_document(guild_id, item)

                except Exception as aviso_erro:
                    print(f"📪 Falha ao avisar o dono do servidor: {aviso_erro}")


    except Exception as e:
      print(f"🔴 - erro na verificação de tags, tentando mais tarde\n{e}")




















  
#GRUPO SERVIDOR 
  servidor=app_commands.Group(name="servidor",description="Comandos de servidores do bot.",allowed_installs=app_commands.AppInstallationType(guild=True,user=False),allowed_contexts=app_commands.AppCommandContext(guild=True, dm_channel=False, private_channel=False))










#COMANDO ICONE DE SERVIDOR
  @servidor.command(name="icone", description='🗄️⠂Exibe o ícone do servidor.')
  async def icone(self, interaction: discord.Interaction):
    await iconeserver(self,interaction , interaction.guild)
   





















#COMANDO BANNER DE SERVIDOR
  @servidor.command(name="banner", description='🗄️⠂Exibe o banner do servidor.')
  async def banner(self, interaction: discord.Interaction):
    await bannerserver(self,interaction,interaction.guild)
        























#COMANDO SPLASH DE SERVIDOR
  @servidor.command(name="splash", description='🗄️⠂Exibe a splash do servidor.')
  async def splash(self, interaction: discord.Interaction):
    await splashserver(self,interaction , interaction.guild)
   


























#COMANDO INFORMAÇÂO DE SERVIDOR
  @servidor.command(name="info", description='🗄️⠂Exibe informações sobre o servidor.')
  @app_commands.describe(id="informe uma id de um servidor")
  async def infoservidor(self, interaction: discord.Interaction, id: str=None):
    if await Res.print_brix(comando="infoservidor",interaction=interaction):
        return
    if id is None:
      servidor = interaction.guild
    else:
      servidor = self.client.get_guild(int(id))
      if servidor is None:
        await interaction.response.send_message(Res.trad(interaction= interaction, str="message_erro_server_notfound"),ephemeral=True , delete_after=30)
        return

    await interaction.response.defer()
    view = ui.LayoutView()
    container = ui.Container()
    container.accent_color = discord.Color.yellow()

    # SE BANNER EXISTE NA COMUNIDADE
    if servidor.banner:
      galery = ui.MediaGallery( )
      galery.add_item(media=servidor.banner.url)
      container.add_item(galery)
    else:
      container.add_item(ui.TextDisplay( Res.trad(interaction=interaction,str="message_erro_server_banner") ))
    container.add_item(ui.Separator())

    # SE A COMUNIDADE TEM ICONE
    if servidor.icon:
      icone_url = ui.Thumbnail(servidor.icon.url)
      container.add_item(ui.Section(ui.TextDisplay(f"# {Res.trad(interaction=interaction,str='servidor_info').format(servidor.name)}") , accessory = icone_url))
    else:
      container.add_item(ui.TextDisplay(f"# {Res.trad(interaction=interaction,str='servidor_info').format(servidor.name)}"))
    
    # SE TEM DESCRIÇÃO
    if servidor.description: container.add_item(ui.TextDisplay(servidor.description))
    container.add_item(ui.Separator())
    container.add_item(ui.TextDisplay( Res.trad(interaction=interaction,str='servidor_usuario_name_total').format(servidor.member_count) ))
    container.add_item(ui.TextDisplay( Res.trad(interaction=interaction,str='servidor_usuario_name').format(sum(1 for member in servidor.members if not member.bot) , sum(1 for member in servidor.members if member.bot)) ))
    container.add_item(ui.Separator(visible=False))
    
    # PARTE DOS CANAIS
    if servidor.channels:
      voz = sum(1 for canal in servidor.channels if isinstance(canal, discord.VoiceChannel))
      texto = sum(1 for canal in servidor.channels if isinstance(canal, discord.TextChannel))
      container.add_item(ui.TextDisplay( Res.trad(interaction=interaction,str='servidor_canais_name_total').format(voz+texto)  ))
      container.add_item(ui.TextDisplay(Res.trad(interaction=interaction,str='servidor_canais_name').format(texto, voz) ))
      container.add_item(ui.Separator())
    container.add_item(ui.TextDisplay(Res.trad(interaction=interaction,str="servidor_owner_name").format(servidor.owner.mention)))
    container.add_item(ui.TextDisplay( f"🆔 ⠂ID: **{servidor.id}**" ))
    container.add_item(ui.TextDisplay( Res.trad(interaction=interaction,str="servidor_emoji_name").format( len(servidor.emojis) ) ))
    container.add_item(ui.TextDisplay( Res.trad(interaction=interaction,str="servidor_figurinha_name").format( len(servidor.stickers) ) ))
    container.add_item(ui.TextDisplay( f"{Res.trad(interaction=interaction,str='servidor_criadoem_name')}: <t:{int(servidor.created_at.timestamp())}:d>  **-**  <t:{int(servidor.created_at.timestamp())}:R>"  ))
    # URL ELEGANTE DA COMUNIDADE SE TIVER
    if servidor.vanity_url : container.add_item(ui.TextDisplay( f"🔗 ⠂URL: **discord.gg/{servidor.vanity_url_code}**"  ))

    # CARGO E ASSINANTES PREMIUM BOOSTER SE TIVER
    if servidor.premium_subscribers:
      container.add_item(ui.Separator())
      container.add_item(ui.TextDisplay( Res.trad(interaction=interaction,str='servidor_premium_name').format( servidor.premium_subscriber_role.name , len( servidor.premium_subscribers) )  ))
  
    #Botões
    botão_icone = ui.Button(label=Res.trad(interaction=interaction,str="botão_ver_icone"),style=discord.ButtonStyle.blurple,emoji="🎨")
    botão_icone.callback = partial(iconeserver,self, servidor = servidor)

    botão_banner = ui.Button(label=Res.trad(interaction=interaction,str="botão_ver_banner"),style=discord.ButtonStyle.blurple,emoji="🖼️")
    botão_banner.callback = partial(bannerserver,self, servidor = servidor)

    botão_plash = ui.Button(label=Res.trad(interaction=interaction,str="botão_ver_splash"),style=discord.ButtonStyle.blurple,emoji="🎪")
    botão_plash.callback = partial(splashserver,self, servidor = servidor)
    
    botões = ui.ActionRow( botão_icone , botão_banner , botão_plash )

    container.add_item(ui.Separator(spacing=discord.SeparatorSpacing.small))
    container.add_item( botões )

    view.add_item(container)
    await interaction.followup.send(view=view , allowed_mentions = discord.AllowedMentions(users=False , roles = False))


    





















  servidortag=app_commands.Group(name="tag",description="Comandos de tag do servidor do bot.", parent=servidor)



#COMANDO DE AJUDA DO SISTEMA DE TAG DO SERVIDOR 
  @servidortag.command(name="ajuda", description='🗄️⠂Exibe informações do sistema de tag do servidor.')
  async def servidor_tag_ajuda (self, interaction: discord.Interaction):
    resposta = discord.Embed( 
      colour=discord.Color.yellow(),
      description=Res.trad(interaction=interaction,str="servidor_tag_ajuda")
    )
    await interaction.response.send_message(embed=resposta)
  




















  #COMANDO DE ATIVAR A ENTREGA DE CARGOS DO SISTEMA DE TAG DO SERVIDOR 
  @servidortag.command(name="ativar", description='🗄️⠂Ative a entrega de cargos para membros que usam a tag do seu servidor.')
  @app_commands.describe(  cargo="qual cargo deseja adicionar ao membro?"  ,  notificar="Notificar usuário em DM?"  )
  async def servidor_tag_ativar (self, interaction: discord.Interaction, cargo : discord.Role, notificar : bool):
    if await Res.print_brix(comando="servidor_tag_ativar", interaction=interaction, condicao=f"{cargo.name}"):
      return
    try:
      if interaction.guild is None:
        await interaction.response.send_message(Res.trad(interaction=interaction, str="message_erro_onlyservers"), delete_after=20, ephemeral=True)
        return
      # Verificando se o usuário tem permissão
      if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message(Res.trad(interaction=interaction, str='message_erro_permissao_user'), delete_after=20, ephemeral=True)
        return
      
      me = interaction.guild.get_member(interaction.client.user.id)
      if not me or not me.guild_permissions.administrator:
        await interaction.response.send_message(Res.trad(interaction=interaction, str='message_erro_permissao'))
        return
      
      await interaction.response.defer()
      item = { "tag_server.cargo": cargo.id , "tag_server.aviso_dm": notificar}
      BancoServidores.update_document(interaction.guild.id, item)
      await interaction.followup.send(Res.trad(interaction=interaction, str="servidor_tag_ativado").format(cargo.mention, "<a:Brix_Check:1371215835653210182>" if notificar else "<a:Brix_Negative:1371215873637093466>"))
    except Exception as e:
      await Res.erro_brix_embed(interaction=interaction, str="message_erro_permissao", e=e,comando="servidor_tag_ativar")





















  #COMANDO DE DESATIVAR A ENTREGA DE CARGOS DO SISTEMA DE TAG DO SERVIDOR 
  @servidortag.command(name="desativar", description='🗄️⠂desative a entrega de cargos para membros que usam a tag do seu servidor.')
  async def servidor_tag_desativar (self, interaction: discord.Interaction):
    if await Res.print_brix(comando="servidor_tag_desativar", interaction=interaction):
      return
    try:
      if interaction.guild is None:
        await interaction.response.send_message(Res.trad(interaction=interaction, str="message_erro_onlyservers"), delete_after=20, ephemeral=True)
        return
      # Verificando se o usuário tem permissão
      if not interaction.user.guild_permissions.manage_roles:
          await interaction.response.send_message(Res.trad(interaction=interaction, str='message_erro_permissao_user'), delete_after=20, ephemeral=True)
          return
      
      await interaction.response.defer()
      item = {"tag_server": interaction.channel.id}
      BancoServidores.delete_field(interaction.guild.id, item)
      await interaction.followup.send(Res.trad(interaction=interaction, str="servidor_tag_desativado"))
    except Exception as e:
      await Res.erro_brix_embed(interaction=interaction, str="message_erro_permissao", e=e,comando="servidor_tag_desativar")
























  #COMANDO DE LISTAR TODOS OS MEMBROS QUE USAM A TAG DO SERVIDOR 
  @servidortag.command(name="listar", description='🗄️⠂Veja todos os membros que usam a tag do seu servidor.')
  async def servidor_tag_listar (self, interaction: discord.Interaction):
    if await Res.print_brix(comando="servidor_tag_listar",interaction=interaction):
      return
    try:
      if interaction.guild is None:
        await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyservers"),delete_after=10,ephemeral=True)
        return
      await interaction.response.defer()

      lista = []
      count_mesma_tag = 0
      count_outras_tags = 0

      # percorre todos os membros e pega quem tem a tag do servidor habilitada
      for member in interaction.guild.members:
        if member.primary_guild and member.primary_guild.identity_enabled:
          if member.primary_guild.id == interaction.guild.id:
            # tag desse servidor
            tag_nome = member.primary_guild.tag
            linha = f"{count_mesma_tag+1} - {member.mention} - ID: `{member.id}`"
            lista.append(linha)
            count_mesma_tag += 1
          else:
            # tag de outro servidor
            count_outras_tags += 1
      if not lista:
          return await interaction.edit_original_response( content= Res.trad(interaction= interaction, str='servidor_tag_lista_sem_membros'))
      
      total_membros = len(interaction.guild.members)
      # calcula porcentagens
      perc_mesma = (count_mesma_tag / total_membros * 100) if total_membros > 0 else 0
      perc_outras = (count_outras_tags / total_membros * 100) if total_membros > 0 else 0

      
      descrição=Res.trad(interaction= interaction, str='servidor_tag_lista_membros_title').format(count_mesma_tag,perc_mesma,count_outras_tags,perc_outras,total_membros, tag_nome)
      blocos = [lista[i:i + 10] for i in range(0, len(lista), 10)] 
      await Paginador_Global(self, interaction, blocos, pagina=0, originaluser=interaction.user,descrição=descrição, thumbnail_url=interaction.guild.icon.url if interaction.guild.icon else None)

    except Exception as e:
      await Res.erro_brix_embed(interaction=interaction, str="message_erro_permissao", e=e,comando="servidor_tag_listar")






















async def setup(client:commands.Bot) -> None:
  await client.add_cog(servers(client))