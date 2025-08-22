import discord,os,asyncio,time,random , datetime ,unicodedata , re
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from typing import List
from src.services.connection.database import BancoServidores
from src.services.essential.respostas import Res




# ======================================================================

load_dotenv(os.path.join(os.path.dirname(__file__), '.env')) #load .env da raiz
idbh = int(os.getenv("id_servidor_bh"))











# ======================================================================

class boasvindas(commands.Cog):
  def __init__(self, client: commands.Bot):
    self.client = client
    self.member_join_error_count = {}







  @commands.Cog.listener()
  async def on_ready(self):
    print("🏠  -  Modúlo Boasvindas carregado.")
  





  @commands.Cog.listener()
  async def on_member_join(self,member : discord.Member):
    print(f"membro {member.id} entrou na {member.guild.id} - {member.guild.name} ")
    
    # Respostas da BH
    membro = member.mention
    resp_macho = [ f"Oiii, bem-vindo, raposa {membro}! Espero que se divirta por aqui, kyu~",f"Salveee! Seja muito bem-vindo, {membro}, à minha casa mágica. Fique à vontade, kyu!",f"O {membro} aterrissou aqui com estilo! Seja bem-vindo, kyu!"]
    resp_femea = [f"Oiiieee! Bem-vindaaa, raposa {membro}! Que bom ter você aqui, kyu~",    f"Bem-vinda, {membro}, à minha humilde residência! Sinta-se em casa, kyu! <:BH_Braix_Happy:1154418207071940778>",    f"Oii, bem-vinda, {membro}! Fique à vontade e aproveite a magia do lar, kyu~"]
    resp_indefinido = [    f"Olá, bem-vinde, raposa {membro}! Espero que curta o aconchego da minha casa, brai~",    f"Bem-vinde, {membro}, à minha casinha mágica! Fique à vontade, kyu!",    f"Oii, bem-vinde, {membro}! Aproveite seu tempo por aqui, kyu~"]
    resp_normal = [    f"Boas-vindas, raposa {membro}! Aproveite a estadia e toda a magia, kyu~",    f"Boas-vindas, {membro}! Minha casinha é sua casinha, fique à vontade, kyu! <:BH_Braix_Happy:1154418207071940778>",    f"Oiii, boas-vindas, {membro}! Espero que se sinta em casa nessa pequena toca que chamo de lar, kyu! <:Braix:1272653348306419824>"]
    resp_naoverificado = [    f"Boas-vindas, raposa {membro}! Não se esqueça de concluir seu registro em <id:customize>, kyu!",    f"Boas-vindas, {membro}! Sinta-se à vontade na minha casinha. Ah, lembre-se de finalizar seu registro em <id:customize>, kyu!",    f"Oiii, {membro}! Boas-vindas! Complete seu registro em <id:customize> pra aproveitar tudo que a comunidade tem pra oferecer, kyu~"]


    #verificar se o servidor tem alguma coisa no banco de dados
    dados_servidor = BancoServidores.insert_document(member.guild.id)

    
    #PARTE DE SEGURANÇA DO BRIX SECURITY
    if "seguranca" in dados_servidor:
      antialt = dados_servidor["seguranca"]
      if "antialt" in antialt:

        tempo_configurado = antialt["antialt"].get('tempo')
        acao_configurada = antialt["antialt"].get('acao')
        notificacao_configurada =  antialt["antialt"].get('notificacao')
        # Calcule o tempo de vida da conta do membro
        tempo_conta = (datetime.datetime.now(datetime.timezone.utc) - member.created_at).total_seconds()
        # Compare o tempo de vida da conta com o tempo configurado
        if tempo_conta < tempo_configurado:
          if notificacao_configurada: # Opcional: Notificar o usuário via DM se a notificação estiver ativada
            try:
              await member.send(Res.trad(user=member,str="message_segurança_antalt_DM").format( Res.trad(user=member,str=f"{acao_configurada}"),member.guild.name))
            except discord.Forbidden:
              # Ocorre se o usuário tiver as DMs desabilitadas
              pass
          try:
            # Se a conta for muito nova, realize a ação configurada
            if acao_configurada == "kick":
              await member.kick(reason="Brix proteção Anti-Alt: Conta muito nova.")
            elif acao_configurada == "ban":
              await member.ban(reason="Brix proteção Anti-Alt: Conta muito nova.")
          except:
            print(f"falha ao aplicar penalidade em :{member.guild.id}")
          return






    #verifica se o membro entrou na BH
    if member.guild.id == idbh:
      channel = await self.client.fetch_channel(968272277709918209)

      for _ in range(60):
        # Verifica se o membro ainda está no servidor
        if member.guild.get_member(member.id) is None:
          # Se o membro saiu, cancela o envio da mensagem
          return
        desired_role = discord.utils.get(member.guild.roles, name='Pequena Raposa')
        # Envia a mensagem de boas-vindas no canal desejado
        if desired_role in member.roles:
          #verifica masculino
          desired_role = discord.utils.get(member.guild.roles, name='♂️ Macho')
          if desired_role in member.roles:
            await channel.send(random.choice(resp_macho))
          elif discord.utils.get(member.guild.roles, name='♀️ Fêmea') in member.roles:
            await channel.send(random.choice(resp_femea))
          elif discord.utils.get(member.guild.roles, name='🏳‍🌈 Não definido') in member.roles:
            await channel.send(random.choice(resp_indefinido))
          else:
            await channel.send(random.choice(resp_normal))
          return
        await asyncio.sleep(1)
      await channel.send(random.choice(resp_naoverificado))
      return
    
    
    if dados_servidor and 'boasvindas' not in dados_servidor:
      return
    try: 
      canal = await self.client.fetch_channel(dados_servidor['boasvindas'].get('canal'))
      mensagem_boas_vindas = dados_servidor['boasvindas'].get('mensagem')
      tempo_delete = dados_servidor['boasvindas'].get('deletar', 0)
      if canal:
        mensagem_final = (mensagem_boas_vindas
                  .replace('@user', member.mention)
                  .replace('guildsize', str(member.guild.member_count))
                  .replace('guild', member.guild.name)
                  .replace('userid', str(member.id)))
        # Verifica se o membro ainda está no servidor
        await asyncio.sleep(5)
        if member.guild.get_member(member.id) is None:
          # Se o membro saiu, cancela o envio da mensagem
          return
        enviado = await canal.send(mensagem_final)
        if tempo_delete != 0 :
          await asyncio.sleep(tempo_delete)
          await enviado.delete()
      # Se o envio foi bem-sucedido, podemos resetar o contador para esse servidor, se houver
      if member.guild.id in self.member_join_error_count:
        del self.member_join_error_count[member.guild.id]

    except:
        # Incrementa o contador de erros para esse servidor
      servidor_id = member.guild.id
      contador = self.member_join_error_count.get(servidor_id, 0) + 1
      self.member_join_error_count[servidor_id] = contador
                
      print(f"Contador de erros para o servidor {servidor_id}: {contador}")
              
      if contador > 2:
          print(f"Mais de 2 erros para o servidor {servidor_id}. Deletando registro.")
          item = {"boasvindas":servidor_id}
          BancoServidores.delete_field(servidor_id,item)
                    # Remove o contador do cache após a deleção
          del self.member_join_error_count[servidor_id]















