import discord,os,random,asyncio,re,aiohttp , zipfile, io
from discord.ext import commands
from discord import app_commands,partial_emoji
from src.services.essential.respostas import Res
     
afklist = []


#--------------------------FUNCÔES AQUII----------------------------------

#FUNÇÂO USUARIO INFO
async def buscaruser( self, interaction,membro,menu):
  if await Res.print_brix(comando="buscaruser",interaction=interaction):
     return
  if membro == None:
    membro = interaction.user
  resposta = discord.Embed(
    colour=discord.Color.yellow(),
    description=Res.trad(interaction=interaction,str='cargo_title').format(membro.name)
  )
  avatar_url = membro.avatar.url if membro.avatar else None
  resposta.set_thumbnail(url=avatar_url)
  resposta.add_field(name=Res.trad(interaction=interaction,str='nome'), value=f"```{membro.name}```", inline=True)
  resposta.add_field(name="🆔 ⠂ID", value=f"```{membro.id}```", inline=True)
  resposta.add_field(name=Res.trad(interaction=interaction,str='menção'), value=membro.mention, inline=True)
  resposta.add_field(name=Res.trad(interaction=interaction,str='usuario_join'), value=f"**<t:{int(membro.created_at.timestamp())}:d>-<t:{int(membro.created_at.timestamp())}:R>**", inline=True)
  try:
    resposta.add_field(name=Res.trad(interaction=interaction,str='usuario_join_guild'), value=f"**<t:{int(membro.joined_at.timestamp())}:d>-<t:{int(membro.joined_at.timestamp())}:R>**", inline=True)
    if len(membro.roles) == 1:
      resposta.add_field(name=Res.trad(interaction=interaction,str='usuario_cargos').format(len(membro.roles) - 1), value=Res.trad(interaction=interaction,str='usuario_not_cargos'), inline=False)
    else:
      roles_list = [role.mention for role in membro.roles if role.name != '@everyone']
      if len(roles_list) > 5:
          roles_list = roles_list[:5]  # Limita a lista aos primeiros 5 cargos
          roles_list.append("...")  # Adiciona "..." para indicar que há mais cargos
          resposta.add_field(name=Res.trad(interaction=interaction,str='usuario_cargos').format(len(membro.roles) - 1), value='\n'.join(roles_list), inline=False)
      else:resposta.add_field(name=Res.trad(interaction=interaction,str='usuario_cargos').format(len(membro.roles) - 1), value='\n'.join([role.mention for role in membro.roles if role.name != '@everyone']), inline=False)
  except:
    resposta.add_field(name=Res.trad(interaction=interaction,str='usuario_on_guild'), value=Res.trad(interaction=interaction,str='usuario_not_guild'), inline=True)
  await interaction.response.send_message(embed=resposta,view=BotoesBuscarUser(client=self,interaction=interaction,user=membro,menu=menu),ephemeral = menu)
  #await interaction.followup.send(embed=resposta,view=BotoesBuscarUser(client=self,interaction=interaction,user=membro,menu=menu))








          #BUSCA BANNER DO USUARIO
async def buscarbanner(self, interaction,membro,menu):
   if await Res.print_brix(comando="buscarbanner",interaction=interaction):
        return
   if membro == None:
        membro = interaction.user
   fetch_user = await self.client.fetch_user(membro.id)
   if fetch_user.banner:
      resposta = discord.Embed(
        title=Res.trad(interaction=interaction, str="banner_global"),
        description=Res.trad(interaction=interaction, str="banner_global_description").format(membro.name),
        colour=discord.Color.yellow()
      )
      resposta.set_image(url=f"{fetch_user.banner.url}")
      await interaction.response.send_message(embed = resposta , view = ViewBannerServidor(interaction=interaction,user=membro, fetch_user = fetch_user ,menu=menu) , ephemeral = menu )
   else:await interaction.response.send_message(Res.trad(interaction= interaction, str="message_erro_banner").format(fetch_user.mention),delete_after=10, ephemeral=True)






      #FUNÇÃO BUSCAR AVATAR DE USUARIO
