import discord,os,asyncio,random,string,re
from discord.ext import commands,tasks
from discord import app_commands
from datetime import datetime,timedelta
from dotenv import load_dotenv
from typing import List
from src.services.connection.database import BancoServidores,BancoUsuarios
from src.services.essential.respostas import Res
from src.services.essential.diversos import Paginador_Global , gerar_id_unica





# ======================================================================
# LOAD DOS DADOS DO .ENV
load_dotenv(os.path.join(os.path.dirname(__file__), '.env')) #load .env da raiz
donoid = int(os.getenv("DONO_ID"))








# ======================================================================
#FUNÇÃO ADICIONAR CARGO TEMPORARIO
async def addtemproleusuario(self, interaction, membro, cargo, tempo):
    try:
        horario = datetime.now()
        tempo_final = horario + timedelta(seconds=tempo)
        horario_meses = horario + timedelta(hours=3650)

        # Checa se o tempo excede o limite de 3650 horas (aproximadamente 5 MESES)
        if tempo_final > horario_meses:
            if interaction:
                await interaction.edit_original_response(content = Res.trad(interaction=interaction, str='cargo_temporario_limit'))
            return
        else:
            item = { f"temprole.{gerar_id_unica()}": { "tempo": tempo_final, "cargo": cargo.id, "usuario": membro.id,  "responsavel": interaction.user.id if interaction else None,  "horaregistro": horario }}
            await membro.add_roles(cargo)
            BancoServidores.update_document(membro.guild.id if interaction is None else interaction.guild.id, item)

            # Responde no canal se houver interação
            if interaction:
                resposta = discord.Embed(
                    color=discord.Color.yellow(),
                    description=Res.trad(interaction=interaction, str='cargo_temporario_add_inguild').format(membro.mention, cargo.mention, int(tempo_final.timestamp()))
                )
                await interaction.edit_original_response(embed=resposta)

            # Envia uma notificação por DM ao membro
            dadosmembro = BancoUsuarios.insert_document(membro)
            try:
              if interaction:
                if dadosmembro['dm-notification'] is True:
                    resposta_dm = discord.Embed(
                        color=discord.Color.yellow(),
                        description=Res.trad(interaction=interaction, str='cargo_temporario_add_indm').format( membro.guild.name if interaction is None else interaction.guild.name, cargo.name, int(tempo_final.timestamp()) )
                    )
                    await membro.send(embed=resposta_dm)
                else:
                    print("membro não recebe notificações via DM")
            except:
                print("erro no envio de dm para informar recebimento de cargo")
    # Excessão para apresentar erro de permissão
    except discord.Forbidden as e:
        if interaction:
          await Res.erro_brix_embed(interaction=interaction, str="message_erro_permissao", e=e,comando="addtemproleusuario")










#-------------------Classe De administrador---------------------------
class admin(commands.Cog):
  def __init__(self, client: commands.Bot):
    self.client = client








# ======================================================================
# ON READY
  @commands.Cog.listener()
  async def on_ready(self):
    print("💼  -  Modúlo Admin carregado.")
    await self.client.wait_until_ready() #Aguardando o bot ficar pronto
     #Ligando tasks
    if not self.verificar_temproles.is_running():
      await asyncio.sleep(240)
      self.verificar_temproles.start()
  













# ======================================================================
  #GRUPO ADMINISTRADOR 
  admin=app_commands.Group(name="admin", description="Comandos administrativos do Brix.",allowed_installs=app_commands.AppInstallationType(guild=True,user=False),allowed_contexts=app_commands.AppCommandContext(guild=True, dm_channel=False, private_channel=False))








# ======================================================================
   #COMANDO BANIR
  @admin.command(name="banir", description='💼⠂Banir um membro do servidor.')
  @app_commands.describe(membro="Qual membro será banido?",razão="Qual a razão do banimento?")
  @commands.has_permissions(ban_members=True)
  async def ban(self,interaction: discord.Interaction, membro: discord.User, razão: str):
    if await Res.print_brix(comando="ban",interaction=interaction,condicao=membro):
      return
    #verificação se ta rodando em servidor
    if interaction.guild is None:
      await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyservers"),delete_after=10,ephemeral=True)
      return
    #verificação se o cara tem permissão de banir
    if interaction.permissions.ban_members is False:
      await interaction.response.send_message(content=Res.trad(interaction=interaction,str='message_erro'),delete_after=10,ephemeral=True)
      return
    
    await interaction.response.defer()
    try:
      membro = interaction.guild.get_member(membro.id)
      resposta = discord.Embed(
          colour=discord.Color.red(),
          title=Res.trad(interaction=interaction,str='ban_title'),
          description=Res.trad(interaction=interaction,str="ban_description").format(membro,razão)
      )
      await membro.ban(reason=razão,delete_message_days=7)
      await interaction.edit_original_response(embed=resposta)

    except Exception as e:
        await Res.erro_brix_embed(interaction=interaction, str="message_erro_banir", e=e,comando="ban")










