import discord,os,asyncio,time,json,random,requests,io,textwrap
from deep_translator import GoogleTranslator
from PIL import Image, ImageFont, ImageDraw, ImageOps
from discord.ext import commands
from functools import partial
from discord import app_commands,Locale
from src.services.essential.respostas import Res
from src.services.essential.funcoes_usuario import userpremiumcheck 
from src.services.connection.database import BancoTrocas
from src.services.essential.pokemon_module import verificar_calendario_pokemon , encontrar_cor_tipo, pokemon_autocomplete , get_pokemon , get_pokemon_sprite , get_all_pokemon
from discord.app_commands import locale_str as _T
from difflib import get_close_matches


tradutor = GoogleTranslator(source="auto",target="pt")



# CODIGO NÂO PRONTO
def create_evolution_grid(evolution_chain):
    # Carregar as imagens dos Pokémon (URLs simuladas, pode ser adaptado)
    def load_pokemon_image(name):
        url = f"https://pokeapi.co/api/v2/pokemon/{name}"
        response = requests.get(url)
        if response.status_code == 200:
            sprite_url = response.json()["sprites"]["other"]["home"]["front_default"]
            if sprite_url:
                sprite_response = requests.get(sprite_url)
                if sprite_response.status_code == 200:
                    return Image.open(io.BytesIO(sprite_response.content)).convert("RGBA")
        return None
    # Remove Pokémon duplicados pela chave 'name'
    def remove_duplicates(variants):
        unique_variants = {}
        for variant in variants:
            unique_variants[variant['name']] = variant  # Usamos o nome como chave para garantir que seja único
        return list(unique_variants.values())
    
    # Classificar a cadeia: simples ou variante
    root = evolution_chain[0]['name']
    variants = [evo for evo in evolution_chain if evo['name'] != root]
    #variants = remove_duplicates(variants)

    altura, largura = 240 , 520
    img = Image.new("RGBA", (largura, altura), (0, 0, 0, 1))
    draw = ImageDraw.Draw(img)
    
    if len(variants) == 2:        
        base_size = 100  # Tamanho inicial da imagem
        size_increment = 30  # Incremento para o tamanho a cada loop
        base_y_position = 170  # Posição fixa do canto inferior
        
        for i, evo in enumerate(evolution_chain):
            x_offset = int(i * (largura / 3))
            pokemon_img = load_pokemon_image(evo['name'])
            
            # Calcular tamanho progressivo
            new_size = base_size + (i * size_increment)
            pokemon_img = pokemon_img.resize((new_size, new_size))
            
            # Ajustar posição vertical para alinhar pelo canto inferior
            y_offset = base_y_position - new_size
            
            img.paste(pokemon_img, (x_offset + 15, y_offset))
            draw.text((x_offset + 40, 180), evo['name'], font=ImageFont.truetype("src/assets/font/KoomikMono-Regular.otf",14), fill="black")
            # Adicionar informações de evolução
            if i < len(evolution_chain):
                next_evo = evolution_chain[i]
                if next_evo['method'] is not None:
                    level_text = f"Lvl:{next_evo['min_level']}" if next_evo['min_level'] else "Evolução"
                    method_text = next_evo['method']
                    # Desenhando o texto
                    draw.text((x_offset - 40, 110), f"{method_text}\n{level_text}", font=ImageFont.truetype("src/assets/font/KoomikMono-Regular.otf",14), fill="black", align="center")



    elif len(variants) > 8:        
        root_offset = (20, altura // 2 - 50)  # Centralizar
        evolution_chain = remove_duplicates(evolution_chain)
 
        # Definir as posições da grade 3x3x3 (em torno do centro)
        positions = [
            (0, 0),
            (80, -70), (170, -70), (260, -70), (350, -70),
            (80, 60),(170, 60), (260, 60), (350, 60),
            (440, -70),(440, 60)
        ]
        
        
        # Adicionar variantes ao redor do centro
        for i, evo in enumerate(evolution_chain):
            # A posição é baseada no índice da variante
            x_offset, y_offset = positions[i]
            
            # Carregar e redimensionar a imagem do Pokémon
            pokemon_img = load_pokemon_image(evo['name'])
            pokemon_img = pokemon_img.resize((70, 70))  # Ajuste de tamanho

            # Colocar a imagem na posição correta
            img.paste(pokemon_img, (root_offset[0] + x_offset, root_offset[1] + y_offset))
            
            # Adicionar o nome e informações de evolução
            draw.text((root_offset[0] + x_offset + 10, root_offset[1] + y_offset + 70), evo['name'], font=ImageFont.truetype("src/assets/font/KoomikMono-Regular.otf",14), fill="black")
            
            # Adicionar informações de evolução (nível e método)
            #level_text = f"Lvl {evo['min_level']}" if evo['min_level'] else "Evolução"
            #method_text = evo['method']
            #draw.text((root_offset[0] + x_offset + 20, root_offset[1] + y_offset + 160), f"{level_text} - {method_text}", font=ImageFont.load_default(), fill="black")

    #else:
       # y_base = 10  # Posição inicial no eixo Y
       # x_center = largura // 2  # Centro da imagem no eixo X
        # PROCURAR VARIANTES CADA POKÈMON
       # for i, pokemon in enumerate(evolution_chain):
       #     r = requests.get(f"https://pokeapi.co/api/v2/pokemon-species/{pokemon['name']}/").json()
       #     print(r)


        """
        for i, pokemon in enumerate(evolution_chain):

            # Posicionar o Pokémon base
            base_name = pokemon['name']
            base_img = load_pokemon_image(base_name)
            base_img = base_img.resize((100, 100)) if base_img else None
            x_base = x_center - 50  # Centralizar horizontalmente
            y_base_offset = y_base + (i * 150)  # Incrementar a posição vertical
            
            if base_img:
                img.paste(base_img, (x_base, y_base_offset))
                draw.text((x_base + 10, y_base_offset + 110), base_name, font=ImageFont.truetype("src/assets/font/KoomikMono-Regular.otf", 14), fill="black")
            
            # Verificar variações do Pokémon atual
            variations = pokemon.get('variations', [])  # Supondo que a estrutura tenha um campo "variations"
            num_variations = len(variations)
            
            if num_variations > 0:
                # Calcular espaçamento horizontal para variantes
                x_step = largura // (num_variations + 1)
                
                for j, variation in enumerate(variations):
                    variation_name = variation['name']
                    variation_img = load_pokemon_image(variation_name)
                    variation_img = variation_img.resize((80, 80)) if variation_img else None
                    x_variation = j * x_step + 10
                    y_variation = y_base_offset + 140
                    
                    if variation_img:
                        img.paste(variation_img, (x_variation, y_variation))
                        draw.text((x_variation + 10, y_variation + 90), variation_name, font=ImageFont.truetype("src/assets/font/KoomikMono-Regular.otf", 12), fill="black")
                    
                    # Adicionar informações de evolução (método e nível)
                    method_text = variation.get('method', 'Método desconhecido')
                    level_text = f"Nível {variation['min_level']}" if variation.get('min_level') else ""
                    draw.text((x_variation + 10, y_variation + 110), f"{method_text}\n{level_text}", font=ImageFont.truetype("src/assets/font/KoomikMono-Regular.otf", 10), fill="black")
        """
    #return img
"""
def extract_evolutions(chain):
    evolution_list = []

    # Extrai detalhes do Pokémon atual
    for details in chain['evolution_details']:
        evolution_list.append({
            'name': chain['species']['name'],
            'min_level': details.get('min_level', "unknown"),
            'method': details['trigger']['name'],
            'item': details['item']['name'] if details.get('item') else None,
            'happiness': details.get('min_happiness'),
            'affection': details.get('min_affection'),
            'move_type': details['known_move_type']['name'] if details.get('known_move_type') else None,
            'location': details['location']['name'] if details.get('location') else None,
            'time_of_day': details.get('time_of_day'),
        })
    
    # Caso não haja evolution_details (primeiro Pokémon da cadeia)
    if not chain['evolution_details']:
        evolution_list.append({
            'name': chain['species']['name'],
            'min_level': None,
            'method': None,
            'item': None,
            'happiness': None,
            'affection': None,
            'move_type': None,
            'location': None,
            'time_of_day': None,
        })

    # Itera sobre todas as evoluções possíveis
    for evolution in chain['evolves_to']:
        evolution_list.extend(extract_evolutions(evolution))  # Chamada recursiva

    return evolution_list

"""



#FUNÇÂO DE MONTAR A POKEDEX INTEIRA

async def montarpokedex(self,interaction: discord.Interaction,pokemon , brilhante, pagina , originaluser):
    await interaction.original_response()
    dex = await get_pokemon(pokemon)
    specie = requests.get(f"{dex['species']}/").json()
    aniversario = await verificar_calendario_pokemon(pokemon_nome=dex['name'])
    try:
        imagempokemon = get_pokemon_sprite( dex['front_shiny'] if brilhante else dex['front_default'], dex["id"], shiny=brilhante)
        #if brilhante is True:
        #    imagempokemon = Image.open(requests.get(dex['front_shiny'], stream=True).raw) 
        #else: imagempokemon = Image.open(requests.get(dex['front_default'], stream=True).raw)
    except:
        imagempokemon = Image.open("src/assets/imagens/Pokedex/Interrogation.png")

    #MONTAGEM INICIAL
    corfundo = encontrar_cor_tipo(dex['types'][0]['type']['name'])
    nomepokemon = dex['name'].capitalize() #DEFININDO NOME
    idpokemon = f"#{dex['id']}" #DEFININDO ID
    fundo = Image.new("RGBA",(800,300), corfundo) #DEFININDO FUNDO
    pokeboladefundo = Image.open("src/assets/imagens/Pokedex/pokeballbranca.png").resize((200,200))
    misturafundo = Image.blend(fundo.resize(pokeboladefundo.size),pokeboladefundo,alpha=0.3)
    fundo.paste(misturafundo , (20,90) , pokeboladefundo ) #COLANDO POKEBOLA FUNDO
    fundo.paste( imagempokemon.resize((240,240)) , (10,55) ,imagempokemon.resize((240,240)) ) #COLANDO POKÈMON
    if brilhante is True:
        shiny = Image.open("src/assets/imagens/Pokedex/Shiny.png")
        fundo.paste( shiny.resize((70,70)) , (60,220) ,shiny.resize((70,70)) ) #COLANDO POKÈMON

    fundobranco = Image.new("RGBA" , (600,350) , "#ffffff")
    mascarafundo = Image.new("L", fundobranco.size, 0)
    drawfundobranco = ImageDraw.Draw(mascarafundo)
    drawfundobranco.rounded_rectangle([0, 0, fundobranco.size[0], fundobranco.size[1]], radius=60, fill=255)
    fundo.paste ( fundobranco , (260,-50) , mascarafundo)
    #ESCREVENDO
    fundodraw = ImageDraw.Draw(fundo)
    fundodraw.text((20,4), nomepokemon ,font=ImageFont.truetype("src/assets/font/PoetsenOne-Regular.ttf",30))
    fundodraw.text((20,37), idpokemon ,font=ImageFont.truetype("src/assets/font/KoomikMono-Regular.otf",18))

    # INDICAR ANIVERSARIO DO POKÈMON
    if aniversario is not None:
        encaixebolo = fundodraw.textbbox((0,0), idpokemon, font=ImageFont.truetype("src/assets/font/KoomikMono-Regular.otf", 18))
        bolo = Image.open("src/assets/imagens/Pokedex/Cake.png")
        fundo.paste( bolo.resize((22,22)) , (30 + encaixebolo[2],40) ,bolo.resize((22,22)) ) #COLANDO POKÈMON
        fundodraw.text((55 + encaixebolo[2],37), f"{aniversario.day:02d}/{aniversario.month:02d}" ,font=ImageFont.truetype("src/assets/font/KoomikMono-Regular.otf",18))
        # Desenhar palavras justificadas
    texto = Res.trad(interaction=interaction,str="message_pokedex_title")
    total_width = 450  # Espaço disponível para as palavras (deixe uma margem)
    text_widths = [drawfundobranco.textbbox((0, 0), word, font=ImageFont.truetype("src/assets/font/KoomikMono-Regular.otf",22))[2] for word in texto]
    space_width = (total_width - sum(text_widths)) // (len(texto) - 1)
    x = 300
    for i, word in enumerate(texto):
        fundodraw.text((x, 10), word, font=ImageFont.truetype("src/assets/font/KoomikMono-Regular.otf",22), fill="black")
        x += text_widths[i] + space_width  # Mover para a próxima palavra

    #MONTAGEM DAS PAGINAS.
    if pagina == 0:
        generas = specie['genera']
        caracteristica = ", ".join(gener['genus'] for gener in generas if gener['language']['name'] == 'en')
        habilidades = ", ".join(ability['ability']['name'] for ability in dex['abilities'])
        
        tipo = ", ".join(type['type']['name'] for type in dex['types'])
        egggroup = specie['egg_groups'][0]['name']
        hattime = f"{specie['hatch_counter']} cycles"
        # TRADUZ VARIAVEIS PARA BR
        if interaction.locale.value == "pt-BR":
            caracteristica = tradutor.translate(caracteristica)
            habilidades = tradutor.translate(habilidades)
            tipo = tradutor.translate(tipo)
            egggroup = tradutor.translate(egggroup)
            hattime = tradutor.translate(hattime)
        habilidades = "\n".join(textwrap.wrap(habilidades.replace(' ​​',''), width=20))

        marcadorpagina = Image.new("RGBA",(40,2), corfundo)
        fundo.paste ( marcadorpagina , (310,38) , marcadorpagina)
        separadorpagina = Image.new("RGBA",(2,200), corfundo)
        fundo.paste ( separadorpagina , (520,65) , separadorpagina)
        #Titulos
        fundodraw.text((340, 45), Res.trad(interaction=interaction,str="Dados"), font=ImageFont.truetype("src/assets/font/KoomikMono-Regular.otf",22), fill="black",align="center")
        fundodraw.text((590, 45), Res.trad(interaction=interaction,str="Reprodução"), font=ImageFont.truetype("src/assets/font/KoomikMono-Regular.otf",22), fill="black",align="center")
        fundodraw.text((610, 160), Res.trad(interaction=interaction,str="Genero"), font=ImageFont.truetype("src/assets/font/KoomikMono-Regular.otf",22), fill="black",align="center")

        #DEMAIS DADOS
        fundodraw.text((270, 100), Res.trad(interaction=interaction,str="Especie"), font=ImageFont.truetype("src/assets/font/KoomikMono-Regular.otf",14), fill="#595959")
        fundodraw.text((370, 100), caracteristica, font=ImageFont.truetype("src/assets/font/KoomikMono-Regular.otf",10 if len(caracteristica) > 19 else 14), fill="black")
        fundodraw.text((270, 130), Res.trad(interaction=interaction,str="Altura"), font=ImageFont.truetype("src/assets/font/KoomikMono-Regular.otf",14), fill="#595959")
        fundodraw.text((370, 130), f"{dex['height']/10} M", font=ImageFont.truetype("src/assets/font/KoomikMono-Regular.otf",14), fill="black")
        fundodraw.text((270, 160), Res.trad(interaction=interaction,str="Peso"), font=ImageFont.truetype("src/assets/font/KoomikMono-Regular.otf",14), fill="#595959")
        fundodraw.text((370, 160), f"{dex['weight']/10} Kg", font=ImageFont.truetype("src/assets/font/KoomikMono-Regular.otf",14), fill="black")
        fundodraw.text((270, 190), Res.trad(interaction=interaction,str="Tipagem"), font=ImageFont.truetype("src/assets/font/KoomikMono-Regular.otf",14), fill="#595959")
        fundodraw.text((370, 190), tipo[:22], font=ImageFont.truetype("src/assets/font/KoomikMono-Regular.otf",14), fill="black")
        fundodraw.text((270, 220), Res.trad(interaction=interaction,str="Habilidades"), font=ImageFont.truetype("src/assets/font/KoomikMono-Regular.otf",14), fill="#595959")
        fundodraw.text((370, 220), habilidades, font=ImageFont.truetype("src/assets/font/KoomikMono-Regular.otf",14), fill="black", spacing=1)
        fundodraw.text((540, 100), Res.trad(interaction=interaction,str="Grupo_de_Ovos"), font=ImageFont.truetype("src/assets/font/KoomikMono-Regular.otf",14), fill="#595959")
        fundodraw.text((660, 100), egggroup, font=ImageFont.truetype("src/assets/font/KoomikMono-Regular.otf",14), fill="black")
        fundodraw.text((540, 130), Res.trad(interaction=interaction,str="eclodir"), font=ImageFont.truetype("src/assets/font/KoomikMono-Regular.otf",14), fill="#595959")
        fundodraw.text((660, 130), hattime, font=ImageFont.truetype("src/assets/font/KoomikMono-Regular.otf",14), fill="black",align="center")
        fundodraw.text((540, 225), Res.trad(interaction=interaction,str="Taxa_de_Captura"), font=ImageFont.truetype("src/assets/font/KoomikMono-Regular.otf",14), fill="#595959")
        fundodraw.text((680, 225), f"{specie['capture_rate']}", font=ImageFont.truetype("src/assets/font/KoomikMono-Regular.otf",14), fill="black",align="center")
        
        # MONTAGEM GENERO E OUTRAS COISAS
        if specie['gender_rate'] <= 0 : 
            fundodraw.text((540, 200), Res.trad(interaction=interaction,str="Sem_Dados_genero"), font=ImageFont.truetype("src/assets/font/KoomikMono-Regular.otf",14), fill="#595959",align="center")
        else:
            #calculos logicos de brobabilidade
            femea = (specie['gender_rate'] / 8) * 100
            macho = 100 - femea
            #MONTAGEM
            fundorosa = Image.new("RGBA" , (200,4) , "#ff00c3")
            fundoazul = Image.new("RGBA" , (200 - specie['gender_rate'] * 25 ,4) , "#0040ff")
            fundo.paste ( fundorosa , (550,190) )
            fundo.paste ( fundoazul , (550,190) )
            Male = Image.open("src/assets/imagens/Pokedex/Male.png").resize((15,15)) #ICONE MACHO
            fundo.paste ( Male , (560,200) , Male)
            fundodraw.text((580, 200), f"{macho:.2f}%", font=ImageFont.truetype("src/assets/font/KoomikMono-Regular.otf",14), fill="black",align="center")
            Female = Image.open("src/assets/imagens/Pokedex/Female.png").resize((15,15)) #ICONE FEMEA
            fundo.paste ( Female , (670,200) , Female)
            fundodraw.text((690, 200), f"{femea:.2f}%", font=ImageFont.truetype("src/assets/font/KoomikMono-Regular.otf",14), fill="black",align="center")

    elif pagina == 1:
        marcadorpagina = Image.new("RGBA",(70,2), corfundo)
                                    # 480,38  660
        fundo.paste ( marcadorpagina , (660,38) , marcadorpagina)
        description = "description: " + next((entry['flavor_text'].replace("\n", " ") for entry in specie['flavor_text_entries'] if entry['language']['name'] == 'en'),"There are no records.")

        for database in dex["stats"]:
            if database['stat']['name'] == 'hp':
                  hp = database['base_stat']
            elif database['stat']['name'] == 'attack':
                  attack = database['base_stat']
            elif database['stat']['name'] == 'defense':
                  defense = database['base_stat']
            elif database['stat']['name'] == 'special-attack':
                  special_attack = database['base_stat']
            elif database['stat']['name'] == 'special-defense':
                  special_defense = database['base_stat']
            elif database['stat']['name'] == 'speed':
                  speed = database['base_stat']

        if interaction.locale.value == "pt-BR":
            description = tradutor.translate(description)
        description_wrapped = "\n".join(textwrap.wrap(description.replace(' ​​',''), width=60))
        fundodraw.text((280, 45), description_wrapped, font=ImageFont.truetype("src/assets/font/KoomikMono-Regular.otf",14), fill="black")
        fundodraw.text((280, 140), "HP", font=ImageFont.truetype("src/assets/font/KoomikMono-Regular.otf",14), fill="#595959")
        fundodraw.text((370, 140), f"{hp}", font=ImageFont.truetype("src/assets/font/KoomikMono-Regular.otf",14), fill="black",align="center")
                                    #  X1  Y1   X2  Y2
        fundodraw.rounded_rectangle(((420,145),(750,150)),fill="#e0e0e0",radius=20)
        fundodraw.rounded_rectangle(((420,145),(750*(hp/200)+420*(1-hp/200),150)),fill=corfundo , radius=20)        

        fundodraw.text((280, 160), Res.trad(interaction=interaction,str="Ataque"), font=ImageFont.truetype("src/assets/font/KoomikMono-Regular.otf",14), fill="#595959")
        fundodraw.text((370, 160), f"{attack}", font=ImageFont.truetype("src/assets/font/KoomikMono-Regular.otf",14), fill="black",align="center")

        fundodraw.rounded_rectangle(((420,165),(750,170)),fill="#e0e0e0",radius=20)
        fundodraw.rounded_rectangle(((420,165),(750*(attack/200)+420*(1-attack/200),170)),fill=corfundo , radius=20)        

        fundodraw.text((280, 180), Res.trad(interaction=interaction,str="Defesa"), font=ImageFont.truetype("src/assets/font/KoomikMono-Regular.otf",14), fill="#595959")
        fundodraw.text((370, 180), f"{defense}", font=ImageFont.truetype("src/assets/font/KoomikMono-Regular.otf",14), fill="black",align="center")

        fundodraw.rounded_rectangle(((420,185),(750,190)),fill="#e0e0e0",radius=20)
        fundodraw.rounded_rectangle(((420,185),(750*(defense/200)+420*(1-defense/200),190)),fill=corfundo , radius=20)        

        fundodraw.text((280, 200), "SP.ATK", font=ImageFont.truetype("src/assets/font/KoomikMono-Regular.otf",14), fill="#595959")
        fundodraw.text((370, 200), f"{special_attack}", font=ImageFont.truetype("src/assets/font/KoomikMono-Regular.otf",14), fill="black",align="center")

        fundodraw.rounded_rectangle(((420,205),(750,210)),fill="#e0e0e0",radius=20)
        fundodraw.rounded_rectangle(((420,205),(750*(special_attack/200)+420*(1-special_attack/200),210)),fill=corfundo , radius=20)        

        fundodraw.text((280, 220), "SP.DEF", font=ImageFont.truetype("src/assets/font/KoomikMono-Regular.otf",14), fill="#595959")
        fundodraw.text((370, 220), f"{special_defense}", font=ImageFont.truetype("src/assets/font/KoomikMono-Regular.otf",14), fill="black",align="center")

        fundodraw.rounded_rectangle(((420,225),(750,230)),fill="#e0e0e0",radius=20)
        fundodraw.rounded_rectangle(((420,225),(750*(special_defense/200)+420*(1-special_defense/200),230)),fill=corfundo , radius=20)        

        fundodraw.text((280, 240), Res.trad(interaction=interaction,str="Velocidade"), font=ImageFont.truetype("src/assets/font/KoomikMono-Regular.otf",14), fill="#595959")
        fundodraw.text((370, 240), f"{speed}", font=ImageFont.truetype("src/assets/font/KoomikMono-Regular.otf",14), fill="black",align="center")

        fundodraw.rounded_rectangle(((420,245),(750,250)),fill="#e0e0e0",radius=20)
        fundodraw.rounded_rectangle(((420,245),(750*(speed/200)+420*(1-speed/200),250)),fill=corfundo , radius=20)        

        fundodraw.text((280, 260), Res.trad(interaction=interaction,str="Total"), font=ImageFont.truetype("src/assets/font/KoomikMono-Regular.otf",14), fill="#595959",align="center")
        fundodraw.text((370, 260), f"{hp + attack + defense + special_attack + special_defense + speed}", font=ImageFont.truetype("src/assets/font/KoomikMono-Regular.otf",14), fill="black",align="center")
    else:
        print("não finalizado")
        #marcadorpagina = Image.new("RGBA",(40,2), corfundo)
        #fundo.paste ( marcadorpagina , (690,38) , marcadorpagina)
        #evolution = requests.get(specie["evolution_chain"]["url"]).json()
        #evolution_chain = extract_evolutions(evolution['chain'])
        #grade = create_evolution_grid(evolution_chain)
        #fundo.paste(grade,(260,50),grade)
    

    #SALVANDO
    buffer = io.BytesIO()
    fundo.save(buffer,format="PNG")
    buffer.seek(0)

    # Botoões
    view = discord.ui.View()
    botaovoltar = discord.ui.Button(emoji="<:setaesquerda:1318698827422765189>", style=discord.ButtonStyle.gray, disabled=(pagina == 0))
    view.add_item(item=botaovoltar)
    botaovoltar.callback = partial(trocardex, self, pokemon = pokemon , brilhante = brilhante , pagina = pagina-1 ,originaluser = originaluser )
    
    if brilhante is True:
        botaoshiny = discord.ui.Button(label="🌟", style=discord.ButtonStyle.green)
    else:
        botaoshiny = discord.ui.Button(label="🌟", style=discord.ButtonStyle.gray)
    view.add_item(item=botaoshiny)
    botaoshiny.callback = partial(trocarshiny, self, pokemon = pokemon , brilhante = brilhante , pagina = pagina ,originaluser = originaluser )

    botaoavancar = discord.ui.Button(emoji="<:setadireita:1318698789225369660>", style=discord.ButtonStyle.gray, disabled=(pagina == 1))
    view.add_item(item=botaoavancar)
    botaoavancar.callback = partial(trocardex, self, pokemon = pokemon , brilhante = brilhante , pagina = pagina+1 ,originaluser = originaluser )

    botaohelp = discord.ui.Button(label="?", style=discord.ButtonStyle.gray)
    view.add_item(item=botaohelp)
    botaohelp.callback = partial(duvidadex)
    
    await interaction.edit_original_response(content = "",attachments=[discord.File(fp=buffer,filename=f"{nomepokemon}.png")],view=view)


@commands.Cog.listener()
async def trocardex(self,interaction,pokemon , brilhante, pagina, originaluser):
  if interaction.user != originaluser:
    await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_interacaoalheia"),delete_after=10,ephemeral=True)
  else:
    view = discord.ui.View.from_message(interaction.message)
    for item in view.children:
            item.disabled = True
        # Atualiza a resposta original para refletir os botões desativados
    await interaction.response.edit_message(view=view)
    #await interaction.response.defer()
    await montarpokedex(self , interaction , pokemon , brilhante, pagina , originaluser)


@commands.Cog.listener()
async def trocarshiny(self,interaction,pokemon , brilhante, pagina, originaluser):
  if interaction.user != originaluser:
    await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_interacaoalheia"),delete_after=10,ephemeral=True)
  else:
    view = discord.ui.View.from_message(interaction.message)
    for item in view.children:
            item.disabled = True
        # Atualiza a resposta original para refletir os botões desativados
    await interaction.response.edit_message(view=view)
    if brilhante is True:
            await montarpokedex(self , interaction , pokemon , False, pagina , originaluser)
    else:     await montarpokedex(self , interaction , pokemon , True, pagina , originaluser)
        

#COMANDO DE EXIBIR AJUDA SOBRE A LOJA, CLASSICO BOTÃO DE AJUDA
@commands.Cog.listener()
async def duvidadex(interaction):
  await interaction.response.send_message(Res.trad(interaction=interaction,str="message_pokedex_duvida"),delete_after=30,ephemeral=True)





class pokedex(commands.Cog):
  def __init__(self, client: commands.Bot):
    self.client = client
    






  @commands.Cog.listener()
  async def on_bot_ready(self):
    print("🔍  -  Modúlo Pokedex Carregado.")
     







    #Comando POKEDEX
  @app_commands.command(name="pokedex",description="🔍⠂Procure um Pokémon na Pokedex.")
  @app_commands.describe(pokemon="Informe o nome de um pokémon...")
  @app_commands.autocomplete(pokemon=pokemon_autocomplete)
  @app_commands.allowed_installs(guilds=True, users=True)
  @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
  async def pokedex(self, interaction: discord.Interaction,pokemon:str):
    if await Res.print_brix(comando="pokedex",interaction=interaction):
        return
     # Busca a lista de Pokémon do autocomplete
    lista_pokemon = [p["name"] for p in await get_all_pokemon()]
    # Verifica se o digitado é próximo de algum nome válido
    match = get_close_matches(pokemon.lower(), [p.lower() for p in lista_pokemon], n=1, cutoff=0.8)
    if not match:
       return await interaction.response.send_message( Res.trad(interaction=interaction, str='message_pokemon_autocomplete_error').format(pokemon), ephemeral=True )
    
    pokemon = match[0].capitalize()  # normaliza o nome

    await interaction.response.defer()
    await montarpokedex(self=self , interaction= interaction , pokemon=pokemon , brilhante= False, pagina=0,originaluser = interaction.user)
    








async def setup(client:commands.Bot) -> None:
  await client.add_cog(pokedex(client))