async def buscaravatar(interaction,membro,menu):
  #await interaction.response.defer(ephemeral = menu)
  if await Res.print_brix(comando="buscaravatar",interaction=interaction):
        return
  if membro == None:
    membro = interaction.user
  if membro.avatar:
    resposta = discord.Embed(
      title=Res.trad(interaction=interaction, str="avatar_global"),
      description=Res.trad(interaction=interaction, str="avatar_global_description").format(membro.name),
      colour=discord.Color.yellow()
    )
    resposta.set_image(url=f"{membro.avatar}")
    await interaction.response.send_message(embed=resposta,view= ViewAvatarServidor(interaction=interaction,user=membro,menu=menu),ephemeral = menu )
  else:await interaction.response.send_message(Res.trad(interaction=interaction, str="message_erro_avatar").format(membro.mention,"Global"),ephemeral = menu , delete_after=20)









#          BOTÂO BUSCAR USUARIO ----------- ESSE É A VIEW QUE È CHAMADA PELO buscaruser
class BotoesBuscarUser(discord.ui.View):
    def __init__(self,interaction,user,menu, client):
        super().__init__(timeout=300)
        self.user = user
        self.menu = menu
        self.client = client
        self.interaction = interaction
        self.value=None

        self.avatar = discord.ui.Button(label=Res.trad(interaction=self.interaction,str="botão_ver_avatar"),style=discord.ButtonStyle.blurple,emoji="🎨")
        self.add_item(item=self.avatar)
        self.avatar.callback = self.botaoavatar

        self.banner = discord.ui.Button(label=Res.trad(interaction=self.interaction,str="botão_ver_banner"),style=discord.ButtonStyle.blurple,emoji="🖼️")
        self.add_item(item=self.banner)
        self.banner.callback = self.botaobanner

        self.cargo = discord.ui.Button(label=Res.trad(interaction=self.interaction,str="botão_ver_cargo"),style=discord.ButtonStyle.blurple,emoji="🔮")
        self.add_item(item=self.cargo)
        self.cargo.callback = self.botaocargos

    def __call__(self):
        return self

    #@discord.ui.button(label="Ver Avatar",style=discord.ButtonStyle.blurple,emoji="🎨")
    async def botaoavatar(self,interaction: discord.Interaction):
      self.value = True
      await buscaravatar(interaction,self.user,self.menu)
    
    #@discord.ui.button(label="Ver Banner",style=discord.ButtonStyle.blurple,emoji="🖼️")
    async def botaobanner(self,interaction: discord.Interaction):
      self.value = True
      await buscarbanner(self.client,interaction,self.user,self.menu)

   #@discord.ui.button(label="Ver Cargos",style=discord.ButtonStyle.blurple,emoji="🔮")
    async def botaocargos(self,interaction: discord.Interaction):
      if await Res.print_brix(comando="botaocargos",interaction=interaction):
        return
      self.value = True
      membro = self.user
      resposta = discord.Embed(
        colour=discord.Color.yellow(),
        description=Res.trad(interaction=interaction,str='cargo_title').format(membro.name)
      )
      #if not interaction.guild.get_member(membro.id):
        #resposta.add_field(name=Res.trad(interaction=interaction,str='usuario_not_cargos'),value=Res.trad(interaction=interaction,str='usuario_not_guild'), inline=False)
      #else:
      try:
        if len(membro.roles) == 1:
            resposta.add_field(name=Res.trad(interaction=interaction,str='usuario_cargos').format(len(membro.roles) - 1), value=Res.trad(interaction=interaction,str='usuario_not_cargos'), inline=False)
        else:
            roles_list = [role.mention for role in membro.roles if role.name != '@everyone']
            for i in range(0, len(roles_list), 20):
              field_value = '\n'.join(roles_list[i:i+20])
              resposta.add_field(name=Res.trad(interaction=interaction,str='usuario_cargos').format(i+1,min(i+20, len(roles_list))), value=field_value, inline=True)
      except:
        resposta.add_field(name=Res.trad(interaction=interaction,str='usuario_not_cargos'),value=Res.trad(interaction=interaction,str='usuario_not_guild'), inline=False)
      await interaction.response.send_message(embed=resposta,ephemeral=self.menu)

















        #BOTÃO EXIBIR O AVATAR DO USUARIO LOCAL NA COMUNIDADE
