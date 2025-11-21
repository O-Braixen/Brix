import discord,os,asyncio,time,json,uuid,datetime,pytz,random
from discord.ext import commands
from discord import app_commands
from src.services.connection.database import BancoUsuarios,BancoEventos,BancoLoja , BancoFinanceiro
from src.services.essential.respostas import Res
from src.services.modules.premium import liberarpremium


#ID de identificação
donoid = int(os.getenv("DONO_ID")) #acessa e define o id do dono
EVENTO_ATIVO = True
BANNER_RECOMPENSA = "natalxen-2025-eventoexclusive"




#FUNÇÂO DE ENTREGAR RECOMPENSAS.
async def entregar_recompensa(self, interaction: discord.Interaction, tipo):
  if tipo is True:  # SIGNIFICA QUE O USUÁRIO ESTÁ ABRINDO UM ITEM PRÓPRIO
        # Sorteador para Braixencoin ou tempo de assinatura premium
    recompensa = random.choice(["Braixencoin", "Assinatura Premium"])
    if recompensa == "Braixencoin":
      dados_do_membro = BancoUsuarios.insert_document(interaction.user)

      quantidade = random.randint(1000, 5000)  
      saldo = dados_do_membro['braixencoin']
      saldonovo = saldo + quantidade

      item = {"braixencoin": saldonovo}
      BancoUsuarios.update_document(interaction.user,item)
      BancoFinanceiro.registrar_transacao(user_id=interaction.user.id,tipo="ganho",origem="Natalxen",valor=quantidade,moeda="braixencoin",descricao="Presente de Evento Natalxen")

      await interaction.followup.send(Res.trad(interaction=interaction, str="natalxen_evento_entrega_propria_braixencoin").format(quantidade) )
    else:  # Assinatura Premium
      dias = random.randint(1, 2)  # Exemplo: duração de 1 a 3 dias
      await interaction.followup.send( Res.trad(interaction=interaction, str="natalxen_evento_entrega_propria_premium").format(dias) )
      await liberarpremium(self,interaction.channel,interaction.user,dias,False)

  else:  # USUÁRIO ESTÁ ABRINDO UM PRESENTE
        # Sorteador para Braixencoin, Assinatura Premium ou Banner
    recompensa = random.choice(["Braixencoin", "Assinatura Premium", "Banner"])
    if recompensa == "Braixencoin":
      dados_do_membro = BancoUsuarios.insert_document(interaction.user)

      quantidade = random.randint(15000, 50000)  
      saldo = dados_do_membro['braixencoin']
      saldonovo = saldo + quantidade

      item = {"braixencoin": saldonovo}
      BancoUsuarios.update_document(interaction.user,item)
      BancoFinanceiro.registrar_transacao(user_id=interaction.user.id,tipo="ganho",origem="Natalxen",valor=quantidade,moeda="braixencoin",descricao="Presente de Evento Natalxen")

      await interaction.followup.send(Res.trad(interaction=interaction, str="natalxen_evento_entrega_presente_braixencoin").format(quantidade) )

    elif recompensa == "Assinatura Premium":
      dias = random.randint(3, 7)  # Exemplo: duração de 3 a 7 dias
      await interaction.followup.send(  Res.trad(interaction=interaction, str="natalxen_evento_entrega_presente_premium").format(dias) )
      await liberarpremium(self,interaction.channel,interaction.user,dias,False)

    else:  # Banner
      dados_do_membro = BancoUsuarios.insert_document(interaction.user)

      itensdousuario = []
      try:
        for item_id in dados_do_membro['backgrouds'].items():
          itensdousuario.append(item_id[0])
      except:
        itensdousuario = [None]

      filtro = {"graveto": {"$ne": 0}}
      itensloja = BancoLoja.select_many_document(filtro)
      try:
        itens_disponiveis = [item for item in itensloja if item["_id"] not in itensdousuario]
        itenescolhido = random.choice(itens_disponiveis)
        # Atualiza o fundo do usuário no banco de dados
        insert = {"backgroud": itenescolhido['_id'],f"backgrouds.{itenescolhido['_id']}": itenescolhido['_id']}
        BancoUsuarios.update_document(interaction.user, insert)

        await interaction.followup.send( Res.trad(interaction=interaction, str="natalxen_evento_entrega_presente_banner").format(itenescolhido['name']) )
      except:
        dias = 5
        await interaction.followup.send( Res.trad(interaction=interaction, str="natalxen_evento_entrega_presente_premium").format(dias) )
        await liberarpremium(self,interaction.channel,interaction.user,dias,False)





#parte da classe do evento
class natalxen(commands.Cog):
  def __init__(self, client: commands.Bot):
    self.client = client

  @commands.Cog.listener()
  async def on_bot_ready(self):
    print("🎄  -  Modulo de natalxen carregado.")
  












