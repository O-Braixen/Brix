import discord,os,asyncio,time,datetime,pytz,re , base64 , io
from functools import partial
from discord.ext import commands,tasks
from discord import app_commands
from src.services.connection.database import BancoUsuarios , BancoFinanceiro , BancoPagamentos
from src.services.essential.respostas import Res
from src.services.essential.API_Mercadopago import criar_link_pagamento , update_pagamentos
from PIL import Image, ImageDraw, ImageFont , ImageOps
from dotenv import load_dotenv


load_dotenv(os.path.join(os.path.dirname(__file__), '.env')) #load .env da raiz
donoid = int(os.getenv("DONO_ID")) 
BH_id = int(os.getenv('id_servidor_bh'))
BH_id_boost_channel = int(os.getenv('BH_id_boost_channel'))






  
#FUNÇÂO DE DAR PREMIUM A MEMBRO
"""async def liberarpremium(self, ctx, user, args, boost, presente = None):
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
        if presente:
          descricao_dm = Res.trad(str="message_premium_presente_send_dm").format(args , presente.mention, int(premium.timestamp()))
        else:
          descricao_dm = (Res.trad(str=f"message_premiumboost_{args}_send_dm").format(args, int(premium.timestamp())) if boost else Res.trad(user=user, str="message_premium_send_dm").format(int(premium.timestamp())) )
        embed_para_usuario = discord.Embed(            colour=discord.Color.yellow(),            description=descricao_dm     )
        embed_para_usuario.set_thumbnail(url="https://cdn.discordapp.com/emojis/1318962131567378432")

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
        print("Falha ao enviar mensagem no chat para avisar do premium.")"""





#FUNÇÂO DE DAR PREMIUM A MEMBRO
async def liberarpremium(self, ctx, user, args, boost, presente = None):
    tz = pytz.timezone('America/Sao_Paulo')
    agora = datetime.datetime.now().astimezone(tz)

    # pega dado do banco ou cria novo
    dado = BancoUsuarios.insert_document(user)
    premium = dado.get("premium", agora)

    # adiciona dias
    premium += datetime.timedelta(days=args)
    BancoUsuarios.update_document(user, {"premium": premium})
    
    message = f"## 🦊 - Brix Premium\nUsuario: {user.mention}"


    # mensagem DM pro usuário
    if presente:
        descricao_dm = Res.trad(str="message_premium_presente_send_dm").format( args, presente.mention, int(premium.timestamp()) )
    elif boost:
        descricao_dm = Res.trad(str=f"message_premiumboost_{args}_send_dm").format( args, int(premium.timestamp()) )
    else:
        descricao_dm = Res.trad(user=user, str="message_premium_send_dm").format( int(premium.timestamp()) )

    embed_para_usuario = discord.Embed( colour=discord.Color.yellow(), description=descricao_dm ).set_thumbnail( url="https://cdn.discordapp.com/emojis/1318962131567378432" )


    # tentativa de enviar DM
    try:
      await user.send(embed=embed_para_usuario)
      message += f":white_check_mark: - DM Enviada.\nDuração: <t:{int(premium.timestamp())}:R>"
    except:
      message += f":x: - DM não enviada.\nDuração: <t:{int(premium.timestamp())}:R>"
      print(f"Falha ao enviar DM para {user.id} - {user.name}")

    if presente:
      try:
          descricao_presenteador = Res.trad(str="message_premium_presenteador_send_dm").format( user.mention ,args )
          embed_para_presenteador = discord.Embed( colour=discord.Color.yellow(), description=descricao_presenteador ).set_thumbnail( url="https://cdn.discordapp.com/emojis/1318962131567378432" )
          await presente.send(embed=embed_para_presenteador)
          message += ":white_check_mark: - Mensagem enviada ao presenteador."
      except:
          message += ":x: - Não consegui enviar DM ao presenteador."

    print(f"Premium ativo para: {user.id} - {user.name}")

    # resposta no chat
    resposta = discord.Embed( color=discord.Color.yellow(), description=message)
    try:
      await ctx.send(embed=resposta)
    except:
      print("Falha ao enviar mensagem no chat para avisar do premium.")