class  ViewAvatarServidor(discord.ui.View):
    def __init__(self,interaction,user,menu):
        super().__init__(timeout=300)
        self.user = user
        self.menu = menu
        self.interaction = interaction
        self.value=None
        item = discord.ui.Button(style=discord.ButtonStyle.blurple,label=Res.trad(interaction=self.interaction,str="botão_abrir_navegador"),url=f"{user.avatar.url}")
        self.add_item(item=item)

    @discord.ui.button(label="Avatar Local",style=discord.ButtonStyle.blurple,emoji="🎨")
    async def avatarlocalservidor(self,interaction: discord.Interaction, button: discord.ui.Button):
      membro = self.user
      self.value = True
      self.stop()
      if await Res.print_brix(comando="Botão Avatar Local",interaction=interaction):
        return
      try:
        resposta = discord.Embed(
          title=Res.trad(interaction=interaction, str="avatar_local"),
          description=Res.trad(interaction=interaction, str="avatar_local_description").format(membro.name,membro.guild.name),
          colour=discord.Color.yellow()
        )
        resposta.set_image(url=f"{membro.guild_avatar}")
        view = discord.ui.View()
        item = discord.ui.Button(style=discord.ButtonStyle.blurple,label=Res.trad(interaction=interaction,str="botão_abrir_navegador"),url=f"{membro.guild_avatar.url}")
        view.add_item(item=item)
        await interaction.response.send_message(embed=resposta,view=view,ephemeral=self.menu)
      except:await interaction.response.send_message(Res.trad(interaction= interaction, str="message_erro_avatar").format(membro.mention,"Local"),delete_after=5, ephemeral=True)














        #BOTÃO EXIBIR O BANNER DO USUARIO LOCAL NA COMUNIDADE
class  ViewBannerServidor(discord.ui.View):
    def __init__(self,interaction,user,menu , fetch_user):
        super().__init__(timeout=300)
        self.user = user
        self.fetch_user = fetch_user
        self.menu = menu
        self.interaction = interaction
        self.value=None
        item = discord.ui.Button(style=discord.ButtonStyle.blurple,label=Res.trad(interaction=self.interaction,str="botão_abrir_navegador"),url=f"{fetch_user.banner.url}")
        self.add_item(item=item)

    @discord.ui.button(label="Banner Local",style=discord.ButtonStyle.blurple,emoji="🎨")
    async def bannerlocalservidor(self,interaction: discord.Interaction, button: discord.ui.Button):
      membro = self.user
      self.value = True
      self.stop()
      if await Res.print_brix(comando="Botão Banner Local",interaction=interaction):
        return
      try:
        resposta = discord.Embed(
          title=Res.trad(interaction=interaction, str="banner_local"),
          description=Res.trad(interaction=interaction, str="banner_local_description").format(membro.name,membro.guild.name),
          colour=discord.Color.yellow()
        )
        resposta.set_image(url=f"{membro.guild_banner}")
        view = discord.ui.View()
        item = discord.ui.Button(style=discord.ButtonStyle.blurple,label=Res.trad(interaction=interaction,str="botão_abrir_navegador"),url=f"{membro.guild_banner.url}")
        view.add_item(item=item)
        await interaction.response.send_message(embed=resposta,view=view,ephemeral=self.menu)
      except:await interaction.response.send_message(Res.trad(interaction= interaction, str="message_erro_avatar").format(membro.mention,"Local"),delete_after=5, ephemeral=True)



