# ======================================================================
#GRUPO DE COMANDOS DE BOAS VINDAS DO BRIX
  boavinda=app_commands.Group(name="bem-vindo",description="Comandos de boas-vindas integrados no Brix.",allowed_installs=app_commands.AppInstallationType(guild=True,user=False),allowed_contexts=app_commands.AppCommandContext(guild=True, dm_channel=False, private_channel=False))







# ======================================================================
#COMANDO BOAS VINDAS CONFIGURAR
  @boavinda.command(name="configurar",description='🦊⠂Configurar boas-vindas no servidor.')
  @commands.has_permissions(manage_guild=True)
  @app_commands.describe(canal="Indique um canal para enviar boas vindas",mensagem="Variaveis disponiveis: @user , guild , guildsize, userid",deletar = "deletar mensagem em x segundos? ignore para não deletar")
  async def boasvindasconfigurar(self,interaction: discord.Interaction,canal : discord.TextChannel, mensagem : str, deletar: int = None):
    if await Res.print_brix(comando="boasvindasconfigurar",interaction=interaction):
      return
    if interaction.guild is None:
      await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyservers"),delete_after=20,ephemeral=True)
      return
    
    if not interaction.permissions.manage_guild:
      await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro"),delete_after=10,ephemeral=True)
      return
    await interaction.response.defer(ephemeral=True)
    if deletar is None:
      deletar = 0
    item = {"boasvindas.canal": canal.id,"boasvindas.mensagem": mensagem, 'boasvindas.deletar': deletar}
    BancoServidores.update_document(interaction.guild.id,item)
    try:
      mensagemteste = await canal.send('kyu')
      await asyncio.sleep(0.1)
      await mensagemteste.delete()
      await interaction.followup.send(Res.trad(interaction=interaction,str="message_boasvindas_confirmado").format(canal.mention,mensagem,deletar))
    except:
      await interaction.followup.send(Res.trad(interaction=interaction,str="message_erro_permissao"))









