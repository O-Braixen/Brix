from typing import Union
import discord,os,asyncio,time,requests , re ,aiohttp , datetime,json
from discord.ext import commands
from discord import app_commands, ui
from src.services.essential.respostas import Res
from src.services.essential.funcoes_usuario import userpremiumcheck, verificar_cooldown
from src.services.essential.gasmii import generate_response_with_text,generate_response_with_image_and_text,generate_response_with_transcribe_audio,generate_response_with_video_and_text , generate_image_by_text











# ======================================================================

class bard(commands.Cog):
  def __init__(self, client: commands.Bot):
    self.client = client

    #registro de comando de context menu
    self.menu_resumirconversa = app_commands.ContextMenu(name="Resumir Conversa",callback=self.resumoaicontext,type=discord.AppCommandType.message,allowed_installs=app_commands.AppInstallationType(guild=True,user=True),allowed_contexts=app_commands.AppCommandContext(guild=True, dm_channel=False, private_channel=False))
    self.client.tree.add_command(self.menu_resumirconversa)
    self.menu_identificarmensagem = app_commands.ContextMenu(name="Investigar Mensagem",callback=self.midiaaskcontext,type=discord.AppCommandType.message,allowed_installs=app_commands.AppInstallationType(guild=True,user=True),allowed_contexts=app_commands.AppCommandContext(guild=True, dm_channel=True, private_channel=True))
    self.client.tree.add_command(self.menu_identificarmensagem)
    






    #Remove os menu se necessario
  async def cog_unload(self) -> None:
    self.client.tree.remove_command(self.menu_resumirconversa, type=self.menu_resumirconversa.type)
    self.client.tree.remove_command(self.menu_identificarmensagem, type=self.menu_identificarmensagem.type)










  @commands.Cog.listener()
  async def on_ready(self):
    print("🦊  -  Modúlo Bard carregado.")

















# ======================================================================
  #comando de contextmenu
  async def resumoaicontext(self,interaction: discord.Interaction, message: discord.Message):
    res =  discord.Embed(description=Res.trad(interaction=interaction,str='message_ia_generate_prompt'), color=discord.Color.yellow() )
    res.set_thumbnail(url="https://cdn.discordapp.com/emojis/1371224437642236067.gif")
    await interaction.response.send_message(embed=res , ephemeral=True)
    await self.resumoai(interaction,message,ephemeral=True)









# ======================================================================
  #comando de contextmenu
  async def midiaaskcontext(self,interaction: discord.Interaction, message: discord.Message):
    res =  discord.Embed(description=Res.trad(interaction=interaction,str='message_ia_generate_prompt'), color=discord.Color.yellow() )
    res.set_thumbnail(url="https://cdn.discordapp.com/emojis/1371224437642236067.gif")
    await interaction.response.send_message(embed=res , ephemeral=True)
    await self.midiaask(interaction,message)
















# ======================================================================

#GRUPO DE COMANDOS DE IMAGENS BOT                                             #allowed_installs=app_commands.AppInstallationType(guild=True, user=True),allowed_contexts=app_commands.AppCommandContext(guild=True, dm_channel=True, private_channel=True)
  brixai=app_commands.Group(name="ai",description="Comandos do Sistema AI integrados no bot.",allowed_installs=app_commands.AppInstallationType(guild=True,user=True),allowed_contexts=app_commands.AppCommandContext(guild=True, dm_channel=True, private_channel=True))
  










# ======================================================================

  @brixai.command( name="gpt", description='❓⠂Pergunte algo para o Braixen inteligente.' )
  @app_commands.checks.cooldown(4, 120)
  @app_commands.describe(pergunta="Pergunte algo para Brix AI...")
  async def gpt(self, interaction: discord.Interaction, pergunta: str):
    if await Res.print_brix(comando="gpt", interaction=interaction, condicao=pergunta):
      return

    # Mensagem inicial
    embed_wait = discord.Embed( description=Res.trad(interaction=interaction, str='message_ia_generate_prompt'), color=discord.Color.yellow() ).set_thumbnail(url="https://cdn.discordapp.com/emojis/1371224437642236067.gif")
    await interaction.response.send_message(embed=embed_wait)

    # Checagem premium e cooldown
    if not await userpremiumcheck(interaction):
      permitido, _ = await verificar_cooldown(interaction, "gpt", 120)
      if not permitido:
        return await interaction.edit_original_response( embed=None, content=Res.trad(interaction=interaction, str='message_ia_cooldown_premium') )

    try:
        # Prompt para a IA
      prompt = (
          f"Você é Brix, um Braixen bot dentro do Discord, curioso, carismático e muito ajudante. "
          f"Você está respondendo para o usuário {interaction.user}, que perguntou: {pergunta}, "
          f"em {interaction.locale.value}. Responda da melhor forma possível e se refira a si mesmo como Brix AI."
      )

      ans = await generate_response_with_text(prompt)

      if len(ans) <= 1990:
          await interaction.edit_original_response(embed=None, content=ans)
      else:
          await interaction.delete_original_response()
          for i in range(0, len(ans), 1990):
              await interaction.followup.send(ans[i:i+1990])

    except Exception as e:
      await Res.erro_brix_embed(interaction=interaction,str="message_ia_erro",e=e,comando="ask GPT")


  @gpt.error
  async def on_test_error(self, interaction:discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error,app_commands.CommandOnCooldown):
      await interaction.response.send_message(Res.trad(interaction=interaction,str='message_ia_erro_cooldown').format(int(time.time() + error.retry_after)), ephemeral= True)











