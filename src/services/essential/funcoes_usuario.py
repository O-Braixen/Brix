import discord,os,asyncio,time,datetime,pytz,random,json,io,textwrap,requests,typing,re
from operator import itemgetter
from functools import partial
from discord.ext import commands,tasks
from discord import app_commands
from discord.interactions import Interaction
from src.services.connection.database import BancoUsuarios,BancoServidores,BancoLoja,BancoBot
from src.services.essential.respostas import Res
from src.services.essential.diversos import calcular_saldo,calcular_nivel
from PIL import Image, ImageFont, ImageDraw, ImageOps #IMPORTAÇÂO Py PIL IMAGEM
from dotenv import load_dotenv





# ======================================================================

load_dotenv()
donoid = int(os.getenv("DONO_ID"))






# ======================================================================
#                           FUNÇÔES AQUIII



# ======================================================================
#FUNÇÃO DE USUARIO PARA CONSULTAR ANIVERSARIO
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

















# ======================================================================
#FUNÇÃO PARA DEFINIR O ANIVERSARIO DO USUARIO
async def aniversariodefinir(interaction: discord.Interaction, dia, mes, ano):
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

    # Tenta validar ano, mês e dia
    try:
        ano_int = int(ano)
        mes_int = int(mes)
        dia_int = int(dia)

        # regra extra: impedir anos menores que 1900 e maiores que o atual
        ano_atual = datetime.datetime.now().year
        if ano_int < 1900 or ano_int > (ano_atual - 8):
            raise ValueError("Ano fora do intervalo permitido.")

        data_nascimento = datetime.datetime(year=ano_int, month=mes_int, day=dia_int)
    except ValueError:
        await interaction.edit_original_response(content=Res.trad(interaction=interaction, str="message_erro_aniversario_data_invalida"))
        return

    data_nascimento_str = data_nascimento.strftime("%d/%m/%Y")
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



















# ======================================================================
# FUNÇÃO PARA CONSULTAR A REPUTAÇÃO DO USUARIO
async def userrepconsulta(interaction,membro,menu):
    if membro is None:
        membro = interaction.user
    try:
        dado = BancoUsuarios.insert_document(membro)
    except:
        await interaction.followup.send(Res.trad(interaction=interaction,str="message_erro_mongodb").format(interaction.user.id),ephemeral=menu)
    await interaction.followup.send(Res.trad(interaction=interaction,str="message_consulta_rep").format(membro.id,dado["rep"]),ephemeral=menu)
    









# ======================================================================
#FUNÇÃO PARA DAR UMA REPUTAÇÃO A UM USUARIO
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
        











# ======================================================================
# CLASSE DO MODAL DO BOTÃO DE DEFINIR ANIVERSARIO DO USUARIO
class ModalEditaraniversario(discord.ui.Modal):
    
    def __init__(self, interaction: discord.Interaction):
        # Traduz o título do modal
        super().__init__(title=Res.trad(interaction=interaction, str="modal_edit_birthday_title"))
        
        # Cria os campos de texto, traduzindo o rótulo e o placeholder
        self.dia = discord.ui.TextInput( label=Res.trad(interaction=interaction, str="birthday_day_label"), style=discord.TextStyle.short, min_length=2, max_length=2, placeholder="03" )
        self.mes = discord.ui.TextInput( label=Res.trad(interaction=interaction, str="birthday_month_label"), style=discord.TextStyle.short, min_length=2, max_length=2, placeholder="12" )
        self.ano = discord.ui.TextInput( label=Res.trad(interaction=interaction, str="birthday_year_label"), style=discord.TextStyle.short, min_length=4, max_length=4, placeholder="1995" )
        
        # Adiciona os campos ao modal
        self.add_item(self.dia)
        self.add_item(self.mes)
        self.add_item(self.ano)

    async def on_submit(self, interaction: discord.Interaction):
        dia = int(self.dia.value)
        mes = int(self.mes.value)
        ano = int(self.ano.value)
        await interaction.response.defer() 
        await aniversariodefinir(interaction, dia, mes, ano)
        await asyncio.sleep(5)
        await userperfil(interaction, interaction.user)








# ======================================================================
# MODAL DO BOTÃO SOBRE MIM DO /PERFIL VER
class ModalEditarSobremim(discord.ui.Modal):
    def __init__(self, interaction: discord.Interaction, descricao: str = None):
        # Traduz o título do modal
        super().__init__(title=Res.trad(interaction=interaction, str="modal_edit_profile_title"))        
        # Cria o campo de texto, traduzindo o rótulo e definindo o valor padrão
        self.sobremim = discord.ui.TextInput( label=Res.trad(interaction=interaction, str="aboutme_input_label"), style=discord.TextStyle.long, max_length=150, default=descricao,  placeholder=Res.trad(interaction=interaction, str="aboutme_input_placeholder") )
        
        # Adiciona o campo de texto ao modal
        self.add_item(self.sobremim)

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