#INICIO DA CLASSE
class misc(commands.Cog):
  def __init__(self, client: commands.Bot) -> None:
        self.client = client
        #Carrega os menu e adiciona eles
        self.menu_useravatar = app_commands.ContextMenu(name="Usuario Avatar",callback=self.useravatarmenu)
        self.menu_userinfo = app_commands.ContextMenu(name="Usuario Info",callback=self.userinfomenu)
        self.client.tree.add_command(self.menu_useravatar)
        self.client.tree.add_command(self.menu_userinfo)









  @commands.Cog.listener()
  async def on_ready(self):
    print("📺  -  Modúlo Misc carregado.")









  @commands.Cog.listener()
  async def on_message(self,message):

    for i in range(len(afklist)):
      if any(f"<@{afklist[i]}>" in mention for mention in [message.content, *[f"<@{m.id}>" for m in message.mentions]]) and not message.author.bot:
        msgenviada = await message.channel.send(Res.trad(user=message.author, str="message_usuario_afk").format(message.author.mention,afklist[i+1]))
        await asyncio.sleep(15.0)
        await msgenviada.delete()
        return None
      break










# verifica se o usuario que esta digitando está afk
  @commands.Cog.listener()
  async def on_typing(self, channel, user, when):
    if user.id in afklist:
      i = afklist.index(user.id)
      afklist.remove(afklist[i+1])
      afklist.remove(user.id)
      msgenviada = await channel.send(Res.trad(user=user, str="message_afk_disable").format(user.mention))
      print(f"{user.mention} saiu do afk")
      await asyncio.sleep(15.0)
      await msgenviada.delete()






  #Remove os menu se necessario
  async def cog_unload(self) -> None:
        self.client.tree.remove_command(self.menu_useravatar, type=self.menu_useravatar.type)
        self.client.tree.remove_command(self.menu_userinfo, type=self.menu_userinfo.type)











#GRUPO USUARIOS 
  usuario=app_commands.Group(name="usuario",description="Comandos de usuarios do Brix.",allowed_installs=app_commands.AppInstallationType(guild=True,user=True),allowed_contexts=app_commands.AppCommandContext(guild=True, dm_channel=True, private_channel=True))





#COMANDO USUARIO AVATAR MENU
  async def useravatarmenu(self,interaction: discord.Interaction, membro: discord.User):
    await buscaravatar(interaction,membro,menu = True)





#COMANDO USUARIO AVATAR SLASH
  @usuario.command(name="avatar",description='👤⠂Exibe o avatar de um membro.')
  @app_commands.describe(membro="informe um membro")
  async def useravatar(self,interaction: discord.Interaction,membro: discord.User=None):
    await buscaravatar(interaction,membro,menu = False)





#COMANDO USUARIO INFO MENU
  async def userinfomenu(self,interaction: discord.Interaction, membro: discord.User):
    await buscaruser(self,interaction,membro, menu = True)





#COMANDO USUARIO INFO SLASH
  @usuario.command(name="info",description='👤⠂Verifica as informações de um membro.')
  @app_commands.describe(membro="informe um membro")
  async def userinfo(self,interaction: discord.Interaction,membro: discord.User=None):
    await buscaruser(self,interaction,membro,menu = False)
 





#COMANDO USUARIO BANNER SLASH
  @usuario.command(name="banner",description='👤⠂Exibe o banner de um membro.')
  @app_commands.describe(membro="informe um membro")
  async def userbanner(self,interaction: discord.Interaction, membro: discord.User=None):
    await buscarbanner(self,interaction,membro,menu=False)