#Função exibir item loja
async def comprarpremium(self, interaction: discord.Interaction, quant, presente_para: discord.User = None):
  await interaction.original_response()
  valor = 4.99
  if quant == 1:
      texto = f"{quant} {Res.trad(interaction=interaction,str='mes')}"
  else:
      texto = f"{quant} {Res.trad(interaction=interaction,str='meses')}"

  view = discord.ui.View()

  if quant == 1:
      menos = discord.ui.Button(label="",emoji="<:menos:1272649363168170176>",style=discord.ButtonStyle.gray, disabled=True)
  else:
      menos = discord.ui.Button(label="",emoji="<:menos:1272649363168170176>",style=discord.ButtonStyle.gray)
  view.add_item(item=menos)

  plano = discord.ui.Button(label=f"{texto} ({round(valor*quant , 2)})",style=discord.ButtonStyle.gray,  disabled=True)
  view.add_item(item=plano)

  if quant >= 12:
      mais = discord.ui.Button(label="",emoji="<:mais:1272649351780372602>",style=discord.ButtonStyle.gray, disabled=True)
  else:
      mais = discord.ui.Button(label="",emoji="<:mais:1272649351780372602>",style=discord.ButtonStyle.gray)
  view.add_item(item=mais)

  adquirir_assinatura = discord.ui.Button(label="Comprar",emoji="🦊",style=discord.ButtonStyle.green,row=2)
  view.add_item(item=adquirir_assinatura)


  async def mover_item(self, interaction , quant):
      view = discord.ui.View.from_message(interaction.message)
      for item in view.children:
          item.disabled = True
      await interaction.response.edit_message(view=view)

      await comprarpremium(self, interaction=interaction, quant=quant, presente_para=presente_para)

  async def comprar_item(self, interaction: discord.Interaction , quant , valor , texto, presente_para=None):
      await interaction.response.defer(ephemeral=True)  
      view = discord.ui.View.from_message(interaction.message)
      for item in view.children:
          item.disabled = True
      await interaction.edit_original_response(content="", view=view)

      # Criar o pagamento no sistema
      valido , existente , id , qrcodebase , link , plano , expira = criar_link_pagamento(interaction.user.id , quant , valor , texto)
      
      if valido is False:
          await interaction.edit_original_response(content=Res.trad(interaction=interaction,str="message_erro_brixsystem"))
          return

      # se for presente, salvar quem recebe
      if presente_para:
          BancoPagamentos.update_payment(id, {"destinatario_id": presente_para.id})

      qr_bytes = base64.b64decode(qrcodebase)
      qr_file = io.BytesIO(qr_bytes)
      qr_file.seek(0)
      file = discord.File(qr_file, filename="qrcode.png")

      view = discord.ui.View()
      button = discord.ui.Button(style=discord.ButtonStyle.blurple,label=Res.trad(interaction=interaction,str="botão_abrir_navegador"),url=link)
      view.add_item(item=button)

      if existente is True:
        embed_retorno = discord.Embed(colour=discord.Color.yellow(),description=Res.trad(interaction=interaction,str="message_compra_pendente").format( int(expira.timestamp()) , id , plano))
      else:
        if presente_para:
          embed_retorno = discord.Embed(colour=discord.Color.yellow(),description=Res.trad(interaction=interaction,str="message_premium_presente_compra").format( int(expira.timestamp()) , id , plano, presente_para.mention))
        else:
          embed_retorno = discord.Embed(colour=discord.Color.yellow(),description=Res.trad(interaction=interaction,str="message_premium_compra").format( int(expira.timestamp()) , id , plano))

      embed_retorno.set_thumbnail(url="https://cdn.discordapp.com/emojis/1318962131567378432")  
      embed_retorno.set_image(url="attachment://qrcode.png")

      await interaction.edit_original_response(content="",embed=embed_retorno , attachments=[file], view = view )    
      try:
          if existente is False:
              qr_file2 = io.BytesIO(qr_bytes)
              qr_file2.seek(0)
              file2 = discord.File(qr_file2, filename="qrcode.png")
              msg_dm = await interaction.user.send(embed=embed_retorno, file=file2 ,  view = view )
              data = { "msg_dm" : msg_dm.id }
              BancoPagamentos.update_payment( id , data )
      except:
          print("DM FECHADA")


  menos.callback = partial(mover_item,self,quant=quant-1)
  mais.callback = partial(mover_item,self,quant=quant+1)
  adquirir_assinatura.callback = partial(comprar_item,self,quant=quant, valor= valor , texto = texto, presente_para=presente_para)
  if presente_para is None:
    await interaction.edit_original_response(content="",attachments=[discord.File("src/assets/imagens/financeiro/banner premium.png")],view=view)
  else:
    fonte = ImageFont.truetype("src/assets/font/PoetsenOne-Regular.ttf",40)
    fundo = Image.new('RGBA', (1600, 700), (0,0,0,0))
    art = Image.open("src/assets/imagens/financeiro/banner premium presentear.png")
    d = ImageDraw.Draw(art)
    d.text((430, 370), f"{presente_para.display_name}", align="center", font=fonte , fill="#f5a3a7")
    d.text((430, 430), f"Name: {presente_para.name}", font=fonte, fill="#f5a3a7")
    d.text((430, 490), f"ID: {presente_para.id}", font=fonte, fill="#f5a3a7")
    if presente_para.avatar:
        membroavatar = await presente_para.avatar.read()
        membroavatar = Image.open(io.BytesIO(membroavatar))
    else:
        membroavatar = Image.open(f"src/assets/imagens/icons/server-not-icon.jpg")
    membroavatar = membroavatar.resize((300,300)) 
    mascaraavatar = Image.open(f"src/assets/imagens/icons/recorte-redondo.png")
    mascaraavatar = mascaraavatar.resize((300,300)) 
    
    fundo.paste(art, (0,0), art)
    fundo.paste(membroavatar,(100,370),mascaraavatar) 
    # Salva a imagem no buffer
    buffer = io.BytesIO()
    fundo.save(buffer, 'PNG')
    buffer.seek(0)

    await interaction.edit_original_response(content="",attachments=[discord.File(fp=buffer, filename="Presente Premium.png")] ,view=view)