# COMANDO POR PREFIXO PARA ATIVAR OU DESATIVAR O EVENTO



                  #COMANDO ATIVAR OU DESATIVAR EVENTO
  @commands.command(name="evento",description='Ative ou desative o evento global de Brix.')
  async def statusevento(self, ctx ):
      global EVENTO_ATIVO
      if ctx.author.id == donoid:
        print (f"Usuario: { ctx.author.name} usou Status Evento")
        # VERIFICA A SITUAÇÃO DO EVENTO, SE TA ATIVO DESATIVA E VICE VERSA
        if EVENTO_ATIVO is True:
          EVENTO_ATIVO = False
          await ctx.send("<:BH_Braix_ew:1154338599496585226> - Evento Desativado Kyuu~~")
        else:
          EVENTO_ATIVO = True
          await ctx.send(":BH_Braix_Like:1154338777226031186> - Evento Ativo Kyuu~~")
      else:
        return await ctx.send(Res.trad(guild=ctx.guild.id,str="message_erro_onlyowner"))
        















  #Fazer coisas aqui nessa parte, lembrar de respeitar a organização
  

  #GRUPO DO EVENTO
  evento = app_commands.Group(name="natalxen",description="Comandos de evento de natal do Brix.")


  #COMANDO enviar do correio elegante
  @evento.command(name="daily", description="🎄⠂Colete seu presente diário.")
  async def natalxen_daily ( self , interaction: discord.Interaction ):
    if EVENTO_ATIVO: 
      await interaction.response.defer ()

      fuso = pytz.timezone('America/Sao_Paulo')
      now = datetime.datetime.now().astimezone(fuso)
      datahoje = now.strftime("%d/%m/%Y")

      membro = interaction.user
      dados_do_membro = BancoEventos.insert_document(membro)

      try:
        daily = dados_do_membro['natal-daily']
      except:
        daily = None

      if daily is None or daily != datahoje:
        presenteentregue = random.randint(1, 3) 
        BancoEventos.update_inc(membro, {"giftscoletados": presenteentregue, "totalcoletados": presenteentregue})
        item = {"natal-daily": datahoje}
        BancoEventos.update_document(membro,item)
        
        if dados_do_membro['totalcoletados'] >= 30 and dados_do_membro['brinde-entregue'] is False:
          # Atualiza o fundo do usuário no banco de dados
          insert = {"backgroud": BANNER_RECOMPENSA,f"backgrouds.{BANNER_RECOMPENSA}": BANNER_RECOMPENSA}
          BancoUsuarios.update_document(interaction.user, insert)
          item = {"brinde-entregue": True}
          BancoEventos.update_document(membro,item)
          await interaction.followup.send(Res.trad(interaction=interaction, str="natalxen_evento_recompensa"))
        else:
          await interaction.followup.send(Res.trad(interaction=interaction, str="natalxen_evento_daily_coleta").format(presenteentregue))
      else:
        await interaction.followup.send(Res.trad(interaction=interaction, str="natalxen_evento_daily_negacao"))

    else:
      await interaction.response.send_message(Res.trad(interaction=interaction, str="natalxen_evento_encerrado"), delete_after=30 ,ephemeral=True)
      return

    


    

  #COMANDO Consultar mensagem enviada Owner apenas
  @evento.command(name="consulta", description="🎄⠂Consulte todos os seus presentes.")
  async def natalxen_consulta (self,interaction: discord.Interaction):
    if EVENTO_ATIVO: 
      await interaction.response.defer ()
      retornobanco = BancoEventos.insert_document(interaction.user.id)
      resposta = discord.Embed(colour=discord.Color.yellow(),
        description= Res.trad(interaction=interaction, str="natalxen_evento_consulta").format(retornobanco['giftscoletados'] , retornobanco['giftspresentes'] , retornobanco['totalcoletados'])
      )
      resposta.set_thumbnail(url=" https://brixbot.xyz/cdn/brix_evento_natalxen_box.png ") 
      resposta.set_footer(text=Res.trad(interaction=interaction, str="natalxen_evento_consulta_footer"))
                
      await interaction.followup.send(embed=resposta)

    else:
      await interaction.response.send_message(Res.trad(interaction=interaction, str="natalxen_evento_encerrado"), delete_after=30 ,ephemeral=True)
      return
  
  #COMANDO Consultar mensagem enviada Owner apenas
  @evento.command(name="ajuda", description="🎄⠂Ajuda sobre o evento de natal na BH.")
  async def natalxen_ajuda (self,interaction: discord.Interaction):
    if EVENTO_ATIVO: 
      await interaction.response.send_message(Res.trad(interaction=interaction, str="natalxen_evento_help"))
    else:
      await interaction.response.send_message(Res.trad(interaction=interaction, str="natalxen_evento_encerrado"), delete_after=30 ,ephemeral=True)
      return

    

