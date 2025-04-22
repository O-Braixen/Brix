from typing import Union
import discord,os,asyncio,time,requests,aiohttp
from discord.ext import commands
from discord import app_commands
from modulos.essential.respostas import Res
from modulos.essential.usuario import userpremiumcheck, verificar_cooldown
from modulos.essential.gasmii import generate_response_with_text,generate_response_with_image_and_text,generate_response_with_transcribe_audio,generate_response_with_video_and_text # , generate_image_by_text







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





  #comando de contextmenu
  async def resumoaicontext(self,interaction: discord.Interaction, message: discord.Message):
    await interaction.response.defer(ephemeral=True)
    await self.resumoai(interaction,message)

  #comando de contextmenu
  async def midiaaskcontext(self,interaction: discord.Interaction, message: discord.Message):
    await interaction.response.defer(ephemeral=True)
    await self.midiaask(interaction,message)












#GRUPO DE COMANDOS DE IMAGENS BOT                                             #allowed_installs=app_commands.AppInstallationType(guild=True, user=True),allowed_contexts=app_commands.AppCommandContext(guild=True, dm_channel=True, private_channel=True)
  brixai=app_commands.Group(name="ai",description="Comandos do Sistema AI integrados no bot.",allowed_installs=app_commands.AppInstallationType(guild=True,user=True),allowed_contexts=app_commands.AppCommandContext(guild=True, dm_channel=True, private_channel=True))


#COMANDO BARD GPT SLASH
  @brixai.command(name="gpt",description='❓⠂Pergunte algo para o Braixen inteligente.')
  @app_commands.checks.cooldown(4,300)
  @app_commands.describe(pergunta="Pergunte algo para Brix AI...")
  async def ask(self,interaction: discord.Integration,pergunta:str):
      if await Res.print_brix(comando="askgpt",interaction=interaction,condicao=pergunta):
        return
      await interaction.response.defer()
      check = await userpremiumcheck(interaction)
      if check == True:
        try:
          prompt=f"{interaction.user} perguntou {pergunta} em {interaction.locale.value}"
          ans = await generate_response_with_text(prompt)
          if len(ans) < 1990:
            await interaction.followup.send(ans, suppress_embeds=True)
          else:
            while len(ans) > 1990:
              ans_text = ans[:1990]
              await interaction.followup.send(ans_text, suppress_embeds=True)
              ans = ans[1990:]
            await interaction.followup.send(ans, suppress_embeds=True)
        except Exception as e:
              await Res.erro_brix_embed(interaction=interaction,str="message_ia_erro",e=e,comando="ask GPT")
      else:
        await interaction.followup.send(Res.trad(interaction=interaction,str='message_ia_only_premium'))
        return

  @ask.error
  async def on_test_error(self, interaction:discord.Integration, error: app_commands.AppCommandError):
    if isinstance(error,app_commands.CommandOnCooldown):
      await interaction.response.send_message(Res.trad(interaction=interaction,str='message_ia_erro_cooldown').format(int(time.time() + error.retry_after)), ephemeral= True)



#COMANDO BARD GPT SLASH
  @brixai.command(name="gerar-fanfic",description='📃⠂Gere uma fanfic curta com Braixen inteligente.')
  @app_commands.checks.cooldown(1,300)
  @app_commands.describe(prompt="Gere uma historia contendo um Braixen usando Brix AI...")
  async def fanfic_gerador(self,interaction: discord.Integration,prompt:str):
      if await Res.print_brix(comando="askgpt",interaction=interaction,condicao=prompt):
        return
      await interaction.response.defer()
      check = await userpremiumcheck(interaction)
      if check == True:
        try:
          prompt=f"Gere uma historia curta sempre tendo um braixen, precisa ter titulo e o texto da historia com base nesses parametros aqui: {prompt} em {interaction.locale.value}"
          ans = await generate_response_with_text(prompt)
          if len(ans) < 1990:
            await interaction.followup.send(ans, suppress_embeds=True)
          else:
            while len(ans) > 1990:
              ans_text = ans[:1990]
              await interaction.followup.send(ans_text, suppress_embeds=True)
              ans = ans[1990:]
            await interaction.followup.send(ans, suppress_embeds=True)
        except Exception as e:
              await Res.erro_brix_embed(interaction=interaction,str="message_ia_erro",e=e,comando="ask GPT")
      else:
        await interaction.followup.send(Res.trad(interaction=interaction,str='message_ia_only_premium'))
        return

  @fanfic_gerador.error
  async def on_test_error(self, interaction:discord.Integration, error: app_commands.AppCommandError):
    if isinstance(error,app_commands.CommandOnCooldown):
      await interaction.response.send_message(Res.trad(interaction=interaction,str='message_ia_erro_cooldown').format(int(time.time() + error.retry_after)), ephemeral= True)






#COMANDO BARD GPT SLASH
  @brixai.command(name="midia-ask",description='❓⠂Pergunte sobre alguma midia para o Braixen inteligente que usa Google.')
  @app_commands.checks.cooldown(4,300)
  @app_commands.describe(midia="Anexe uma midia para saber sobre ela...")
  async def imgask(self, interaction: discord.Interaction, midia: discord.Attachment):
    await interaction.response.defer()
    await self.midiaask(interaction,midia)

  @imgask.error
  async def on_test_error(self, interaction:discord.Integration, error: app_commands.AppCommandError):
    if isinstance(error,app_commands.CommandOnCooldown):
      await interaction.response.send_message(Res.trad(interaction=interaction,str='message_ia_erro_cooldown').format(int(time.time() + error.retry_after)), ephemeral= True)


