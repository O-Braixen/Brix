import discord,os,asyncio,time,datetime,pytz,random,json,io,textwrap,requests,typing,re
from operator import itemgetter
from functools import partial
from discord.ext import commands,tasks
from discord import app_commands
from discord.interactions import Interaction
from modulos.connection.database import BancoUsuarios,BancoServidores,BancoLoja,BancoBot
from modulos.essential.respostas import Res
from modulos.essential.calculos import calcular_saldo,calcular_nivel
from PIL import Image, ImageFont, ImageDraw, ImageOps #IMPORTAÇÂO Py PIL IMAGEM
from dotenv import load_dotenv

load_dotenv()
donoid = int(os.getenv("DONO_ID"))


#FUNÇÔES AQUIII
    #função usuario aniversario consultar
async def useraniversario(interaction,membro,menu):
    if membro is None:
        membro = interaction.user
    try:
        dado = BancoUsuarios.insert_document(membro)
    except:
        await interaction.followup.send(Res.trad(interaction=interaction,str="message_erro_mongodb").format(interaction.user.id),ephemeral=menu)
    if dado['nascimento'] == "00/00/0000":
        await interaction.followup.send(Res.trad(interaction=interaction,str="message_aniversario_consulta_erro"),ephemeral=menu)
    else:
        dia, mes, ano = dado['nascimento'].split("/")
        data_formatada = Res.trad(interaction=interaction, str="padrao_data").replace("%d", dia).replace("%m", mes).replace("%Y", ano)
        await interaction.followup.send(Res.trad(interaction=interaction,str="message_aniversario_consulta").format(dado['_id'],data_formatada[:5]),ephemeral=menu)


#função usuario aniversario salvar
async def aniversariodefinir(interaction: discord.Integration, dia, mes, ano):
    if await Res.print_brix(comando="aniversariodefinir", interaction=interaction):
      return
    await interaction.original_response()
    membro = interaction.user
    data_hoje = datetime.datetime.now()
    data_execucao_str = data_hoje.strftime("%d/%m/%Y")
    
    # Recupera os dados do banco, se houver
    dados_usuario = BancoUsuarios.insert_document(membro)
    data_nascimento_registro = dados_usuario.get("nascimentoregistro")

    # Verifica se já existe uma data registrada e se faz menos de 1 mês
    if data_nascimento_registro:
        data_nascimento_registro_dt = datetime.datetime.strptime(data_nascimento_registro, "%d/%m/%Y")
        diferenca = data_hoje - data_nascimento_registro_dt

        if diferenca.days < 150:
            await interaction.edit_original_response(content=Res.trad(interaction=interaction, str="message_erro_aniversario_registro"))
            return
    
    if 1 <= dia <= 31:
        if 1 <= int(mes) <= 12:
            if len(str(ano)) == 4:
                dia_str = str(dia).zfill(2)
                mes_str = str(mes).zfill(2)
                #data_nascimento = datetime.datetime(year=int(ano), month=int(mes), day=int(dia))
                data_nascimento_str = f"{dia_str}/{mes_str}/{ano}"
                                
                item = {
                    "nascimento": data_nascimento_str,
                    "nascimentoregistro": data_execucao_str  # Registra o dia que o comando foi rodado
                }
                
                try:
                    BancoUsuarios.update_document(membro, item)
                except:
                    await interaction.edit_original_response(content=Res.trad(interaction=interaction, str="message_erro_mongodb").format(interaction.user.id))
                    return
                
                await interaction.edit_original_response(content=Res.trad(interaction=interaction, str="message_aniversario_registro").format(data_nascimento_str))
            else:
                await interaction.edit_original_response(content=Res.trad(interaction=interaction, str="message_erro_aniversario_ano"))
        else:
            await interaction.edit_original_response(content=Res.trad(interaction=interaction, str="message_erro_aniversario_mes"))
    else:
        await interaction.edit_original_response(content=Res.trad(interaction=interaction, str="message_erro_aniversario_dia"))




    #função usuario reputação consultar
async def userrepconsulta(interaction,membro,menu):
    if membro is None:
        membro = interaction.user
    try:
        dado = BancoUsuarios.insert_document(membro)
    except:
        await interaction.followup.send(Res.trad(interaction=interaction,str="message_erro_mongodb").format(interaction.user.id),ephemeral=menu)
    await interaction.followup.send(Res.trad(interaction=interaction,str="message_consulta_rep").format(membro.id,dado["rep"]),ephemeral=menu)
    
    #função usuario reputação avaliar