# ======================================================================
#COMANDO BOAS VINDAS DESATIVAR
  @boavinda.command(name="desativar",description='🦊⠂Desative as boas-vindas na sua comunidade.')
  @commands.has_permissions(manage_guild=True)
  async def boasvindasdesativar(self,interaction: discord.Interaction):
    if await Res.print_brix(comando="boasvindasdesativar",interaction=interaction):
      return
    if interaction.guild is None:
      await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyservers"),delete_after=20,ephemeral=True)
      return
    
    if not interaction.permissions.manage_guild:
      await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro"),delete_after=10,ephemeral=True)
      return
    
    await interaction.response.defer(ephemeral=True)
    item = {"boasvindas":interaction.channel.id}
    BancoServidores.delete_field(interaction.guild.id,item)
    await interaction.followup.send(Res.trad(interaction=interaction,str="message_boasvindas_desativado"))











# ======================================================================
  #COMANDO BOAS VINDAS AJUDAR
  @boavinda.command(name="ajuda",description='🦊⠂Dicas de uso do boas-vindas.')
  async def boasvindasdicas(self,interaction: discord.Interaction):
    await interaction.response.send_message(Res.trad(interaction=interaction,str="message_boasvindas_dica"),delete_after=60)

























# ======================================================================

#GRUPO DE COMANDOS DE SEGURANÇA DO BRIX
  seguranca=app_commands.Group(name="segurança",description="Comandos de segurança integrados no Brix.",allowed_installs=app_commands.AppInstallationType(guild=True,user=False),allowed_contexts=app_commands.AppCommandContext(guild=True, dm_channel=False, private_channel=False))




  # FUNÇÃO DE NORMALIZAR UM NOME DE USUARIO REMOVENDO QUALQUER FONTE INADEQUADA
  def normalizar_nome(self, nome: str) -> str:
    nome_norm = unicodedata.normalize('NFKD', nome)
    nome_ascii = ''.join(c for c in nome_norm if ord(c) < 128)
    return re.sub(r'\s+', ' ', nome_ascii).strip()



  # COMANDO DE NORMALIZAR NOMES, SÓ PODE SER USADO POR AQUELES QUE PODEM GERENCIAR NICKNAMES
  @seguranca.command(name="normalizar_nomes", description='📝⠂Normaliza nicknames cque tenham fontes diferentes ou emojis no servidor.')
  @commands.has_permissions(manage_nicknames=True)
  async def normalizar_nomes_cmd(self, interaction: discord.Interaction):
    if await Res.print_brix(comando="normalizar_nomes", interaction=interaction):
      return

    if interaction.guild is None:
      await interaction.response.send_message( Res.trad(interaction=interaction, str="message_erro_onlyservers"), delete_after=20, ephemeral=True )
      return

    if not interaction.permissions.manage_nicknames:
        await interaction.response.send_message( Res.trad(interaction=interaction, str="message_erro"), delete_after=10, ephemeral=True )
        return

    # Verifica permissão do bot
    if not interaction.guild.me.guild_permissions.manage_nicknames:
      await interaction.response.send_message( Res.trad(interaction=interaction, str='message_erro_permissao'), delete_after=10, ephemeral=True )
      return
    
    await interaction.response.defer()
    status_msg = await interaction.original_response()

    alterados = 0
    sem_permissao = 0
    processados = 0
    total_membros = sum(1 for m in interaction.guild.members if not m.bot)

    for member in interaction.guild.members:
      if member.bot:
        continue

      nome_original = member.display_name
      nome_novo = self.normalizar_nome(nome_original)

      if nome_novo != nome_original:
        try:
          await member.edit(nick=nome_novo, reason="Normalização de fonte")
          await asyncio.sleep(0.5)  # Delay para evitar rate limit
          alterados += 1
        except discord.Forbidden:
          sem_permissao += 1
        except discord.HTTPException:
          sem_permissao += 1

      processados += 1
      print(nome_original)
      # Atualiza apenas a cada 10 processados ou no final
      if processados % 10 == 0 or processados == total_membros:
        if status_msg:
          try:
              await status_msg.edit( content=Res.trad(interaction=interaction, str="normatizar_nomes") .format(processados, total_membros, alterados, sem_permissao) )
          except discord.NotFound:
              status_msg = None

    if status_msg:
      try:
        await status_msg.edit(content=Res.trad(interaction=interaction, str="normatizar_nomes_concluido").format(alterados,sem_permissao ) )

      except discord.NotFound:
        pass













