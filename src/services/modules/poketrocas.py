import discord ,datetime , re , io , requests
from discord.ext import commands
from discord import app_commands,Locale
from functools import partial
from src.services.essential.respostas import Res
from src.services.essential.funcoes_usuario import userpremiumcheck 
from src.services.essential.diversos import gerar_id_unica
from src.services.connection.database import BancoTrocas
from src.services.essential.pokemon_module import pokemon_autocomplete , jogos_autocomplete , encontrar_cor_tipo , get_jogo_nome, get_pokemon
from PIL import Image, ImageDraw, ImageFont , ImageOps







async def gerar_arte_trocas(interaction, troca):
    dex = await get_pokemon(troca['pokemon'])
            
    # Criação da imagem
    backgroud = Image.new('RGBA', (500, 300), (0,0,0,0))
    fundoicones = Image.open("src/assets/imagens/icons/iconpoketrocapokemon.png")
    corbase = encontrar_cor_tipo(dex['types'][0]['type']['name'])

    bw = fundoicones.convert('L')
    fundo_colorido = ImageOps.colorize(bw, black="black", white=corbase)
    fundo_colorido = fundo_colorido.convert("RGBA")

    # Desenha um retângulo com bordas arredondadas na máscara
    mascara = Image.new("L", backgroud.size, 0)  # 'L' para imagem em escala de cinza
    draw = ImageDraw.Draw(mascara)
    draw.rounded_rectangle([0, 0, backgroud.size[0], backgroud.size[1]], radius=10, fill=255)
                    
    
    d = ImageDraw.Draw(fundo_colorido)
    fontegrande = ImageFont.truetype("src/assets/font/Hey Comic.ttf",34)
    fontemedia = ImageFont.truetype("src/assets/font/KoomikMono-Regular.otf",32)
    fontepequena = ImageFont.truetype("src/assets/font/PoetsenOne-Regular.ttf",16)

    # Escreve os dados da troca
    texto = troca['pokemon'].capitalize()
    largura_texto = draw.textlength(texto, font=fontegrande)
    pos_x = (295 - largura_texto) // 2

    d.text((pos_x+210, 5), texto, font=fontegrande)
    d.text((210, 50), f"{Res.trad(interaction=interaction, str='user_id')} {troca['user_id']}", font=fontepequena)
    d.text((210, 70), f"{Res.trad(interaction=interaction, str='username')}  {troca['username']}", font=fontepequena)
    d.text((210, 90), f"{Res.trad(interaction=interaction, str='registrado_em')}  {troca['data_registro'].strftime(Res.trad(interaction=interaction, str='padrao_data'))}", font=fontepequena)
    status_list = Res.trad(interaction=interaction, str='message_poketroca_status')
    status = status_list[troca['status']-1]

    d.text((210, 110), f"status: {status}", font=fontepequena)
    if troca['user_id_aceitou'] is not None:
        d.text((210, 140), Res.trad(interaction=interaction, str='message_poketroca_treinadordados'), font=fontepequena)
        d.text((210, 160), f"{Res.trad(interaction=interaction, str='user_id')} {troca['user_id_aceitou']}", font=fontepequena)
        d.text((210, 180), f"{Res.trad(interaction=interaction, str='username')} {troca['username_aceitou']}", font=fontepequena)

    nome, plataforma = await get_jogo_nome(troca['jogo'])
    d.text((118, 210), f"ID:{troca['id_troca']}",  font=fontemedia)
    d.text((118, 265), f"{nome} ({plataforma})", font=fontepequena)
    

    #MONTAGEM DA IMAGEM
    try:
        if troca["shiny"] is True:
            pokeimagem = Image.open(requests.get(dex['front_shiny'], stream=True).raw)
        else:
            pokeimagem = Image.open(requests.get(dex['front_default'], stream=True).raw)
    except:
        pokeimagem = Image.open("src/assets/imagens/Pokedex/Interrogation.png")        

    pokeimagem = pokeimagem.resize((190,190))
    #backgroud.paste(fundoicones,(0,0), fundoicones)
    backgroud.paste(fundo_colorido, (0,0), fundo_colorido)
    backgroud.paste(pokeimagem,(10,10), pokeimagem)
    #CAPA JOGO
    capajogo = Image.open(f"src/assets/imagens/JogosCapa/{troca['jogo']}.png")
    capajogo.thumbnail((100, 100))
    backgroud.paste(capajogo,(10,185), capajogo)

    if troca["shiny"] is True:
        shiny = Image.open("src/assets/imagens/Pokedex/Shiny.png")
        backgroud.paste( shiny.resize((80,80)) , (40,100) ,shiny.resize((80,80)) ) #COLANDO POKÈMON
    
    # Salva a imagem no buffer
    buffer = io.BytesIO()
    backgroud.save(buffer, 'PNG')
    buffer.seek(0)

    return buffer