# ======================================================================
#COMANDO DESBANIR
  @admin.command(name="desbanir", description='💼⠂Desbanir um membro do servidor.')
  @app_commands.describe(membro="Qual membro será desbanido?")
  @commands.has_permissions(ban_members=True)
  async def unban(self,interaction: discord.Interaction, membro:str):
    if await Res.print_brix(comando="unban",interaction=interaction,condicao=membro):
      return
    #verificação se ta rodando em servidor
    if interaction.guild is None:
      await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyservers"),delete_after=10,ephemeral=True)
      return
     #verificação se o cara tem permissão de banir
    if interaction.permissions.ban_members is False:
      await interaction.response.send_message(content=Res.trad(interaction=interaction,str='message_erro'),delete_after=10,ephemeral=True)
      return
    
    await interaction.response.defer()
    try:
      membro = int(membro)
      user = await self.client.fetch_user(membro)
      await interaction.guild.unban(user)
      resposta = discord.Embed(
          colour=discord.Color.yellow(),
          title=Res.trad(interaction=interaction,str='desban_title'),
          description=Res.trad(interaction=interaction,str="desban_description").format(membro)
      )
      await interaction.edit_original_response(embed=resposta)

    except Exception as e:
        await Res.erro_brix_embed(interaction=interaction, str="message_erro_desbanir", e=e,comando="unban")











# ======================================================================
    #COMANDO KICK
  @admin.command(name="kick", description='💼⠂Expulsar um membro do servidor.')
  @app_commands.describe(membro="Qual membro será expulso?", razão="Qual a razão da expulsão?")
  @commands.has_permissions(kick_members=True)
  async def kick(self, interaction: discord.Interaction, membro: discord.User, razão: str):
    if await Res.print_brix(comando="kick",interaction=interaction,condicao=membro):
      return
    if interaction.guild is None:
      await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyservers"),delete_after=10,ephemeral=True)
      return
    if interaction.permissions.kick_members is False:
      await interaction.response.send_message(content=Res.trad(interaction=interaction,str='message_erro'),delete_after=10,ephemeral=True)
      return
    
    await interaction.response.defer()
    try:
      membro = interaction.guild.get_member(membro.id)
      resposta = discord.Embed(
          colour=discord.Color.orange(),
          title=Res.trad(interaction=interaction,str='kick_title'),
          description=Res.trad(interaction=interaction,str="kick_description").format(membro,razão)
      )
      await membro.kick(reason=razão)
      await interaction.edit_original_response(embed=resposta)
            
    except discord.Forbidden as e:
        await Res.erro_brix_embed(interaction=interaction, str="message_erro_kick", e=e,comando="kick")

      












  #------------------GRUPO CHAT ------------------
  chat=app_commands.Group(name="chat",description="Comandos para chat do Brix.",allowed_installs=app_commands.AppInstallationType(guild=True,user=True),allowed_contexts=app_commands.AppCommandContext(guild=True, dm_channel=False, private_channel=False))







# ======================================================================
  #COMANDO DELETE CHAT
  @chat.command(name="deletar",description='🗨️⠂Deleta um chat existente.')
  @commands.has_permissions(manage_channels = True)
  async def deletechat(self,interaction: discord.Interaction):
    if await Res.print_brix(comando="deletechat",interaction=interaction,condicao=interaction.channel.name):
      return
    if interaction.guild is None:
      await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyservers"),delete_after=10,ephemeral=True)
      return
    if not interaction.permissions.manage_channels:
      await interaction.response.send_message(Res.trad(interaction=interaction,str='message_erro'),delete_after=10,ephemeral=True)
      return
    
    await interaction.response.send_message(Res.trad(interaction=interaction,str='chat_delete'))
    await asyncio.sleep(4.0)
    await interaction.channel.delete()