async def userrepavaliar(interaction,membro,menu):
        if interaction.user == membro:
            await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_autorep"), ephemeral= True)
            return
        try:
            await interaction.response.defer()
            # Verifica o cooldown antes de permitir a ação
            permitido, tempo_restantante = await verificar_cooldown(interaction, "cdrep", 15)
            if not permitido:
                await interaction.followup.send( Res.trad(interaction=interaction, str="message_erro_cooldown").format(tempo_restantante),  ephemeral=True  )
                return
            
            # PARTE DO BANCO DE DADOS 
            dado = BancoUsuarios.insert_document(membro)
            item = dado['rep'] + 1
            item = {"rep": item}
            BancoUsuarios.update_document(membro,item)
            await interaction.followup.send(Res.trad(interaction=interaction,str="message_aviso_rep").format(membro.id,item["rep"],interaction.user.id),ephemeral=menu)
        except:
            await interaction.followup.send(Res.trad(interaction=interaction,str="message_erro_mongodb").format(interaction.user.id),ephemeral=menu)
            return
        


#Classe do MODAL Sobremim
class ModalEditaraniversario(discord.ui.Modal,title = "Editando seu Aniversário"):
    dia = discord.ui.TextInput(label="Dia (day)",style=discord.TextStyle.short,min_length=2,max_length=2,placeholder="03")
    mes = discord.ui.TextInput(label="Mês (month)",style=discord.TextStyle.short,min_length=2,max_length=2,placeholder="12")
    ano = discord.ui.TextInput(label="Ano (year)",style=discord.TextStyle.short,min_length=4,max_length=4,placeholder="1995")

    async def on_submit(self, interaction: discord.Interaction):
        dia = int(self.dia.value)
        mes = int(self.mes.value)
        ano = int(self.ano.value)
        await interaction.response.defer() 
        await aniversariodefinir(interaction,dia,mes,ano)
        await asyncio.sleep(5)
        await userperfil(interaction,interaction.user)


#Classe do MODAL Sobremim
class ModalEditarSobremim(discord.ui.Modal,title = "Editando seu Perfil"):
    sobremim = discord.ui.TextInput(label="Sobremim",style=discord.TextStyle.long,max_length=150)
    def __init__(self, descricao):
        super().__init__()
        self.sobremim.default = descricao

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if len(self.sobremim.value) <= 150:
            try:
                item = {"descricao": self.sobremim.value}
                BancoUsuarios.update_document(interaction.user,item)
            except:await interaction.edit_original_response(content=Res.trad(interaction=interaction,str="message_erro_mongodb").format(interaction.user.id))
            await interaction.edit_original_response(content=Res.trad(interaction=interaction,str="message_sobremim").format(self.sobremim.value))
            await asyncio.sleep(2)
            await userperfil(interaction,interaction.user)
        else:await interaction.edit_original_response(content=Res.trad(interaction=interaction,str="message_sobremim_limit"))
        

  #função Check premium usuario
async def userpremiumcheck(interaction):
    dado = BancoUsuarios.insert_document(interaction.user)
    premiumativo = BancoBot.insert_document()
    if premiumativo['premiumsys'] is False:
        print("sistema premium desativado, comando liberado")
        return True
    else:
        try:
          dado['premium']
          return True 
        except:
          return False 


  #função verificar_cooldown dos usuarios
async def verificar_cooldown(interaction, campo: str, tempo_cooldown: int):
    #fuso = pytz.timezone('America/Sao_Paulo')
    # Obtém os dados do usuário no banco
    usuario = BancoUsuarios.insert_document(interaction.user)
    # Tenta obter o tempo de cooldown 
    try:
        cd_atual = usuario[campo]
        cd_atual = cd_atual.replace(tzinfo=None)
    except:
        cd_atual = datetime.datetime.now().replace(tzinfo=None)

    agora = datetime.datetime.now().replace(tzinfo=None)
    print(f"agora {agora}")
    print(f"cd_atual {cd_atual} - {cd_atual.timestamp()}")
    if agora < cd_atual:
        return False, int(cd_atual.timestamp())  # Ainda está no cooldown

    # Atualiza o cooldown no banco de dados
    novo_cd = {campo: agora + datetime.timedelta(minutes=tempo_cooldown)}
    BancoUsuarios.update_document(usuario['_id'], novo_cd)

    return True, 0  # Cooldown expirado, ação permitida