# GRUPO DE COMANDO ANTIALT (CONTRA CONTAS NOVAS NA COMUNIDADE)
  anti_alt=app_commands.Group(name="anti-alt",description="Comandos de segurança anti-alt integrados no Brix.",parent=seguranca)






# ======================================================================

#COMANDO ANTIALT ATIVAR
  @anti_alt.command(name="ativar",description='🔒⠂Configurar sistema contra contas novas no servidor.')
  @commands.has_permissions(manage_guild=True)
  @app_commands.choices(ação=[app_commands.Choice(name="Expulsar", value="kick"),app_commands.Choice(name="Banir", value="ban")])
  @app_commands.describe(tempo ="Tempo minimo da conta criada?",ação="Defina uma ação para acontecer",notificar="Notificar usuário em DM?")
  async def segurancaantalt(self,interaction: discord.Interaction,tempo : int , ação : str , notificar: bool ):
    if await Res.print_brix(comando="segurancaantalt",interaction=interaction):
      return
    if interaction.guild is None:
      await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyservers"),delete_after=20,ephemeral=True)
      return
    
    if not interaction.permissions.manage_guild:
      await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro"),delete_after=10,ephemeral=True)
      return
    
    await interaction.response.defer()
    horario = datetime.datetime.now()
    tempo_final = horario + datetime.timedelta(seconds=tempo)
    horario_meses = horario + datetime.timedelta(hours=720)

    # Checa se o tempo excede o limite de 3650 horas (aproximadamente 30 dias)
    if tempo_final > horario_meses:
      if interaction:
        await interaction.edit_original_response(content = Res.trad(interaction=interaction, str='message_segurança_antalt_limit'))
      return
    
    item = {"seguranca.antialt.tempo": tempo,"seguranca.antialt.acao": ação,"seguranca.antialt.notificacao": notificar}
    BancoServidores.update_document(interaction.guild.id,item)
    tempo_formatado = ""
    if tempo >= 86400: # Se for 24 horas ou mais
        tempo_formatado = f"{int(tempo / 86400)} {Res.trad(interaction=interaction,str='dias')}"
    elif tempo >= 3600: # Se for 1 hora ou mais
        tempo_formatado = f"{int(tempo / 3600)} {Res.trad(interaction=interaction,str='horas')}"
    else: # Se for menos que 1 hora
        tempo_formatado = f"{int(tempo / 60)} {Res.trad(interaction=interaction,str='minutos')}"

    await interaction.followup.send(Res.trad(interaction=interaction,str="message_segurança_antalt_confirmado").format(tempo_formatado,ação,"<a:Brix_Check:1371215835653210182>" if notificar else "<a:Brix_Negative:1371215873637093466>"))
    

  @segurancaantalt.autocomplete("tempo")
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

#COMANDO ANTIALT DESATIVAR
  @anti_alt.command(name="desativar",description='🔒⠂Desative o sistema contra contas novas no servidor.')
  @commands.has_permissions(manage_guild=True)
  async def segurancaantaltdesativar(self,interaction: discord.Interaction):
    if await Res.print_brix(comando="boasvindasdesativar",interaction=interaction):
      return
    if interaction.guild is None:
      await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyservers"),delete_after=20,ephemeral=True)
      return
    
    if not interaction.permissions.manage_guild:
      await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro"),delete_after=10,ephemeral=True)
      return
    
    await interaction.response.defer(ephemeral=True)
    item = {"seguranca.antialt":interaction.channel.id}
    BancoServidores.delete_field(interaction.guild.id,item)
    await interaction.followup.send(Res.trad(interaction=interaction,str="message_segurança_antalt_desativado"))



  #COMANDO BOAS VINDAS AJUDAR
  @anti_alt.command(name="ajuda",description='🔒⠂Dicas de uso do anti-alt.')
  async def segurancaantaltdicas(self,interaction: discord.Interaction):
    await interaction.response.send_message(Res.trad(interaction=interaction,str="message_segurança_antalt_dica"),delete_after=60)

























# ======================================================================

async def setup(client:commands.Bot) -> None:
  await client.add_cog(boasvindas(client))