# ======================================================================
# FUNÇÃO QUE VERIFICA SE O USUARIO É ASSINANTE PREMIUM
async def userpremiumcheck(interaction):
    try:
        usuario = interaction.user
    except:
        usuario = interaction

    # Carrega os dados
    dado = BancoUsuarios.insert_document(usuario)
    premiumativo = BancoBot.insert_document()

    # Se o sistema premium estiver desligado
    if not premiumativo.get('premiumsys', True):
        print("💎  -  sistema premium desativado, comando liberado")
        return True

    # Verifica se o usuário tem premium normal 
    if 'premium' in dado:
        return True

    return False











# ======================================================================
# FUNÇÃO QUE VERIFICA O COOLDONW PARA DETEMINADO COMANDO REALIZADO PELO USUARIO
async def verificar_cooldown(interaction, campo: str, tempo_cooldown: int):
    try: 
        usuario = interaction.user
    except:
        usuario = interaction
    # Obtém os dados do usuário no banco
    usuario = BancoUsuarios.insert_document(usuario)
    # Tenta obter o tempo de cooldown 
    try:
        cd_atual = usuario[campo]
        cd_atual = cd_atual.replace(tzinfo=None)
    except:
        cd_atual = datetime.datetime.now().replace(tzinfo=None)

    agora = datetime.datetime.now().replace(tzinfo=None)
    if agora < cd_atual:
        return False, int(cd_atual.timestamp())  # Ainda está no cooldown

    # Atualiza o cooldown no banco de dados
    novo_cd = {campo: agora + datetime.timedelta(minutes=tempo_cooldown)}
    BancoUsuarios.update_document(usuario['_id'], novo_cd)

    return True, 0  # Cooldown expirado, ação permitida















# ======================================================================
# VIEW DA CARTELA /PERFIL VER ONDE É EXIBIDO OS BOTÕES PARA O USUARIO
class PerfilEditar(discord.ui.View):
    def __init__(self,interaction,membro,descricao,aniversario):
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
        if aniversario == "00/00/0000":
            self.aniversario = discord.ui.Button(label=Res.trad(interaction=self.interaction,str="botão_aniversario"),style=discord.ButtonStyle.blurple,emoji="<:Braix_bolo_cake:1290452116208357436>")
            self.add_item(item=self.aniversario)
            self.aniversario.callback = self.aniversariobutton

    def __call__(self):
        return self
    
    async def sobremimbutton(self,interaction: discord.Interaction):
        if interaction.user != self.membro:
            await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_interacaoalheia"),delete_after=30,ephemeral=True)
        else:

            await interaction.response.send_modal(ModalEditarSobremim(interaction, self.descricao))

    
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

    async def aniversariobutton(self,interaction: discord.Interaction):
        if interaction.user != self.membro:
            await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_interacaoalheia"),delete_after=30,ephemeral=True)
        else:
            await interaction.response.send_modal(ModalEditaraniversario(interaction=interaction))














# ======================================================================
# CLASSE COM BOTÃO DE CONSULTA DO /PERFIL VER
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
