#COMANDO USUARIO AFK
  @usuario.command(name="afk",description='👤⠂Fique inativo na comunidade.')
  @app_commands.describe(motivo="informe um membro")
  async def userafk(self,interaction: discord.Interaction,motivo: str=None):
    if await Res.print_brix(comando="userafk",interaction=interaction):
        return
    if motivo == None:
      motivo = "ele não falou kyuuu"
    afklist.append(interaction.user.id)
    afklist.append(motivo)
    resposta = discord.Embed( title=Res.trad(interaction=interaction,str="message_afk_enable_title"), description=Res.trad(interaction=interaction,str="message_afk_enable_description"),      colour=discord.Color.yellow()    )
    await interaction.response.send_message(embed=resposta,delete_after=5,ephemeral=True)











#GRUPO USUARIOS 
  roleplay=app_commands.Group(name="roleplay",description="Comandos de roleplay do Brix.",allowed_installs=app_commands.AppInstallationType(guild=True,user=True),allowed_contexts=app_commands.AppCommandContext(guild=True, dm_channel=True, private_channel=True))







#COMANDO USUARIO ABRAÇO SLASH
  @roleplay.command(name="abraçar",description='👤⠂Abraçe um membro.')
  @app_commands.describe(membro="informe um membro")
  async def userabraco(self,interaction: discord.Interaction,membro: discord.User):
    if await Res.print_brix(comando="funcaoabracarusuario",interaction=interaction,condicao=membro.name):
      return
    imagem = ["https://33.media.tumblr.com/8ac1eaeaa670c65b7dbb9ceff34e4d8b/tumblr_ntdyqagJ101r8sc3ro1_r1_500.gif","https://media.tenor.com/AyIx-RCO4aQAAAAC/pokemon-hug.gif","https://i.gifer.com/GDLs.gif"]
    resposta = discord.Embed(
      description=Res.trad(interaction= interaction, str="message_abraço").format(interaction.user.mention,membro.mention),
      colour=discord.Color.yellow()
    )
    resposta.set_image(url=f"{random.choice(imagem)}")
    await interaction.response.send_message(embed=resposta)








#COMANDO USUARIO ABRAÇO SLASH
  @roleplay.command(name="atacar",description='👤⠂Ataque um membro.')
  @app_commands.describe(membro="informe um alvo")
  async def useratack(self,interaction: discord.Interaction,membro: discord.User):
    if await Res.print_brix(comando="useratack",interaction=interaction):
        return
    resposta = discord.Embed(
      description=Res.trad(interaction= interaction, str="message_atacar").format(interaction.user.mention,membro.mention),
      colour=discord.Color.yellow()
    )
    imagem = ["https://64.media.tumblr.com/dcfc44e780bdf2427abdc852f960e981/tumblr_oktry4hti91tgjlm2o1_500.gif","https://i.gifer.com/8Upq.gif","https://i.kym-cdn.com/photos/images/original/001/013/414/b50.gif"]
    resposta.set_image(url=f"{random.choice(imagem)}")
    await interaction.response.send_message(embed=resposta)
  







#COMANDO USUARIO ABRAÇO SLASH
  @roleplay.command(name="carinho",description='👤⠂Faça carinho em um membro.')
  @app_commands.describe(membro="informe um membro")
  async def usercarinho(self,interaction: discord.Interaction,membro: discord.User):
    if await Res.print_brix(comando="usercarinho",interaction=interaction):
        return
    resposta = discord.Embed(
      description=Res.trad(interaction= interaction, str="message_carinho").format(interaction.user.mention,membro.mention),
      colour=discord.Color.yellow()
    )
    resposta.set_image(url=f"https://i.makeagif.com/media/6-13-2015/5aAShu.gif")
    await interaction.response.send_message(embed=resposta)










