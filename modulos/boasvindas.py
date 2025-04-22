import discord,os,asyncio,time,random
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from modulos.connection.database import BancoServidores
from modulos.essential.respostas import Res


load_dotenv(os.path.join(os.path.dirname(__file__), '.env')) #load .env da raiz
idbh = int(os.getenv("id_servidor_bh"))








class boasvindas(commands.Cog):
  def __init__(self, client: commands.Bot):
    self.client = client
    self.member_join_error_count = {}







  @commands.Cog.listener()
  async def on_ready(self):
    print("🏠  -  Modúlo Boasvindas carregado.")
  





  @commands.Cog.listener()
  async def on_member_join(self,member):
    print(f"membro {member.id} entrou na {member.guild.id} - {member.guild.name} ")


    # Respostas
    membro = member.mention
    resp_macho = [ f"Oiii, bem-vindo, raposa {membro}! Espero que se divirta por aqui, kyu~",f"Salveee! Seja muito bem-vindo, {membro}, à minha casa mágica. Fique à vontade, kyu!",f"O {membro} aterrissou aqui com estilo! Seja bem-vindo, kyu!"]
    resp_femea = [f"Oiiieee! Bem-vindaaa, raposa {membro}! Que bom ter você aqui, kyu~",    f"Bem-vinda, {membro}, à minha humilde residência! Sinta-se em casa, kyu! <:BH_Braix_Happy:1154418207071940778>",    f"Oii, bem-vinda, {membro}! Fique à vontade e aproveite a magia do lar, kyu~"]
    resp_indefinido = [    f"Olá, bem-vinde, raposa {membro}! Espero que curta o aconchego da minha casa, brai~",    f"Bem-vinde, {membro}, à minha casinha mágica! Fique à vontade, kyu!",    f"Oii, bem-vinde, {membro}! Aproveite seu tempo por aqui, kyu~"]
    resp_normal = [    f"Boas-vindas, raposa {membro}! Aproveite a estadia e toda a magia, kyu~",    f"Boas-vindas, {membro}! Minha casinha é sua casinha, fique à vontade, kyu! <:BH_Braix_Happy:1154418207071940778>",    f"Oiii, boas-vindas, {membro}! Espero que se sinta em casa nessa pequena toca que chamo de lar, kyu! <:Braix:1272653348306419824>"]
    resp_naoverificado = [    f"Boas-vindas, raposa {membro}! Não se esqueça de concluir seu registro em <id:customize>, kyu!",    f"Boas-vindas, {membro}! Sinta-se à vontade na minha casinha. Ah, lembre-se de finalizar seu registro em <id:customize>, kyu!",    f"Oiii, {membro}! Boas-vindas! Complete seu registro em <id:customize> pra aproveitar tudo que a comunidade tem pra oferecer, kyu~"]

    


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
    
    
    
    else:
      #verificar se o servidor tem boas vindas habilitado
      dados = BancoServidores.insert_document(member.guild.id)
      if dados and 'boasvindas' in dados:
        try: 
          canal = await self.client.fetch_channel(dados['boasvindas'].get('canal'))
          mensagem_boas_vindas = dados['boasvindas'].get('mensagem')
          tempo_delete = dados['boasvindas'].get('deletar', 0)
          if canal:
            mensagem_final = (mensagem_boas_vindas
                      .replace('@user', member.mention)
                      .replace('guildsize', str(member.guild.member_count))
                      .replace('guild', member.guild.name)
                      .replace('userid', str(member.id)))
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
      else: return














#GRUPO DE COMANDOS DE IMAGENS BOT 
  boavinda=app_commands.Group(name="bem-vindo",description="Comandos de boas-vindas integrados no Brix.",allowed_installs=app_commands.AppInstallationType(guild=True,user=False),allowed_contexts=app_commands.AppCommandContext(guild=True, dm_channel=False, private_channel=False))



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
    
    elif interaction.permissions.manage_guild:
      await interaction.response.defer(ephemeral=True)
      if deletar is None:
        deletar = 0
      item = {"boasvindas.canal": canal.id,"boasvindas.mensagem": mensagem, 'boasvindas.deletar': deletar}
      BancoServidores.update_document(interaction.guild.id,item)
      try:
        mensagemteste = await canal.send('kyu')
        await asyncio.sleep(0.1)
        await mensagemteste.delete()
        await interaction.followup.send(Res.trad(interaction=interaction,str="message_boasvindas_confirmado"))
      except:
        await interaction.followup.send(Res.trad(interaction=interaction,str="message_erro_permissao"))

    else: await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro"),delete_after=10,ephemeral=True)
  

#COMANDO BOAS VINDAS DESATIVAR
  @boavinda.command(name="desativar",description='🦊⠂Desative as boas-vindas na sua comunidade.')
  @commands.has_permissions(manage_guild=True)
  async def boasvindasdesativar(self,interaction: discord.Interaction):
    if await Res.print_brix(comando="boasvindasdesativar",interaction=interaction):
      return
    if interaction.guild is None:
      await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyservers"),delete_after=20,ephemeral=True)
      return
    
    elif interaction.permissions.manage_guild:
      await interaction.response.defer(ephemeral=True)
      item = {"boasvindas":interaction.channel.id}
      BancoServidores.delete_field(interaction.guild.id,item)
      await interaction.followup.send(Res.trad(interaction=interaction,str="message_boasvindas_desativado"))

    else: await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro"),delete_after=10,ephemeral=True)



  #COMANDO BOAS VINDAS DESATIVAR
  @boavinda.command(name="ajuda",description='🦊⠂Dicas de uso do boas-vindas.')
  async def boasvindasdicas(self,interaction: discord.Interaction):
    await interaction.response.send_message(Res.trad(interaction=interaction,str="message_boasvindas_dica"),delete_after=60)















async def setup(client:commands.Bot) -> None:
  await client.add_cog(boasvindas(client))