# ======================================================================
# FUNÇÃO DE USUARIO PERFIL DO /PERFIL VER
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
            backgroud = Image.open(f"src/assets/imagens/backgroud/all-itens/{banner['_id']}.png")
        except:
            backgroud = Image.open(requests.get(banner['url'], stream=True).raw)

        corfonte = banner['font_color']
        if membro.avatar:
            membroavatar = await membro.avatar.read()
            membroavatar = Image.open(io.BytesIO(membroavatar))
        else:
            membroavatar = Image.open(f"src/assets/imagens/icons/server-not-icon.jpg")
        membroavatar = membroavatar.resize((100,100)) #112,112
        

        mascaraavatar = Image.open(f"src/assets/imagens/icons/recorte-redondo.png")
        mascaraavatar = mascaraavatar.resize((100,100)) #112,112
        fundo.paste(backgroud,(0,0))
        fundo.paste(membroavatar,(18,18),mascaraavatar) # 11,11
        
        fundodraw = ImageDraw.Draw(fundo)
        membronome = re.sub('[^A-Za-zÀ-ú0-9.]+', ' ',membro.display_name)
        descricao = re.sub('[^A-Za-zÀ-ú0-9.]+', ' ',dado['descricao'])
        fundodraw.text((140, 11), f"{membronome[:14]}..." if len(membronome) > 14 else membronome, font=ImageFont.truetype("src/assets/font/PoetsenOne-Regular.ttf", 24), fill=corfonte)
        #fundodraw.text((140, 11), f"{membronome[:13]}", font=ImageFont.truetype("src/assets/font/PoetsenOne-Regular.ttf", 24), fill=corfonte)
        fundodraw.text((140,40),f"@{membro.name}",font = ImageFont.truetype("src/assets/font/PoetsenOne-Regular.ttf",12),fill=corfonte)
        fundodraw.text((160,68),f"{datetime.datetime.strftime(membro.created_at, Res.trad(interaction=interaction, str='padrao_data'))}",font = ImageFont.truetype("src/assets/font/Quick-Fox.ttf",13),fill=corfonte)
        if membro.bot:
            tamanho_texto_mention = fundodraw.textlength(text=f"@{membro.name}",font=ImageFont.truetype("src/assets/font/PoetsenOne-Regular.ttf",12))
            iconbot = Image.open(f"src/assets/imagens/icons/bot-badge.png")
            iconbot = iconbot.resize((22,22))
            fundo.paste(iconbot,(145 + int(tamanho_texto_mention),37),iconbot)
        try:
            guildavatar = await interaction.guild.icon.read()
            guildavatar = Image.open(io.BytesIO(guildavatar))
        except:
            guildavatar = Image.open(f"src/assets/imagens/icons/server-not-icon.jpg")
        guildavatar = guildavatar.resize((21,21))
        mascaraguild = Image.open(f"src/assets/imagens/icons/recorte-redondo.png")
        mascaraguild = mascaraguild.resize((21,21))
        try: 
            fundodraw.text((265,68),f"{datetime.datetime.strftime(membro.joined_at, Res.trad(interaction=interaction, str='padrao_data'))}",font = ImageFont.truetype("src/assets/font/Quick-Fox.ttf",13),fill=corfonte)
            fundo.paste(guildavatar,(242,63),mascaraguild)
        except:
            print("usuario não está na comunidade")
        fundodraw.text((170,98),f"{data_formatada[:5]}",font = ImageFont.truetype("src/assets/font/Quick-Fox.ttf",18),fill=corfonte)
        
        try:
            if dado['premium']:
                braixenicon = Image.open(f"src/assets/imagens/icons/icon-premium.png")
                fundo.paste(braixenicon,(236,91),braixenicon) # 236,91
                fundodraw.text((264, 95), "PREMIUM", font=ImageFont.truetype("src/assets/font/PoetsenOne-Regular.ttf", 18), fill=corfonte)
                
        except:
            print(f"usuario {membro.id} não é premium")
        try:
            fundodraw.text((65,150),"{:,.0f}".format(dado['graveto']),font = ImageFont.truetype("src/assets/font/Quick-Fox.ttf",20),fill=corfonte)
        except:
            item = {"graveto": 0}
            BancoUsuarios.update_document(membro,item)
            print(f"usuario {membro.id} registrando no banco graveto")
            fundodraw.text((68,150),"0",font = ImageFont.truetype("src/assets/font/Quick-Fox.ttf",20),fill=corfonte)

        fundodraw.text((238,205),f"{dado['rep']}",font = ImageFont.truetype("src/assets/font/Quick-Fox.ttf",20),fill=corfonte)
        braixencoin = calcular_saldo(dado['braixencoin'])
        fundodraw.text((65,205),"{}".format(braixencoin),font = ImageFont.truetype("src/assets/font/Quick-Fox.ttf",20),fill=corfonte)
        #fundodraw.text((65,205),"{:,.0f}".format(braixencoin),font = ImageFont.truetype("src/assets/font/Quick-Fox.ttf",20),fill=corfonte)
        if dado['braixencoin'] != 0:
            fundodraw.text((75+fundodraw.textlength(str(braixencoin),ImageFont.truetype("src/assets/font/Quick-Fox.ttf",20)),202),"TOP",font = ImageFont.truetype("src/assets/font/Quick-Fox.ttf",14),fill=corfonte)
            fundodraw.text((75+fundodraw.textlength(str(braixencoin),ImageFont.truetype("src/assets/font/Quick-Fox.ttf",20)),213),"{:,.0f}".format(classificacao),font = ImageFont.truetype("src/assets/font/Quick-Fox.ttf",14),fill=corfonte)

        nivel = calcular_nivel(dado['xpg'])
        fundodraw.text((238,150),f"{nivel}",font = ImageFont.truetype("src/assets/font/Quick-Fox.ttf",20),fill=corfonte)
        h = fundodraw.textlength(str(nivel),ImageFont.truetype("src/assets/font/Quick-Fox.ttf",20))
        fundodraw.text((242+h,147),f"{dado['xpg']}",font = ImageFont.truetype("src/assets/font/Quick-Fox.ttf",14),fill=corfonte)
        fundodraw.text((242+h,158),f"XP",font = ImageFont.truetype("src/assets/font/Quick-Fox.ttf",14),fill=corfonte)
        fundodraw.multiline_text((20,255),f"\n".join(textwrap.wrap(descricao,width=41)),font=ImageFont.truetype("src/assets/font/KoomikMono-Regular.otf",14),spacing=0,align ="left",fill=corfonte)        
        try:
            if dado['ban']:  #SE O USUARIO ESTIVER BANIDO IMPRIME UM BAN GIGANTE
                ban = True
                # Cria uma camada preta semitransparente do mesmo tamanho do fundo
                overlay = Image.new("RGBA", fundo.size, (0, 0, 0, 100))  # 150 = opacidade
                fundo = Image.alpha_composite(fundo.convert("RGBA"), overlay)

                # Carrega e cola a marca de banido
                artebanido = Image.open(f"src/assets/imagens/icons/Artbanned.png")
                fundo.paste(artebanido,(0,0),artebanido) 
        except:
            ban = False
        buffer = io.BytesIO()
        fundo.save(buffer,format="PNG")
        buffer.seek(0)

        if banner_temporario:
            await interaction.followup.send(content="",file=discord.File(fp=buffer,filename="perfil-temporário.png"),ephemeral=True)
        elif interaction.user == membro:
            await interaction.edit_original_response(content="",attachments=[discord.File(fp=buffer,filename="perfil.png")],view = PerfilEditar(interaction,membro,descricao,dado['nascimento']))
        elif ban == True:
            await interaction.edit_original_response(content="",attachments=[discord.File(fp=buffer,filename="perfil.png")])
        else:await interaction.edit_original_response(content="",attachments=[discord.File(fp=buffer,filename="perfil.png")],view = PerfilConsultar(interaction,membro))
    except Exception as e:
            #Chamando embed de erro
        await Res.erro_brix_embed(interaction,str="message_erro_brixsystem",e=e,comando="Userperfil")


