#Botão Editar sobremim perfil Proprio usuario
class PerfilEditar(discord.ui.View):
    def __init__(self,interaction,membro,descricao):
        super().__init__(timeout=300)
        self.value=None
        self.membro = membro
        self.descricao = descricao
        self.interaction = interaction

        self.aboutme = discord.ui.Button(label=Res.trad(interaction=self.interaction,str="botão_sobremim"),style=discord.ButtonStyle.blurple,emoji="📝")
        self.add_item(item=self.aboutme)
        self.aboutme.callback = self.sobremimbutton
        self.skins = discord.ui.Button(label=Res.trad(interaction=self.interaction,str="botão_skins"),style=discord.ButtonStyle.blurple,emoji="🖼️")
        self.add_item(item=self.skins)
        self.skins.callback = self.skinsbutton
        self.aniversario = discord.ui.Button(label=Res.trad(interaction=self.interaction,str="botão_aniversario"),style=discord.ButtonStyle.blurple,emoji="<:Braix_bolo_cake:1290452116208357436>")
        self.add_item(item=self.aniversario)
        self.aniversario.callback = self.aniversariobutton

    def __call__(self):
        return self
    
    async def sobremimbutton(self,interaction: discord.Interaction):
            if interaction.user != self.membro:
                await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_interacaoalheia"),delete_after=30,ephemeral=True)
            else:

                await interaction.response.send_modal(ModalEditarSobremim(self.descricao))

    
    async def skinsbutton(self,interaction: discord.Interaction):
            if interaction.user != self.membro:
                await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_interacaoalheia"),delete_after=30,ephemeral=True)
            else:
                lista = []
                await interaction.response.defer()
                #LOGICA BRAIXEN E DUNE TODOS OS ITENS LIBERADOS
                if interaction.user.id == donoid or interaction.user.id == 943289140265512991:
                    filtro = {"name": {"$exists":True}}
                    dado = BancoLoja.select_many_document(filtro).sort('raridade',-1)
                    for item_id in dado:
                            lista.append(item_id['_id'])
                else: #LOGICA PADRÂO PUXANDO OS ITENS QUE O CARA COMPROU
                    dado = BancoUsuarios.insert_document(interaction.user)
                    for item_id in dado['backgrouds'].items():
                            lista.append(item_id[0])

                # Dividindo a lista em lotes de 20 itens
                lotes = [lista[i:i + 25] for i in range(0, len(lista), 25)]
                await painelescolhaskin(self,interaction,lotes=lotes,paginatual=1,totalpages = len(lotes))

    @app_commands.checks.cooldown(1,130000)
    async def aniversariobutton(self,interaction: discord.Interaction):
        if interaction.user != self.membro:
            await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_interacaoalheia"),delete_after=30,ephemeral=True)
        else:
            await interaction.response.send_modal(ModalEditaraniversario())


#Botão Editar sobremim perfil usuario diferente
class PerfilConsultar(discord.ui.View):
    def __init__(self,interaction,membro):
        super().__init__(timeout=300)
        self.membro = membro
        self.interaction = interaction
        self.value=None

        self.rep = discord.ui.Button(label=Res.trad(interaction=self.interaction,str="botão_rep"),style=discord.ButtonStyle.blurple,emoji="<:badge_rep:1345111116803608616>")
        self.add_item(item=self.rep)
        self.rep.callback = self.botaoreputacao

    def __call__(self):
        return self

    async def botaoreputacao(self,interaction: discord.Interaction):
        menu = False
        await userrepavaliar(interaction,self.membro,menu)


    #função Usuario Perfil
