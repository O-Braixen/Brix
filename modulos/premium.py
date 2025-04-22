import discord,os,asyncio,time,datetime,pytz,re
from functools import partial
from discord.ext import commands,tasks
from discord import app_commands
from modulos.connection.database import BancoUsuarios
from modulos.essential.respostas import Res
from dotenv import load_dotenv


load_dotenv(os.path.join(os.path.dirname(__file__), '.env')) #load .env da raiz
donoid = int(os.getenv("DONO_ID")) 
BH_id = int(os.getenv('id_servidor_bh'))
BH_id_boost_channel = int(os.getenv('BH_id_boost_channel'))







#FUNÇÂO DE DAR PREMIUM A MEMBRO
async def liberarpremium(self, ctx, user, args, boost):
    dado = BancoUsuarios.insert_document(user)
    message = f"## 🦊 - Brix Premium\nUsuario: {user.mention}"
    try:
        premium = dado.get('premium', datetime.datetime.now().astimezone(pytz.timezone('America/Sao_Paulo')))
    except:
        premium = datetime.datetime.now().astimezone(pytz.timezone('America/Sao_Paulo'))

    premium += datetime.timedelta(days=args)
    item = {"premium": premium}

    try:
        BancoUsuarios.update_document(user, item)
        message += "\n:white_check_mark: - Premium Ativado."
        descricao_dm = (Res.trad(str=f"message_premiumboost_{args}_send_dm").format(args, int(premium.timestamp())) if boost else Res.trad(user=user, str="message_premium_send_dm").format(int(premium.timestamp())) )
        embed_para_usuario = discord.Embed(            colour=discord.Color.yellow(),            description=descricao_dm     )
        embed_para_usuario.set_thumbnail(url="https://cdn.discordapp.com/emojis/1318962131567378432.png")

        try:
            await user.send(embed=embed_para_usuario)
            message += f"\n:white_check_mark: - DM Enviada.\nDuração: <t:{int(premium.timestamp())}:R>"
        except:
            message += f"\n:x: - DM não enviada.\nDuração: <t:{int(premium.timestamp())}:R>"
            print(f"Falha ao enviar DM para {user.id} - {user.name}")

        print(f"Premium ativo para: {user.id} - {user.name}")

    except Exception as e:
        message += "\n:x: - Falha ao ativar Premium."
        print(f"Erro ao atualizar documento no banco: {e}")

    resposta = discord.Embed(color=discord.Color.yellow(), description=message)
    try:
        await ctx.send(embed=resposta)
    except:
        print("Falha ao enviar mensagem no chat para avisar do premium.")











class premium(commands.Cog):
  def __init__(self, client: commands.Bot):
    self.client = client





    
  @commands.Cog.listener()
  async def on_ready(self):
    print("💎  -  Modúlo Premium carregado.")
    
    if not self.verificar_premium.is_running():
      await asyncio.sleep(60) #1800
      self.verificar_premium.start()
  






  @commands.Cog.listener()
  async def on_message(self,message):

    if message.guild and message.guild.id == BH_id:
      if message.channel.name == "💜┃boosts" and message.author != self.client.user:
        # Definindo a expressão regular para capturar a ID do usuário e a quantidade de boosts
        match = re.match(r'<@(\d+)> virou (\d)x booster', message.content)
        if match:
          user_id = match.group(1)
          boost_count = match.group(2)

            # Imprimindo as variáveis extraídas
          user = await self.client.fetch_user(user_id)
          if boost_count == '1': #premium de 7 Dias

            #envia o embed de notificação no chat geral
            canal = self.client.get_channel(BH_id_boost_channel)
            embed = discord.Embed(colour=discord.Color.from_str('#f78da7'),description=f"### Um Boost a gente nunca esquece né {user.name}\n**Muito obrigado pelo boost {user.mention}!!!**\nSabia isso nos ajuda a **manter o servidor** cada vez melhor e nos **incentiva** cada vez mais então por isso **manteremos esse momento** aqui salvo neste chat para que você possa se gabar.\n\nConfira todos os **Benefícios** em <#888402749887217685> na opção **Vip/Nitro**\nE você ganhou alguns dias da **minha assinatura premium** como cortesia ~kyuuu.\nAproveite!!!" )
            embed.set_thumbnail(url="https://emoji.discord.st/emojis/548e713f-cfd9-4c49-9caa-d0dbe3dcec91.gif")
            messageenviada = await canal.send(f"Aviso para {user.mention}!!!!!!",embed=embed)
            await messageenviada.add_reaction('<a:BH_nitro:1154334548478402650>')

            #ativa o premium do cara
            await liberarpremium(self,None,user,7,True)
          elif boost_count == '2': #premium 24 Dias
            await asyncio.sleep(4)
            await liberarpremium(self,None,user,24,True) 