# ======================================================================
# SELETOR DE SKINS DO COMANDO /PERFIL VER 
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




















# ======================================================================
# BOTÃO PARA TROCAR A PAGINA DE ESCOLHA DE SKIN DO /PERFIL VER
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
















# ======================================================================
# FUNÇÃO PARA EXIBIR A CLASSIFICAÇÃO DE MEMBROS DO OS COMANDO FINANCEIRO E DE REPUTAÇÃO
async def exibirtops(self, interaction, bloco_classificacao,pagina,originaluser,background):
    await interaction.original_response()
    try:
            # Obtendo IDs dos membros no bloco
        bloco_atual = bloco_classificacao[pagina-1]
        ids_membros = [membro[1] for membro in bloco_atual]

            # Buscando os usuários e carregando os avatares
        membros = await asyncio.gather(*[self.client.fetch_user(membro_id) for membro_id in ids_membros])

            # Processando avatares de forma assíncrona
        avatares = await asyncio.gather(*[process_avatar(self,membro) for membro in membros])

            # Configurações de imagem
        fundo = Image.new("RGB", (600, 400), "yellow")
        fundo.paste(background, (0, 0))

        avatar_positions = [(382, 86), (380, 148), (382, 212), (381, 277), (379, 337)]
        for avatar, pos in zip(avatares, avatar_positions):
            fundo.paste(avatar, pos, self.tops_recorte_mascara)

        fundodraw = ImageDraw.Draw(fundo)

        text_positions = [(434, 91), (434, 153), (434, 218), (434, 281), (434, 341)]
        saldo_positions = [(450, 114), (450, 176), (450, 240), (450, 304), (450, 364)]

        for i, ((classificacao, membro_id, saldo), membro, pos_text, pos_saldo) in enumerate(zip(bloco_atual, membros, text_positions, saldo_positions)):
            try:
                fundodraw.text(pos_text, f"{classificacao} - {membro.name[:12]}", font=self.tops_font)
            except:
                fundodraw.text(pos_text, "semnome", font=self.tops_font)
            fundodraw.text(pos_saldo, "{:,.0f}".format(saldo), font=self.tops_font_numero)

        fundodraw.text((10,10), f"{Res.trad(interaction=interaction,str='botão_pagina')} {pagina}/{len(bloco_classificacao)}", font=self.tops_font_numero)

        buffer = io.BytesIO()
        fundo.save(buffer, format="PNG")
        buffer.seek(0)
        view = discord.ui.View()

            # Botoões
        botaovoltarfast = discord.ui.Button(emoji="<:setaduplaesquerda:1318716104474099722>", style=discord.ButtonStyle.gray, disabled=(pagina == 1))
        view.add_item(item=botaovoltarfast)
        botaovoltarfast.callback = partial(trocarpaginatops, self, blocos_classificacao=bloco_classificacao, pagina=1,originaluser=originaluser , background = background)

        botaovoltar = discord.ui.Button(emoji="<:setaesquerda:1318698827422765189>", style=discord.ButtonStyle.gray, disabled=(pagina == 1))
        view.add_item(item=botaovoltar)
        botaovoltar.callback = partial(trocarpaginatops, self, blocos_classificacao=bloco_classificacao, pagina=pagina-1,originaluser=originaluser , background = background)

        #botaopagina = discord.ui.Button(label=f"{pagina}/{len(bloco_classificacao)}", style=discord.ButtonStyle.gray, disabled=True)
        #view.add_item(item=botaopagina)

        botaoavancar = discord.ui.Button(emoji="<:setadireita:1318698789225369660>", style=discord.ButtonStyle.gray, disabled=(pagina == len(bloco_classificacao)))
        view.add_item(item=botaoavancar)
        botaoavancar.callback = partial(trocarpaginatops, self, blocos_classificacao=bloco_classificacao, pagina=pagina+1,originaluser=originaluser , background = background)

        botaoavancarfast = discord.ui.Button(emoji="<:setadupladireita:1318715892242190419>", style=discord.ButtonStyle.gray, disabled=(pagina == len(bloco_classificacao)))
        view.add_item(item=botaoavancarfast)
        botaoavancarfast.callback = partial(trocarpaginatops, self, blocos_classificacao=bloco_classificacao, pagina=len(bloco_classificacao),originaluser=originaluser , background = background)

            # Botão para buscar a página do usuário original
        botaobuscar = discord.ui.Button(label=Res.trad(interaction=interaction,str="botão_buscarpaginausuario"),emoji="<:lupa:1318713789872603187>", style=discord.ButtonStyle.primary)
        view.add_item(item=botaobuscar)
        botaobuscar.callback = partial(buscar_pagina_usuario, self, blocos_classificacao=bloco_classificacao, originaluser=originaluser , background = background)

        await interaction.edit_original_response(attachments={discord.File(fp=buffer, filename="Rank.png")},view=view)

    except Exception as e:
        await Res.erro_brix_embed(interaction, str="message_erro_brixsystem", e=e,comando="exibirtops")

