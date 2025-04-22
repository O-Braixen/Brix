import discord,os,asyncio,time,datetime,pytz,random,requests,io
from functools import partial
from discord.ext import commands,tasks
from discord import app_commands
from modulos.connection.database import BancoLoja,BancoUsuarios,BancoBot
from modulos.essential.respostas import Res
from modulos.essential.usuario import userperfil
from PIL import Image, ImageFont, ImageDraw, ImageOps #IMPORTAÇÂO Py PIL IMAGEM
from dotenv import load_dotenv


load_dotenv(os.path.join(os.path.dirname(__file__), '.env')) #load .env da raiz
donoid = int(os.getenv("DONO_ID")) #acessa e define o id do dono





# AQUI SÒ SERVE PARA CHAMAR A LOJA DE FATO, AQUI É RESPONSAVEL POR COLETAR OS DADOS PARA ENVIAR PARA A CONTRUÇÃO DA LOJA
async def chamarlojadiaria(self,interaction:discord.Interaction,item):
    await interaction.original_response()
    try:
      #consulta no banco de dados para saber quais são os itens disponiveis na loja de hoje
      filtro = {"_id": "diaria"}
      diaria = BancoLoja.select_many_document(filtro)
      lista = []
      #ordena os itens na loja de hoje em uma nova lista
      for id,art in diaria[0].items():
        if id.startswith('item'):
          lista.append(art)
      #usa a lista ordenada para coletar mais informações dos itens, nome, valores essas coisas
      filtro = {"_id": {"$in":lista}}
      dados = BancoLoja.select_many_document(filtro)
      #chama a função de exibit loja, ela montará a loja com base nas informações passadas
      await exibiritemloja(self,interaction,item=item,loja=dados,tamanholoja=lista,originaluser = interaction.user)
    except:
      await interaction.followup.send(content=Res.trad(interaction=interaction,str="message_erro_mongodb").format(interaction.user.id))
      return