# ======================================================================
#COMANDO DE RESUMIR CONVERSAS VIA SLASH
  @brixai.command(name="resumo",description='❓⠂Faça um resumo da conversa de um chat.')
  @app_commands.checks.cooldown(1,120)
  @app_commands.describe(chat="informe um chat para consultar")
  async def resumoaislash(self, interaction: discord.Interaction, chat: discord.TextChannel):
    #await interaction.response.defer()
    res =  discord.Embed(description=Res.trad(interaction=interaction,str='message_ia_generate_prompt'), color=discord.Color.yellow() )
    res.set_thumbnail(url="https://cdn.discordapp.com/emojis/1371224437642236067.gif")
    await interaction.response.send_message(embed=res)
    await self.resumoai(interaction,item=chat , ephemeral=False)

  
  @resumoaislash.error
  async def on_test_error(self, interaction:discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error,app_commands.CommandOnCooldown):
      await interaction.response.send_message(Res.trad(interaction=interaction,str='message_ia_erro_cooldown').format(int(time.time() + error.retry_after)), ephemeral= True)










# ======================================================================

#COMANDO DE AJUDA SOBRE IA
  @brixai.command(name="ajuda", description="❓⠂Receba ajuda sobre Braixen Inteligente.")
  async def aihelp(self, interaction: discord.Interaction):
    resposta = discord.Embed( 
      colour=discord.Color.yellow(),
      description=Res.trad(interaction=interaction,str="message_ia_help")
    )
    await interaction.response.send_message(embed=resposta)
  










# ======================================================================
  ask=app_commands.Group(name="ask",description="Comandos de pergunta com Sistema AI integrados no bot.",parent=brixai)






# ======================================================================
#COMANDO BARD GPT SLASH PARA BUSCAR MIDIAS
  @ask.command(name="midia",description='❓⠂Pergunte sobre alguma midia para o Braixen inteligente que usa Google.')
  @app_commands.checks.cooldown(4,120)
  @app_commands.describe(midia="Anexe uma midia para saber sobre ela...")
  async def imgask(self, interaction: discord.Interaction, midia: discord.Attachment):
    #await interaction.response.defer()
    res =  discord.Embed(description=Res.trad(interaction=interaction,str='message_ia_generate_prompt'), color=discord.Color.yellow() )
    res.set_thumbnail(url="https://cdn.discordapp.com/emojis/1371224437642236067.gif")
    await interaction.response.send_message(embed=res)
    await self.midiaask(interaction,midia)

  @imgask.error
  async def on_test_error(self, interaction:discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error,app_commands.CommandOnCooldown):
      await interaction.response.send_message(Res.trad(interaction=interaction,str='message_ia_erro_cooldown').format(int(time.time() + error.retry_after)), ephemeral= True)



  






# ======================================================================

  create=app_commands.Group(name="criar",description="Comandos de Criaçção com Sistema AI integrados no bot.",parent=brixai)




# ======================================================================
  
# API AINDA NÂO DISPONIVEL PARA USUARIOS FREE
  #@create.command(name="imagem",description='📃⠂Gere uma imagem com Brix Gemini.')
  #@app_commands.checks.cooldown(1,120)
  #@app_commands.describe(prompt="Descreva como deseja sua imagem...")
  #async def generate_image(self,interaction: discord.Interaction,prompt:str):
  #  res =  discord.Embed(description=Res.trad(interaction=interaction,str='message_ia_generate_prompt'), color=discord.Color.yellow() )
  #  res.set_thumbnail(url="https://cdn.discordapp.com/emojis/1371224437642236067.gif")
  #  await interaction.response.send_message(embed=res)
  #  check = await userpremiumcheck(interaction)
  #  if check == False:
  #    permitido, tempo_restantante = await verificar_cooldown(interaction, "generate_image", 120)
  #    if not permitido:
  #      await interaction.edit_original_response(embed=None , content=Res.trad(interaction=interaction,str='message_ia_cooldown_premium'))
  #      return
  #  art , text= await generate_image_by_text(prompt)
  #  file = discord.File(fp=art, filename="Brix_gemini_image.png")
  #  res =  discord.Embed(description=Res.trad(interaction=interaction, str="message_ia_generate_imagen").format(text), color=discord.Color.yellow() )
  #  res.set_image(url="attachment://Brix_gemini_image.png")
    

  #  await interaction.edit_original_response(content="",embed=res , attachments=[file])  

  #@generate_image.error
  #async def on_test_error(self, interaction:discord.Interaction, error: app_commands.AppCommandError):
  #  if isinstance(error,app_commands.CommandOnCooldown):
  #    await interaction.response.send_message(Res.trad(interaction=interaction,str='message_ia_erro_cooldown').format(int(time.time() + error.retry_after)), ephemeral= True)
  











