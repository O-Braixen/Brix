import discord,urllib.request,requests,re,asyncio,io,pytz,datetime,os
from discord.ext import commands,tasks
from discord import app_commands
from src.services.essential.pokemon_module import verificar_calendario_pokemon , encontrar_cor_tipo , get_pokemon , get_pokemon_sprite
from src.services.connection.database import BancoServidores
from src.services.essential.respostas import Res
from PIL import Image, ImageFont, ImageDraw, ImageOps #IMPORTAÇÂO Py PIL IMAGEM
Image.MAX_IMAGE_PIXELS = None


urlcalendario = 'https://calendar.google.com/calendar/ical/j5gnr9l1o867fke2cocmjieaa8@group.calendar.google.com/public/basic.ics'









class Pokeday(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.pokeday_error_count = {}






    @commands.Cog.listener()
    async def on_ready(self):
        print("⚽  -  Modúlo Pokeday carregado.")
        if not self.postagempokeday.is_running():
            downloadcalendario.start()
            self.postagempokeday.start()




        



        

    #TRABALHO DE ENVIO DA POSTAGEM POKEDAY # hour=8, minute= 0
    @tasks.loop(time=datetime.time(hour=8, minute= 0, tzinfo=datetime.timezone(datetime.timedelta(hours=-3))))
    async def postagempokeday(self):
        data_atual = datetime.datetime.now()
        #data_atual = datetime.date(data_atual.year , 10 , 7) #LINHA PARA CHECAGEM
        pokemon = await verificar_calendario_pokemon(data_atual=data_atual)
        
        if pokemon:
            print(f"Hoje é dia dos pokémon: {pokemon}")
            buffers = []
            #montar a postagem
            for poke in pokemon:
                try:
                    #poke = re.sub(r'[^a-zA-Z0-9]', '', poke)
                    specie = requests.get(f"https://pokeapi.co/api/v2/pokemon-species/{poke.lower()}/").json()
                    dex = await get_pokemon(specie['id'])
            
                    #CONJUNTO DAS FONTES
                    fontegrande = ImageFont.truetype("src/assets/font/Hey Comic.ttf",40)
                    fontepequena = ImageFont.truetype("src/assets/font/Quick-Fox.ttf",20)
                    fontemini = ImageFont.truetype("src/assets/font/Quick-Fox.ttf",11)
                    backgroud = Image.new("RGBA", (520,150), (0,0,0,0) )
                    fundo = Image.open("src/assets/imagens/icons/iconpokedaybackground.png")
                    corbase = encontrar_cor_tipo(dex['types'][0]['type']['name'])
                    bw = fundo.convert('L')
                    fundo = ImageOps.colorize(bw, black="black", white=corbase)
                    fundo = fundo.convert("RGBA")

                    #fundo = Image.new("RGBA", (520,150), encontrar_cor_tipo(dex['types'][0]['type']['name']))

                    # Desenha um retângulo com bordas arredondadas na máscara
                    mascara = Image.new("L", fundo.size, 0)  # 'L' para imagem em escala de cinza
                    draw = ImageDraw.Draw(mascara)
                    draw.rounded_rectangle([0, 0, fundo.size[0], fundo.size[1]], radius=30, fill=255)
                    fundodraw = ImageDraw.Draw(fundo)
                    fundodraw.text((155,5),f"Dia do {next((item['name'] for item in specie['names'] if item['language']['name'] == 'en'), None)}!",font = fontegrande)
                    
                    #ICONS
                    fundoicones = Image.open("src/assets/imagens/icons/iconpokeday.png")
                    fundoicones = fundoicones.convert("RGBA")

                    #textos
                    fundodraw.text((185,65),f"{next((item['name'] for item in specie['names'] if item['language']['name'] == 'en'), None)}",font = fontepequena)
                    fundodraw.text((360,65),f"#{dex['id']}",font = fontepequena)
                    fundodraw.text((185,100),f"{next((item['name'] for item in specie['names'] if item['language']['name'] == 'roomaji'), None)}",font = fontepequena)
                    fundodraw.text((360,100),f"{data_atual.strftime('%d/%m')}",font = fontepequena)
                    fundodraw.text((155,130),f"Gerado por Brix",font = fontemini)
                    
                    #MONTAGEM DA IMAGEM
                    pokeimagem = get_pokemon_sprite( dex['front_default'], pokemon=specie["id"], shiny=False )
                    #try:
                    #    pokeimagem = Image.open(requests.get(dex['front_default'], stream=True).raw)
                    #except:
                    #    pokeimagem = Image.open("src/assets/imagens/Pokedex/Interrogation.png")
                    pokeimagem = pokeimagem.resize((140,140))
                    fundo.paste(fundoicones,(0,0), fundoicones)
                    backgroud.paste(fundo,(0,0),mascara)
                    backgroud.paste(pokeimagem,(5,0), pokeimagem)
                    
                    #SALVANDO A IMAGEM
                    buffer = io.BytesIO()
                    backgroud.save(buffer,format="PNG")
                    buffer.seek(0)
                    buffers.append((buffer,f"{next((item['name'] for item in specie['names'] if item['language']['name'] == 'en'), None)}.png"))
                except Exception as e:
                    print(f"❌ Erro ao buscar dados do {poke}: {e}")
                    continue

            #FILTRANDO TODAS AS COMUNIDADES QUE HABILITARAM O SISTEMA DE AVISO POKEDAY
            filtro = {"pokeday": {"$exists":True}}
            canais = BancoServidores.select_many_document(filtro)
            buffer_final = combinar_imagens_verticais(buffers)
            imagem_bytes = buffer_final.getvalue()
            for linha in canais:
                #await asyncio.sleep(0.2)
                try: 
                    servidor = await self.client.fetch_guild(linha['_id'])
                    canal = await self.client.fetch_channel(linha['pokeday'].get('canal'))
                    ping = f"<@&{linha['pokeday'].get('ping')}>" if linha['pokeday'].get('ping') is not None else servidor.name
                    if len(pokemon) == 1:
                        message_content = f"Bom dia {ping} hoje é dia do Pokémon: **{poke}**"
                    else:
                        message_content = f"Bom dia {ping} hoje é dia dos Pokémon: **{', '.join(pokemon)}**"

                    print(f"enviando pokeday em {servidor.name}") 
                    novo_buffer = io.BytesIO(imagem_bytes)
                    novo_buffer.seek(0)
                    file = discord.File(novo_buffer, filename=f"pokemon_do_dia_{data_atual.strftime('%d-%m')}.png")
                    await canal.send(content=message_content,file=file)

                    # Se o envio foi bem-sucedido, podemos resetar o contador para esse servidor, se houver
                    if linha['_id'] in self.pokeday_error_count:
                        del self.pokeday_error_count[linha['_id']]

                except Exception as e:
                    print(f"gerei o erro: {e} para o ID: {linha['_id']}")
                        # Incrementa o contador de erros para esse servidor
                    servidor_id = linha['_id']
                    contador = self.pokeday_error_count.get(servidor_id, 0) + 1
                    self.pokeday_error_count[servidor_id] = contador
                        
                    print(f"Contador de erros para o servidor {servidor_id}: {contador}")
                    
                    if contador > 2:
                        print(f"Mais de 2 erros para o servidor {servidor_id}. Deletando registro.")
                        item_remover = {"pokeday": linha['pokeday']}
                        BancoServidores.delete_field(servidor_id, item_remover)
                            # Remove o contador do cache após a deleção
                        del self.pokeday_error_count[servidor_id]

            buffer_final.close() # Limpa o buffer existente

        else: #aqui a baixo ignora o dia 
            print("🦊 - Nada para hoje kyu")
            return














#GRUPO DE COMANDOS DE POKEMON DO DIA DO BRIX
    grupoday=app_commands.Group(name="pokeday",description="Comandos de pokeday do Brix.",allowed_installs=app_commands.AppInstallationType(guild=True,user=False),allowed_contexts=app_commands.AppCommandContext(guild=True, dm_channel=False, private_channel=False))









    #COMANDO POKEDAY CONFIGURAR
    @grupoday.command(name="configurar",description='📅⠂Configurar pokeday no servidor.')
    @commands.has_permissions(manage_guild=True)
    @app_commands.describe(canal="Indique um canal para postar o pokémon do dia",cargo="Selecione um cargo que será pingado...")
    async def pokedayconfigurar(self,interaction: discord.Interaction,canal : discord.TextChannel, cargo: discord.Role = None):
        if await Res.print_brix(comando="pokedayconfigurar",interaction=interaction):
            return
        if interaction.guild is None:
            await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyservers"),delete_after=20,ephemeral=True)
            return
        
        elif interaction.permissions.manage_guild:
            await interaction.response.defer(ephemeral=True)
            if cargo is None:
                cargo = None
            else:
                cargo = cargo.id
            item = {"pokeday.canal": canal.id,"pokeday.ping": cargo}
            BancoServidores.update_document(interaction.guild.id,item)
            try:
                mensagemteste = await canal.send(content='kyu' , file= discord.File("src/assets/imagens/icons/BH_Pokeball.png"))
                await asyncio.sleep(0.2)
                await mensagemteste.delete()
                await interaction.edit_original_response(content=Res.trad(interaction=interaction,str="message_pokeday_confirmado"))
            except:
                await interaction.edit_original_response(content=Res.trad(interaction=interaction,str="message_pokeday_erro"))

        else: await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro"),delete_after=20,ephemeral=True)












    
    #COMANDO POKEDAY DESATIVAR
    @grupoday.command(name="desativar",description='📅⠂Desative o pokeday na sua comunidade.')
    @commands.has_permissions(manage_guild=True)
    async def pokedaydesativar(self,interaction: discord.Interaction):
        if await Res.print_brix(comando="pokedaydesativar",interaction=interaction):
            return
        if interaction.guild is None:
            await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyservers"),delete_after=20,ephemeral=True)
            return
        
        elif interaction.permissions.manage_guild:
            await interaction.response.defer(ephemeral=True)
            item = {"pokeday":interaction.channel.id}
            BancoServidores.delete_field(interaction.guild.id,item)
            await interaction.edit_original_response(content=Res.trad(interaction=interaction,str="message_pokeday_desativado"))

        else: await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro"),delete_after=10,ephemeral=True)









    #COMANDO POKEDAY AJUDA
    @grupoday.command(name="ajuda",description='📅⠂Dicas de uso do Pokeday.')
    async def pokedaydicas(self,interaction: discord.Interaction):
        await interaction.response.send_message(Res.trad(interaction=interaction,str="message_pokeday_dica"),delete_after=60)










#REALIZA O DONWLOAD DO CALENDARIO POKEDAY
@tasks.loop(hours=360)
async def downloadcalendario():
    try:
        urllib.request.urlretrieve(urlcalendario, "modulos/caches/pokedaycalendar.ics")
        print("📅  -  Calendario Pokémon baixado via URL")
    except:
        print("📅  -  Calendario Pokémon usando local")










#COMBINADOR VERTICAL DE IMAGENS
def combinar_imagens_verticais(buffers):
    # Carregar as imagens dos buffers
    imagens = [Image.open(buffer) for buffer, _ in buffers]

    # Calcular a largura máxima e a altura total da imagem final
    largura_total = max(imagem.width for imagem in imagens)
    altura_total = sum(imagem.height for imagem in imagens)
    
    # Criar uma nova imagem com largura máxima e altura somada
    imagem_final = Image.new("RGBA", (largura_total, altura_total))
    
    # Colar cada imagem uma abaixo da outra
    y_offset = 0
    for imagem in imagens:
        imagem_final.paste(imagem, (0, y_offset))
        y_offset += imagem.height  # Move o y para a próxima posição
    
    # Salvar a imagem final no buffer
    buffer_final = io.BytesIO()
    imagem_final.save(buffer_final, format="PNG")
    buffer_final.seek(0)
    return buffer_final



async def setup(client: commands.Bot) -> None:
    await client.add_cog(Pokeday(client))