#Função exibir item loja
async def exibiritemloja(self,interaction:discord.Interaction,item,loja,tamanholoja,originaluser):
  await interaction.original_response()
  MAX_h = 600
  fundo = Image.new("RGB",(MAX_h,430),"yellow")
  try:
    backgroud = Image.open(f"imagens/backgroud/all-itens/{loja[item]['_id']}.png")
  except:
    backgroud = Image.open(requests.get(loja[item]['url'], stream=True).raw)
  backgroud = backgroud.resize((500,250))
  #fundo.paste(backgroud,(50,65))
  fundo.paste(backgroud,(50,50))
  #artloja = Image.open(f"imagens/financeiro/art-loja.png")
  fundo.paste(self.loja_artloja,(0,0),self.loja_artloja)

  #fontegrande = ImageFont.truetype("font/PoetsenOne-Regular.ttf", 27)
  textoname = Res.trad(interaction=interaction,str="loja_diaria")
  fundodraw = ImageDraw.Draw(fundo)
  h = fundodraw.textlength(textoname,self.loja_fontegrande)
  fundodraw.text(((MAX_h-h)/2, 5), textoname, font=self.loja_fontegrande, fill='#eff1f3',align='center')
                              #25
  #fonte = ImageFont.truetype("font/PoetsenOne-Regular.ttf", 27)
  textoname = loja[item]['name']
  graveto = '-' if str(loja[item]['graveto']) == '0' else "{:,}".format(int(loja[item]['graveto']))
  braixencoin = '-' if str(loja[item]['braixencoin']) == '0' else "{:,}".format(int(loja[item]['braixencoin']))
  pagina = f"{item+1}/{len(tamanholoja)}"

  #fundodraw = ImageDraw.Draw(fundo)
  h = fundodraw.textlength(textoname,self.loja_fontegrande)
  fundodraw.text(((MAX_h-h)/2, 300), textoname, font=self.loja_fontegrande, fill='#ffffff',align='center')
                              #325
  if loja[item]['raridade'] == 0:
    textoname = "Item Comum"
  elif loja[item]['raridade'] == 1:
    textoname = "Item Raro"
  elif loja[item]['raridade'] == 2:
    textoname = "Item Epico"
  elif loja[item]['raridade'] == 3:
    textoname = "Item Exclusivo"

  #fontepequena = ImageFont.truetype("font/PoetsenOne-Regular.ttf", 22)
  #fundodraw = ImageDraw.Draw(fundo)
  h = fundodraw.textlength(textoname,self.loja_fontepequena)
  fundodraw.text(((MAX_h-h)/2, 325), textoname, font=self.loja_fontepequena, fill='#ffffff',align='center')
        #                      355
  fundodraw.text((45, 375), graveto, font=self.loja_fontegrande, fill='#ffffff')
  fundodraw.text((495, 375), braixencoin, font=self.loja_fontegrande, fill='#ffffff')
  #item+1}/{len(tamanholoja)
  h = fundodraw.textlength(pagina,self.loja_fontepequena)
  fundodraw.text(((MAX_h-h)/2, 385), pagina, font=self.loja_fontepequena, fill='#ffffff',align='center')

  buffer = io.BytesIO()
  fundo.save(buffer,format="PNG")
  buffer.seek(0)

  dado = BancoUsuarios.insert_document(interaction.user)
      #VIEW DOS BOTÔES
  view = discord.ui.View()

    #BOTOÊS DE AÇÂO DO PAINEL
    #BOTÂO VOLTAR RAPIDO
  botaovoltarfast = discord.ui.Button(emoji="<:setaduplaesquerda:1318716104474099722>",style=discord.ButtonStyle.gray,disabled=(item == 0),row=1)
  view.add_item(item=botaovoltarfast)
  botaovoltarfast.callback = partial(mover_item,self,item=item, loja=loja,tamanholoja=tamanholoja,originaluser=originaluser,sentido=-item)
    #BOTÂO VOLTAR NORMAL
  botaovoltar = discord.ui.Button(emoji="<:setaesquerda:1318698827422765189>",style=discord.ButtonStyle.gray,disabled=(item == 0),row=1)
  view.add_item(item=botaovoltar)
  botaovoltar.callback = partial(mover_item,self,item=item, loja=loja,tamanholoja=tamanholoja,originaluser=originaluser,sentido=-1)

  lista = []
  try:
    for item_id in dado['backgrouds'].items():
      lista.append(item_id[0])
  except:
    lista = [None]

  #BOTÂO COMPRA
  if loja[item]['_id'] in lista: #BOTÂO ITEM JÀ COMPRADO
    botaojacomprado = discord.ui.Button(label=Res.trad(interaction=interaction,str="botão_item_adquirido"),style=discord.ButtonStyle.blurple,emoji="<:BH_Braix_Happy4:1154338634011521054>",disabled=True,row=2)
    view.add_item(item=botaojacomprado)
  else: #ELSE CASO O ITEM NÂO TENHA SIDO COMPRADO
    botaograveto = discord.ui.Button(label="{:,.0f}".format(loja[item]['graveto']),style=discord.ButtonStyle.blurple,emoji="<:Graveto:1318962131567378432>",row=2)
    view.add_item(item=botaograveto)
    botaograveto.callback = partial(confirmacao_comprar,self,item=item,loja=loja,tamanholoja=tamanholoja, originaluser=originaluser,moeda ="graveto")

    if loja[item]['braixencoin'] != 0:
      botaocoin = discord.ui.Button(label="{:,.0f}".format(loja[item]['braixencoin']),style=discord.ButtonStyle.green,emoji="<:BraixenCoin:1272655353108103220>",row=2)
      view.add_item(item=botaocoin)
      botaocoin.callback = partial(confirmacao_comprar,self,item=item,loja=loja,tamanholoja=tamanholoja,originaluser=originaluser,moeda ="braixencoin")
  
    botaoteste = discord.ui.Button(style=discord.ButtonStyle.blurple,row=2,emoji="<:art:1322226736116666469>")
    view.add_item(item=botaoteste)
    botaoteste.callback = partial(testar_fundo,self,item=item,loja=loja,originaluser=originaluser,moeda ="braixencoin")

  botaoduvida = discord.ui.Button(label="?",style=discord.ButtonStyle.gray,row=2)
  view.add_item(item=botaoduvida)
  botaoduvida.callback = partial(duvidaloja)

  botaoavancar = discord.ui.Button(emoji="<:setadireita:1318698789225369660>",style=discord.ButtonStyle.gray,disabled=(item == len(tamanholoja) -1),row=1)
  view.add_item(item=botaoavancar)
  botaoavancar.callback = partial(mover_item,self,item=item, loja=loja,tamanholoja=tamanholoja,originaluser=originaluser,sentido=+1)
  
  botaoavancarfast = discord.ui.Button(emoji="<:setadupladireita:1318715892242190419>",style=discord.ButtonStyle.gray,disabled=(item == len(tamanholoja) -1),row=1)
  view.add_item(item=botaoavancarfast)
  botaoavancarfast.callback = partial(mover_item,self,item=item, loja=loja,tamanholoja=tamanholoja,originaluser=originaluser,sentido=len(tamanholoja) - item - 1)

  fuso = pytz.timezone('America/Sao_Paulo')
  data_coleta_daily = datetime.datetime.now().astimezone(fuso).replace(hour=0, minute=0, second=0) + datetime.timedelta(days=1)
  await interaction.edit_original_response(content=Res.trad(interaction=interaction,str="loja_diaria_reseta").format(int(data_coleta_daily.timestamp())),attachments=[discord.File(fp=buffer,filename="loja.png")],view=view)