class premium(commands.Cog):
  def __init__(self, client: commands.Bot):
    self.client = client




    
  @commands.Cog.listener()
  async def on_ready(self):
    print("💎  -  Modúlo Premium carregado.")
    await self.client.wait_until_ready() #Aguardando o bot ficar pronto

    #criar_link_pagamento(197071176810364928 , 1 , 1 , "texto")
    if not self.TASK_VERIFICAR_PAGAMENTOS.is_running():
      await asyncio.sleep(120) #120
      self.TASK_VERIFICAR_PAGAMENTOS.start()

    if not self.verificar_premium.is_running():
      await asyncio.sleep(600) #1800
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
            embed = discord.Embed(colour=discord.Color.from_str('#f78da7'),description=f"### Um Boost a gente nunca esquece né {user.name}\n**Muito obrigado pelo boost {user.mention}!!!**\nSabia isso nos ajuda a **manter o servidor** cada vez melhor e nos **incentiva** cada vez mais então por isso **manteremos esse momento** aqui salvo neste chat para que você possa se gabar.\n\nConfira todos os **Benefícios** em <#888402749887217685> na opção **Místicas/Booster**\nE você ganhou alguns dias da **minha assinatura premium** como cortesia ~kyuuu.\nAproveite!!!" )
            embed.set_thumbnail(url="https://emoji.discord.st/emojis/548e713f-cfd9-4c49-9caa-d0dbe3dcec91.gif")
            messageenviada = await canal.send(f"Aviso para {user.mention}!!!!!!",embed=embed)
            await messageenviada.add_reaction('<a:BH_nitro:1154334548478402650>')

            #ativa o premium do cara
            await liberarpremium(self,None,user,7,True)
          elif boost_count == '2': #premium 24 Dias
            await asyncio.sleep(4)
            await liberarpremium(self,None,user,24,True) 