#COMANDO DE RESUMIR CONVERSAS VIA SLASH
  @brixai.command(name="resumo",description='❓⠂Faça um resumo da conversa de um chat.')
  @app_commands.checks.cooldown(1,300)
  @app_commands.describe(chat="informe um chat para consultar")
  async def resumoaislash(self, interaction: discord.Interaction, chat: discord.TextChannel):
    await interaction.response.defer()
    await self.resumoai(interaction,item=chat)
  
  @resumoaislash.error
  async def on_test_error(self, interaction:discord.Integration, error: app_commands.AppCommandError):
    if isinstance(error,app_commands.CommandOnCooldown):
      await interaction.response.send_message(Res.trad(interaction=interaction,str='message_ia_erro_cooldown').format(int(time.time() + error.retry_after)), ephemeral= True)


  @brixai.command(name="ajuda", description="❓⠂Receba ajuda sobre Braixen Inteligente.")
  async def aihelp(self, interaction: discord.Interaction):
    resposta = discord.Embed( 
      colour=discord.Color.yellow(),
      description=Res.trad(interaction=interaction,str="message_ia_help")
    )
    await interaction.response.send_message(embed=resposta)
  


# API AINDA NÂO DISPONIVEL PARA USUARIOS FREE
#  @brixai.command(name="gerar-imagem",description='🖼️⠂Gere uma imagem com Brix Gemini.')
#  @app_commands.checks.cooldown(1,300)
 # @app_commands.describe(prompt="Descreva como deseja sua imagem...")
 # async def generate_image(self,interaction: discord.Integration,prompt:str):
 #   await interaction.response.defer()
 #   ans = await generate_image_by_text(prompt)
  #  await interaction.followup.send(file=discord.File(fp=ans,filename="Brix_gemini_image.png"))





















# ------------------FUNÇÔES--------------------------
#------MIDIA ASK----------
  async def midiaask(self, interaction: discord.Interaction, midia: Union[discord.Message, discord.Attachment]):
    if await Res.print_brix(comando="midiaask", interaction=interaction):
      return
    
    check = await userpremiumcheck(interaction)
    if not check:
      await interaction.followup.send(Res.trad(interaction=interaction, str='message_ia_only_premium'))
      return

    permitido, tempo_restantante = await verificar_cooldown(interaction, "midiaask", 5)
    if not permitido:
      await interaction.followup.send( Res.trad(interaction=interaction, str="message_erro_cooldown").format(tempo_restantante),  ephemeral=True  )
      return

    #if check:
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
      await interaction.followup.send(embed=resposta)

    except Exception as e:
      await Res.erro_brix_embed(interaction, str="message_ia_erro", e=e,comando="midia GPT")
    #else:
        #await interaction.followup.send(Res.trad(interaction=interaction, str='message_ia_only_premium'))

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

  def extract_url_from_message(self, message):
    import re
    urls = re.findall(r'(https?://\S+)', message)
    return urls[0] if urls else None













  # COMANDO DE RESUMO AI COM SUPORTE A MENSAGEM OU TEXTCHANNEL
  async def resumoai(self, interaction: discord.Interaction, item: Union[discord.Message, discord.TextChannel]):
    if await Res.print_brix(comando="resumoai", interaction=interaction):
      return
    # Verifica se o usuário tem premium
    check = await userpremiumcheck(interaction)
    if not check:
      await interaction.followup.send(Res.trad(interaction=interaction, str='message_ia_only_premium'))
      return
    # Verifica se o Comando não está em cooldown
    permitido, tempo_restantante = await verificar_cooldown(interaction, "resumoai", 15)
    if not permitido:
      await interaction.followup.send( Res.trad(interaction=interaction, str="message_erro_cooldown").format(tempo_restantante),  ephemeral=True  )
      return
    
    # Define o canal com base no tipo de item (Message ou TextChannel)
    channel = item.channel if isinstance(item, discord.Message) else item
    # Verifica se o canal é de um servidor e se o bot tem permissão
    if channel.guild is None:
      await interaction.followup.send(Res.trad(interaction=interaction, str='message_ia_resumoai_not_permission'))
      return
    if not channel.permissions_for(channel.guild.me).read_message_history:
      await interaction.followup.send(Res.trad(interaction=interaction, str='message_ia_resumoai_not_permission'))
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
      ans = await generate_response_with_text(f"faça um resumo disso aqui em {interaction.locale.value}: {mensagens_str}")
    except Exception as e:
      # Lida com qualquer exceção durante a chamada à API (aqui você pode melhorar o tratamento de exceções)
      await interaction.followup.send(Res.trad(interaction=interaction, str='message_ia_resumoai_workfiltrer'))
      return

    # Envia o resumo como embed
    resposta = discord.Embed(
      colour=discord.Color.yellow(), 
      description=Res.trad(interaction=interaction, str='message_ia_resumoai_text').format(ans[:1900])
    )
    await interaction.followup.send(embed=resposta)















async def setup(client:commands.Bot) -> None:
  await client.add_cog(bard(client))