# COMANDO PARA COMFIRMAR A COMPRAR DE UM ITEM
@commands.Cog.listener()
async def confirmacao_comprar(self,interaction:discord.Interaction, item, tamanholoja , loja, originaluser, moeda):
  if interaction.user != originaluser:
        await interaction.response.send_message(Res.trad(interaction=interaction, str="message_erro_interacaoalheia"), delete_after=20, ephemeral=True)
        return
  
  await interaction.response.defer(ephemeral=True)
  await interaction.original_response()
  usuario = BancoUsuarios.insert_document(interaction.user)

  if usuario[moeda] < loja[item][moeda]:
    await interaction.followup.send(Res.trad(interaction=interaction, str="message_financeiro_saldo_insuficiente"), ephemeral=True)
    return
  novosaldo = usuario[moeda] - loja[item][moeda]
  if moeda == 'braixencoin':
     emoji = "**{:,.0f}** <:BraixenCoin:1272655353108103220>".format(loja[item][moeda])
  else: emoji = "**{:,.0f}** <:Graveto:1318962131567378432>".format(loja[item][moeda])
  botão = discord.ui.View()

  botaosair = discord.ui.Button(emoji="<:setasair:1318701737648980008>",style=discord.ButtonStyle.gray)
  botão.add_item(item=botaosair)
  botaosair.callback = partial(mover_item,self,item=item, loja=loja,tamanholoja=tamanholoja,originaluser=originaluser,sentido=0)

  botãoconfirmação = discord.ui.Button(label=Res.trad(interaction=interaction, str='botão_confirmartransacao'),style=discord.ButtonStyle.green,emoji="<:Braix_Glass:1272664403296260126>")
  botão.add_item(item=botãoconfirmação)
  botãoconfirmação.callback = partial(comprar_moeda,self,item=item,loja=loja, moeda = moeda , novosaldo = novosaldo , originaluser=originaluser)

  await interaction.edit_original_response(content = Res.trad(interaction=interaction, str='loja_diaria_Comprar_item').format(loja[item]['name'],loja[item]['url'],emoji),view=botão, attachments=[])