async def userperfil(interaction:discord.Interaction,membro, banner_temporario = None):
    await interaction.original_response()
    try:
        if membro is None:
            membro = interaction.user
        try:
            dado = BancoUsuarios.insert_document(membro)
        except:
            await interaction.edit_original_response(content=Res.trad(interaction=interaction,str="message_erro_mongodb").format(interaction.user.id))
            await asyncio.sleep(15)
            await interaction.delete_original_response()
            return
    
            #PEGA CLASSIFICAÇÂO DO CARA SE FOR DIFERENTE DE 0
        if dado['braixencoin'] != 0:
            filtro = {"braixencoin": {"$exists": True, "$gt": 0}, "ban": {"$exists": False}}
            user_cursor = BancoUsuarios.select_many_document(filtro).sort('braixencoin', -1)#.batch_size(400)
            for classificacao,x in enumerate(user_cursor,1):
                if membro.id == x['_id']:
                    break
        
            #GERAR O PADRÂO DE USO DE DATA DE ANIVERSARIO        
        dia, mes, ano = dado['nascimento'].split("/")    
        data_formatada = Res.trad(interaction=interaction, str="padrao_data").replace("%d", dia).replace("%m", mes).replace("%Y", ano)

        try:
            #Definindo o Fundo com as informações do membro
            if banner_temporario is not None:
                banner_name = banner_temporario
            else:    
                banner_name = dado['backgroud']
        except:
            #Caso o membro não tenha um fundo, damos um a ele
            banner_name = "braixen-house-2023"
            item = {"backgroud": banner_name,f"backgrouds.{banner_name}": banner_name}
            try:
                BancoUsuarios.update_document(membro,item)
            except:
                await interaction.edit_original_response(content=Res.trad(interaction=interaction,str="message_erro_mongodb").format(interaction.user.id))
                await asyncio.sleep(15)
                await interaction.delete_original_response()

        banner = BancoLoja.select_one(banner_name)
        #gerando banner
        fundo = Image.new("RGB",(800,400),"yellow")
        try:
            backgroud = Image.open(f"imagens/backgroud/all-itens/{banner['_id']}.png")
        except:
            backgroud = Image.open(requests.get(banner['url'], stream=True).raw)

        corfonte = banner['font_color']
        if membro.avatar:
            membroavatar = await membro.avatar.read()
            membroavatar = Image.open(io.BytesIO(membroavatar))
        else:
            membroavatar = Image.open(f"imagens/icons/server-not-icon.jpg")
        membroavatar = membroavatar.resize((100,100)) #112,112
        

        mascaraavatar = Image.open(f"imagens/icons/recorte-redondo.png")
        mascaraavatar = mascaraavatar.resize((100,100)) #112,112
        fundo.paste(backgroud,(0,0))
        fundo.paste(membroavatar,(18,18),mascaraavatar) # 11,11
        
        fundodraw = ImageDraw.Draw(fundo)
        membronome = re.sub('[^A-Za-zÀ-ú0-9.]+', ' ',membro.display_name)
        descricao = re.sub('[^A-Za-zÀ-ú0-9.]+', ' ',dado['descricao'])
        fundodraw.text((140, 11), f"{membronome[:14]}..." if len(membronome) > 14 else membronome, font=ImageFont.truetype("font/PoetsenOne-Regular.ttf", 24), fill=corfonte)
        #fundodraw.text((140, 11), f"{membronome[:13]}", font=ImageFont.truetype("font/PoetsenOne-Regular.ttf", 24), fill=corfonte)
        fundodraw.text((140,40),f"@{membro.name}",font = ImageFont.truetype("font/PoetsenOne-Regular.ttf",12),fill=corfonte)
        fundodraw.text((160,68),f"{datetime.datetime.strftime(membro.created_at, Res.trad(interaction=interaction, str='padrao_data'))}",font = ImageFont.truetype("font/Quick-Fox.ttf",13),fill=corfonte)
        if membro.bot:
            tamanho_texto_mention = fundodraw.textlength(text=f"@{membro.name}",font=ImageFont.truetype("font/PoetsenOne-Regular.ttf",12))
            iconbot = Image.open(f"imagens/icons/bot-badge.png")
            iconbot = iconbot.resize((22,22))
            fundo.paste(iconbot,(145 + int(tamanho_texto_mention),37),iconbot)
        try:
            guildavatar = await interaction.guild.icon.read()
            guildavatar = Image.open(io.BytesIO(guildavatar))
        except:
            guildavatar = Image.open(f"imagens/icons/server-not-icon.jpg")
        guildavatar = guildavatar.resize((21,21))
        mascaraguild = Image.open(f"imagens/icons/recorte-redondo.png")
        mascaraguild = mascaraguild.resize((21,21))
        try: 
            fundodraw.text((265,68),f"{datetime.datetime.strftime(membro.joined_at, Res.trad(interaction=interaction, str='padrao_data'))}",font = ImageFont.truetype("font/Quick-Fox.ttf",13),fill=corfonte)
            fundo.paste(guildavatar,(242,63),mascaraguild)
        except:
            print("usuario não está na comunidade")
        fundodraw.text((170,98),f"{data_formatada[:5]}",font = ImageFont.truetype("font/Quick-Fox.ttf",18),fill=corfonte)
        
        try:
            if dado['premium']:
                braixenicon = Image.open(f"imagens/icons/icon-premium.png")
                fundo.paste(braixenicon,(236,91),braixenicon) # 236,91
                fundodraw.text((264, 95), "PREMIUM", font=ImageFont.truetype("font/PoetsenOne-Regular.ttf", 18), fill=corfonte)
                
        except:
            print(f"usuario {membro.id} não é premium")
        try:
            fundodraw.text((65,150),"{:,.0f}".format(dado['graveto']),font = ImageFont.truetype("font/Quick-Fox.ttf",20),fill=corfonte)
        except:
            item = {"graveto": 0}
            BancoUsuarios.update_document(membro,item)
            print(f"usuario {membro.id} registrando no banco graveto")
            fundodraw.text((68,150),"0",font = ImageFont.truetype("font/Quick-Fox.ttf",20),fill=corfonte)

        fundodraw.text((238,205),f"{dado['rep']}",font = ImageFont.truetype("font/Quick-Fox.ttf",20),fill=corfonte)
        braixencoin = calcular_saldo(dado['braixencoin'])
        fundodraw.text((65,205),"{}".format(braixencoin),font = ImageFont.truetype("font/Quick-Fox.ttf",20),fill=corfonte)
        #fundodraw.text((65,205),"{:,.0f}".format(braixencoin),font = ImageFont.truetype("font/Quick-Fox.ttf",20),fill=corfonte)
        if dado['braixencoin'] != 0:
            fundodraw.text((75+fundodraw.textlength(str(braixencoin),ImageFont.truetype("font/Quick-Fox.ttf",20)),202),"TOP",font = ImageFont.truetype("font/Quick-Fox.ttf",14),fill=corfonte)
            fundodraw.text((75+fundodraw.textlength(str(braixencoin),ImageFont.truetype("font/Quick-Fox.ttf",20)),213),"{:,.0f}".format(classificacao),font = ImageFont.truetype("font/Quick-Fox.ttf",14),fill=corfonte)

        nivel = calcular_nivel(dado['xpg'])
        fundodraw.text((238,150),f"{nivel}",font = ImageFont.truetype("font/Quick-Fox.ttf",20),fill=corfonte)
        h = fundodraw.textlength(str(nivel),ImageFont.truetype("font/Quick-Fox.ttf",20))
        fundodraw.text((242+h,147),f"{dado['xpg']}",font = ImageFont.truetype("font/Quick-Fox.ttf",14),fill=corfonte)
        fundodraw.text((242+h,158),f"XP",font = ImageFont.truetype("font/Quick-Fox.ttf",14),fill=corfonte)
        fundodraw.multiline_text((20,255),f"\n".join(textwrap.wrap(descricao,width=41)),font=ImageFont.truetype("font/KoomikMono-Regular.otf",14),spacing=0,align ="left",fill=corfonte)        
        try:
            if dado['ban']:  #SE O USUARIO ESTIVER BANIDO IMPRIME UM BAN GIGANTE
                ban = True
                artebanido = Image.open(f"imagens/icons/Artbanned.png")
                fundo.paste(artebanido,(0,0),artebanido) 
        except:
            ban = False
        buffer = io.BytesIO()
        fundo.save(buffer,format="PNG")
        buffer.seek(0)

        if banner_temporario:
            await interaction.followup.send(content="",file=discord.File(fp=buffer,filename="perfil-temporário.png"),ephemeral=True)
        elif interaction.user == membro:
            await interaction.edit_original_response(content="",attachments=[discord.File(fp=buffer,filename="perfil.png")],view = PerfilEditar(interaction,membro,descricao))
        elif ban == True:
            await interaction.edit_original_response(content="",attachments=[discord.File(fp=buffer,filename="perfil.png")])
        else:await interaction.edit_original_response(content="",attachments=[discord.File(fp=buffer,filename="perfil.png")],view = PerfilConsultar(interaction,membro))
    except Exception as e:
            #Chamando embed de erro
        await Res.erro_brix_embed(interaction,str="message_erro_brixsystem",e=e,comando="Userperfil")