# ======================================================================
  #COMANDO PRUNE CHAT
  @chat.command(name="limpar", description='🗨️⠂Limpa as mensagens de um canal.')
  @app_commands.describe(quantidade="Informe a quantidade de mensagens para deletar",deletar="Delete apenas as mensagens desse usuário",manter="Mantém as mensagens desse usuário, apagando o resto")
  @commands.has_permissions(manage_messages=True)
  async def prunechat(self,interaction: discord.Interaction,quantidade: int,deletar: discord.User = None,manter: discord.User = None):
    if await Res.print_brix(comando="prunechat", interaction=interaction, condicao=interaction.channel.name):
      return

    if interaction.guild is None:
      await interaction.response.send_message(Res.trad(interaction=interaction, str="message_erro_onlyservers"),delete_after=10, ephemeral=True)
      return

    # Verifica permissão do bot
    if not interaction.guild.me.guild_permissions.manage_messages:
      await interaction.response.send_message( Res.trad(interaction=interaction, str='message_erro_permissao'), delete_after=10, ephemeral=True )
      return

    if not interaction.permissions.manage_messages:
      await interaction.response.send_message(Res.trad(interaction=interaction, str='message_erro'),delete_after=10, ephemeral=True)
      return

    if deletar and manter:
      await interaction.response.send_message(Res.trad(interaction=interaction, str='message_erro_chatprune'),ephemeral=True)
      return

    try:
      status_msg = await interaction.response.send_message(Res.trad(interaction=interaction,str='chat_prune').format(f"0/{quantidade}"),ephemeral=True)
      status_msg = await interaction.original_response()
    
      total_deletadas = 0

      # Tenta com purge Modo rápido: nenhuma filtragem
      if not deletar and not manter:
        while quantidade > 0:
          bloco = min(quantidade, 10)
          deletadas = await interaction.channel.purge(limit=bloco)
          if not deletadas:
            break
          total_deletadas += len(deletadas)
          quantidade -= len(deletadas)
          await status_msg.edit(content=Res.trad(interaction=interaction,str='chat_prune').format(f"{total_deletadas}/{quantidade}"))
          await asyncio.sleep(3)
      else:
        mensagens_para_apagar = []
        async for msg in interaction.channel.history(limit=500):
          if len(mensagens_para_apagar) >= quantidade:
            break
          if deletar and msg.author == deletar:
            mensagens_para_apagar.append(msg)
          elif manter and msg.author != manter:
            mensagens_para_apagar.append(msg)

        for msg in mensagens_para_apagar:
          try:
            await msg.delete()
            total_deletadas += 1
            await status_msg.edit(content=Res.trad(interaction=interaction,str='chat_prune').format(f"{total_deletadas}/{len(mensagens_para_apagar)}"))
            await asyncio.sleep(1.5)
          except:
              pass

      await status_msg.edit(content=Res.trad(interaction=interaction,str='chat_prune_concluido').format(total_deletadas))

    except Exception as e:
        await Res.erro_brix_embed(interaction=interaction,str="message_erro_brixsystem",e=e,comando="prunechannel")


  
  








# ======================================================================
  #COMANDO CRIAR CHAT
  @chat.command(name="criar",description='🗨️⠂Crie um novo chat.')
  @commands.has_permissions(manage_channels = True)
  @app_commands.describe(nome="informe um nome para o chat",categoria="Selecione uma categoria")
  async def createchat(self,interaction: discord.Interaction, nome:str,categoria:discord.CategoryChannel=None):
    if await Res.print_brix(comando="createchat",interaction=interaction,condicao=interaction.channel.name):
      return
    if interaction.guild is None:
      await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyservers"),delete_after=10,ephemeral=True)
      return
    if not interaction.permissions.manage_channels:
      await interaction.response.send_message(Res.trad(interaction=interaction,str='message_erro'),delete_after=10,ephemeral=True)
      return
    else:
      if categoria is None:
        novo_canal = await interaction.guild.create_text_channel(nome)
      else: novo_canal = await interaction.guild.create_text_channel(nome,category=categoria)
      await interaction.response.send_message(Res.trad(interaction=interaction,str='chat_create').format(novo_canal.mention),delete_after=10,ephemeral=True)









# ======================================================================
  #COMANDO INFO CHAT
  @chat.command(name="info",description='🗨️⠂Informações sobre um chat.')
  @app_commands.describe(chat="informe um chat para consultar")
  async def infochat(self,interaction: discord.Interaction, chat: discord.TextChannel=None):
    if await Res.print_brix(comando="infochat",interaction=interaction):
      return
    if interaction.guild is None:
      await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyservers"),delete_after=10,ephemeral=True)
      return
    
    await interaction.response.defer()
    chat = chat if chat is not None else interaction.channel
    topico = chat.topic or Res.trad(interaction=interaction,str='topic_none')
    nsfw = Res.trad(interaction=interaction, str='sim' if chat.nsfw else 'não')
    slow = Res.trad(interaction=interaction, str='desativado' if chat.slowmode_delay == 0 else 'slow_ativado').format(chat.slowmode_delay)

    resposta = discord.Embed(
      colour=discord.Color.yellow(),
      title=Res.trad(interaction=interaction,str='chat_title'), 
      description=f"```{topico}```"
    )
    resposta.add_field(name=Res.trad(interaction=interaction,str='menção'), value=f"<#{chat.id}>", inline=True)
    resposta.add_field(name=Res.trad(interaction=interaction,str='tipo'), value=Res.trad(interaction=interaction,str='chat_texto'), inline=True)    
    resposta.add_field(name="🔞⠂NSFW", value=f"```{nsfw}```", inline=True)
    resposta.add_field(name=Res.trad(interaction=interaction,str='slow_text'), value=f"```{slow}```", inline=True)    
    resposta.add_field(name=Res.trad(interaction=interaction,str='nome'), value=f"```{chat.name}```", inline=True)    
    resposta.add_field(name=Res.trad(interaction=interaction,str='criação'), value=f"```{datetime.strftime(chat.created_at, Res.trad(interaction=interaction, str='padrao_data')+' - %H:%M')}```", inline=True)    
    await interaction.edit_original_response(embed=resposta)