# COMANDO PARA USUARIO COMPRAR UM ITEM, SUPORTA TANTO GRAVETOS QUANTO BRAIXENCOIN DIRETO
@commands.Cog.listener()
async def comprar_moeda(self,interaction, item, loja, moeda , novosaldo, originaluser):
  if interaction.user != originaluser:
    await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_interacaoalheia"),delete_after=10,ephemeral=True)
  else:
    view = discord.ui.View.from_message(interaction.message)
    for button in view.children:
            button.disabled = True

        # Atualiza a resposta original para refletir os botões desativados
    await interaction.response.edit_message(view=view)
    banner_name = loja[item]['_id']
    insert = {moeda: novosaldo,f"backgrouds.{banner_name}": banner_name,"backgrouds.braixen-house-2023": "braixen-house-2023"}
    BancoUsuarios.update_document(interaction.user, insert)

    botão = discord.ui.View()
    botaodefinirfundo = discord.ui.Button(label=Res.trad(interaction=interaction,str="botão_alterarbanner"),style=discord.ButtonStyle.blurple,emoji="🖼️",row=1)
    botão.add_item(item=botaodefinirfundo)
    botaodefinirfundo.callback = partial(definir_fundo,banner_name = banner_name)

    # Mensagem de sucesso personalizada com base na moeda
    if moeda == 'braixencoin':
        mensagem_sucesso = Res.trad(interaction=interaction, str="message_financeiro_compracor").format(loja[item]['name'], novosaldo)
    else:
        mensagem_sucesso = Res.trad(interaction=interaction, str="message_financeiro_compra_graveto").format(loja[item]['name'], novosaldo)

    await interaction.followup.send(mensagem_sucesso,view=botão, ephemeral=True)
    await chamarlojadiaria(self,interaction,item)


#BOTÃO PARA TROCA DE PAGINA DE ITENS, ELE SUPORTA TANTO IR PARA FRENTE QUANTO IR PARA TRÁS
@commands.Cog.listener()
async def mover_item(self,interaction,item,loja,tamanholoja,originaluser,sentido):

  if interaction.user != originaluser:
    await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_interacaoalheia"),delete_after=10,ephemeral=True)
  else:
    view = discord.ui.View.from_message(interaction.message)
    for button in view.children:
            button.disabled = True

        # Atualiza a resposta original para refletir os botões desativados
    await interaction.response.edit_message(view=view)
    await exibiritemloja(self,interaction,item=item+sentido,loja=loja,tamanholoja=tamanholoja,originaluser=originaluser)


#COMANDO DE EXIBIR AJUDA SOBRE A LOJA, CLASSICO BOTÃO DE AJUDA
@commands.Cog.listener()
async def duvidaloja(interaction):
  await interaction.response.send_message(Res.trad(interaction=interaction,str="botão_duvida_loja"),delete_after=30,ephemeral=True)


#BOTÃO PARA DEFINIR FUNDO QUE O USUARIO ACABOU DE COMPRAR, ELE SALVA O NOVO FUNDO E TAMBÉM EXIBE COMO FICOU
@commands.Cog.listener()
async def definir_fundo(interaction: discord.Interaction, banner_name):  
    await interaction.response.defer(ephemeral=True)
    await interaction.original_response()
    
    # Atualiza o fundo do usuário no banco de dados
    insert = {"backgroud": banner_name}
    BancoUsuarios.update_document(interaction.user, insert)
    
    # Confirma a mudança do fundo
    #await interaction.followup.send(Res.trad(interaction=interaction, str="message_fundo_definido").format(banner_name),ephemeral=True)
    await interaction.edit_original_response(content=Res.trad(interaction=interaction, str="message_fundo_definido").format(banner_name),view=None)
    await asyncio.sleep(1)
    await userperfil(interaction,interaction.user)