async def gerar_arte_trocas_disponiveis(interaction,trocas):
    # Carrega imagem de fundo
    fundo = Image.open("src/assets/imagens/icons/trocapokemon_disponiveis.png").convert("RGBA")
    img = fundo.copy()

    draw = ImageDraw.Draw(img)
    fontegrande = ImageFont.truetype("src/assets/font/Hey Comic.ttf", 36)
    fontemedia = ImageFont.truetype("src/assets/font/KoomikMono-Regular.otf", 28)
    fontepequena = ImageFont.truetype("src/assets/font/KoomikMono-Regular.otf", 20)

    # Posições e tamanhos
    posicoes_pokemon = [ (28, 90), (490, 255), (28, 418), (490, 580) ]
    posicoes_capa = [ (540, 135), (50, 295), (540, 455), (50, 625) ]
    posicoes_texto = [ (250, 120), (455, 280), (250, 445), (455, 610) ]

    texto = Res.trad(interaction=interaction, str='message_poketroca_disponiveis')
    fontetitulo = ImageFont.truetype("src/assets/font/Hey Comic.ttf", 55)
    largura_texto = draw.textlength(texto, font=fontetitulo)
    pos_x = (700 - largura_texto) // 2
    draw.text((pos_x, 20), texto, font=fontetitulo, fill=(254,226,156))

    # Limita pra no máximo 4 pokémon por página
    for idx, t in enumerate(trocas[:4]):
        pos_poke = posicoes_pokemon[idx]
        pos_capa = posicoes_capa[idx]
        text_x, text_y = posicoes_texto[idx]
        alinhado_invertido = idx in [1, 3]  # posições 2 e 4

        # Busca sprite do pokémon
        try:
            dex = await get_pokemon(t['pokemon'])
            sprite_url = dex['front_shiny'] if t["shiny"] else dex['front_default']
            pokeimg = Image.open(requests.get(sprite_url, stream=True).raw).convert("RGBA")
        except:
            pokeimg = Image.open("src/assets/imagens/Pokedex/Interrogation.png").convert("RGBA")

        # Redimensiona pokémon para 180x180
        pokeimg = pokeimg.resize((180, 180))

        # Cola imagem do pokémon
        img.paste(pokeimg, pos_poke, pokeimg)

        # Capa do jogo
        try:
            capa = Image.open(f"src/assets/imagens/JogosCapa/{t['jogo']}.png").convert("RGBA")
            capa = capa.resize((110, 110))
            img.paste(capa, pos_capa, capa)
        except:
            pass

        # Monta textos
        nome, plataforma = await get_jogo_nome(t['jogo'])
        data_str = t['data_registro'].strftime("%d/%m/%Y") if isinstance(t['data_registro'], datetime.datetime) else str(t['data_registro'])
        textos = [
            (f"{t['pokemon'].capitalize()}", fontegrande, 0),
            (f"{t['id_troca']}", fontegrande, 30),
            (f"{data_str}", fontemedia, 70),
            (f"{nome}", fontepequena, 110)
            
        ]

        # Escreve os textos
        for texto, fonte, offset_y in textos:
            if alinhado_invertido:
                # calcula largura e ajusta x pra alinhar à direita
                largura_texto = draw.textlength(texto, font=fonte)
                pos = (text_x - largura_texto, text_y + offset_y)
            else:
                pos = (text_x, text_y + offset_y)
            draw.text(pos, texto, font=fonte, fill=(238,129,48))

    # Salva no buffer
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    return buffer