# Checador de erro caso o bot não tenha permissão de acessar os dados de um chat
  @infochat.error
  async def infochat_error(self, interaction: discord.Interaction, error: Exception):
    await interaction.response.defer(ephemeral=True)
    await Res.erro_brix_embed(interaction=interaction, str="message_erro_brixsystem", e=error,comando="infochat")



















  #------------------GRUPO CANAL ------------------
  canal=app_commands.Group(name="canal",description="Comandos de canais do Brix.",allowed_installs=app_commands.AppInstallationType(guild=True,user=True),allowed_contexts=app_commands.AppCommandContext(guild=True, dm_channel=False, private_channel=False))








# ======================================================================
  #COMANDO DELETE CANAL
  @canal.command(name="deletar",description='🔈⠂Deleta um canal existente.')
  @commands.has_permissions(manage_channels = True)
  @app_commands.describe(canal="informe um canal para deletar")
  async def deletechannel(self,interaction: discord.Interaction,canal: discord.VoiceChannel):
    if await Res.print_brix(comando="deletechannel",interaction=interaction,condicao=interaction.channel.name):
      return
    if interaction.guild is None:
      await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyservers"),delete_after=10,ephemeral=True)
      return
    if not interaction.permissions.manage_channels:
      await interaction.response.send_message(Res.trad(interaction=interaction,str='message_erro'),delete_after=10,ephemeral=True)
      return
    await interaction.response.send_message(Res.trad(interaction=interaction,str='canal_delete'),delete_after=10)
    await canal.delete()









# ======================================================================
  #COMANDO CRIAR CANAL
  @canal.command(name="criar",description='🔈⠂Crie um novo canal.')
  @app_commands.describe(nome="informe um nome para o chat",categoria="Selecione uma categoria")
  @commands.has_permissions(manage_channels = True)
  async def createchannel(self,interaction: discord.Interaction, nome:str,categoria:discord.CategoryChannel=None):
    if await Res.print_brix(comando="createchannel",interaction=interaction,condicao=nome):
      return
    if interaction.guild is None:
      await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyservers"),delete_after=10,ephemeral=True)
      return
    if not interaction.permissions.manage_channels:
      await interaction.response.send_message(Res.trad(interaction=interaction,str='message_erro'),delete_after=10,ephemeral=True)
      return

    if categoria is None:
      novo_canal = await interaction.guild.create_voice_channel(nome)
    else: novo_canal = await interaction.guild.create_voice_channel(nome,category=categoria)
    await interaction.response.send_message(Res.trad(interaction=interaction,str='canal_create').format(novo_canal.mention),delete_after=10,ephemeral=True)










# ======================================================================
#COMANDO INFO CANAL
  @canal.command(name="info",description='🔈⠂Informações sobre um canal.')
  @app_commands.describe(canal="informe um chat para consultar")
  async def infochannel(self,interaction: discord.Interaction, canal: discord.VoiceChannel):
    if await Res.print_brix(comando="infochannel",interaction=interaction):
      return
    if interaction.guild is None:
      await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyservers"),delete_after=10,ephemeral=True)
      return
    
    await interaction.response.defer()
    canal = canal if canal is not None else interaction.channel
    nsfw = Res.trad(interaction=interaction, str='sim' if canal.nsfw else 'não')
    canallimite = Res.trad(interaction=interaction, str='ilimitado') if canal.user_limit == 0 else canal.user_limit

    resposta = discord.Embed(
      colour=discord.Color.yellow(),
      title=Res.trad(interaction=interaction,str='chat_title'), 
    )
    resposta.add_field(name=Res.trad(interaction=interaction,str='menção'), value=f"<#{canal.id}>", inline=True)
    resposta.add_field(name=Res.trad(interaction=interaction,str='tipo'), value=Res.trad(interaction=interaction,str='chat_voz'), inline=True)    
    resposta.add_field(name="🔞⠂NSFW", value=f"```{nsfw}```", inline=True)
    resposta.add_field(name=Res.trad(interaction=interaction,str='bits_canal'), value=f"```{round(canal.bitrate / 1000)}kbps```", inline=True)    
    resposta.add_field(name=Res.trad(interaction=interaction,str='membros'), value=f"```{canallimite}```", inline=True)    
    resposta.add_field(name=Res.trad(interaction=interaction,str='criação'), value=f"```{datetime.strftime(canal.created_at, Res.trad(interaction=interaction, str='padrao_data')+' - %H:%M')}```", inline=True)    
    await interaction.edit_original_response(embed=resposta)

  @infochannel.error
  async def infochanel_error(self, interaction: discord.Interaction, error: Exception):
    await interaction.response.defer(ephemeral=True)
    await Res.erro_brix_embed(interaction=interaction, str="message_erro_brixsystem", e=error,comando="infochannel")


















  #------------------GRUPO CARGO ------------------
  cargo=app_commands.Group(name="cargo",description="Comandos de cargo do Brix.",allowed_installs=app_commands.AppInstallationType(guild=True,user=False),allowed_contexts=app_commands.AppCommandContext(guild=True, dm_channel=False, private_channel=False))