# PAINEL DE ESCOLHA DE Skins
class menuskins(discord.ui.Select):
    def __init__(self, lista: list, interaction: discord.Interaction,paginatual):
        self.membro = interaction.user
        options = []
       
        # Utiliza a lista fornecida em vez de buscar no banco de dados
        for item in lista:
            if item['raridade'] == 0:
                emoji = "<:Pokeball:1272668305190162524>"
            elif item['raridade'] == 1:
                emoji = "💠"
            elif item['raridade'] == 2:
                emoji = "<:BH_Badge_Exclusivebadge:1154180111445270608>"
            elif item['raridade'] == 3:
                emoji = "<:BH_vipbadge:1154180197600473159>"
                
            descricao = str(item['descricao'])
            if len(descricao) > 95:
                descricao = descricao[:95] + '...'
            options.append(discord.SelectOption(value=str(item['_id']),label=str(item['name']),description=descricao,emoji=emoji))
        
        super().__init__(
            placeholder=f"{Res.trad(interaction=interaction,str='botão_pagina')} {paginatual}",
            min_values=1,
            max_values=1,
            options=options,
        )
        
    async def callback(self, interaction: discord.Interaction): #Retorno seleção Dropdown
        #coleta os dados do membro no banco de dados
        if interaction.user != self.membro:
            await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_interacaoalheia"),delete_after=30,ephemeral=True)
        else:
            menu=False
            await interaction.response.defer(ephemeral=menu)
            BancoUsuarios.update_document(interaction.user,{"backgroud": self.values[0]})
            await userperfil(interaction,interaction.user)