#FUNÇÂO DE VERIFICAÇÃO DE ASSINANTES PREMIUM
  @tasks.loop(minutes=30) #6H loop 6*60*60
  async def verificar_premium(self): 
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
  


  
#FUNÇÂO DE VERIFICAÇÃO DE PAGAMENTOS PREMIUM
  @tasks.loop(minutes=5)
  async def TASK_VERIFICAR_PAGAMENTOS(self): 
    await self.VERIFICAR_PAGAMENTOS()




  async def VERIFICAR_PAGAMENTOS(self):
    try:
      await update_pagamentos(self)
      filtro = {"ativado": False, "mp_status": "approved"}
      busca = BancoPagamentos.select_by_filter(filtro)
      for pagamento in busca:
        try:
            usuario = pagamento['user_id']
            dias = 31 * pagamento['quant_meses']
            # se for presente, envia para o destinatário
            if "destinatario_id" in pagamento and pagamento["destinatario_id"]:
              user = await self.client.fetch_user(pagamento["destinatario_id"])
              presente = await self.client.fetch_user(usuario)
            else:
              user = await self.client.fetch_user(usuario)
              presente = None
            
            BancoPagamentos.update_payment(pagamento["mp_payment_id"], {"ativado": True})
            await liberarpremium(self, None, user, dias, False , presente)
            banner_name = "braixen-premium-v2"
            item = {f"backgrouds.{banner_name}": banner_name}
            BancoUsuarios.update_document(user, item)

        except Exception as e:
            print(f"Erro ao ativar premium para {usuario}: {e}")
    except Exception as e:
        print(f"erro na verificação de pagamentos do mercadopago.\n{e}")








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






#COMANDO EXIBIR ASSINANTES PREMIUM
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
  premium = app_commands.Group(name="premium",description="Comandos premium do Brix.",allowed_installs=app_commands.AppInstallationType(guild=True,user=True),allowed_contexts=app_commands.AppCommandContext(guild=True, dm_channel=True, private_channel=False))





  
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

    async def botãopremium(self,interaction: discord.Interaction):
      await interaction.response.send_message("Por Favor Aguarde....",ephemeral=True)
      await comprarpremium(self,interaction=interaction, quant=1 )


    adquirir.callback = partial(botãopremium,interaction)
    await interaction.response.send_message(file = discord.File("src/assets/imagens/financeiro/banner premium.png"),view=view)
    
  
    
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
          BancoFinanceiro.registrar_transacao(user_id=interaction.user.id,tipo="gasto",origem="Premium",valor=valor,moeda=moeda,descricao=f"Compra de assinatura premium.")

          await interaction.response.send_message(Res.trad(interaction=interaction, str="message_premium_confirm").format(novosaldo,emoji),ephemeral = True)
          await liberarpremium(self,interaction.channel,interaction.user,2,False)

    braixencoin.callback = partial(buypremium,self,moeda = 'braixencoin',valor = 350000)
    gravetocoin.callback = partial(buypremium,self,moeda = 'graveto',valor = 6300)
    
    await interaction.response.send_message(file = discord.File("src/assets/imagens/financeiro/banner premium negociar.png"),view=view)









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
      botaoteste = discord.ui.Button(label="testar por 5 dias",emoji="💎",style=discord.ButtonStyle.green)
    
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
      await liberarpremium(self,interaction.channel,interaction.user,5,False)
    
    botaoteste.callback = partial(liberarteste,self)
    await interaction.response.send_message(file = discord.File("src/assets/imagens/financeiro/banner premium testar.png"),view=view)





  @premium.command(name="presentear", description="💎⠂Presenteie outro membro com o Premium.")
  @app_commands.describe(membro="Quem vai receber o presente")
  async def premiumpresentear(self, interaction: discord.Interaction, membro: discord.User):
    if await Res.print_brix(comando="premiumpresentear", interaction=interaction):
      return
    if interaction.user == membro:
      return await interaction.response.send_message(Res.trad(interaction=interaction,str="message_premium_presente_autopresente"), ephemeral=True)
    
    await interaction.response.send_message("Por Favor Aguarde....", ephemeral=True)
    await comprarpremium(self, interaction=interaction, quant=1, presente_para=membro)





async def setup(client:commands.Bot) -> None:
  await client.add_cog(premium(client))