# ======================================================================
  #COMANDO ADICIONAR ROLE A UM USUARIO
  @cargo.command(name="adicionar",description='🔑⠂Adiciona um cargo a um membro.')
  @app_commands.describe(membro="informe um membro",cargo="qual cargo deseja adicionar ao membro?")
  @commands.has_permissions(manage_roles=True)
  async def roleadd(self,interaction: discord.Interaction, membro: discord.Member, cargo: discord.Role):
    if await Res.print_brix(comando="roleadd",interaction=interaction,condicao=f"{membro.name} cargo {cargo.name}"):
      return
    if interaction.guild is None:
        await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyservers"),delete_after=10,ephemeral=True)
    # Verifique se o autor do comando tem permissão para gerenciar o cargo que está sendo adicionado.
    if interaction.user != membro and membro.top_role.position >= interaction.user.top_role.position or interaction.user.top_role.position <= cargo.position:
      await interaction.response.send_message(Res.trad(interaction=interaction,str='message_erro_permissao_cargo'),delete_after=10, ephemeral=True)
      return
  
    try:
      if not interaction.permissions.manage_roles:
        await interaction.response.send_message(Res.trad(interaction=interaction,str='message_erro_permissao_user'),delete_after=10,ephemeral=True)
        return
      
      await interaction.response.defer()
      resposta = discord.Embed(
        colour=discord.Color.yellow(),
        title=Res.trad(interaction=interaction,str='cargo_add_title'),
        description=Res.trad(interaction=interaction,str='cargo_description').format(membro.mention,cargo)
      )
      await membro.add_roles(cargo)
      await interaction.edit_original_response(embed=resposta)
    except discord.Forbidden as e:
      await Res.erro_brix_embed(interaction=interaction, str="message_erro_permissao", e=e,comando="roleadd")
      









# ======================================================================
  #COMANDO REMOVER ROLE DE UM USUARIO
  @cargo.command(name="remover",description='🔑⠂Remove um cargo de um membro.')
  @app_commands.describe(membro="informe um membro",cargo="qual cargo deseja remover do membro?")
  @commands.has_permissions(manage_roles=True)
  async def rolerem(self,interaction: discord.Interaction, membro: discord.Member, cargo: discord.Role):
    if await Res.print_brix(comando="rolerem",interaction=interaction,condicao=f"{membro.name} cargo {cargo.name}"):
      return
    if interaction.guild is None:
      await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyservers"),delete_after=10,ephemeral=True)
      return
    if interaction.user != membro and membro.top_role.position >= interaction.user.top_role.position or interaction.user.top_role.position <= cargo.position:
      await interaction.response.send_message(Res.trad(interaction=interaction,str='message_erro_permissao_cargo'),delete_after=10, ephemeral=True)
      return
    
    try:
      if not interaction.permissions.manage_roles:
        await interaction.response.send_message(Res.trad(interaction=interaction,str='message_erro_permissao_user'),delete_after=10,ephemeral=True)
        return
      await interaction.response.defer()
      resposta = discord.Embed(
        colour=discord.Color.yellow(),
        title=Res.trad(interaction=interaction,str='cargo_rem_title'),
        description=Res.trad(interaction=interaction,str='cargo_description').format(membro.mention,cargo)
      )
      await membro.remove_roles(cargo)
      await interaction.edit_original_response(embed=resposta)
    except discord.Forbidden as e:
      await Res.erro_brix_embed(interaction=interaction, str="message_erro_permissao", e=e,comando="rolerem")
     









# ======================================================================
    #COMANDO SWITCH ROLE
  @cargo.command(name="trocar",description='🔑⠂Troca o cargo a um membro.')
  @app_commands.describe(membro="informe um membro",retirar="qual cargo deseja remover do membro?",colocar="qual cargo deseja adicionar ao membro?")
  @commands.has_permissions(manage_roles=True)
  async def rolecharge(self,interaction: discord.Interaction, membro: discord.Member, retirar: discord.Role, colocar: discord.Role):
    if await Res.print_brix(comando="rolecharge",interaction=interaction,condicao=f"{membro.name} - {retirar.name} - {colocar.name}"):
      return
    if interaction.guild is None:
      await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyservers"),delete_after=10,ephemeral=True)
    if interaction.user != membro and membro.top_role.position >= interaction.user.top_role.position or interaction.user.top_role.position <= retirar.position or interaction.user.top_role.position <= colocar.position:
      await interaction.response.send_message(Res.trad(interaction=interaction,str='message_erro_permissao_cargo'),delete_after=10, ephemeral=True)
      return
    try:
      if not interaction.permissions.manage_roles:
        await interaction.response.send_message(Res.trad(interaction=interaction,str='message_erro_permissao_user'),delete_after=10,ephemeral=True)
        return
      await interaction.response.defer()
      resposta = discord.Embed(
        colour=discord.Color.yellow(),
        title=Res.trad(interaction=interaction,str='cargo_trocado_title'),
        description=Res.trad(interaction=interaction,str='cargo_trocado_description').format(membro.mention,retirar.mention,colocar.mention)
      )
      await membro.remove_roles(retirar)
      await membro.add_roles(colocar)
      await interaction.edit_original_response(embed=resposta)
    except discord.Forbidden as e:
      await Res.erro_brix_embed(interaction=interaction, str="message_erro_permissao", e=e,comando="rolecharge")
  