#FUNÇÂO DE VERIFICAÇÃO DE ASSINANTES PREMIUM
  @tasks.loop(minutes=10) #6H loop 6*60*60
  async def verificar_premium(self): 
    await asyncio.sleep(600)
    try:
      filtro = {"premium": {"$exists":True}}
      dado = BancoUsuarios.select_many_document(filtro)
      for member in dado:
          fuso = pytz.timezone('America/Sao_Paulo')
          if datetime.datetime.now().astimezone(fuso) > member['premium'].replace(tzinfo=fuso):
            membro = await self.client.fetch_user(member['_id'])
            item = {"premium": datetime.datetime.now()}
            BancoUsuarios.delete_field(membro,item)
            print(f"o premium de {membro.name} acabou!")
            try:
              await membro.send(Res.trad(user=membro ,str="message_premium_encerrado"))
            except:
              print(f"DM de {membro.name} está fechada!")
      return
    except Exception as e:
      print(f"erro na verificação de assinantes premium.\n{e}")
      return
  





#COMANDO DAR VIP
  @commands.command(name="givepremium", description='Ativa o premium para um usuario...')
  async def premiumonwer(self,ctx,user:discord.User = None,*,args:int = None):
    try:
        await ctx.message.delete()
    except:
        print("falta de permissão na comunidade")
    if ctx.author.id == donoid:
      if user is None or args is None:
        await ctx.send(Res.trad(guild=ctx.guild.id,str="message_erro_notargument").format("use ```-givepremium @dousuario 3```"))
        return
      else:
        await liberarpremium(self,ctx,user,args,boost=False)
    else:
      await ctx.send(Res.trad(guild=ctx.guild.id,str="message_erro_onlyowner"))
      return






#COMANDO DAR VIP
  @commands.command(name="showpremium", description='Ativa o premium para um usuario...')
  async def premiumshow(self,ctx):
    try:
        await ctx.message.delete()
    except:
        print("falta de permissão na comunidade")
    if ctx.author.id == donoid:
      filtro = {"premium": {"$exists": True}}
      dados = BancoUsuarios.select_many_document(filtro).sort('premium',-1)
      lista_itens = []
      lista_itens.extend([f"<@{item['_id']}> - termina <t:{int(item['premium'].timestamp())}:R>" for item in dados])

      embed = discord.Embed(title="Assinaturas Premium Atuais", color=discord.Color.yellow()) # Cor verde

      for i in range(0, len(lista_itens), 15):
        mensagem = "\n".join(lista_itens[i:i + 15])
        embed.add_field(name="\u200b", value=mensagem, inline=False) # Adicionando um campo ao embed

      await ctx.send(embed=embed) # Enviando o embed
    else:
      await ctx.send(Res.trad(guild = ctx.guild.id,str="message_erro_onlyowner"))
      return






#GRUPO Premium
  premium = app_commands.Group(name="premium",description="Comandos premium do Brix.",allowed_installs=app_commands.AppInstallationType(guild=True,user=True),allowed_contexts=app_commands.AppCommandContext(guild=True, dm_channel=False, private_channel=False))



#CONSULTAR INFORMAÇÕES SOBRE A ASSINATURA PREMIUM.
  @premium.command(name="info", description='💎⠂Envia informações sobre o plano premium.')
  async def premiuminfo(self,interaction: discord.Interaction):
    if await Res.print_brix(comando="premiuminfo",interaction=interaction):
      return
    dado = BancoUsuarios.insert_document(interaction.user)
    view = discord.ui.View()
    adquirir = discord.ui.Button(label="Adquirir Premium",emoji="<:Graveto:1318962131567378432>",style=discord.ButtonStyle.green)
    view.add_item(item=adquirir)

    try:
      assinatura = discord.ui.Button(label=f"Ativo até {dado['premium'].astimezone(pytz.timezone('America/Sao_Paulo')).strftime('%d/%m/%Y - %H:%M')}",style=discord.ButtonStyle.gray,disabled=True)
    except:
      assinatura = discord.ui.Button(label="Sem Assinatura",style=discord.ButtonStyle.red,disabled=True)
    view.add_item(item=assinatura)

    async def botãopremium(self,interaction):
      await interaction.response.send_message("Adquira esse item diretamente no atendimento da [braixen's House](https://dsc.gg/braixen) em <#980610937851609128> opção **Brix Premium**",ephemeral = True)

    adquirir.callback = partial(botãopremium,interaction)
    await interaction.response.send_message(file = discord.File("imagens/financeiro/banner premium.png"),view=view)
    

    