async def process_avatar(self, membro):
        try:
            avatar = await membro.avatar.read()
            avatar = Image.open(io.BytesIO(avatar)).resize((44, 44))
        except:
            avatar = self.default_avatar
        return avatar

@commands.Cog.listener()
async def trocarpaginatops(self,interaction,blocos_classificacao,pagina,originaluser,background):

  if interaction.user != originaluser:
    await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_interacaoalheia"),delete_after=10,ephemeral=True)
  else:
    view = discord.ui.View.from_message(interaction.message)
    for item in view.children:
            item.disabled = True

        # Atualiza a resposta original para refletir os botões desativados
    await interaction.response.edit_message(view=view)
    #await interaction.response.defer()
    await exibirtops(self,interaction,blocos_classificacao,pagina,originaluser,background)

@commands.Cog.listener()
async def buscar_pagina_usuario(self, interaction, blocos_classificacao, originaluser,background):
    # Verifica se o botão foi clicado pelo usuário correto
    if interaction.user != originaluser:
        await interaction.response.send_message(Res.trad(interaction=interaction, str="message_erro_interacaoalheia"), delete_after=20, ephemeral=True)
        return

    # Busca a página onde o usuário está
    for idx, bloco in enumerate(blocos_classificacao):
        for classificacao, membro_id, saldo in bloco:
            if membro_id == originaluser.id:
                view = discord.ui.View.from_message(interaction.message)
                for item in view.children:
                        item.disabled = True

                    # Atualiza a resposta original para refletir os botões desativados
                await interaction.response.edit_message(view=view)
                # Usuário encontrado, exibir página
                await exibirtops(self, interaction, blocos_classificacao, idx + 1, originaluser,background)
                return

    # Caso o usuário não seja encontrado
    await interaction.response.send_message(Res.trad(interaction=interaction, str="message_financeiro_ausentelista"), ephemeral=True)