async def montar_pagina_status(interaction: discord.Interaction, trocas, pagina, user_id):
    # Gere a imagem/arte da página
    buffer = await gerar_arte_trocas(interaction,trocas[pagina])
    # View com botões
    view = discord.ui.View()
    # Botão de voltar para o começo
    botao_primeira = discord.ui.Button(emoji="<:setaduplaesquerda:1318716104474099722>", style=discord.ButtonStyle.gray, disabled=(pagina == 0))
    botao_primeira.callback = partial(trocar_pagina_status, trocas=trocas, pagina=0,  user_id=user_id)
    view.add_item(botao_primeira)

    # Botão de voltar
    botaovoltar = discord.ui.Button(emoji="<:setaesquerda:1318698827422765189>", style=discord.ButtonStyle.gray, disabled=(pagina == 0))
    view.add_item(item=botaovoltar)
    botaovoltar.callback = partial(trocar_pagina_status, trocas=trocas, pagina=pagina-1, user_id=user_id)

    botão_page = discord.ui.Button(label=f"{pagina+1}/{len(trocas)}", style=discord.ButtonStyle.gray, disabled=True)
    view.add_item(botão_page)

    # Botão de avançar
    botaoavancar = discord.ui.Button(emoji="<:setadireita:1318698789225369660>", style=discord.ButtonStyle.gray, disabled=(pagina == len(trocas) - 1))
    view.add_item(item=botaoavancar)
    botaoavancar.callback = partial(trocar_pagina_status, trocas=trocas, pagina=pagina+1, user_id=user_id)
    # Botão de avançar até o fim
    botao_ultima = discord.ui.Button(emoji="<:setadupladireita:1318715892242190419>", style=discord.ButtonStyle.gray, disabled=(pagina == len(trocas) - 1))
    botao_ultima.callback = partial(trocar_pagina_status, trocas=trocas, pagina=len(trocas)-1, user_id=user_id)
    view.add_item(botao_ultima)


    # Envia a mensagem com a imagem e os botões
    await interaction.edit_original_response(content="", attachments=[discord.File(fp=buffer, filename="troca.png")], view=view)


@commands.Cog.listener()
async def trocar_pagina_status(interaction, trocas, pagina, user_id):
    if interaction.user.id != user_id:
        await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_interacaoalheia"),delete_after=10,ephemeral=True)
        return

    # Desabilita os botões
    view = discord.ui.View.from_message(interaction.message)
    for item in view.children:
        item.disabled = True
    await interaction.response.edit_message(view=view)

    # Atualiza a página com a nova arte
    await montar_pagina_status(interaction, trocas, pagina, user_id)









async def montar_pagina_disponiveis(interaction: discord.Interaction, paginas, pagina, user_id):
    # Gere a arte da página (com 4 Pokémon por vez)
    buffer = await gerar_arte_trocas_disponiveis(interaction,paginas[pagina])

    # View com botões
    view = discord.ui.View()

    botao_primeira = discord.ui.Button(emoji="<:setaduplaesquerda:1318716104474099722>", style=discord.ButtonStyle.gray, disabled=(pagina == 0))
    botao_primeira.callback = partial(trocar_pagina_disponiveis, paginas=paginas, pagina=0,  user_id=user_id)
    view.add_item(botao_primeira)

    # Botão de voltar
    botaovoltar = discord.ui.Button(emoji="<:setaesquerda:1318698827422765189>", style=discord.ButtonStyle.gray, disabled=(pagina == 0))
    view.add_item(item=botaovoltar)
    botaovoltar.callback = partial(trocar_pagina_disponiveis,  paginas=paginas, pagina=pagina-1, user_id=user_id)

    botão_page = discord.ui.Button(label=f"{pagina+1}/{len(paginas)}", style=discord.ButtonStyle.gray, disabled=True)
    view.add_item(botão_page)

    # Botão de avançar
    botaoavancar = discord.ui.Button(emoji="<:setadireita:1318698789225369660>", style=discord.ButtonStyle.gray, disabled=(pagina == len(paginas) - 1))
    view.add_item(item=botaoavancar)
    botaoavancar.callback = partial(trocar_pagina_disponiveis, paginas=paginas, pagina=pagina+1, user_id=user_id)

    botao_ultima = discord.ui.Button(emoji="<:setadupladireita:1318715892242190419>", style=discord.ButtonStyle.gray, disabled=(pagina == len(paginas) - 1))
    botao_ultima.callback = partial(trocar_pagina_disponiveis, paginas=paginas, pagina=len(paginas)-1, user_id=user_id)
    view.add_item(botao_ultima)

    # Envia a mensagem com a imagem e os botões
    await interaction.edit_original_response(content="", attachments=[discord.File(fp=buffer, filename="trocas_disponiveis.png")], view=view)


@commands.Cog.listener()
async def trocar_pagina_disponiveis( interaction, paginas, pagina, user_id):
    if interaction.user.id != user_id:
        await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_interacaoalheia"),delete_after=10,ephemeral=True)
        return

    # Desabilita os botões
    view = discord.ui.View.from_message(interaction.message)
    for item in view.children:
        item.disabled = True
    await interaction.response.edit_message(view=view)

    # Atualiza a página com a nova arte
    await montar_pagina_disponiveis(interaction, paginas, pagina, user_id)