# ======================================================================
  #COMANDO CARGO INFO
  @cargo.command(name="info",description='🔑⠂Verifica as informações de um cargo.')
  @app_commands.describe(cargo="selecione um cargo")
  async def roleinfo(self,interaction: discord.Interaction, cargo: discord.Role):
    if await Res.print_brix(comando="roleinfo",interaction=interaction):
      return
    if interaction.guild is None:
      await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyservers"),delete_after=10,ephemeral=True)
      return
    await interaction.response.defer()
    resposta = discord.Embed( 
        colour=cargo.color,
        description=Res.trad(interaction=interaction,str='cargo_title').format(cargo.name)
    )
    mençãocargo = "<a:Brix_Check:1371215835653210182>" if cargo.mentionable else "<a:Brix_Negative:1371215873637093466>"
    cargoseparado = "<a:Brix_Check:1371215835653210182>" if cargo.hoist else "<a:Brix_Negative:1371215873637093466>"
    integracao = "<a:Brix_Check:1371215835653210182>" if cargo.managed else "<a:Brix_Negative:1371215873637093466>"

    resposta.set_thumbnail(url=cargo.icon)
    resposta.add_field(name=Res.trad(interaction=interaction,str='nome'), value=f"```{cargo.name}```", inline=True)
    resposta.add_field(name="🆔⠂ID", value=f"```{cargo.id}```", inline=True)
    resposta.add_field(name=Res.trad(interaction=interaction,str='menção'), value=cargo.mention, inline=True)
    resposta.add_field(name=Res.trad(interaction=interaction,str='especificacoes'), value=Res.trad(interaction=interaction,str="especificacoes_value").format(mençãocargo,cargoseparado,integracao), inline=True)
    resposta.add_field(name=Res.trad(interaction=interaction,str='criação'), value=f"{datetime.strftime(cargo.created_at, Res.trad(interaction=interaction, str='padrao_data')+' - %H:%M')}\n<t:{int(cargo.created_at.timestamp())}:R>", inline=True)
    if cargo.members: resposta.add_field(name=Res.trad(interaction=interaction,str='membros'), value=Res.trad(interaction=interaction,str='membro_value').format(len(cargo.members)), inline=True)
    await interaction.edit_original_response(embed=resposta)

  @roleinfo.error
  async def roleinfo_error(self, interaction: discord.Interaction, error: Exception):
    await interaction.response.defer(ephemeral=True)
    await Res.erro_brix_embed(interaction=interaction, str="message_erro_brixsystem", e=error,comando="inforole")
    











# ======================================================================
#COMANDO CARGO LISTAR
  @cargo.command(name="listar",description='🔑⠂Liste todos os cargos do servidor.')
  async def rolelist(self,interaction: discord.Interaction):
    if await Res.print_brix(comando="rolelist",interaction=interaction):
      return
    if interaction.guild is None:
      await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyservers"),delete_after=10,ephemeral=True)
      return
    await interaction.response.defer()
    roles_list = [role.mention for role in interaction.guild.roles if role.name != '@everyone']
    roles_list.reverse()
    resposta = discord.Embed( 
      colour=discord.Color.yellow(),
      title=Res.trad(interaction=interaction,str='cargo_listar_title').format(interaction.guild.name),
    )
    # Adiciona campos a cada 20 itens
    for i in range(0, len(roles_list), 20):
        field_value = '\n'.join(roles_list[i:i+20])
        resposta.add_field(name=Res.trad(interaction=interaction,str='cargo_listar_field').format(i+1,min(i+20, len(roles_list))), value=field_value, inline=True)
        
    await interaction.edit_original_response(embed=resposta)
















#--------------------------TODA A ESTRUTURA DE CARGO TEMPORARIO------------------
  #GRUPO cargotemporario
  temprole = app_commands.Group(name="temporario",description="Comandos de cargo temporario do Brix.",parent=cargo )