#COMANDO enviar do correio elegante
  @evento.command(name="presentear", description="🎄⠂Envie um presente.")
  @app_commands.choices(anonimo=[app_commands.Choice(name="Sim", value="True"),app_commands.Choice(name="Não", value="False")])
  @app_commands.describe(destinatario ="Selecione alguém para enviar uma mensagem.", anonimo = "enviar anonimamente?")
  async def natalxen_presentear ( self , interaction: discord.Interaction, anonimo : app_commands.Choice[str] , destinatario : discord.User = None):
    if EVENTO_ATIVO: 
      await interaction.response.defer (ephemeral=True)
      retornobanco = BancoEventos.insert_document(interaction.user.id)
      if retornobanco["giftscoletados"] == 0:
        await interaction.followup.send(Res.trad(interaction=interaction, str="natalxen_evento_presentear_sempresente"))
        return

      else:

        if destinatario is None:
          #LOGICA DE SORTEIO DE USUARIO
          filtro = {"_id": {"$exists":True}}
          dados = BancoEventos.select_many_document(filtro)
          id_para_evitar = interaction.user.id

          dados_filtrados = [dado["_id"] for dado in dados if dado["_id"] != id_para_evitar]
          if dados_filtrados:
            selecionado = random.choice(dados_filtrados)
            usuario = await self.client.fetch_user(selecionado)
          else:
            await interaction.followup.send(Res.trad(interaction=interaction, str="natalxen_evento_presentear_aleatorio_erro")) #Enviado com Sucesso indicar cobrança
            return
        elif destinatario == interaction.user:
          await interaction.followup.send(Res.trad(interaction=interaction, str="natalxen_evento_presentear_si_mesmo"))  #Enviado com Sucesso indicar cobrança
          return
        else:
          usuario = destinatario

        resposta = discord.Embed(colour=discord.Color.yellow(),  description=Res.trad(interaction=interaction, str="natalxen_evento_presentear_msg"))
        resposta.set_thumbnail(url=" https://brixbot.xyz/cdn/brix_evento_natalxen_box.png ") 
      
        if (anonimo.value == "False"):
            footer = Res.trad(interaction=interaction, str="natalxen_envio_enviado_por").format(interaction.user.name , interaction.user.id)
        else:
            footer = Res.trad(interaction=interaction, str="natalxen_envio_anonimo")

        resposta.set_footer(text=footer)
        BancoEventos.update_inc(interaction.user.id, {"giftscoletados": -1})
        BancoEventos.update_inc(usuario, {"giftspresentes": 1})
        try:
          await usuario.send(embed=resposta) # mensagem ao membro
          await interaction.followup.send( Res.trad(interaction=interaction, str="natalxen_envio_concluido").format(usuario.name)) #Enviado com Sucesso indicar cobrança
        except:
          await interaction.followup.send(Res.trad(interaction=interaction, str="natalxen_envio_concluido_sem_aviso").format(usuario.name)) # DM do membro fechada, nenhuma cobrança foi feita
    else:
      await interaction.response.send_message(Res.trad(interaction=interaction, str="natalxen_evento_encerrado"), delete_after=30 ,ephemeral=True)
      return

  aberturagift = app_commands.Group(name="abrir",description="Comandos de cargo temporario do Brix.",parent=evento)

#COMANDO ABRIR PRESENTE COLETADO
  @aberturagift.command(name="coletado", description="🎄⠂Abra um presente que foi coletado.")
  async def natalxen_abrircoletado ( self , interaction: discord.Interaction):
    if EVENTO_ATIVO: 
      await interaction.response.defer ()
      retornobanco = BancoEventos.insert_document(interaction.user.id)
      if retornobanco["giftscoletados"] == 0:
        await interaction.followup.send(Res.trad(interaction=interaction, str="natalxen_evento_coletado_sempresente"))
        return
      BancoEventos.update_inc(interaction.user.id, {"giftscoletados": -1})
      await entregar_recompensa(self,interaction,True)

    else:
      await interaction.response.send_message(Res.trad(interaction=interaction, str="natalxen_evento_encerrado"), delete_after=30 ,ephemeral=True)
      return



#COMANDO ABRIR PRESENTE RECEBIDO
  @aberturagift.command(name="recebido", description="🎄⠂Abra um presente que você ganhou.")
  async def natalxen_abrirrecebido ( self , interaction: discord.Interaction):
    if EVENTO_ATIVO: 
      await interaction.response.defer ()
      retornobanco = BancoEventos.insert_document(interaction.user.id)
      if retornobanco["giftspresentes"] == 0:
        await interaction.followup.send(Res.trad(interaction=interaction, str="natalxen_evento_recebido_sempresente"))
        return
      BancoEventos.update_inc(interaction.user.id, {"giftspresentes": -1})
      await entregar_recompensa(self,interaction,False)

    else:
      await interaction.response.send_message(Res.trad(interaction=interaction, str="natalxen_evento_encerrado"), delete_after=30 ,ephemeral=True)
      return


async def setup(client:commands.Bot) -> None:
  await client.add_cog(natalxen(client))