class trocaspokemon(commands.Cog):
  def __init__(self, client: commands.Bot):
    self.client = client
    






  @commands.Cog.listener()
  async def on_ready(self):
    print("🔄️  -  Modúlo Trocas Pokémon Carregado.")
     

 









    #SISTEMA DE TROCAS POKÈMON
  trocaspokemon=app_commands.Group(name="trocas", description="Comandos para realizar trocas de Pokémon.",allowed_installs=app_commands.AppInstallationType(guild=True,user=True),allowed_contexts=app_commands.AppCommandContext(guild=True, dm_channel=True, private_channel=True))





  @trocaspokemon.command(name="ajuda", description="🦊⠂Saiba mais sobre o sistema de trocas.")
  async def troca_help(self, interaction: discord.Interaction):
    if await Res.print_brix(comando="troca_help",interaction=interaction):
      return
    await interaction.response.send_message(Res.trad(interaction=interaction,str="message_poketroca_help"))
    return




  @trocaspokemon.command(name="adicionar", description="🦊⠂Registre um pokémon para conseguir trocando com outro jogador.")
  @app_commands.describe(pokemon="Informe o nome de um pokémon...", jogo="Informe para qual jogo deseja a troca...", shiny="Deseja que o pokémon seja Shiny?")
  @app_commands.autocomplete(pokemon= pokemon_autocomplete , jogo= jogos_autocomplete)
  async def troca_adicionar(self, interaction: discord.Interaction, pokemon: str, jogo: str, shiny: bool):
    if await Res.print_brix(comando="troca_adicionar",interaction=interaction,condicao=f"Pokémon:{pokemon} - Jogo:{jogo} - Shiny: {shiny}"):
      return
    await interaction.response.defer()
    user_id = interaction.user.id
    username = str(interaction.user)

    premium = await userpremiumcheck(interaction)
    if premium == False:
        # Conta quantas trocas 'disponivel' o user já tem
        trocas_ativas = BancoTrocas.select_many_document({"user_id": user_id,"status": 1})
        if len(trocas_ativas) >= 2:
            await interaction.followup.send(Res.trad(interaction=interaction,str="message_poketroca_limit_trocas"))
            return
        
    check , doc = BancoTrocas.insert_document(gerar_id_unica(), user_id, username, pokemon, jogo, shiny)
    if check is False:
        await interaction.followup.send(Res.trad(interaction=interaction,str="message_poketroca_pokemon_duplicado").format(doc['id_troca']))
        return

    buffer = await gerar_arte_trocas(interaction,doc)
    await interaction.followup.send(Res.trad(interaction=interaction,str="message_poketroca_registro_sucesso"), files=[discord.File(fp=buffer, filename="registro.png")])









  @trocaspokemon.command(name="aceitar", description="🦊⠂Aceite uma troca de outro jogador.")
  @app_commands.describe(id_troca="ID da troca que você quer aceitar")
  async def troca_aceitar(self, interaction: discord.Interaction, id_troca: str):
    if await Res.print_brix(comando="troca_aceitar", interaction=interaction, condicao=f"id_troca:{id_troca} "):
        return
    await interaction.response.defer()

    # Exemplo de lógica depois:
    troca = BancoTrocas.select_many_document({"id_troca": id_troca, "status": 1})
    if not troca:
        await interaction.followup.send(Res.trad(interaction=interaction,str="message_poketroca_pokemon_indisponivel"))
        return
    
    if troca[0]['user_id'] == interaction.user.id:
        await interaction.followup.send(Res.trad(interaction=interaction,str="message_poketroca_registro_mesmo_user"))
        return

    # Atualiza troca no banco pra setar quem aceitou
    update = {
        "status": 2,
        "user_id_aceitou": interaction.user.id,
        "username_aceitou": str(interaction.user),
        "data_aceitou": datetime.datetime.now()
    }
    BancoTrocas.update_document(troca[0]['_id'], update)
    await interaction.followup.send(Res.trad(interaction=interaction,str="message_poketroca_pokemon_aceito").format(id_troca))
    try:
        usuario = await self.client.fetch_user(troca[0]['user_id'])
        troca = BancoTrocas.select_many_document({"id_troca": id_troca})
        buffer = await gerar_arte_trocas(interaction,troca[0])
        link_perfil = f"https://discord.com/users/{interaction.user.id}"
        view = discord.ui.View()
        item = discord.ui.Button(style=discord.ButtonStyle.blurple,label=Res.trad(interaction=interaction,str="botão_abrir_navegador"),url=f"{link_perfil}")
        view.add_item(item=item)
        await usuario.send(Res.trad(user=usuario, str='message_poketroca_pokemon_avisoDM').format(interaction.user.id , interaction.user.name, interaction.user.mention,link_perfil), view=view ,files=[discord.File(fp=buffer, filename="registro.png")] , suppress_embeds=True)
    except:print(f"DM FECHADA PARA {troca[0]['user_id']} na troca {troca[0]['id_troca']}")
  
  
  # Autocomplete para ID da troca disponível
  @troca_aceitar.autocomplete("id_troca")
  async def troca_id_autocomplete(self, interaction: discord.Interaction, current: str):
    # Busca trocas disponíveis no banco
    trocas_disponiveis = BancoTrocas.select_many_document({"status": 1})
    sugestoes = []
    for t in trocas_disponiveis:
        if current.lower() in t['id_troca'].lower():
            try:
                nome_pokemon = t['pokemon']
                nome_jogo = t['jogo']
                shiny = "⭐" if t['shiny'] else ""
                sugestoes.append(app_commands.Choice(
                    name=f"ID: {t['id_troca']} - {nome_pokemon} {shiny} ({nome_jogo})",
                    value=t['id_troca']
                ))
            except Exception as e:
                print(f"[ERRO] Falha ao montar sugestão: {e}")

    # Se não achou nada, põe msg opcional (opcional mesmo)
    if not sugestoes:
        sugestoes.append(app_commands.Choice(name=Res.trad(interaction=interaction, str="message_poketroca_notlist"), value=""))

    return sugestoes[:25]








  @trocaspokemon.command(name="cancelar", description="🦊⠂Cancele uma das suas trocas ou desfaça seu aceite.")
  @app_commands.describe(id_troca="ID da troca que você quer cancelar ou desfazer")
  async def troca_cancelar(self, interaction: discord.Interaction, id_troca: str):
    if await Res.print_brix(comando="troca_cancelar", interaction=interaction, condicao=f"id_troca:{id_troca}"):
        return
    await interaction.response.defer()
    # Busca a troca que tenha status disponivel ou aceito
    troca = BancoTrocas.select_many_document({        "id_troca": id_troca,        "status": {"$in": [1, 2]}    })

    if not troca:
        await interaction.followup.send(Res.trad(interaction=interaction,str="message_poketroca_pokemon_indisponivel"))
        return
    troca = troca[0]
    if troca['user_id'] == interaction.user.id:
        # É o criador → cancela
        BancoTrocas.update_document(troca['_id'], {"status": 4})
        await interaction.followup.send(Res.trad(interaction=interaction,str="message_poketroca_registro_cancelado").format(id_troca))
    elif troca.get('user_id_aceitou') == interaction.user.id:
        # Foi quem aceitou → limpa aceite e volta pra disponivel
        update = { "status": 1, "user_id_aceitou": None, "username_aceitou": None, "data_aceitou": None }
        BancoTrocas.update_document(troca['_id'], update)
        await interaction.followup.send(Res.trad(interaction=interaction,str="message_poketroca_registro_negado").format(id_troca))
        try:
            troca = BancoTrocas.select_many_document({"id_troca": id_troca})
            usuario = await self.client.fetch_user(troca[0]['user_id'])
            buffer = await gerar_arte_trocas(interaction,troca[0])
            await usuario.send(Res.trad(user=usuario, str='message_poketroca_registro_negado_avisoDM') ,files=[discord.File(fp=buffer, filename="registro.png")] , suppress_embeds=True)
        except:print(f"DM FECHADA PARA {troca[0]['user_id']} na troca {troca[0]['id_troca']}")
    else:
        await interaction.followup.send(Res.trad(interaction=interaction,str="message_poketroca_registro_mesmo_user"))