# ======================================================================

  #COMANDO BARD GPT SLASH PARA GERAR FANFIC
  @create.command(name="fanfic",description='📃⠂Gere uma fanfic curta com Braixen inteligente.')
  @app_commands.checks.cooldown(1,120)
  @app_commands.describe(prompt="Gere uma historia contendo um Braixen usando Brix AI...")
  async def fanfic_gerador(self,interaction: discord.Interaction,prompt:str):
      if await Res.print_brix(comando="fanfic_gerador",interaction=interaction,condicao=prompt):
        return
      #await interaction.response.defer()
      res =  discord.Embed(description=Res.trad(interaction=interaction,str='message_ia_generate_prompt'), color=discord.Color.yellow() )
      res.set_thumbnail(url="https://cdn.discordapp.com/emojis/1371224437642236067.gif")
      await interaction.response.send_message(embed=res)
      check = await userpremiumcheck(interaction)
      if check == False:
        permitido, tempo_restantante = await verificar_cooldown(interaction, "fanfic_gerador", 120)
        if not permitido:
          await interaction.edit_original_response(embed=None , content=Res.trad(interaction=interaction,str='message_ia_cooldown_premium'))
          return

      try:
        prompt=f"Gere uma historia curta sempre tendo um braixen, precisa ter titulo e o texto da historia com base nesses parametros aqui: {prompt} em {interaction.locale.value}"
        ans = await generate_response_with_text(prompt)
        if len(ans) < 1990:
          await interaction.edit_original_response(embed=None , content=ans)
        else:
          await interaction.delete_original_response()
          while len(ans) > 1990:
            ans_text = ans[:1990]
            await interaction.followup.send(ans_text)
            ans = ans[1990:]
          await interaction.followup.send(ans)
      except Exception as e:
            await Res.erro_brix_embed(interaction=interaction,str="message_ia_erro",e=e,comando="ask GPT")
        

  @fanfic_gerador.error
  async def on_test_error(self, interaction:discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error,app_commands.CommandOnCooldown):
      await interaction.response.send_message(Res.trad(interaction=interaction,str='message_ia_erro_cooldown').format(int(time.time() + error.retry_after)), ephemeral= True)