#COMANDO USUARIO CAFUNÉ SLASH
  @roleplay.command(name="cafuné",description='👤⠂Faça cafuné em um membro.')
  @app_commands.describe(membro="informe um membro")
  async def usercafune(self,interaction: discord.Interaction,membro: discord.User):
    if await Res.print_brix(comando="usercafune",interaction=interaction):
        return
    resposta = discord.Embed(
      description=Res.trad(interaction= interaction, str="message_cafune").format(interaction.user.mention,membro.mention),
      colour=discord.Color.yellow()
    )
    resposta.set_image(url=f"https://cdn.discordapp.com/attachments/1067789510097768528/1139147429367791696/Braixen_carinho.gif")
    await interaction.response.send_message(embed=resposta)














#GRUPO Emoji 
  emojis=app_commands.Group(name="emoji",description="Comandos de emoji do bot.",allowed_installs=app_commands.AppInstallationType(guild=True,user=True),allowed_contexts=app_commands.AppCommandContext(guild=True, dm_channel=False, private_channel=True))





#COMANDO INFORMAÇÂO DO EMOJI
  @emojis.command(name="info", description="🥳⠂Obtenha informações sobre um emoji")
  @app_commands.describe(emoji="O emoji sobre o qual deseja obter informações")
  async def emojiinfo(self, interaction: discord.Interaction, emoji: str):
    if await Res.print_brix(comando="emojiinfo",interaction=interaction):
        return
    await interaction.response.defer()
    try:
      emojivariavel = partial_emoji.PartialEmoji.from_str(emoji)
      
      resposta = discord.Embed( title=f"🦊┃Informações de emoji",colour=discord.Color.yellow())
      resposta.add_field(name=f"🆔{emojivariavel.id}", value=f":hourglass_flowing_sand: <t:{int(emojivariavel.created_at.timestamp())}:d>-<t:{int(emojivariavel.created_at.timestamp())}:R>\n🖼️ {'animado' if emojivariavel.animated else 'estatico'}")
      emojiinfo = self.client.get_emoji(emojivariavel.id)
      if emojiinfo:
        resposta.add_field(name=f"🏠 {emojiinfo.guild.name} ", value=f"🆔 **{emojiinfo.guild_id}**")
      resposta.set_thumbnail(url=emojivariavel.url)
      view = discord.ui.View()
      item = discord.ui.Button(style=discord.ButtonStyle.blurple,label="Abrir no navegador",url=emojivariavel.url)
      view.add_item(item=item)
      await interaction.followup.send(embed=resposta, view=view)
    except:
      await interaction.followup.send(Res.trad(interaction=interaction,str='message_erro_emojibusca'))