async def painelescolhaskin(self,interaction: discord.Interaction,lotes,paginatual,totalpages):
    await interaction.original_response()

    filtro = {"_id": {"$in": lotes[paginatual-1]}}
    dados = BancoLoja.select_many_document(filtro).sort('raridade',-1)

    view = discord.ui.View()
    view.add_item(menuskins(dados, interaction,paginatual))

    async def botaodesair(interaction):
        # Decrementando o índice da página
        if interaction.user != self.membro:
            await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_interacaoalheia"),delete_after=30,ephemeral=True)
        else:
            await interaction.response.defer()
            await userperfil(interaction,interaction.user)

    async def voltaritem(interaction):
        # Decrementando o índice da página
        if interaction.user != self.membro:
            await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_interacaoalheia"),delete_after=30,ephemeral=True)
        else:
            await interaction.response.defer()
            await painelescolhaskin(self,interaction,lotes=lotes,paginatual=paginatual-1,totalpages=totalpages)

    async def avancaritem(interaction):
        # Incrementando o índice da página
        if interaction.user != self.membro:
            await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_interacaoalheia"),delete_after=30,ephemeral=True)
        else:
            await interaction.response.defer()
            await painelescolhaskin(self,interaction,lotes=lotes,paginatual=paginatual+1,totalpages=totalpages)

    botaosair = discord.ui.Button(emoji="<:setasair:1318701737648980008>",style=discord.ButtonStyle.gray)
    view.add_item(item=botaosair)
    botaosair.callback = partial(botaodesair)

    #if paginatual == 1:
    botaovoltar = discord.ui.Button(emoji="<:setaesquerda:1318698827422765189>",style=discord.ButtonStyle.gray,disabled=(paginatual == 1))
    #else:
        #botaovoltar = discord.ui.Button(label="<",style=discord.ButtonStyle.gray)
    view.add_item(item=botaovoltar)
    botaovoltar.callback = partial(voltaritem)

    botaopagina = discord.ui.Button(label=f"{paginatual}/{totalpages}",style=discord.ButtonStyle.gray,disabled=True)
    view.add_item(item=botaopagina)

    #if paginatual == totalpages:
    botaoavancar = discord.ui.Button(emoji="<:setadireita:1318698789225369660>",style=discord.ButtonStyle.gray,disabled=(paginatual == totalpages))
    #else:
        #botaoavancar = discord.ui.Button(label=">",style=discord.ButtonStyle.gray)
    view.add_item(item=botaoavancar)
    botaoavancar.callback = partial(avancaritem)

    if interaction.user.id == donoid or interaction.user.id == 943289140265512991:
        await interaction.edit_original_response(content="<:Braix_Jay:1272669280932069437>┃ Por Algum Milagre da programação todos os itens são liberado para você ~kyuu", view=view)
    else:await interaction.edit_original_response(content="", view=view)