# ======================================================================
#FUNÇÂO DE VERIFICAÇÃO DE ASSINANTES PREMIUM
  @tasks.loop(minutes=5) #5*60
  async def verificar_temproles(self): 
    filtro = {"temprole": {"$exists":True}}
    try:
      dados = BancoServidores.select_many_document(filtro)

      for servidor in dados:
        for registro,info in servidor['temprole'].items():
          if datetime.now() > info['tempo']:
            item = {f"temprole.{registro}": 0}
            BancoServidores.delete_field(servidor['_id'],item)
            try:
              server = self.client.get_guild(servidor['_id'])
              cargo = server.get_role(info['cargo'])
              member = server.get_member(int(info['usuario']))
              await member.remove_roles(cargo)
              print(f"usuario: {info['usuario']} teve o {cargo} removido")
            except:
              print(f"falha ao remover cargo de usuario: {info['usuario']}")
          
          # Após remover os cargos expirados, verifica se o campo 'temprole' está vazio
        servidor_atualizado = BancoServidores.insert_document(servidor['_id'])
        if 'temprole' in servidor_atualizado and not servidor_atualizado['temprole']:
          # Se o 'temprole' estiver vazio, remove o campo do documento
          print(f"Deletado o campo do servidor: {servidor['_id']}")
          BancoServidores.delete_field(servidor['_id'], {"temprole": 0})
    except Exception as e:
      print(f"erro na verificação de temproles, tentando mais tarde\n{e}")
    return









# ======================================================================
  #COMANDO TEMPROLE ADICIONAR
  @temprole.command(name="adicionar", description="🔑⠂Adicione um cargo temporário a alguém.")
  @app_commands.describe(membro="informe um membro",cargo="qual cargo deseja adicionar ao membro?",tempo ="Quantos tempo devo deixar o cargo?")
  @commands.has_permissions(manage_roles=True)
  async def temproleadd ( self , interaction: discord.Interaction , membro : discord.User, cargo: discord.Role, tempo:int):
    if await Res.print_brix(comando="temproleadd",interaction=interaction,condicao=f"{membro.name} - {cargo.name} - {tempo}"):
      return
    try:
      
      if interaction.guild is None:
        await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyservers"),delete_after=10,ephemeral=True)
        return
      if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_permissao_user"),delete_after=10,ephemeral=True)
        return
      if interaction.user == membro or membro == interaction.guild.owner:
        await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_permissao_cargo_user_or_onwer"),delete_after=10,ephemeral=True)
        return
      #if interaction.user != membro and membro.top_role.position >= interaction.user.top_role.position or interaction.user.top_role.position <= cargo.position:
      if  membro.top_role.position >= interaction.user.top_role.position   or   interaction.user.top_role.position <= cargo.position:
        await interaction.response.send_message(Res.trad(interaction=interaction,str='message_erro_permissao_cargo'),delete_after=10, ephemeral=True)
        return
      
      await interaction.response.defer()
      # Verificação de duplicação: verificar se o usuário e cargo já estão registrados no banco
      consulta = BancoServidores.insert_document(interaction.guild.id)
      if 'temprole' in consulta:
        for registro, info in consulta['temprole'].items():
          if info['usuario'] == membro.id and info['cargo'] == cargo.id:
            await interaction.edit_original_response(content=Res.trad(interaction=interaction, str="cargo_temporario_duplicado").format(registro))
            return
      await addtemproleusuario(self,interaction,membro,cargo,tempo)
    except Exception as e:
      await Res.erro_brix_embed(interaction=interaction, str="message_erro_permissao", e=e,comando="temproleadd")
      await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_permissao"),delete_after=10, ephemeral=True)

  @temproleadd.autocomplete("tempo")
  async def temproleadd_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    valor = 0
    if current.isdigit():
      valor = int(current)  
    sugestoes = [
      app_commands.Choice(
        name=f"{int(valor):_} {Res.trad(interaction=interaction,str='minutos')}",
        value=int(valor)*60,
      ),
      app_commands.Choice(
        name=f"{int(valor):_} {Res.trad(interaction=interaction,str='horas')}",
        value=int(valor)*60*60,
      ),
      app_commands.Choice(
        name=f"{int(valor):_} {Res.trad(interaction=interaction,str='dias')}",
        value=int(valor)*86400,
      )
    ]
    return sugestoes