#BOTÃO PARA USUARIO VISUALIZAR O FUNDO ANTES DE COMPRA-LO
@commands.Cog.listener()
async def testar_fundo(self,interaction, item, loja, originaluser, moeda):
    if interaction.user != originaluser:
        await interaction.response.send_message(Res.trad(interaction=interaction, str="message_erro_interacaoalheia"), delete_after=20, ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    await userperfil(interaction,interaction.user,loja[item]['_id'])











class loja(commands.Cog):
  def __init__(self, client: commands.Bot):
    self.client = client

# CARREGANDO COISAS PADROES DE USO NO SISTEMA DE TOPS DO BOT
    self.loja_artloja = Image.open(f"imagens/financeiro/art-loja.png")
    self.loja_fontegrande = ImageFont.truetype("font/PoetsenOne-Regular.ttf", 27)
    self.loja_fontepequena = ImageFont.truetype("font/PoetsenOne-Regular.ttf", 22)
  
  @commands.Cog.listener()
  async def on_ready(self):
    print("🍕  -  Modúlo Loja carregado.")
   # fuso = pytz.timezone('America/Sao_Paulo')
    #now = datetime.datetime.now().astimezone(fuso)
    #target_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
    #if now > target_time:
   #   target_time += datetime.timedelta(days=1)
   # time_until_target = target_time - now
    #await asyncio.sleep(time_until_target.total_seconds())

    if not self.lojadiariatrocaitens.is_running():
      self.lojadiariatrocaitens.start()
  



#FUNÇÂO DE TROCA DE ITENS DA LOJA
  #@tasks.loop(seconds=24*60*60) #24H loop 24*60*60
  @tasks.loop(time=datetime.time(hour=0, minute= 0, tzinfo=datetime.timezone(datetime.timedelta(hours=-3))))
  async def lojadiariatrocaitens(self): 
    print(f"Rodando Troca de itens da loja diaria")
    try:
      itens_para_banco = {}
      lojaativo = BancoBot.insert_document()

      if lojaativo['rotacaoloja'] is False:
        print("❌ - rotação de loja desativada")
        for i in range(1,9): #DICA SEMPRE INDICAR +1 no FINAL
          chave = f"item{i}"
          valor = lojaativo[f'lojaitem{i}']
          itens_para_banco[chave] = valor
          print(f"Entro na loja o item: {lojaativo[f'lojaitem{i}']}")

          #Envia para banco de dados para uso futuro
        BancoLoja.update_one(id='diaria',item=itens_para_banco)
        print("update realizado com sucesso kyuu")
        return
      else:
            # CONSULTANDO NO BANCO TODOS OS ITENS
        filtro = {"graveto": {"$ne": 0}, "_id": {"$ne": "diaria"}}
        itens = BancoLoja.select_many_document(filtro)

            # CONSULTANDO NO BANCO OS ITENS ATUAIS
        filtro = {"_id": "diaria"}
        diaria = BancoLoja.select_many_document(filtro)

        listaatual = []
        for id,item in diaria[0].items():
          if id.startswith('item'):
            listaatual.append(item)

            # Listas para armazenar os itens de diferentes raridades
        raridade_0 = []
        raridade_1 = []
        raridade_2 = []
        itens_selecionados = []
        # Separar os itens por raridade
        for item in itens:
            if item['raridade'] == 0:
                raridade_0.append(item)
            elif item['raridade'] == 1:
                raridade_1.append(item)
            elif item['raridade'] == 2:
                raridade_2.append(item)
        # Verificar se o item não está na lista anterior
        def item_nao_na_lista_anterior(item, lista_anterior):
            for item_anterior in lista_anterior:
              if item_anterior == item['_id']:
                return False
            return True

        # Selecionar 2 itens de raridade 0 sem duplicatas # essa parte foi desativada para exibir itens mais raros
        while len(itens_selecionados) < 3 and len(raridade_0) > 0:
            item = random.choice(raridade_0)
            if item not in itens_selecionados and item_nao_na_lista_anterior(item, listaatual):
               itens_selecionados.append(item)

        # Selecionar 1 item de raridade 1 sem duplicatas
        while len(itens_selecionados) < 6 and (len(raridade_1) + len(raridade_0)) > 0:
            raridades_1_ou_0 = raridade_1 + raridade_0 
            item = random.choice(raridades_1_ou_0)
            if item not in itens_selecionados and item_nao_na_lista_anterior(item, listaatual):
               itens_selecionados.append(item)

        # Selecionar 1 item de raridade 1 ou 2 sem duplicatas
        while len(itens_selecionados) < 8 and (len(raridade_2) ) > 0:
            raridades_1_ou_2 = raridade_2
            item = random.choice(raridades_1_ou_2)
            if item not in itens_selecionados and item_nao_na_lista_anterior(item, listaatual):
               itens_selecionados.append(item)

        # Selecionar 1 item de raridade 1 sem duplicatas
        #while len(itens_selecionados) < 8 and (len(raridade_1) + len(raridade_0) + len(raridade_2)) > 0:
        #    raridades = raridade_1 + raridade_0 + raridade_2
        #    item = random.choice(raridades)
        #    if item not in itens_selecionados and item_nao_na_lista_anterior(item, listaatual):
        #        itens_selecionados.append(item)


            # Criar um dicionário com os itens selecionados
        
        for i, item in enumerate(itens_selecionados,start=1):
          chave = f"item{i}"
          valor = item['_id']
          itens_para_banco[chave] = valor
          print(f"Entro na loja o item: {item['_id']}")

          #Envia para banco de dados para uso futuro
        BancoLoja.update_one(id='diaria',item=itens_para_banco)
        print("🔄️ - loja atualizada")
        bannerbrix = random.choice(itens_selecionados)
        insert = {"backgroud": bannerbrix['_id']}
        BancoUsuarios.update_document(self.client.user,insert)
        print(f"banner do Brix atualizado para: {bannerbrix['_id']}")
        return
    except:
      print("erro na atualização da loja diaria.")
      return
  




  #COMANDO ADICIONAR ITENS A LOJA OWNER
  @commands.command(name="addloja", description="adiciona um item a loja do bot...")
  async def addloja(self,ctx,id:str = None,name:str = None,graveto:int = None,braixencoin:int = None,raridade:int = None,url:str = None,fontcor:str = None, *, descricao: str = None):
    try:
        await ctx.message.delete()
    except:
        print("falta de permissão na comunidade")
    if ctx.author.id == donoid:
      if id is None or name is None or braixencoin is None or graveto is None or raridade is None or url is None or descricao is None or fontcor is None:
        await ctx.send(Res.trad(guild=ctx.guild.id,str="message_erro_notargument").format("use ```-addloja id nome em parenteses graveto braixencoin raridade url com parenteses #CorFonte descrição```"))
        return
      else:
        BancoLoja.update_document(id,name,braixencoin,graveto,raridade,url,descricao,fontcor)
        msg = await ctx.send(f"registrado o item {name} - {braixencoin} <:BraixenCoin:1272655353108103220> - Raridade: {raridade}")
        await asyncio.sleep(10)
        await msg.delete()
    else:
      await ctx.send(Res.trad(user=ctx.author,str='message_erro_onlyowner'))
      return




    
  # COMANDO ADICIONAR ITENS A LOJA OWNER
  @commands.command(name="showloja", description="exibe os itens registrados da loja do bot...")
  async def showloja(self, ctx):
    if ctx.author.id == donoid:
        filtro = {"braixencoin": {"$exists": True}}
        dados = BancoLoja.select_many_document(filtro).sort('raridade', -1)
        itens_por_mensagem = 10  # Defina o número máximo de itens por mensagem
        lista_itens = [f"**Itens na Loja**"]
        lista_itens.extend([f"{contador:02d} - Rar: **{item['raridade']}** | **{item['graveto']}** <:Graveto:1318962131567378432> | **{item['braixencoin']}** <:BraixenCoin:1272655353108103220> | ID: {item['_id']}" for contador, item in enumerate(dados, start=1)])

        #lista_itens.extend([f"Raridade: **{item['raridade']}** - **{item['graveto']}** <:Graveto:1318962131567378432> - **{item['braixencoin']}** <:BraixenCoin:1272655353108103220> : {item['_id']}" for item in dados])

        for i in range(0, len(lista_itens), itens_por_mensagem):
            mensagem = "\n".join(lista_itens[i:i + itens_por_mensagem])
            await ctx.send(mensagem)
            await asyncio.sleep(0.3)
    else:
        await ctx.send(Res.trad(user=ctx.author,str='message_erro_onlyowner'))





  #COMANDO ADICIONAR ITENS A LOJA OWNER
  @commands.command(name="showitem", description="exibe os itens registrados da loja do bot...")
  async def showitem(self,ctx,id:str):
    if ctx.author.id == donoid:
      try:
        dados = BancoLoja.select_one(id)
        lista = f"[{dados['name']}]({dados['url']}) Raridade: **{dados['raridade']}**\n**{dados['graveto']}** <:Graveto:1318962131567378432> --- **{dados['braixencoin']}** <:BraixenCoin:1272655353108103220> - ID: {dados['_id']}\nDescrição: {dados['descricao']}\n\n```-addloja {dados['_id']} '{dados['name']}' {dados['graveto']} {dados['braixencoin']} {dados['raridade']} {dados['url']} {dados['font_color']} {dados['descricao']}```"
      except:
        lista = "<:BH_Braix_Blank:1154338535894155315>┃ Não achei esse item, verifique a ID...     ~kyu"
      await ctx.send(lista)
    else:
      await ctx.send(Res.trad(user=ctx.author,str='message_erro_onlyowner'))
      return











  
  #GRUPO COMANDOS DA LOJA DO BRIX 
  loja=app_commands.Group(name="loja",description="Comandos da loja do Brix.",allowed_installs=app_commands.AppInstallationType(guild=True,user=True),allowed_contexts=app_commands.AppCommandContext(guild=True, dm_channel=True, private_channel=True))



  #COMANDO LOJA DIARIA DO BRIX
  @loja.command(name="diaria", description="🦊⠂Exibe a loja diária de brix.")
  async def lojadiaria(self,interaction: discord.Interaction):
    if await Res.print_brix(comando="lojadiaria",interaction=interaction):
      return 
    await interaction.response.defer() #defer como resposta
    await chamarlojadiaria(self,interaction,0)
  


  # COMANDO DE EXIBIR OS ITENS DA LOJA DO BRIX
  @loja.command(name="itens", description="🦊⠂Exibe os itens da diária de brix.")
  async def lojaitens(self,interaction: discord.Interaction):
    if await Res.print_brix(comando="lojaitens",interaction=interaction):
      return
    #self.membro = interaction.user
    await interaction.response.defer()
    await painelexibirskin(self,interaction,lotes=0,banner='braixen-house-2023',paginatual=1,totalpages=0,originaluser = interaction.user)
           





# PAINEL ONDE SERÀ EXIBIDO OS ITENS DA LOJA
async def painelexibirskin(self,interaction: discord.Interaction,lotes,banner,paginatual,totalpages,originaluser):
    await interaction.original_response()
    lista = []
    filtro = {"name": {"$exists":True}}
    try:
      resultadobanco = BancoLoja.select_many_document(filtro).sort('raridade',-1)
      umitem = BancoLoja.select_one(banner)
    except:
      await interaction.followup.send(content=Res.trad(interaction=interaction,str="message_erro_mongodb").format(interaction.user.id))
      return
    
    for item_id in resultadobanco:
        lista.append({'_id':item_id['_id'], 'name':item_id['name'] , 'raridade':item_id['raridade'],'descricao': item_id['descricao'],'url':item_id['url'], 'graveto':item_id['graveto'], 'braixencoin':item_id['braixencoin'] })
    lotes = [lista[i:i + 24] for i in range(0, len(lista), 24)]
    
    view = discord.ui.View()
    view.add_item(exibirskins(lotes, interaction,paginatual,originaluser))

    async def mudarpagina(interaction,posicao):
        # Decrementando o índice da página
        if interaction.user != originaluser:
            await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_interacaoalheia"),delete_after=10,ephemeral=True)
        else:
            view = discord.ui.View.from_message(interaction.message)
            for item in view.children:
                    item.disabled = True

                # Atualiza a resposta original para refletir os botões desativados
            await interaction.response.edit_message(view=view)
            #await interaction.response.defer()
            await painelexibirskin(self,interaction,lotes=lotes,banner=banner,paginatual=paginatual+posicao,totalpages=len(lotes),originaluser=originaluser)

    #if paginatual == 1:
    botaovoltar = discord.ui.Button(emoji="<:setaesquerda:1318698827422765189>",style=discord.ButtonStyle.gray,disabled=(paginatual == 1))
   # else:
        #botaovoltar = discord.ui.Button(label="<",style=discord.ButtonStyle.gray)
    view.add_item(item=botaovoltar)
    botaovoltar.callback = partial(mudarpagina,posicao=-1)

    botaopagina = discord.ui.Button(label=f"{paginatual}/{len(lotes)}",style=discord.ButtonStyle.gray,disabled=True)
    view.add_item(item=botaopagina)

    #if paginatual == totalpages:
    botaoavancar = discord.ui.Button(emoji="<:setadireita:1318698789225369660>",style=discord.ButtonStyle.gray,disabled=(paginatual == totalpages))
    #else:
        #botaoavancar = discord.ui.Button(label=">",style=discord.ButtonStyle.gray)
    view.add_item(item=botaoavancar)
    botaoavancar.callback = partial(mudarpagina,posicao=+1)
    resposta = discord.Embed( 
            colour=discord.Color.yellow(),
            title=umitem['name'],
            description=umitem['descricao']
    )
    resposta.set_image(url=umitem['url'])
    try:
      if umitem['raridade'] == 0:
        raridade = "Comum"
      elif umitem['raridade'] == 1:
        raridade = "Raro"
      elif umitem['raridade'] == 2:
        raridade = "Epica"
      elif umitem['raridade'] == 3:
        raridade = "Exclusiva"

      resposta.add_field(name="Braixencoin", value="{:,.0f} <:BraixenCoin:1272655353108103220>".format(umitem['braixencoin']), inline=True)
      resposta.add_field(name="Gravetos", value="{:,.0f} <:Graveto:1318962131567378432>".format(umitem['graveto']), inline=True)
      resposta.add_field(name="Raridade", value="{}".format(raridade), inline=True)
    except:
      resposta.add_field(name="item a venda?", value="não", inline=True)
    await interaction.edit_original_response(content='',embed=resposta, view=view)






# PAINEL DE ESCOLHA DE Skins
class exibirskins(discord.ui.Select):
    def __init__(self, lotes: list, interaction: discord.Interaction,paginatual,originaluser):
        self.membro = interaction.user
        options = []

        # Utiliza a lista fornecida em vez de buscar no banco de dados
        for item in lotes[paginatual-1]:
            if item['raridade'] == 0:
              emoji = "<:Pokeball:1272668305190162524>"
            elif item['raridade'] == 1:
              emoji = "💠"
            elif item['raridade'] == 2:
              emoji = "<:Badge_Exclusivebadge:1272667548596441180>"
            elif item['raridade'] == 3:
              emoji = "<:Vipbadge:1335106288161525770>"

            #IMPEDE QUE O PAINEL QUEBRE PELO TAMANHO DA DESCRIÇÃO
            descricao = str(item['descricao'])
            if len(descricao) > 99:
                
                descricao = descricao[:96] + "..."
            options.append(discord.SelectOption(value=str(item['_id']),label=str(item['name']),description=descricao,emoji=emoji))
        
        super().__init__(
            placeholder=f"{Res.trad(interaction=interaction,str='botão_pagina')} {paginatual}",
            min_values=1,
            max_values=1,
            options=options,
        )
        
    async def callback(self, interaction): #Retorno seleção Dropdown
        #coleta os dados do membro no banco de dados
        if interaction.user != self.membro:
            await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_interacaoalheia"),delete_after=10,ephemeral=True)
        else:
            view = discord.ui.View.from_message(interaction.message)
            for item in view.children:
              item.disabled = True
            # Atualiza a resposta original para refletir os botões desativados
            await interaction.response.edit_message(view=view)
            #await interaction.response.defer()
            await painelexibirskin(self,interaction,lotes=0,banner=self.values[0],paginatual=1,totalpages=0,originaluser=self.membro)











async def setup(client:commands.Bot) -> None:
  await client.add_cog(loja(client))