#COMANDO ADICIONAR UM EMOJI
  @emojis.command(name="adicionar", description="🥳⠂Adicione um emoji ao servidor")
  @app_commands.describe(url="URL da imagem do emoji (opcional)", attachment="Anexo da imagem do emoji (opcional)", emoji="Emoji existente de outro servidor (opcional)")
  async def add_emoji(self, interaction: discord.Interaction, url: str = None, attachment: discord.Attachment = None, emoji: str = None):
    if await Res.print_brix(comando="add_emoji", interaction=interaction):
      return     
    if not interaction.user.guild_permissions.manage_emojis:
      await interaction.response.send_message(Res.trad(interaction=interaction, str='message_erro'),ephemeral=True , delete_after=30)
      return
    await interaction.response.defer()
    if not url and not attachment and not emoji:
      await interaction.followup.send(Res.trad(interaction=interaction, str="message_erro_notargument").format("URL / Anexo(attachment) / Emoji"))
      return
    
    if emoji:
            # Extrai as informações do emoji
      emoji_obj = partial_emoji.PartialEmoji.from_str(emoji)
      emoji_name = emoji_obj.name  # Usa o mesmo nome do emoji original
      try:
        response = await interaction.client.http._HTTPClient__session.get(emoji_obj.url)
        image_data = await response.read()
      except:
        await interaction.followup.send(Res.trad(interaction=interaction, str="message_erro_emojiadd"))
        return
    elif url:
        response = await interaction.client.http._HTTPClient__session.get(url)
        if response.status != 200:
          await interaction.followup.send(Res.trad(interaction=interaction, str="message_erro_emojiadd_url"))
          return
        image_data = await response.read()
            
            # Extrai o nome do emoji a partir da URL (nome do arquivo)
        emoji_name = url.split("/")[-1].split(".")[0]  # Pega o nome sem a extensão
    else:
      image_data = await attachment.read()
            # Extrai o nome do emoji a partir do nome do arquivo do anexo
      emoji_name = attachment.filename.split(".")[0]  # Pega o nome sem a extensão
        # Sanitiza o nome do emoji, removendo caracteres não permitidos
    emoji_name = re.sub(r'\W+', '', emoji_name)  # Remove caracteres especiais
    emoji_name = emoji_name[:25]  # Limita o nome a 25 caracteres

        # Verifica se o nome é válido, caso contrário define um nome padrão
    if len(emoji_name) < 2:
            emoji_name = "emoji_custom"

        # Cria o emoji no servidor
    new_emoji = await interaction.guild.create_custom_emoji(name=emoji_name, image=image_data)
    await interaction.followup.send(Res.trad(interaction=interaction, str="message_emojiadd").format(new_emoji))

  @add_emoji.error
  async def add_emoji_error(self, interaction: discord.Interaction, error: Exception):
    await Res.erro_brix_embed(interaction=interaction, str="message_erro_brixsystem", e=error,comando="add_emoji")

 









#COMANDO REMOVER UM EMOJI
  @emojis.command(name="remover", description="🥳⠂Remova um emoji do servidor")
  @app_commands.describe(emoji="Nome do emoji que deseja remover")
  async def remove_emoji(self, interaction: discord.Interaction, emoji: str):
    if await Res.print_brix(comando="remove_emoji",interaction=interaction):
       return
    if not interaction.user.guild_permissions.manage_emojis:
        await interaction.response.send_message(Res.trad(interaction=interaction, str='message_erro'),ephemeral=True , delete_after=30)
        return
    await interaction.response.defer()
    emojivariavel = partial_emoji.PartialEmoji.from_str(emoji)
    emoji_to_remove = self.client.get_emoji(emojivariavel.id)
    
    if emoji_to_remove is None:
        await interaction.followup.send(Res.trad(interaction=interaction,str='message_erro_emojibusca'))
        return
    await emoji_to_remove.delete()
    await interaction.followup.send(Res.trad(interaction=interaction,str='message_emojirem'))
  
  @remove_emoji.error
  async def remove_emoji_error(self, interaction: discord.Interaction, error: Exception):
    await Res.erro_brix_embed(interaction=interaction, str="message_erro_brixsystem", e=error,comando="remove_emoji")













#COMANDO DE EMOJI BIG DO BRIX
  @emojis.command(name="big", description="🥳⠂Amplie um emoji")
  @app_commands.describe(emoji="O emoji que deseja ampliar")
  async def enlarge_emoji(self, interaction: discord.Interaction, emoji: str):
    if await Res.print_brix(comando="enlarge_emoji",interaction=interaction):
       return
    await interaction.response.defer()
    try:
      emojivariavel = discord.PartialEmoji.from_str(emoji)       
      await interaction.followup.send(emojivariavel.url)
    except Exception as e:
        await Res.erro_brix_embed(interaction,str="message_erro_brixsystem",e=e,comando="engarge_emoji")
  












# TAMANHO MÁXIMO POR ARQUIVO (7MB)