# Autocomplete para cancelar troca: só as trocas do próprio user, status disponivel ou aceito
  @troca_cancelar.autocomplete("id_troca")
  async def troca_cancelar_id_autocomplete(self, interaction: discord.Interaction, current: str):
    trocas_user = BancoTrocas.select_many_document({ "$or": [ {"user_id": interaction.user.id}, {"user_id_aceitou": interaction.user.id} ], "status": {"$in": [1, 2]} })
    sugestoes = []
    for t in trocas_user:
        if current.lower() in t['id_troca'].lower():
            nome_pokemon = t['pokemon']
            nome_jogo = t['jogo']
            shiny = "⭐" if t.get('shiny') else ""
            sugestoes.append(app_commands.Choice(
                name=f"ID: {t['id_troca']} - {nome_pokemon} {shiny} ({nome_jogo})",
                value=t['id_troca']
            ))
    if not sugestoes:
        sugestoes.append(app_commands.Choice(name=Res.trad(interaction=interaction, str="message_poketroca_notlist"), value=""))
    return sugestoes[:25]







  @trocaspokemon.command(name="confirmar", description="🦊⠂Confirme que a troca foi realizada com sucesso.")
  @app_commands.describe(id_troca="ID da troca que você quer confirmar")
  async def troca_confirmar(self, interaction: discord.Interaction, id_troca: str):
    if await Res.print_brix(comando="troca_confirmar", interaction=interaction, condicao=f"id_troca:{id_troca}"):
        return
    await interaction.response.defer()
    # Busca troca que foi aceita e pertence ao user
    troca = BancoTrocas.select_many_document({ "id_troca": id_troca, "user_id": interaction.user.id, "status": 2    })

    if not troca:
        await interaction.followup.send(Res.trad(interaction=interaction,str="message_poketroca_confirmar_invalido"))
        return
    # Atualiza como concluída
    update = { "troca_concluida": True, "data_conclusao": datetime.datetime.now(), "status": 3    }
    BancoTrocas.update_document(troca[0]['_id'], update)

    await interaction.followup.send(Res.trad(interaction=interaction,str="message_poketroca_registro_finalizado").format(id_troca))


  @troca_confirmar.autocomplete("id_troca")
  async def troca_confirmar_id_autocomplete(self, interaction: discord.Interaction, current: str):
    trocas_aceitas = BancoTrocas.select_many_document({"user_id": interaction.user.id,"status": 2    })
    sugestoes = []
    for t in trocas_aceitas:
        if current.lower() in t['id_troca'].lower():
            nome_pokemon = t['pokemon']
            nome_jogo = t['jogo']
            shiny = "⭐" if t.get('shiny') else ""
            sugestoes.append(app_commands.Choice(
                name=f"ID: {t['id_troca']} - {nome_pokemon} {shiny} ({nome_jogo})",
                value=t['id_troca']
            ))

    if not sugestoes:
        sugestoes.append(app_commands.Choice(name=Res.trad(interaction=interaction, str="message_poketroca_notlist"), value=""))

    return sugestoes[:25]










  @trocaspokemon.command(name="status", description="🦊⠂Veja o status das suas trocas.")
  async def troca_status(self, interaction: discord.Interaction):
    if await Res.print_brix(comando="troca_status", interaction=interaction, condicao=""):
        return
    await interaction.response.defer()
    trocas = BancoTrocas.select_many_document({"$or": [{"user_id": interaction.user.id},{"user_id_aceitou": interaction.user.id}    ]})

    if not trocas:
        await interaction.followup.send(Res.trad(interaction=interaction, str="message_poketroca_notlist"))
        return
    # Ordena: aceito > disponivel > concluido > cancelado
    status_order = {2: 1, 1: 2, 3: 3, 4: 4}
    trocas.sort(key=lambda x: status_order.get(x['status'], 99))
    # Cria a página inicial e envia com botões
    await montar_pagina_status(interaction, trocas, 0, interaction.user.id)



    
  @trocaspokemon.command(name="disponiveis", description="🦊⠂Veja os Pokémon disponíveis para troca.")
  async def troca_disponiveis(self, interaction: discord.Interaction):
    if await Res.print_brix(comando="troca_disponiveis", interaction=interaction, condicao=""):
        return
    await interaction.response.defer()
    # Pega todas as trocas disponíveis
    trocas_disponiveis = BancoTrocas.select_many_document({"status": 1})
    if not trocas_disponiveis:
        await interaction.followup.send(Res.trad(interaction=interaction, str="message_poketroca_notlist"))
        return
    # Organiza as trocas em grupos de 4 por página
    trocas_disponiveis = list(trocas_disponiveis)[::-1]
    paginas = [trocas_disponiveis[i:i + 4] for i in range(0, len(trocas_disponiveis), 4)]
    # Chama a função para montar a página inicial com os botões
    await montar_pagina_disponiveis(interaction, paginas, 0, interaction.user.id)









async def setup(client:commands.Bot) -> None:
  await client.add_cog(trocaspokemon(client))