#NEGOCIAR A COMPRAR DO PREMIUM COM AS MOEDAS DO BOT
  @premium.command(name="negociar", description='💎⠂Compre dias adicionais com braixencoin ou gravetos.')
  async def premiumnegociar(self,interaction: discord.Interaction):
    if await Res.print_brix(comando="premiumnegociar",interaction=interaction):
      return
    self.user = interaction.user
    view = discord.ui.View()
    braixencoin = discord.ui.Button(label="Adquirir com BC",emoji="<:BraixenCoin:1272655353108103220>",style=discord.ButtonStyle.gray)
    view.add_item(item=braixencoin)
    gravetocoin = discord.ui.Button(label="Adquirir com GC",emoji="<:Graveto:1318962131567378432>",style=discord.ButtonStyle.green)
    view.add_item(item=gravetocoin)

    async def buypremium(self,interaction: discord.Interaction,moeda,valor):
      if interaction.user != self.user:
        await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_interacaoalheia"),delete_after=10,ephemeral=True)
        return
      else: 
        dado = BancoUsuarios.insert_document(interaction.user)
        emoji = '<:BraixenCoin:1272655353108103220>' if moeda == 'braixencoin' else '<:Graveto:1318962131567378432>'

        if dado[moeda] < valor:
          await interaction.response.send_message(Res.trad(interaction=interaction, str="message_financeiro_saldo_insuficiente"),ephemeral=True)
          return
        else:
          novosaldo = dado[moeda] - valor
          insert = {moeda: novosaldo}
          BancoUsuarios.update_document(interaction.user,insert)
          await interaction.response.send_message(Res.trad(interaction=interaction, str="message_premium_confirm").format(novosaldo,emoji),ephemeral = True)
          await liberarpremium(self,interaction.channel,interaction.user,2,False)

    braixencoin.callback = partial(buypremium,self,moeda = 'braixencoin',valor = 100000)
    gravetocoin.callback = partial(buypremium,self,moeda = 'graveto',valor = 1800)
    
    await interaction.response.send_message(file = discord.File("imagens/financeiro/banner premium negociar.png"),view=view)









#COMANDO DE ADQUIRIR A ASSINATURA PREMIUM COMO TESTE POR 15 DIAS
  @premium.command(name="testar", description='💎⠂Ganhe alguns dias de teste da minha assinatura premium.')
  async def premiumtestar(self,interaction: discord.Interaction):
    if await Res.print_brix(comando="premiumnegociar",interaction=interaction):
      return
    dado = BancoUsuarios.insert_document(interaction.user)
    #verifica se o cara já realizou teste antes
    if 'testepremium' in dado:
      botaoteste = discord.ui.Button(label="Sem teste disponível",style=discord.ButtonStyle.red,disabled=True)
    else:
      botaoteste = discord.ui.Button(label="testar por 15 dias",emoji="💎",style=discord.ButtonStyle.green)
    
    self.user = interaction.user
    view = discord.ui.View()
    view.add_item(item=botaoteste)

    #liberar assinatura teste
    async def liberarteste(self,interaction: discord.Interaction):
      if interaction.user != self.user:
        await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_interacaoalheia"),delete_after=10,ephemeral=True)
        return
      view = discord.ui.View.from_message(interaction.message)
      for item in view.children:
        item.disabled = True
      await interaction.response.edit_message(view=view)
      
      fuso = pytz.timezone('America/Sao_Paulo')
      insert = {'testepremium': datetime.datetime.now().astimezone(fuso)}
      BancoUsuarios.update_document(interaction.user,insert)
      await interaction.followup.send(Res.trad(interaction=interaction, str="message_premium_teste"),ephemeral = True)
      await liberarpremium(self,interaction.channel,interaction.user,15,False)
    
    botaoteste.callback = partial(liberarteste,self)
    await interaction.response.send_message(file = discord.File("imagens/financeiro/banner premium testar.png"),view=view)







async def setup(client:commands.Bot) -> None:
  await client.add_cog(premium(client))