# COMANDO DE REALIZAÇÃO DE BACKUP DE EMOJIS
  @emojis.command(name="backup", description="🥳⠂Realize um backup de todos os emojis deste servidor")
  async def backup_emoji(self, interaction: discord.Interaction):
    if await Res.print_brix(comando="Backup_emoji", interaction=interaction):
      return

    if not interaction.user.guild_permissions.manage_emojis:
      await interaction.response.send_message( Res.trad(interaction=interaction, str='message_erro'), ephemeral=True, delete_after=30 )
      return

    guild = interaction.guild
    if not guild.emojis:
      await interaction.response.send_message( Res.trad(interaction=interaction, str="message_erro_notemoji"), ephemeral=True, delete_after=30 )
      return

    await interaction.response.send_message( Res.trad(interaction=interaction, str="message_emojibackup"), delete_after=30 )

    folder_name = f"{guild.id}_emojis"
    os.makedirs(folder_name, exist_ok=True)

    # BAIXAR EMOJIS
    async with aiohttp.ClientSession() as session:
      for emoji in guild.emojis:
        try:
          ext = "gif" if emoji.animated else "png"
          filename = f"{emoji.name}({emoji.id}).{ext}"

          async with session.get(str(emoji.url)) as resp:
            if resp.status == 200:
              with open(f"{folder_name}/{filename}", "wb") as f:
                f.write(await resp.read())
        except Exception as e:
          await Res.erro_brix_embed( interaction, str="message_erro_brixsystem", e=e, comando=f"Erro ao baixar {emoji.name}" )

    # GERAR ZIPs EM PARTES
    part = 1
    current_zip_path = f"{folder_name}_part{part}.zip"
    current_zip = zipfile.ZipFile(current_zip_path, 'w')
    opened_zips = [current_zip]
    current_size = 0
    zip_files = [current_zip_path]

    for file in os.listdir(folder_name):
        filepath = os.path.join(folder_name, file)
        filesize = os.path.getsize(filepath)

        # troca de zip se ultrapassar 7MB
        if current_size + filesize > 7 * 1024 * 1024:
            current_zip.close()
            part += 1
            current_zip_path = f"{folder_name}_part{part}.zip"
            current_zip = zipfile.ZipFile(current_zip_path, "w")
            opened_zips.append(current_zip)
            zip_files.append(current_zip_path)
            current_size = 0

        current_zip.write(filepath, arcname=file)
        current_size += filesize

    # FECHAR O ÚLTIMO ZIP
    current_zip.close()

    # PREPARAR ARQUIVOS PARA ENVIAR (em memória, sem travar)
    file_objects = []
    for f in zip_files:
        with open(f, "rb") as fp:
            data = fp.read()
        file_objects.append(discord.File(io.BytesIO(data), filename=os.path.basename(f)))

    # ENVIAR PARA O USUÁRIO
    await interaction.user.send(
        content=Res.trad(interaction=interaction, str="message_emojibackup_finalizado").format(guild.id),
        files=file_objects
    )

    # ESPERAR O DISCORD FECHAR HANDLES INTERNOS
    await asyncio.sleep(0.3)

    # LIMPAR ARQUIVOS TEMPORÁRIOS
    try:
        # arquivos dentro da pasta
        for f in os.listdir(folder_name):
            os.remove(os.path.join(folder_name, f))

        os.rmdir(folder_name)

        # apagar ZIPs
        for f in zip_files:
            if os.path.exists(f):
                os.remove(f)

    except Exception as e:
        print("Erro ao limpar:", e)













#COMANDO DE EMOJI DO BRIX
  @commands.command(name="emoji", description='🦊⠂Exibe um emoji em tamanho maior.')
  async def enlarge_emojiprefix(self,ctx,*,emoji:str = None):
    if emoji is None:
       await ctx.send(Res.trad(user=ctx.author, str="message_erro_notargument").format("use -emoji <:Braix:1272653348306419824>"))
    else:
      await ctx.message.delete()
      emojivariavel = discord.PartialEmoji.from_str(emoji)
      await ctx.send(emojivariavel.url)















async def setup(client:commands.Bot) -> None:
  await client.add_cog(misc(client))