# ======================================================================
#COMANDO LISTAR TODOS OS TEMPROLE DO SERVIDOR
  @temprole.command(name="listar", description="🔑⠂Lista todos os cargos temporários.")
  async def temprolelistar ( self , interaction: discord.Interaction):
    if await Res.print_brix(comando="temprolelistar",interaction=interaction):
      return
    try:
      if interaction.guild is None:
        await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyservers"),delete_after=10,ephemeral=True)
        return
      if interaction.user.guild_permissions.manage_roles is not True :
        await interaction.response.send_message(Res.trad(interaction=interaction,str='message_erro_permissao_cargo_consulta'),delete_after=10, ephemeral=True)
        return
      await interaction.response.send_message("https://cdn.discordapp.com/emojis/1370974233588404304.gif")

      consulta = BancoServidores.insert_document(interaction.guild.id)
        # Verifica se 'temprole' existe e não está vazio
      if 'temprole' not in consulta or not consulta['temprole']:
        lista =[f"{Res.trad(interaction= interaction, str='cargo_temporario_notlist')}"]
      else:
        registros_ordenados = sorted(consulta['temprole'].items(), key=lambda item: item[1]['tempo'])
        lista = []
        for registro,info in registros_ordenados:
          linha = f"ID registro:**{registro}**\n<@{info['usuario']}> - <@&{info['cargo']}> - <t:{int(info['tempo'].timestamp())}:R>"
          lista.append(linha)
      descrição=Res.trad(interaction= interaction, str='cargo_temporario_title')
      blocos = [lista[i:i + 10] for i in range(0, len(lista), 10)] 
      await Paginador_Global(self, interaction, blocos, pagina=0, originaluser=interaction.user,descrição=descrição, thumbnail_url=None)

    except Exception as e:
      await Res.erro_brix_embed(interaction=interaction, str="message_erro_permissao", e=e,comando="temprolelistar")
      
      












# ======================================================================
# COMANDO PARA REMOVER UM CARGO TEMPORARIO DE ALGUM USUARIO
  @temprole.command(name="remover", description="🔑⠂Remova um cargo temporário de alguém.")
  @app_commands.describe(idregistro="informe a ID do registro que deseja remover")
  @commands.has_permissions(manage_roles=True)
  async def temproleremover(self, interaction: discord.Interaction, idregistro: str):
    if await Res.print_brix(comando="temproleremover", interaction=interaction, condicao=f"ID: {idregistro}"):
      return
    try:
      if interaction.guild is None:
        await interaction.response.send_message(Res.trad(interaction=interaction, str="message_erro_onlyservers"), delete_after=20, ephemeral=True)
        return
      # Verificando se o usuário tem permissão
      if not interaction.user.guild_permissions.manage_roles:
          await interaction.response.send_message(Res.trad(interaction=interaction, str='message_erro_permissao_user'), delete_after=20, ephemeral=True)
          return
      # Consulta no banco de dados para encontrar o cargo temporário pelo ID
      consulta = BancoServidores.insert_document(interaction.guild.id)
      if 'temprole' not in consulta or idregistro not in consulta['temprole']:
          await interaction.response.send_message(Res.trad(interaction=interaction, str="cargo_temporario_erro"),delete_after=10, ephemeral=True)
          return

      # Remover o cargo temporário do usuário e atualizar o banco
      item = {f"temprole.{idregistro}": 0}
      BancoServidores.delete_field(interaction.guild.id,item)
      cargo = interaction.guild.get_role(int(consulta['temprole'][idregistro]['cargo']))
      user = interaction.guild.get_member(consulta['temprole'][idregistro]['usuario'])
      await user.remove_roles(cargo)

      # Enviar uma mensagem confirmando a remoção
      await interaction.response.send_message(Res.trad(interaction=interaction, str="cargo_temporario_rem").format(user.name, cargo.name))

    except Exception as e:
      await Res.erro_brix_embed(interaction=interaction, str="message_erro_permissao", e=e,comando="temproleremover")
 

# Autocomplete para ID de registro
  @temproleremover.autocomplete("idregistro")
  async def temproleremover_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    # Consulta no banco de dados para obter registros de cargos temporários
    consulta = BancoServidores.insert_document(interaction.guild.id)
    sugestoes = []

    if 'temprole' in consulta:
        # Adiciona os registros encontrados como sugestões para o autocomplete
        for registro_id, info in consulta['temprole'].items():
            if current.lower() in registro_id.lower():  # Filtra sugestões com base no texto do usuário
              try:
                cargo = interaction.guild.get_role(int(info['cargo']))
                user = interaction.guild.get_member(info['usuario'])
                sugestoes.append(app_commands.Choice(name=f"ID: {registro_id} - {user.name} - {cargo.name}", value=registro_id))
              except:
                sugestoes.append(app_commands.Choice(name=f"ID: {registro_id} - {info['usuario']} - {info['cargo']}", value=registro_id))
                
    # Caso não haja sugestões, adiciona a mensagem de "sem registros"
    if not sugestoes:
        mensagem_sem_registros = Res.trad(interaction=interaction, str="cargo_temporario_notlist")
        sugestoes.append(app_commands.Choice(name=mensagem_sem_registros, value=""))

    return sugestoes
  












# ======================================================================
  #COMANDO DE AJUDA DO CARGO TEMPORARIO
  @temprole.command(name="ajuda", description="🔑⠂Receba ajuda sobre cargos temporários.")
  async def temproleremoverhelp(self, interaction: discord.Interaction):
    resposta = discord.Embed( 
      colour=discord.Color.yellow(),
      description=Res.trad(interaction=interaction,str="cargo_temporario_help")
    )
    await interaction.response.send_message(embed=resposta)























# ======================================================================
# PARTE DO SETUP DA COG
async def setup(client:commands.Bot) -> None:
  await client.add_cog(admin(client))