# ======================================================================

  #COMANDO BARD GPT SLASH PARA GERAR SERVIDORES
  @create.command(name="servidor", description="📃⠂Crie um servidor com a ajuda de um Braixen Inteligente.")
  @app_commands.checks.cooldown(3, 360)
  @commands.has_permissions(administrator=True)
  @app_commands.choices(emojis=[app_commands.Choice(name="Sim", value="Sim"),app_commands.Choice(name="Não", value="não"),] , cores=[app_commands.Choice(name="Sim", value="Sim"),app_commands.Choice(name="Não", value="Não"),] , vip=[app_commands.Choice(name="Sim", value="Sim"),app_commands.Choice(name="Não", value="não"),])
  @app_commands.describe(tema="Descreva qual será o tema do servidor..." , emojis = "Deseja que canais tenham emoji?",vip = "Deseja um setor para vips?", cores = "Deseja cargos dedicados para cores?", divisoria = "Deseja definir uma divisoria entre emoji e nome?")
  async def servercreate(self , interaction: discord.Interaction, tema: str , emojis: app_commands.Choice[str] = None, cores: app_commands.Choice[str] = None, vip: app_commands.Choice[str] = None, divisoria: str = None ):
    if await Res.print_brix(comando="servercreate",interaction=interaction,condicao=f"Tema:{tema} - Emoji:{emojis} - Cores:{cores} - Vip:{vip} - Divisoria:{divisoria}"):
      return
    await interaction.response.defer()
    check = await userpremiumcheck(interaction)
    if check == False:
      permitido, tempo_restantante = await verificar_cooldown(interaction, "servercreate", 120)
      if not permitido:
        await interaction.followup.send(Res.trad(interaction=interaction, str='message_ia_cooldown_premium'))
        return

    if interaction.guild is None:
        await interaction.followup.send(Res.trad(interaction=interaction, str="message_erro_onlyservers"))
        return

    # Verificar se o usuário é administrador
    member = interaction.user
    if not member.guild_permissions.administrator:
        await interaction.followup.send(Res.trad(interaction=interaction, str='message_erro_permissao_user_admin'))
        return

    guild = interaction.guild
    idade_servidor = datetime.datetime.now(datetime.timezone.utc) - guild.created_at
    if idade_servidor > datetime.timedelta(days=14):
        await interaction.followup.send(Res.trad(interaction=interaction, str='message_ia_servercreate_ageserver'))
        return

    me = guild.get_member(interaction.client.user.id)
    if not me or not me.guild_permissions.administrator:
        await interaction.followup.send(Res.trad(interaction=interaction, str='message_erro_permissao_general'))
        return
    
    res =  discord.Embed(description=Res.trad(interaction=interaction,str='message_ia_servercreate_creater'), color=discord.Color.yellow() )
    res.set_thumbnail(url = "https://cdn.discordapp.com/emojis/1370974233588404304.gif")
    await interaction.followup.send(embed =res)    
    try:
      # Primeiro prompt: obter nome e roles
      ia_prompt_1 = (
          f"Gere apenas um JSON com o nome do servidor e os cargos seguindo este formato:\n"
          "{\n"
          "  \"server_name\": \"...\",\n"
          "  \"roles\": [\n"
          "    {{\"name\": \"...\", \"color\": \"#rrggbb\", \"permissions\": \"admin|staff|Bot|vip|cor|default|notificação\"}}\n"
          "  ]\n"
          "}\n\n"
          f"Regras:\n"
          f"- Tema do servidor: {tema}, linguagem: {interaction.locale.value}\n"
          f"- Cargos de cor: {'Não, sem cores' if cores is None else cores}\n"
          f"- Cargo para membros vips: {'sem cargo para vip' if vip is None else vip}\n"
          f"- Crie no mínimo 15 cargos. Se tiver cores, inclua 5 variantes das cores fora os cargos, caso seja pedido cargo de vip crie apenas 1.\n"
          f"- Ordem dos Cargos: staff, cores (se houver), vip (se houver), bot, cargos gerais, cargos de notificações.\n"
      )

      resposta_1 = await generate_response_with_text(ia_prompt_1)
      resposta_1 = re.sub(r"^```(json)?|```$", "", resposta_1.strip(), flags=re.MULTILINE)
      json_roles = json.loads(resposta_1)
      server_name = json_roles["server_name"]
      roles = json_roles["roles"]

      ia_prompt_2 = (
          f"Gere apenas um JSON com categorias e canais para o seguinte servidor:\n"
          "{\n"
          "  \"categories\": [\n"
          "    {{\n"
          "      \"name\": \"...\",\n"
          "      \"permissions\": [\"admin|staff|vip|default|leitura\"],\n"
          "      \"channels\": [\n"
          "        {{\"name\": \"emoji{divisoria}nome\", \"type\": \"text|voice\"}}\n"
          "      ]\n"
          "    }}\n"
          "  ]\n"
          "}\n\n"
          f"Regras:\n"
          f"- Nome: {server_name}\n"
          f"- Tema do servidor: {tema}\n"
          f"- Emoji: {'não' if emojis is None else emojis}\n"
          f"- Separador: {'sem divisorias' if divisoria is None else divisoria}\n"
          f"- vip: {'sem canais para vip' if vip is None else vip}\n"
          f"- Organize em no mínimo 20 canais distribuídos em categorias\n"
          f"- Deve conter: categoria staff com permissão exclusiva, leitura para boas-vindas e regras, bot commands junto do bate-papo, vip(se pedido) eles precisam ser acessíveis pela staff\n"
          f"- Ordem dos Ccanais: canais de leitura ( permissão leitura / staff/ não colocar default), canais de batepapo ou uso de bots (permissão default), vip (se houver, permissão vip/staff/admin), setor da staff(permissão staff).\n"

      )

      resposta_2 = await generate_response_with_text(ia_prompt_2)
      resposta_2 = re.sub(r"^```(json)?|```$", "", resposta_2.strip(), flags=re.MULTILINE)

      json_categorias = json.loads(resposta_2)
      categories = json_categorias["categories"]

      data = {    "server_name": server_name,    "roles": roles,    "categories": categories}
     
      embed = discord.Embed(description=Res.trad(interaction=interaction,str='message_ia_servercreate_msg').format(data['server_name']), color=discord.Color.yellow() )
      cargos = ""
      for role in data["roles"]:
          cargos += f"- {role['name']} ({role['permissions']})\n"
      embed.add_field(name=Res.trad(interaction=interaction,str='cargos'), value=cargos or "Nenhum", inline=False)

      # Categorias e canais
      for categoria in data["categories"]:
        canais = ""
        for ch in categoria["channels"]:
          tipo = "💬 - " if ch["type"] == "text" else "🔊 - "
          canais += f"{tipo} {ch['name']}\n"
        embed.add_field(name=f"{categoria['name']}", value=canais or "Nenhum canal", inline=False)

      view = ConfirmarAplicacao(interaction, data)
      await interaction.edit_original_response( view=view  , embed=embed)

    except Exception as e:
        await interaction.followup.send(Res.trad(interaction=interaction,str='message_ia_servercreate_erro').format(e))
   


  @servercreate.error
  async def on_test_error(self, interaction:discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error,app_commands.CommandOnCooldown):
      await interaction.response.send_message(Res.trad(interaction=interaction,str='message_ia_erro_cooldown').format(int(time.time() + error.retry_after)), ephemeral= True)



  # autocomplete da opção 'divisoria'
  @servercreate.autocomplete("divisoria")
  async def divisoria_autocomplete( self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    DIVISORIAS_SUGERIDAS = [ "⫶", "∘", "⤷", "›", "•", "⇢", "⟡", "・", "➤", "➟", "➥", "➔", "⮞", "☼", "┃", "→", "≫", "✧", "⋆", "⋙", "☀", "✦", "❯", "⨠"]
    sugestoes = [ app_commands.Choice(name=div, value=div)        for div in DIVISORIAS_SUGERIDAS        if current in div    ]
    if current and current not in DIVISORIAS_SUGERIDAS:
        sugestoes.insert(0, app_commands.Choice(  name=f"Opção personalizada: {current}", value=current ))
    return sugestoes[:25]




















# ------------------FUNÇÔES--------------------------
#------MIDIA ASK----------
  async def midiaask(self, interaction: discord.Interaction, midia: Union[discord.Message, discord.Attachment]):
    if await Res.print_brix(comando="midiaask", interaction=interaction):
      return
    
    check = await userpremiumcheck(interaction)
    if check == False:
      permitido, tempo_restantante = await verificar_cooldown(interaction, "midiaask", 120)
      if not permitido:
        await interaction.edit_original_response(embed=None , content=Res.trad(interaction=interaction, str='message_ia_cooldown_premium'))
        return

    try:
      envio = None
      midia_url = None
      # Caso o midia seja um attachment diretamente
      if isinstance(midia, discord.Attachment):
        arquivo = await midia.read()
        content_type = midia.content_type
        
        if content_type.startswith('image/'):
          midia_url = midia.proxy_url                     
          ans = await generate_response_with_image_and_text(arquivo, text=f"identifique essa imagem em {interaction.locale.value}")
          envio = Res.trad(interaction=interaction, str='message_ia_text_image').format(ans[:1900])
        elif content_type.startswith('audio/'):
          ans = await generate_response_with_transcribe_audio(arquivo, text=f"Transcreva esse áudio em {interaction.locale.value}")
          envio = Res.trad(interaction=interaction, str='message_ia_text_audio').format(ans[:1900])
        elif content_type.startswith('video/'):
          midia_url = midia.proxy_url
          ans = await generate_response_with_video_and_text(arquivo, text=f"Do que esse video se trata em {interaction.locale.value}")
          envio = Res.trad(interaction=interaction, str='message_ia_text_video').format(ans[:1900])
        else:
          envio = Res.trad(interaction=interaction, str='message_ia_text_outrasmidias')

      # Caso o midia seja uma mensagem
      elif isinstance(midia, discord.Message):
        # Verifica se há attachments na mensagem
        if midia.attachments:
          attachment = midia.attachments[0]
          arquivo = await attachment.read()
          content_type = attachment.content_type
          
          if content_type.startswith('image/'):
            midia_url = attachment.proxy_url
            ans = await generate_response_with_image_and_text(arquivo, text=f"Você se chama Brix ai e precisa identifique essa imagem em {interaction.locale.value}")
            envio = Res.trad(interaction=interaction, str='message_ia_text_image').format(ans[:1900])
          elif content_type.startswith('audio/'):
            ans = await generate_response_with_transcribe_audio(arquivo, text=f"Você se chama Brix ai e precisa transcreva esse áudio em {interaction.locale.value}")
            envio = Res.trad(interaction=interaction, str='message_ia_text_audio').format(ans[:1900])
          elif content_type.startswith('video/'):
            midia_url = midia.proxy_url
            ans = await generate_response_with_video_and_text(arquivo, text=f"Você se chama Brix ai e precisa falar do que esse video se trata em {interaction.locale.value}")
            envio = Res.trad(interaction=interaction, str='message_ia_text_video').format(ans[:1900])
          else:
            envio = Res.trad(interaction=interaction, str='message_ia_text_outrasmidias')
        
        # Verifica se há URLs ou emojis no conteúdo da mensagem
        elif midia.content.strip():
          if 'http' in midia.content:
            midia_url = self.extract_url_from_message(midia.content)
          elif '<:' in midia.content:
            emoji = discord.PartialEmoji.from_str(midia.content)      
            midia_url = emoji.url
          if midia_url:
            try:
              arquivo, content_type = await self.fetch_image_from_url(midia_url)
              if content_type.startswith('image/') and not content_type.endswith('gif'):
                if isinstance(arquivo, tuple):
                  arquivo = arquivo[0]  # Extrair bytes se for uma tupla
                ans = await generate_response_with_image_and_text(arquivo, text=f"identifique essa imagem em {interaction.locale.value}")
                envio = Res.trad(interaction=interaction, str='message_ia_text_image').format(ans[:1900])
              else:
                envio = Res.trad(interaction=interaction, str='message_ia_text_outrasmidias')
            except:envio = Res.trad(interaction=interaction, str='message_ia_text_outrasmidias')
          else:
              envio = Res.trad(interaction=interaction, str='message_ia_text_outrasmidias')

        # Verifica se há embeds com imagens
        
        elif midia.embeds:
          embed = midia.embeds[0]
          if embed.image:
              midia_url = embed.image.url
              arquivo = await self.fetch_image_from_url(midia_url)
              if isinstance(arquivo, tuple):
                arquivo = arquivo[0]
              ans = await generate_response_with_image_and_text(arquivo, text=f"identifique essa imagem em {interaction.locale.value}")
              envio = Res.trad(interaction=interaction, str='message_ia_text_image').format(ans[:1900])
        else:
          envio = Res.trad(interaction=interaction, str='message_ia_text_outrasmidias')

      # Envia a resposta
      if envio:
        resposta = discord.Embed(colour=discord.Color.yellow(), description=envio)
        if midia_url: resposta.set_image(url=midia_url)
      else:
        resposta = discord.Embed(colour=discord.Color.yellow(), description=Res.trad(interaction=interaction, str='message_ia_text_outrasmidias'))
      await interaction.edit_original_response(embed=resposta, content=None)

    except Exception as e:
      await Res.erro_brix_embed(interaction, str="message_ia_erro", e=e,comando="midia GPT")






# ======================================================================
# Métodos auxiliares
  async def fetch_image_from_url(self, url):
    async with aiohttp.ClientSession() as session:
      async with session.get(url) as response:
        if response.status == 200:
          content_type = response.headers.get('Content-Type')
          if content_type:
            arquivo = await response.read()
            return arquivo, content_type
          else:
            raise Exception(f"Falha ao buscar imagem do URL: {url} - No Content-Type")
        else:
          raise Exception(f"Falha ao buscar imagem do URL: {url}")


# ======================================================================

  def extract_url_from_message(self, message):
    import re
    urls = re.findall(r'(https?://\S+)', message)
    return urls[0] if urls else None





















# ======================================================================

  # COMANDO DE RESUMO AI COM SUPORTE A MENSAGEM OU TEXTCHANNEL
  async def resumoai(self, interaction: discord.Interaction, item: Union[discord.Message, discord.TextChannel], ephemeral):
    if await Res.print_brix(comando="resumoai", interaction=interaction):
      return
    # Verifica se o usuário tem premium
    check = await userpremiumcheck(interaction)
    if check == False:
      permitido, tempo_restantante = await verificar_cooldown(interaction, "resumoai", 120)
      if not permitido:
        await interaction.edit_original_response(embed=None , content=Res.trad(interaction=interaction, str='message_ia_cooldown_premium'))
        return
    
    # Define o canal com base no tipo de item (Message ou TextChannel)
    channel = item.channel if isinstance(item, discord.Message) else item
    # Verifica se o canal é de um servidor e se o bot tem permissão
    if channel.guild is None:
      await interaction.edit_original_response(embed=None, content=Res.trad(interaction=interaction, str='message_ia_resumoai_not_permission'))
      return
    if not channel.permissions_for(channel.guild.me).read_message_history:
      await interaction.edit_original_response(embed=None, content=Res.trad(interaction=interaction, str='message_ia_resumoai_not_permission'))
      return

    # Coleta as últimas 100 mensagens
    mensagens = []
    async for message in channel.history(limit=100):
      mensagens.append((message.author.name, message.content))
    # Inverte a ordem para manter a cronologia
    mensagens.reverse()
    # Formata as mensagens em uma string
    mensagens_str = "\n".join([f"{autor}: {conteudo}" for autor, conteudo in mensagens])
    # Tenta gerar o resumo usando a API
    try:
      ans = await generate_response_with_text(f"Você se chama Brix ai e precisa fazer um resumo disso aqui em {interaction.locale.value}: {mensagens_str}")
    except Exception as e:
      # Lida com qualquer exceção durante a chamada à API (aqui você pode melhorar o tratamento de exceções)
      await interaction.edit_original_response(embed=None, content=Res.trad(interaction=interaction, str='message_ia_resumoai_workfiltrer'))
      return

    # Envia o resumo como embed
    resposta = discord.Embed(
      colour=discord.Color.yellow(), 
      description=Res.trad(interaction=interaction, str='message_ia_resumoai_text').format(ans[:1900])
    )
    
    if ephemeral:
      
      async def enviar_callback(button_interaction: discord.Interaction):
        resposta = discord.Embed(      colour=discord.Color.yellow(),       description=Res.trad(interaction=interaction, str='message_ia_resumoai_text').format(ans[:1900])    )
        await channel.send(embed= resposta)
        await button_interaction.response.edit_message(content=Res.trad(interaction=interaction, str='message_say'), embed=None, view=None)
      view = ui.View()
      botão = ui.Button(label=Res.trad(interaction=interaction,str="botão_compartilhar_chat") ,style=discord.ButtonStyle.gray,emoji="🦊")
      botão.callback = enviar_callback
      view.add_item( botão )

      await interaction.edit_original_response(view=view,embed=resposta, content=None)
    await interaction.edit_original_response( embed=resposta, content=None)



















# ======================================================================
  #GERADOR DE SERVIDOR
  # View com botões de confirmação
class ConfirmarAplicacao(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, data):
      super().__init__(timeout=None)
      self.interaction = interaction
      self.data = data

    @discord.ui.button(label="Aplicar", style=discord.ButtonStyle.green)
    async def aplicar(self, interaction: discord.Interaction, button: discord.ui.Button):
      if interaction.user != self.interaction.user:
        await interaction.response.send_message(Res.trad(interaction=interaction,str='message_erro_interacaoalheia'), ephemeral=True)
        return
        
      await interaction.response.edit_message( view=None , embed=discord.Embed(description=Res.trad(interaction=interaction,str='message_ia_servercreate_criando').format("<a:Brix_Check:1371215835653210182>","<a:Brix_Loadingl:1371224437642236067>","<a:Brix_Loadingl:1371224437642236067>","<a:Brix_Loadingl:1371224437642236067>","<a:Brix_Loadingl:1371224437642236067>","<a:Brix_Loadingl:1371224437642236067>",), color=discord.Color.yellow() ))
      msg_enviada = await interaction.original_response()
      await aplicar_estrutura(interaction.guild, interaction, self.data , msg_enviada)

    @discord.ui.button(label="Cancelar", style=discord.ButtonStyle.red)
    async def cancelar(self, interaction: discord.Interaction, button: discord.ui.Button):
      if interaction.user != self.interaction.user:
        await interaction.response.send_message(Res.trad(interaction=interaction,str='message_erro_interacaoalheia'), ephemeral=True)
        return
      await interaction.response.edit_message(content=Res.trad(interaction=interaction,str='message_ia_servercreate_cancelado'), view=None, embed=None)









# ======================================================================
# Função que aplica a estrutura no servidor
async def aplicar_estrutura(guild : discord.Guild, interaction : discord.Interaction, data , msg_enviada : discord.Message):
  canal_origem = interaction.channel
  await msg_enviada.edit( embed = discord.Embed(description=Res.trad(interaction=interaction,str='message_ia_servercreate_criando').format("<a:Brix_Check:1371215835653210182>","<a:Brix_Loadingl:1371224437642236067>","<a:Brix_Loadingl:1371224437642236067>","<a:Brix_Loadingl:1371224437642236067>","<a:Brix_Loadingl:1371224437642236067>","<a:Brix_Loadingl:1371224437642236067>",), color=discord.Color.yellow() ))

   # Deletar cargos
  for role in guild.roles:
    if role.is_default() or role.managed:
      continue
    if role >= guild.me.top_role:
      await canal_origem.send(content=Res.trad(interaction=interaction,str='message_ia_erro_delroles').format(role.name), embed = None)
      continue
    try:
      await role.delete()
      await asyncio.sleep(0.4)
    except Exception as e:
      await msg_enviada.edit(content=Res.trad(interaction=interaction,str='message_ia_erro_delroles').format(role.name), embed = None)
      print(e)
      return

  embed = discord.Embed(description=Res.trad(interaction=interaction,str='message_ia_servercreate_criando').format("<a:Brix_Check:1371215835653210182>","<a:Brix_Check:1371215835653210182>","<a:Brix_Loadingl:1371224437642236067>","<a:Brix_Loadingl:1371224437642236067>","<a:Brix_Loadingl:1371224437642236067>","<a:Brix_Loadingl:1371224437642236067>",), color=discord.Color.yellow() )
  await msg_enviada.edit(content="" , embed = embed)

  # Deletar canais
  for channel in guild.channels:
    if channel.id != canal_origem.id:
      try:
        await channel.delete()
        await asyncio.sleep(0.4)
      except discord.Forbidden:
        await msg_enviada.edit(content=Res.trad(interaction=interaction,str='message_ia_erro_delchannel').format(channel.name), embed = None)
        return
  
  embed = discord.Embed(description=Res.trad(interaction=interaction,str='message_ia_servercreate_criando').format("<a:Brix_Check:1371215835653210182>","<a:Brix_Check:1371215835653210182>","<a:Brix_Check:1371215835653210182>","<a:Brix_Loadingl:1371224437642236067>","<a:Brix_Loadingl:1371224437642236067>","<a:Brix_Loadingl:1371224437642236067>",), color=discord.Color.yellow() )
  await msg_enviada.edit(content="" , embed = embed)

  # Renomear servidor
  try:
    await guild.edit(name=data["server_name"])
  except discord.Forbidden:
    await canal_origem.send(content=Res.trad(interaction=interaction,str='message_ia_erro_nameserver').format(data["server_name"]))

  # Criar cargos
  cargos_criados = {}
  for role_data in data["roles"]:
    perms = discord.Permissions()
    if role_data["permissions"] == "admin":
      perms = discord.Permissions(administrator=True)
    elif role_data["permissions"] == "staff":
      perms= discord.Permissions(manage_channels=True, manage_messages=True , kick_members=True , moderate_members = True)
    elif role_data["permissions"] == "bot":
      perms= discord.Permissions(manage_channels=True, manage_messages=True , kick_members=True , moderate_members = True , manage_guild= True , manage_roles = True)
    elif role_data["permissions"] == "default":
      perms = discord.Permissions()

    try:
      cor_hex = role_data.get("color")
      cor_discord = discord.Colour(int(cor_hex.replace("#", ""), 16)) if cor_hex else discord.Colour.default()

      role = await guild.create_role(
        name=role_data["name"],
        colour=cor_discord,
        permissions=perms
      )
      # Salva referência
      key = role_data["permissions"]
      cargos_criados.setdefault(key, []).append(role)
    except discord.HTTPException as e:
      await canal_origem.send(content=f"Erro ao criar cargo {role_data['name']}: {e}")

  # Criar categorias e canais
  embed = discord.Embed(description=Res.trad(interaction=interaction,str='message_ia_servercreate_criando').format("<a:Brix_Check:1371215835653210182>","<a:Brix_Check:1371215835653210182>","<a:Brix_Check:1371215835653210182>","<a:Brix_Check:1371215835653210182>","<a:Brix_Loadingl:1371224437642236067>","<a:Brix_Loadingl:1371224437642236067>",), color=discord.Color.yellow() )
  await msg_enviada.edit(content="" , embed = embed)
  ContadorCanais = 0
  for category_data in data["categories"]:
    overwrites = {}

    if any(p in ["admin", "staff" , "vip"] for p in category_data["permissions"]):
      overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
      }
      for perm in category_data["permissions"]:
        # Filtra os cargos da estrutura que têm esse tipo de permissão
        nomes_roles = [role["name"].lower() for role in data["roles"] if role["permissions"] == perm]
        for role in guild.roles:
          if role.name.lower() in nomes_roles:
            overwrites[role] = discord.PermissionOverwrite(view_channel=True , send_messages=True , create_public_threads= True , create_polls=False)
          if perm == "leitura":
            overwrites[guild.default_role] = discord.PermissionOverwrite(view_channel=True , send_messages=False , create_private_threads=False , create_polls=False)
          if perm == "default":
            overwrites[guild.default_role] = discord.PermissionOverwrite(view_channel=True , send_messages=True , create_private_threads=False , create_polls=False)
            
    else:
      # Caso seja pública (sem perms especiais)
      overwrites[guild.default_role] = discord.PermissionOverwrite(view_channel=True)

    # Criar categoria com overwrites definidos
    categoria = await guild.create_category(name=category_data["name"], overwrites=overwrites)

    for channel_data in category_data["channels"]:
      ContadorCanais += 1
      if channel_data["type"] == "text":
        await guild.create_text_channel(name=channel_data["name"], category=categoria)
      elif channel_data["type"] == "voice":
        await guild.create_voice_channel(name=channel_data["name"], category=categoria)


  embed = discord.Embed(description=Res.trad(interaction=interaction,str='message_ia_servercreate_criando').format("<a:Brix_Check:1371215835653210182>","<a:Brix_Check:1371215835653210182>","<a:Brix_Check:1371215835653210182>","<a:Brix_Check:1371215835653210182>","<a:Brix_Check:1371215835653210182>","<a:Brix_Check:1371215835653210182>",), color=discord.Color.yellow() )
  await msg_enviada.edit(content="" , embed = embed)
  await asyncio.sleep(3)
  embed = discord.Embed(description=Res.trad(interaction=interaction,str='message_ia_servercreate_finalizado').format(data['server_name'],len (data['roles']),len (data['categories']),ContadorCanais), color=discord.Color.yellow() )
  #await Res.print_brix(comando="servercreate",interaction=interaction,condicao="CONSTRUÇÂO CONCLUIDA")
  await msg_enviada.edit(content="" , embed = embed)



























# ======================================================================

async def setup(client:commands.Bot) -> None:
  await client.add_cog(bard(client))
