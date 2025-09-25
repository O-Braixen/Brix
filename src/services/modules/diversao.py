import discord,os,asyncio,requests,random,io,textwrap,time
from discord.ext import commands,tasks
from discord import app_commands
from discord.voice_client import VoiceClient 
from typing import List
from functools import partial
from src.services.essential.E621api import E621
from src.services.connection.database import BancoServidores
from src.services.essential.respostas import Res
from src.services.essential.funcoes_usuario import userpremiumcheck , verificar_cooldown
from src.services.essential.gasmii import generate_response_with_text
from src.services.essential.imagem import pegar_imagem
from src.services.essential.diversos import container_media_button_url
from PIL import Image, ImageFont, ImageDraw, ImageOps #IMPORTAÇÂO Py PIL IMAGEM
Image.MAX_IMAGE_PIXELS = None


# ======================================================================

id_chatBH = int(os.getenv('id_chatBH'))








# ======================================================================
#REALIZANDO O LOGIN DA API DO E621
try:
    time.sleep(2)  # Espera de 2 segundos
    e621api = E621()
    e621api.login(os.getenv("E621_Login"), os.getenv("E621_Api"))
    print("🦊  -  Login e621 bem-sucedido!")
except:
    print(f"❌  -  Falha no login do e621")













#API E621 VIA SLASH
async def buscae621slash(interaction,quantidade,item, MOD_NSFW):
    if await Res.print_brix(comando="buscare621slash",interaction=interaction,condicao=item):
        return
    try:
        await interaction.response.defer()
        if quantidade == None:
            quantidade = 1
        else:
            quantidade = quantidade.value
        if quantidade <= 15:
            page = random.randint(1,15)
            i = 0
            try:
                if interaction.channel.is_nsfw():
                    busca = item
                    filtro = "rating:s,urine,gore,feces,diaper"
                    messagefooter = Res.trad(interaction=interaction,str='message_APIE621_footer')
                else:
                    busca = f"{item} rating:s"
                    filtro = "rating:e,rating:q,urine,gore,feces,breasts,genitals,butt,diaper"
                    messagefooter = Res.trad(interaction=interaction,str='message_APIE926_footer')
            except:
                MOD_NSFW = MOD_NSFW.value if MOD_NSFW else False
                if MOD_NSFW:
                    busca = item
                    filtro = "rating:s,urine,gore,feces,diaper"
                    messagefooter = Res.trad(interaction=interaction,str='message_APIE621_footer')
                else:
                    busca = f"{item} rating:s"
                    filtro = "rating:e,rating:q,urine,gore,feces,breasts,genitals,butt,diaper"
                    messagefooter = Res.trad(interaction=interaction,str='message_APIE926_footer')

            r=e621api.posts.search(busca, filtro ,50 ,page,ignorepage=True)
            if r == []:
                r=e621api.posts.search(busca, filtro ,100 ,1,ignorepage=True)
            if len(r) < quantidade: # caso quantidade seja inferior ao pedido
                r=e621api.posts.search(busca, filtro ,50 ,page-1,ignorepage=True)
            r = random.sample(r,quantidade)
            while (i< len(r) ):
                post = r[i]
                i=i+1
                descrição = Res.trad(interaction=interaction,str="artista").format(post['tags']['artist'][0] if post['tags']['artist'] else '-')
                view = container_media_button_url(titulo= item, descricao= descrição, galeria = post['file']['url'], buttonLABEL=Res.trad(interaction=interaction,str="botão_abrir_navegador") , buttonURL=f"https://e621.net/posts/{post['id']}" , footer=messagefooter)
                await interaction.followup.send(view=view)

        else:await interaction.followup.send(Res.trad(interaction=interaction,str="message_erro_E621_limit").format(quantidade),ephemeral = True)    
    except Exception as e:
        print(e)
        await interaction.followup.send(Res.trad(interaction=interaction,str="message_erro_APIE621"),ephemeral = True)


















#API ANIMAL RANDOMICO VIA SLASH
async def animalrandomico(interaction, quantidade, apirandom , getter):
    try:
        await interaction.response.defer()
        if quantidade is None:
            quantidade = 1
        if quantidade <= 5:
            for _ in range(quantidade):
                r = requests.get(apirandom)
                res_list = r.json()
                # Se a resposta for um dict, transforme em lista para iterar uniformemente
                if isinstance(res_list, dict):
                    res_list = [res_list]

                for res in res_list:
                    if getter in res:
                        image_url = res[getter]
                        view = container_media_button_url(titulo= Res.trad(interaction=interaction,str="message_titulo_apirandomica"),galeria = image_url, buttonLABEL=Res.trad(interaction=interaction,str="botão_abrir_navegador") , buttonURL=image_url)
                        await interaction.followup.send(view = view)
                    else:
                        await interaction.followup.send(Res.trad(interaction=interaction,str="message_erro_apirandomica_url"), ephemeral=True)
        else:
            await interaction.followup.send(Res.trad(interaction=interaction,str="message_erro_apirandomica_limit").format(quantidade), ephemeral=True)
    except:
        await interaction.followup.send(Res.trad(interaction=interaction,str="message_erro_apirandomica"), ephemeral=True)





















# ======================================================================


class diversao(commands.Cog):
  def __init__(self, client: commands.Bot):
    self.client = client
     # Cache para contar erros de cada registro: chave = ID do servidor, valor = contador
    self.autophox_error_count = {}
    












  @commands.Cog.listener()
  async def on_ready(self):
    print("🎲  -  Modúlo Diversao carregado.")
    await self.client.wait_until_ready() #Aguardando o bot ficar pronto
    if not self.autophox.is_running():
        await asyncio.sleep(1200) #1200
        self.autophox.start()
  















  @commands.Cog.listener()
  async def on_message(self,message):

        if message.author == self.client.user or message.author.bot:
            return
        
        elif message.guild is None:
            return

        elif "kyu" in message.content.lower() and message.author != self.client.user and message.channel.id != id_chatBH:
            try:
                await message.reply(random.choice(Res.trad(guild=message.guild.id,str='responsekyu')))
            except:
                print(f"falha ao enviar Kyu no servidor {message.guild.name} - {message.guild.id} para o {message.author.name} - {message.author.id}")


















    #LOOP DE POSTAGEM DO AUTOPHOX
  @tasks.loop(hours=1) # hours=1
  async def autophox(self):
    print("🦊 - rodando Auto Phox")
    try:
        pesquisa = ['fennekin','braixen','delphox','mega_delphox']
        item = random.choice(pesquisa)
        retorno = []
        page = random.randint(1,45)
        while not retorno:
            retorno=e621api.posts.search(tags=f"{item} rating:s -breasts -genitals -butt -diaper",blacklist="rating:e,rating:q,urine,gore,feces,breasts,genitals,butt,diaper" ,limit=200 ,page=page,ignorepage=True)
            await asyncio.sleep(1)
            page = random.randint(1,page)
        post = random.choice(retorno)
        filtro = {"autophox": {"$exists":True}}
        canais = BancoServidores.select_many_document(filtro)
        for linha in canais:
            try:
                servidor = await self.client.fetch_guild(linha['_id'])
                canal = await self.client.fetch_channel(linha['autophox'])
                #view = discord.ui.View()
                #button = discord.ui.Button(style=discord.ButtonStyle.blurple,label=Res.trad(guild=servidor.id,str="botão_abrir_navegador"),url=f"https://e621.net/posts/{post['id']}")
                #view.add_item(item=button)
                
                #await canal.send(f"[{post['tags']['artist'][0]}]({post['file']['url']})\n-# {Res.trad(guild=servidor.id,str='message_autophox_footer')}",view=view)

                descrição = Res.trad(guild=servidor.id,str="artista").format(post['tags']['artist'][0] if post['tags']['artist'] else '-')
                view = container_media_button_url(titulo= Res.trad(guild=servidor.id,str="message_autophox_titulo").format(item.replace("_", " ").title()), descricao= descrição, galeria = post['file']['url'], buttonLABEL=Res.trad(guild=servidor.id,str="botão_abrir_navegador") , buttonURL=f"https://e621.net/posts/{post['id']}" , footer= Res.trad(guild=servidor.id,str='message_autophox_footer') )
                await canal.send(view=view)

                # Se o envio foi bem-sucedido, podemos resetar o contador para esse servidor, se houver
                if linha['_id'] in self.autophox_error_count:
                    del self.autophox_error_count[linha['_id']]
            except Exception as e:
                print(f"gerei o erro: {e} para o ID: {linha['_id']}")
                
                # Incrementa o contador de erros para esse servidor
                servidor_id = linha['_id']
                contador = self.autophox_error_count.get(servidor_id, 0) + 1
                self.autophox_error_count[servidor_id] = contador
                    
                print(f"Contador de erros para o servidor {servidor_id}: {contador}")
                  
                if contador > 5:
                    print(f"Mais de 5 erros para o servidor {servidor_id}. Deletando registro.")
                    item_remover = {"autophox": linha['autophox']}
                    BancoServidores.delete_field(servidor_id, item_remover)
                        # Remove o contador do cache após a deleção
                    del self.autophox_error_count[servidor_id]
                


    except Exception as e:
        print(f"erro na api, tentarei novamente depois, confira o erro gerado: {e}")
      
























#------------------COMANDOS-------------------------------

  # Comando AutoPhox
  @app_commands.command(name="autophox", description="🦊⠂Ative ou desative a postagem automática de imagens.")
  @app_commands.describe(opcao="Ativar ou desativar?")
  async def optionautophox(self, interaction: discord.Interaction, opcao: bool):
    if await Res.print_brix(comando="autophox", interaction=interaction):
        return
    await interaction.response.defer()
    if interaction.guild is None:
        await interaction.followup.send(Res.trad(interaction=interaction, str="message_erro_onlyservers"))
    elif interaction.permissions.manage_guild:
        if opcao:
            item = {"autophox": interaction.channel.id}
            BancoServidores.update_document(interaction.guild.id, item)
        else:
            item = {"autophox": interaction.channel.id}
            BancoServidores.delete_field(interaction.guild.id, item)
        texto = "ativado" if opcao else "desativado"
        await interaction.followup.send(Res.trad(interaction=interaction, str="message_autophox_notificacao").format(texto))
    else:
        await interaction.followup.send(Res.trad(interaction=interaction, str="message_erro"), ephemeral=True)












    
#GRUPO DE COMANDOS DE KYU DO BOT 
  kyu=app_commands.Group(name="kyu",description="Comandos de voz do Brix.")

#COMANDO JOIN CANAL DE VOZ
  @kyu.command(name="conectar",description='🔈⠂Faz Brix se conectar a um canal.')
  async def join(self,interaction:discord.Interaction):
    if await Res.print_brix(comando="kyujoin",interaction=interaction):
        return
    await interaction.response.defer()
    try:
        canal = interaction.user.voice.channel
        voice_client = await asyncio.wait_for(canal.connect(), timeout=2)  # Tempo máximo de 2 segundos
        #await canal.connect()
        resposta = discord.Embed( 
            colour=discord.Color.yellow(),
            title="🦊┃kyu~",
            description=f"e-estou **conectado ao {canal.name}!**"
        )
        await interaction.followup.send(embed=resposta)
    except Exception as e:
        await Res.erro_brix_embed(interaction,str="message_erro_brixsystem",e=e,comando="join")


#COMANDO LEAVE CANAL DE VOZ
  @kyu.command(name="desconectar",description='🔈⠂Faz Brix sair de um canal.')
  async def leave(self,interaction:discord.Interaction):
    if await Res.print_brix(comando="kyuleave",interaction=interaction):
        return
    await interaction.response.defer()
    try:
        resposta = discord.Embed( 
            colour=discord.Color.yellow(),
            title="🦊┃kyu~",
            description=f"f-fui **desconectado!**"
        )
        await interaction.guild.voice_client.disconnect(force=True)
        await interaction.followup.send(embed=resposta)
    except Exception as e:
        await Res.erro_brix_embed(interaction,str="message_erro_brixsystem",e=e,comando="leave")

































  #GRUPO DE COMANDOS DE IMAGENS BOT 
  img=app_commands.Group(name="img",description="Comandos de imagens do bot.",allowed_installs=app_commands.AppInstallationType(guild=True,user=True),allowed_contexts=app_commands.AppCommandContext(guild=True, dm_channel=True, private_channel=True))












#COMANDO BRAIXEN SLASH
  @img.command(name="braixen",description='🎨⠂imagem de Braixen.')
  @app_commands.choices(quantidade=[app_commands.Choice(name=f"{i}", value=i) for i in range(1, 16)] , filtro=[app_commands.Choice(name="SFW", value=False), app_commands.Choice(name="NSFW", value=True)])
  @app_commands.describe(quantidade="quantidade de imagens, limite 15", filtro = "Opção valida somente para canais privados ou DM")
  async def braixen(self,interaction: discord.Interaction,quantidade:app_commands.Choice[int]=None , filtro: app_commands.Choice[int] = None):
    item = "braixen"
    await buscae621slash(interaction,quantidade,item,filtro)













#COMANDO FENNEKIN SLASH
  @img.command(name="fennekin",description='🎨⠂imagem de Fennekin.')
  @app_commands.choices(quantidade=[app_commands.Choice(name=f"{i}", value=i) for i in range(1, 16)] , filtro=[app_commands.Choice(name="SFW", value=False), app_commands.Choice(name="NSFW", value=True)])
  @app_commands.describe(quantidade="quantidade de imagens, limite 15", filtro = "Opção valida somente para canais privados ou DM")
  async def fennekin(self,interaction: discord.Interaction,quantidade:app_commands.Choice[int]=None , filtro: app_commands.Choice[int] = None):
    item = "fennekin"
    await buscae621slash(interaction,quantidade,item,filtro)













#COMANDO DELPHOX SLASH
  @img.command(name="delphox",description='🎨⠂imagem de Delphox.')
  @app_commands.choices(quantidade=[app_commands.Choice(name=f"{i}", value=i) for i in range(1, 16)] , filtro=[app_commands.Choice(name="SFW", value=False), app_commands.Choice(name="NSFW", value=True)])
  @app_commands.describe(quantidade="quantidade de imagens, limite 15", filtro = "Opção valida somente para canais privados ou DM")
  async def delphox(self,interaction: discord.Interaction,quantidade:app_commands.Choice[int]=None , filtro: app_commands.Choice[int] = None):
    item = "delphox"
    await buscae621slash(interaction,quantidade,item,filtro)
  









#COMANDO DELPHOX SLASH
  @img.command(name="mega-delphox",description='🎨⠂imagem de Mega Delphox.')
  @app_commands.choices(quantidade=[app_commands.Choice(name=f"{i}", value=i) for i in range(1, 16)] , filtro=[app_commands.Choice(name="SFW", value=False), app_commands.Choice(name="NSFW", value=True)])
  @app_commands.describe(quantidade="quantidade de imagens, limite 15", filtro = "Opção valida somente para canais privados ou DM")
  async def megadelphox(self,interaction: discord.Interaction,quantidade:app_commands.Choice[int]=None , filtro: app_commands.Choice[int] = None):
    item = "mega_delphox"
    await buscae621slash(interaction,quantidade,item,filtro)












  #COMANDO PRIMARINA SLASH
  @img.command(name="busca",description='🎨⠂Procure algo no e621 ou e926.')
  @app_commands.choices(quantidade=[app_commands.Choice(name=f"{i}", value=i) for i in range(1, 16)] , filtro=[app_commands.Choice(name="SFW", value=False), app_commands.Choice(name="NSFW", value=True)])
  @app_commands.describe(tag="indique uma tag",quantidade="quantidade de imagens, limite 15", filtro = "Opção valida somente para canais privados ou DM")
  async def buscae621(self,interaction: discord.Interaction,tag:str,quantidade:app_commands.Choice[int]=None , filtro: app_commands.Choice[int] = None):
    await buscae621slash(interaction,quantidade,tag,filtro)
     

  @buscae621.autocomplete("tag")
  async def valor_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
      sugestao: List[app_commands.Choice[str]] = []

      try:
          # tenta buscar no e621
          r = requests.get( "https://e621.net/tags/autocomplete.json", params={"search[name_matches]": current}, headers={"User-Agent": "DiscordBot/1.0 (by YourUsername on e621)"}, timeout=2 )
          r.raise_for_status()  # se retornar erro HTTP, levanta exceção
          data = r.json()
      except requests.exceptions.ReadTimeout:
          data = e621api.tags.search(current)
      except:
          data = []

      # monta sugestões
      for tag in data:
          try:
              sugestao.append(
                  app_commands.Choice(
                      name=f"{tag['name']} ({tag['post_count']})",
                      value=tag['name']
                  )
              )
          except Exception:
              continue

      return sugestao[:25]  # Discord só aceita até 25 opções








#COMANDO PRIMARINA SLASH
  @img.command(name="ajuda",description='🎨⠂Ajuda sobre o meu modulo de imagens.')
  async def img_help(self,interaction: discord.Interaction):
    if await Res.print_brix(comando="img_help",interaction=interaction):
      return
    view = container_media_button_url(descricao= Res.trad(interaction=interaction,str="message_APIE621_E926_help") )

    await interaction.response.send_message(view=view)
     





















#GRUPO DE COMANDOS DE DIVERSÂO DO BOT 
  modulodiversao=app_commands.Group(name="diversao",description="Comandos de diversão do Brix.",allowed_installs=app_commands.AppInstallationType(guild=True,user=True),allowed_contexts=app_commands.AppCommandContext(guild=True, dm_channel=True, private_channel=True))







#COMANDO GIRAR MOEDA
  @modulodiversao.command(name='girarmoeda',description='🪙⠂Veja se a moeda cai cara ou coroa.')
  async def coinflip(self, interaction:discord.Interaction):
    if await Res.print_brix(comando="coinflip",interaction=interaction):
        return
    sorteiobot = ["cara","coroa"]
    moedasorteada = random.choice(sorteiobot)
    if moedasorteada == "cara":
        mensagem = "<:BraixenCoin:1272655353108103220>  - **Cara**"
    else:
        mensagem = "<:BraixenCoinCoroa:1272655802070732852>  - **coroa**"
    await interaction.response.send_message(mensagem)













#COMANDO D20
  @modulodiversao.command(name="d20", description="🪙⠂Rode o D20.")
  async def d20(self, interaction: discord.Interaction):
        if await Res.print_brix(comando="d20", interaction=interaction):
            return

        moedasorteada = random.randint(1, 20)
        file = discord.File(f"src/assets/imagens/D20/d20_{moedasorteada}.png", filename=f"d20_{moedasorteada}.png")

        view = discord.ui.View(timeout=None)
        botao = discord.ui.Button(label="D20",emoji="🔁", style=discord.ButtonStyle.primary)
        botao.callback = partial(self.reroll_d20, original_user=interaction.user)
        view.add_item(botao)
                                                    #content=f"## 🎲 - `{moedasorteada}`"
        await interaction.response.send_message( file=file, view=view )

  async def reroll_d20(self, interaction: discord.Interaction, original_user: discord.User):
        if interaction.user != original_user:
            await interaction.response.send_message( content=Res.trad(interaction=interaction, str='message_erro_interacaoalheia'), ephemeral=True )
            return

        moedasorteada = random.randint(1, 20)
        file = discord.File(f"src/assets/imagens/D20/d20_{moedasorteada}.png", filename=f"d20_{moedasorteada}.png")

        view = discord.ui.View(timeout=None)
        botao = discord.ui.Button(label="D20",emoji="🔁", style=discord.ButtonStyle.primary)
        botao.callback = partial(self.reroll_d20, original_user=original_user)
        view.add_item(botao)

        await interaction.response.edit_message(  attachments=[file], view=view )



















#COMANDO 8BALL
  @modulodiversao.command(name='8ball',description='🎱⠂Pergunte algo de sim/não ao Brix.')
  @app_commands.describe(pergunta = "Escreva sua pergunta de sim ou não...")
  async def ball8(self, interaction:discord.Interaction,pergunta:str):
    if await Res.print_brix(comando="ball8",interaction=interaction):
        return
    await interaction.response.defer()
    msg = random.choice(Res.trad( interaction=interaction, str='message_8ball'))
    resposta = discord.Embed( 
            colour=discord.Color.yellow(),
            title="🎱┃8Ball",
            description=Res.trad(interaction=interaction,str="message_8ball_description").format(pergunta,msg)
            )
    view = container_media_button_url( descricao_thumbnail="https://www.clipartmax.com/png/full/103-1034729_pokemon-braixen-fire-fox-ask-vixen-the-braixen-january-17.png", descricao=Res.trad(interaction=interaction,str="message_8ball_description").format(pergunta,msg) )
    await interaction.followup.send(view=view)


















#COMANDO SABEDORIA DE BRIX
  @modulodiversao.command(name='sabedoria',description='🦊⠂Adquira um conhecimento aleatório de brix.')
  async def sabedoriabrix(self, interaction:discord.Interaction):
    if await Res.print_brix(comando="sabedoriabrix",interaction=interaction):
        return
    await interaction.response.defer()
    #resposta = discord.Embed( colour=discord.Color.yellow(),description=random.choice(Res.trad( interaction=interaction, str='message_diversao_sabedoria')))
    #await interaction.followup.send(embed=resposta)
    view = container_media_button_url(descricao=random.choice(Res.trad( interaction=interaction, str='message_diversao_sabedoria')) , descricao_thumbnail="https://i.imgur.com/OEgfv4K.png")
    await interaction.followup.send(view=view)














#COMANDO DIARIO DE BRIX
  @modulodiversao.command(name='diario-de-raposa',description='🦊⠂Leia algum dia aleatório de brix.')
  async def diario_de_raposa(self, interaction:discord.Interaction):
    if await Res.print_brix(comando="diario-de-raposa",interaction=interaction):
        return
    await interaction.response.defer()
    diario = random.choice(Res.trad( interaction=interaction, str='message_diversao_diariobrix'))
    view = container_media_button_url(descricao=Res.trad( interaction=interaction, str='message_diversao_diariobrix_descricao').format(diario), descricao_thumbnail="https://i.imgur.com/eUJJ5BA.png")
    await interaction.followup.send(view=view)


















  @modulodiversao.command(name="pokequiz", description="🎮⠂Teste seus conhecimentos de Pokémon!")
  async def pokequiz(self, interaction: discord.Interaction):
    if await Res.print_brix(comando="pokequiz",interaction=interaction):
        return
    await interaction.response.defer()

    # Puxa direto do teu JSON carregado (ex: Res.trad)
    quiz_list = Res.trad(interaction=interaction, str='pokequiz')

    pergunta = random.choice(quiz_list)
    alternativas = pergunta["alternativas"]
    random.shuffle(alternativas)
    correta = pergunta["correta"]

    view = discord.ui.View(timeout=120)
    for alt in alternativas:
        botao = discord.ui.Button(label=alt, style=discord.ButtonStyle.secondary)
        botao.callback = partial(self.verificar_quiz, correta=correta, original_user=interaction.user, resposta_usuario=alt)
        view.add_item(botao)

    resposta = discord.Embed( colour=discord.Color.yellow(),description=Res.trad( interaction=interaction, str='message_pokequiz').format(pergunta['pergunta']))
    resposta.set_thumbnail(url="https://cdn.discordapp.com/emojis/1196968606269976596.png")
    await interaction.followup.send(embed=resposta, view=view)

  async def verificar_quiz(self, interaction: discord.Interaction, correta: str, original_user: discord.User, resposta_usuario: str):
    if interaction.user != original_user:
        await interaction.response.send_message(content=Res.trad(interaction=interaction, str='message_erro_interacaoalheia'), ephemeral=True)
        return

    view = discord.ui.View(timeout=None)
    for child in interaction.message.components[0].children:
        btn = discord.ui.Button(label=child.label)
        btn.disabled = True
        if child.label == correta:
            btn.style = discord.ButtonStyle.success
        elif child.label == resposta_usuario:
            btn.style = discord.ButtonStyle.danger
        else:
            btn.style = discord.ButtonStyle.secondary
        view.add_item(btn)

    if resposta_usuario == correta:
        msg = Res.trad(interaction=interaction, str='message_pokequiz_correta')
    else:
        msg = Res.trad(interaction=interaction, str='message_pokequiz_errada').format(correta)
    resposta = discord.Embed( colour=discord.Color.yellow(),description=msg)
    resposta.set_thumbnail(url="https://cdn.discordapp.com/emojis/1196968606269976596.png")
    await interaction.response.edit_message(embed=resposta, view=view)






























  #GRUPO DE COMANDOS DE IMAGENS RANDOMICAS BOT 
  gruporand=app_commands.Group(name="randomico",description="Comandos de imagens randomicos.",parent = modulodiversao)

















#COMANDO RAPOSA RANDOMICA SLASH
  @gruporand.command(name="raposa",description='🎨⠂imagem aleatoria de uma raposa.')
  @app_commands.choices(quantidade=[app_commands.Choice(name=f"{i}", value=i) for i in range(1, 6)])
  @app_commands.describe(quantidade="quantidade de imagens, limite 5")
  async def randraposa(self,interaction: discord.Interaction,quantidade:int=None):
    if await Res.print_brix(comando="randraposa",interaction=interaction):
        return
    apirandom = "https://randomfox.ca/floof/"
    await animalrandomico(interaction,quantidade,apirandom,'image')












#COMANDO GATO RANDOMICO SLASH
  @gruporand.command(name="gato",description='🎨⠂imagem aleatoria de um gato.')
  @app_commands.choices(quantidade=[app_commands.Choice(name=f"{i}", value=i) for i in range(1, 6)])
  @app_commands.describe(quantidade="quantidade de imagens, limite 5")
  async def randgato(self,interaction: discord.Interaction,quantidade:int=None):
    if await Res.print_brix(comando="randgato",interaction=interaction):
        return
    apirandom = "https://api.thecatapi.com/v1/images/search"
    await animalrandomico(interaction,quantidade,apirandom,'url')













#COMANDO CACHORRO RANDOMICO SLASH
  @gruporand.command(name="cachorro",description='🎨⠂imagem aleatoria de um cachorro.')
  @app_commands.choices(quantidade=[app_commands.Choice(name=f"{i}", value=i) for i in range(1, 6)])
  @app_commands.describe(quantidade="quantidade de imagens, limite 5")
  async def randcachorro(self,interaction: discord.Interaction,quantidade:int=None):
    if await Res.print_brix(comando="randcachorro",interaction=interaction):
        return
    apirandom = "https://api.thedogapi.com/v1/images/search"
    await animalrandomico(interaction,quantidade,apirandom,'url')











































#--------------------------------  SETOR DOS MEMES ------------------------------------
  

#GRUPO DE COMANDOS DE MEMES DO BOT 
  meme=app_commands.Group(name="meme",description="Comandos de geração de imangens do Brix.",parent=modulodiversao)












#criador de memes Braixen REAL
  @meme.command(name="braixen-real",description='🤡⠂Oque Vinicius está segurando?')
  @app_commands.describe(imagem="Anexe uma imagem para virar meme", url_imagem="URL de uma imagem", avatar_usuario="Use o avatar de um usuário")
  async def braixenrealmeme(self,interaction: discord.Interaction, imagem: discord.Attachment = None, url_imagem: str = None, avatar_usuario: discord.User = None):
    if await Res.print_brix(comando="braixenrealmeme",interaction=interaction):
        return    
    try:
        await interaction.response.defer()
        imagem_pil = await pegar_imagem(interaction, imagem, url_imagem, avatar_usuario)
        if not imagem_pil:
            await interaction.followup.send(Res.trad(interaction=interaction,str="message_erro_apimemes_notmidia"), ephemeral=True)
            return

        fundo = Image.new("RGB",(362,480),"white")

        imagem_pil  = imagem_pil.resize((224,153))
        meme = Image.open("src/assets/imagens/memes/Vinicius_Segurando_Cartao_Sem_Fundo.png")
        fundo.paste(imagem_pil,(71,237))
        fundo.paste(meme,(0,0),meme)
        buffer = io.BytesIO()
        fundo.save(buffer,format="PNG")
        buffer.seek(0)
        await interaction.followup.send(file=discord.File(fp=buffer,filename="braixen da vida real.png"))
    except Exception as e:
        await Res.erro_brix_embed(interaction,str="message_erro_apimemes",e=e,comando="braixenrealmeme")
        

















#criador de memes Braixen INTERNET
  @meme.command(name="braixen-internet",description='🤡⠂Oque assustou Braixen?')
  @app_commands.describe(imagem="Anexe uma imagem para virar meme", url_imagem="URL de uma imagem", avatar_usuario="Use o avatar de um usuário")
  async def braixenmonitor(self,interaction: discord.Interaction, imagem: discord.Attachment = None, url_imagem: str = None, avatar_usuario: discord.User = None):
    if await Res.print_brix(comando="braixenmonitor",interaction=interaction):
        return

    try:
        await interaction.response.defer()
        fundo = Image.new("RGB",(800,751),"white")
        imagem_pil = await pegar_imagem(interaction, imagem, url_imagem, avatar_usuario)
        if not imagem_pil:
            await interaction.followup.send(Res.trad(interaction=interaction,str="message_erro_apimemes_notmidia"), ephemeral=True)
            return
        
        imagem_pil = imagem_pil.resize((345,245))
        meme = Image.open("src/assets/imagens/memes/braixen monitor.png")
        fundo.paste(imagem_pil,(337,94))
        fundo.paste(meme,(0,0),meme)
        buffer = io.BytesIO()
        fundo.save(buffer,format="PNG")
        buffer.seek(0)
        await interaction.followup.send(file=discord.File(fp=buffer,filename="braixen e seu pc.png"))
    except Exception as e:
        await Res.erro_brix_embed(interaction,str="message_erro_apimemes",e=e,comando="braixenmonitor")


















#criador de memes MINHA Braixen
  @meme.command(name="my-braixen",description='🤡⠂garanta a braixen para você.')
  @app_commands.describe(rival="Indique um rival")
  async def mybraixen(self,interaction: discord.Interaction, rival:discord.User):
    if await Res.print_brix(comando="mybraixen",interaction=interaction):
        return
  
    try:
        await interaction.response.defer()
        
        
        if not interaction.user.avatar or not rival.avatar:
            await interaction.followup.send(Res.trad(interaction=interaction,str="message_erro_apimemes_notavatar")) 
            return
        
        interaction_image_data = await interaction.user.avatar.replace(size=512, format="png").read()
        rival_image_data = await rival.avatar.replace(size=512, format="png").read()

        mascaraavatar = Image.open(f"src/assets/imagens/icons/recorte-redondo.png")
        mascaraavatar = mascaraavatar.resize((75,75))

        membro_bytesio = io.BytesIO(interaction_image_data)
        avatar1 = Image.open(membro_bytesio)
        avatar1 = avatar1.resize((75,75))
        
        membro_bytesio = io.BytesIO(rival_image_data)
        avatar2 = Image.open(membro_bytesio)
        avatar2 = avatar2.resize((75,75))

        fundo = Image.new("RGB",(440,550),"white")
        meme = Image.open("src/assets/imagens/memes/don_t_touch_her.png")
        fundo.paste(meme,(0,0))
        fundo.paste(avatar1,(120,370),mascaraavatar)
        fundo.paste(avatar2,(300,31),mascaraavatar)
        fundo.paste(avatar2,(270,380),mascaraavatar)

        buffer = io.BytesIO()
        fundo.save(buffer,format="PNG")
        buffer.seek(0)
        await interaction.followup.send(file=discord.File(fp=buffer,filename="minha braixen.png"))
    except Exception as e:
        await Res.erro_brix_embed(interaction,str="message_erro_apimemes",e=e,comando="mybraixen")





















#criador de memes NOSSA Braixen
  @meme.command(name="nossa-braixen",description='🤡⠂3 caras e uma Braixen.')
  @app_commands.describe(cara1="Indique o cara 1",cara2="Indique o cara 2",cara3="Indique o cara 3",braixen="Indique alguem para ficar no lugar da braixen")
  async def nossabraixen(self,interaction: discord.Interaction, cara1:discord.User, cara2:discord.User, cara3:discord.User, braixen:discord.User=None):
    if await Res.print_brix(comando="nossabraixen",interaction=interaction):
        return
    try:
        await interaction.response.defer()

        if not cara1.avatar or not cara2.avatar or not cara3.avatar:
            await interaction.followup.send(Res.trad(interaction=interaction,str="message_erro_apimemes_notavatar")) 
            return

        membro_image_data = await cara1.avatar.replace(size=512, format="png").read()
        membro_bytesio = io.BytesIO(membro_image_data)
        avatar1 = Image.open(membro_bytesio)
        avatar1 = avatar1.resize((90,90))

        membro_image_data = await cara2.avatar.replace(size=512, format="png").read()
        membro_bytesio = io.BytesIO(membro_image_data)
        avatar2 = Image.open(membro_bytesio)
        avatar2 = avatar2.resize((90,90))

        membro_image_data = await cara3.avatar.replace(size=512, format="png").read()
        membro_bytesio = io.BytesIO(membro_image_data)
        avatar3 = Image.open(membro_bytesio)
        avatar3 = avatar3.resize((90,90))

        fundo = Image.new("RGB",(500,500),"white")
        meme = Image.open("src/assets/imagens/memes/3-caras-e-uma-braixen.png")

        mascaraavatar = Image.open(f"src/assets/imagens/icons/recorte-redondo.png")
        mascaraavatar = mascaraavatar.resize((90,90))

        fundo.paste(meme,(0,0))
        fundo.paste(avatar1,(37,110),mascaraavatar)
        fundo.paste(avatar2,(195,95),mascaraavatar)
        fundo.paste(avatar3,(375,105),mascaraavatar)
        if braixen is None:
            buffer = io.BytesIO()
            fundo.save(buffer,format="PNG")
            buffer.seek(0)
            await interaction.followup.send(file=discord.File(fp=buffer,filename="nossa braixen.png"))
        else:
            if not braixen.avatar:
                await interaction.followup.send(Res.trad(interaction=interaction,str="message_erro_apimemes_notavatar")) 
                return
            membro_image_data = await braixen.avatar.replace(size=512, format="png").read()
            membro_bytesio = io.BytesIO(membro_image_data)
            avatar4 = Image.open(membro_bytesio)
            avatar4 = avatar4.resize((80,80))
            mascara4 = Image.open(f"src/assets/imagens/icons/recorte-redondo.png")
            mascara4 = mascara4.resize((80,80))
            fundo.paste(avatar4,(220,234),mascara4)
            buffer = io.BytesIO()
            fundo.save(buffer,format="PNG")
            buffer.seek(0)
            await interaction.followup.send(file=discord.File(fp=buffer,filename="nossa braixen.png"))
    except Exception as e:
        await Res.erro_brix_embed(interaction,str="message_erro_apimemes",e=e,comando="nossabraixen")



















#criador de memes Braixen ABRAÇO
  @meme.command(name="braixen-hug",description='🤡⠂Seja abraçado por uma braixen.')
  @app_commands.describe(membro="Indique alguem para ser abraçado")
  async def braixenhug(self,interaction: discord.Interaction, membro:discord.User):
    if await Res.print_brix(comando="braixenhug",interaction=interaction):
        return
    
    try:
        await interaction.response.defer()
        fundo = Image.new("RGB",(750,750),"white")
        if not membro.avatar:
            await interaction.followup.send(Res.trad(interaction=interaction,str="message_erro_apimemes_notavatar")) 
            return
        
        membro_image_data = await membro.avatar.replace(size=512, format="png").read()
        membro_bytesio = io.BytesIO(membro_image_data)
        membro = Image.open(membro_bytesio)
        membro = membro.resize((170,170))
        meme = Image.open("src/assets/imagens/memes/braixen-hug.png")
        fundo.paste(membro,(290,260))
        fundo.paste(meme,(0,0),meme)
        buffer = io.BytesIO()
        fundo.save(buffer,format="PNG")
        buffer.seek(0)
        await interaction.followup.send(file=discord.File(fp=buffer,filename="braixen hug.png"))
    except Exception as e:
        await Res.erro_brix_embed(interaction,str="message_erro_apimemes",e=e,comando="braixenhug")



















#criador de memes Braixen TABLET
  @meme.command(name="braixen-tablet",description='🤡⠂Oque Braixen viu em seu tablet?')
  @app_commands.describe(imagem="Anexe uma imagem para virar meme", url_imagem="URL de uma imagem", avatar_usuario="Use o avatar de um usuário")
  async def braixentablet(self,interaction: discord.Interaction, imagem: discord.Attachment = None, url_imagem: str = None, avatar_usuario: discord.User = None):
    if await Res.print_brix(comando="braixentablet",interaction=interaction):
        return
    
    try:
        await interaction.response.defer()
        fundo = Image.new("RGB",(593,900),"white")
        imagem_pil = await pegar_imagem(interaction, imagem, url_imagem, avatar_usuario)
        if not imagem_pil:
            await interaction.followup.send(Res.trad(interaction=interaction,str="message_erro_apimemes_notmidia"), ephemeral=True)
            return
        
        imagem_pil = imagem_pil.resize((495,380))
        meme = Image.open("src/assets/imagens/memes/braixen tablet.png")
        fundo.paste(imagem_pil,(50,478))
        fundo.paste(meme,(0,0),meme)
        buffer = io.BytesIO()
        fundo.save(buffer,format="PNG")
        buffer.seek(0)
        await interaction.followup.send(file=discord.File(fp=buffer,filename="braixen e seu tablet.png"))
    except Exception as e:
        await Res.erro_brix_embed(interaction,str="message_erro_apimemes",e=e,comando="braixentablet")






















#criador de memes Braixen TRISTE
  @meme.command(name="braixen-triste",description='🤡⠂Oque deixou Braixen triste?')
  @app_commands.describe(imagem="Anexe uma imagem para virar meme", url_imagem="URL de uma imagem", avatar_usuario="Use o avatar de um usuário")
  async def braixentriste(self,interaction: discord.Interaction, imagem: discord.Attachment = None, url_imagem: str = None, avatar_usuario: discord.User = None):
    if await Res.print_brix(comando="braixentriste",interaction=interaction):
        return
    
    try:
        await interaction.response.defer()
        fundo = Image.new("RGB",(460,281),"white")
        imagem_pil = await pegar_imagem(interaction, imagem, url_imagem, avatar_usuario)
        if not imagem_pil:
            await interaction.followup.send(Res.trad(interaction=interaction,str="message_erro_apimemes_notmidia"), ephemeral=True)
            return
        imagem_pil = imagem_pil.resize((460,281))
        meme = Image.open("src/assets/imagens/memes/braixen-sad.png")
        fundo.paste(imagem_pil,(0,0))
        fundo.paste(meme,(0,0),meme)
        buffer = io.BytesIO()
        fundo.save(buffer,format="PNG")
        buffer.seek(0)
        await interaction.followup.send(file=discord.File(fp=buffer,filename="braixen sad.png"))
    except Exception as e:
        await Res.erro_brix_embed(interaction,str="message_erro_apimemes",e=e,comando="braixentriste")





















#criador de memes Braixen SMASH
  @meme.command(name="braixen-smash",description='🤡⠂desça a porrada em alguém com raiva.')
  @app_commands.describe(membro="Indique alguem para ser socado")
  async def braixensmash(self,interaction: discord.Interaction, membro:discord.User):
    if await Res.print_brix(comando="braixensmash",interaction=interaction):
        return
   
    try:
        await interaction.response.defer()
        fundo = Image.new("RGB",(600,332),"white")
        if not membro.avatar:
                await interaction.followup.send(Res.trad(interaction=interaction,str="message_erro_apimemes_notavatar")) 
                return
        membro_image_data = await membro.avatar.replace(size=512, format="png").read()
        membro_bytesio = io.BytesIO(membro_image_data)
        membro = Image.open(membro_bytesio)
        membro = membro.resize((230,230))
        membro = membro.rotate(-10)
        meme = Image.open("src/assets/imagens/memes/braixen-smash.png")
        fundo.paste(membro,(410,32))          
        fundo.paste(meme,(0,0),meme)
        buffer = io.BytesIO()
        fundo.save(buffer,format="PNG")
        buffer.seek(0)
        await interaction.followup.send(file=discord.File(fp=buffer,filename="braixen smash.png"))
    except Exception as e:
        await Res.erro_brix_embed(interaction,str="message_erro_apimemes",e=e,comando="braixensmash")






















#criador de memes Braixen Sleep
  @meme.command(name="braixen-sleep",description='🤡⠂Oque Braixen está sonhando?')
  @app_commands.describe(imagem="Anexe uma imagem para virar meme", url_imagem="URL de uma imagem", avatar_usuario="Use o avatar de um usuário")
  async def braixensleep(self,interaction: discord.Interaction, imagem: discord.Attachment = None, url_imagem: str = None, avatar_usuario: discord.User = None):
    if await Res.print_brix(comando="braixensleep",interaction=interaction):
        return
    
    try:
        await interaction.response.defer()
        fundo = Image.new("RGB",(558,787),"white")
        imagem_pil = await pegar_imagem(interaction, imagem, url_imagem, avatar_usuario)
        if not imagem_pil:
            await interaction.followup.send(Res.trad(interaction=interaction,str="message_erro_apimemes_notmidia"), ephemeral=True)
            return
        
        imagem_pil = imagem_pil.resize((243,274))
        meme = Image.open("src/assets/imagens/memes/braixen-sleep.png")
        fundo.paste(imagem_pil,(0,0))
        fundo.paste(meme,(0,0),meme)
        buffer = io.BytesIO()
        fundo.save(buffer,format="PNG")
        buffer.seek(0)
        await interaction.followup.send(file=discord.File(fp=buffer,filename="braixen Sleep.png"))
    except Exception as e:
        await Res.erro_brix_embed(interaction,str="message_erro_apimemes",e=e,comando="braixensleep")

























#Criador de memes Braixen citação famosa
  @meme.command(name="braixen-citacao-famosa",description='🤡⠂Uma citação que Braixen diria.')
  @app_commands.describe(variante="Selecione uma variante...",imagem="envie uma imagem que será anexada",frase="Frase marcante de no Máximo 72 caracteres",ia = "Peça algo gerado por Inteligencia artificial")
  @app_commands.choices(variante=[app_commands.Choice(name="armado olho fechado", value="gun"),app_commands.Choice(name="armado olho aberto", value="gun2")])
  async def braixencitacao(self,interaction: discord.Interaction,variante:app_commands.Choice[str], imagem: discord.Attachment=None, frase: str = None ,ia: str=None):
    if await Res.print_brix(comando="braixencitacao",interaction=interaction):
        return
    
    try:
        await interaction.response.defer()
        if frase is not None:
            if len(frase) > 72:
                await interaction.followup.send(f"Limite de caracteres atingido, você enviou {len(frase)} caracteres", ephemeral = True)
                return
            
        if ia is not None:
            Check = await userpremiumcheck(interaction)
            if Check == False:
                permitido, tempo_restantante = await verificar_cooldown(interaction, "braixencitacao", 120)
                if not permitido:
                    await interaction.followup.send(Res.trad(interaction=interaction, str='message_ia_cooldown_premium'))
                    return
            frase = await generate_response_with_text(f"{ia} que braixen diria limite 60 caracteres totais")
            frase.replace('"','')
            
        if (variante.value == 'gun'):
                meme = Image.open("src/assets/imagens/memes/braixen-citacao-gun.png")
        if (variante.value == 'gun2'):
                meme = Image.open("src/assets/imagens/memes/braixen-citacao-gun-olhoaberto.png")
        fonte = ImageFont.truetype("src/assets/font/Hey Comic.ttf",30)
        fontegrande = ImageFont.truetype("src/assets/font/Hey Comic.ttf",50)
        if imagem is None:
            fundo = Image.new("RGB",(835,367),"white")
            fundo.paste(meme,(0,0))
            fundodraw = ImageDraw.Draw(fundo)
            fundodraw.text((35,30),f"Citação\nFamosa",font = fontegrande)
            fundodraw.multiline_text((30,200),f"\n".join(textwrap.wrap(f"'{frase}'",width=22)),font=fonte,spacing=0,align ="right")
            fundodraw.text((205,325),f"-Braixen",font = fonte)

        else:
            fundo = Image.new("RGB",(835,870),"white")
            arquivo = await imagem.read()
            imagem = Image.open(io.BytesIO(arquivo))
            imagem = imagem.resize((835,502))
            fundo.paste(imagem,(0,0))
            fundo.paste(meme,(0,502))

            fundodraw = ImageDraw.Draw(fundo)
            fundodraw.text((35,540),f"Citação\nFamosa",font = fontegrande)
            for i in range(24, len(frase), 24):
                frase = frase[:i] + "\n" + frase[i:]
            fundodraw.multiline_text((30,700),f"'{frase}'",font=fonte,spacing=0,align ="right")
            fundodraw.text((205,830),f"-Braixen",font = fonte)

        buffer = io.BytesIO()
        fundo.save(buffer,format="PNG")
        buffer.seek(0)
        await interaction.followup.send(file=discord.File(fp=buffer,filename="braixen citacao.png"))
    except Exception as e:
        await Res.erro_brix_embed(interaction,str="message_erro_apimemes",e=e,comando="braixencitacao")


























#Criador de memes Braixen citação famosa
  @meme.command(name="braixen-placa",description='🤡⠂Braixen e sua placa coloque algo nela.')
  @app_commands.describe(frase="Frase marcante de no Máximo 72 caracteres",ia = "Peça algo gerado por Inteligencia artificial",imagem="Anexe uma imagem para virar meme", url_imagem="URL de uma imagem", avatar_usuario="Use o avatar de um usuário")
  async def braixensays(self,interaction: discord.Interaction, frase: str=None, ia:str=None, imagem: discord.Attachment = None, url_imagem: str = None, avatar_usuario: discord.User = None):
    if await Res.print_brix(comando="braixensays",interaction=interaction):
        return
    try:
        await interaction.response.defer()
        ignoreimage = False
        if frase is not None:
            ignoreimage = True
            if len(frase) > 72:
                await interaction.followup.send(f"Limite de caracteres atingido, você enviou {len(frase)} caracteres", ephemeral = True)
                return
            
        if ia is not None:
            ignoreimage = True
            Check = await userpremiumcheck(interaction)
            if Check == False:
                permitido, tempo_restantante = await verificar_cooldown(interaction, "braixensays", 120)
                if not permitido:
                    await interaction.followup.send(Res.trad(interaction=interaction, str='message_ia_cooldown_premium'))
                    return
            frase = await generate_response_with_text(f"{ia} que braixen diria limite 68 caracteres totais")
        if ignoreimage is True:
            meme = Image.open("src/assets/imagens/memes/braixen-says.png")
            fundo = Image.new("RGBA", meme.size, (0, 0, 0, 0))
            fundo.paste(meme,(0,0),meme)
            fonte = ImageFont.truetype("src/assets/font/Hey Comic.ttf",24)

            frase_wrapped = "\n".join(textwrap.wrap(frase.replace('"',''), width=17))

                # Criar uma nova imagem para o texto, com transparência
            text_img = Image.new("RGBA", (fundo.width, fundo.height), (0, 0, 0, 0))
            text_draw = ImageDraw.Draw(text_img)
            text_draw.multiline_text((0, 0), frase_wrapped, font=fonte, fill="black", spacing=0, align="left")
                
            text_img = text_img.rotate(-9, expand=1)
            bbox = text_img.getbbox()
            text_img = text_img.crop(bbox)
                
                # Posição do texto na imagem final
            text_pos = (195, 265)
            fundo.paste(text_img, text_pos, text_img)

        else:
            meme = Image.open("src/assets/imagens/memes/braixen-says-imagem.png")
            mask = Image.open("src/assets/imagens/memes/braixen-says-imagem-mask.png")
            fundo = Image.new("RGBA", meme.size, (0, 0, 0, 0))
            imagem_pil = await pegar_imagem(interaction, imagem, url_imagem, avatar_usuario)
            if not imagem_pil:
                await interaction.followup.send(Res.trad(interaction=interaction,str="message_erro_apimemes_notmidia"), ephemeral=True)
                return
            imagem_pil = imagem_pil.resize((255,180)).rotate(-9,expand=True)
            fundo.paste(imagem_pil,(160,250))
            fundo.paste(Image.new("RGBA", meme.size, (0, 0, 0, 0)),(0,0),mask)
            fundo.paste(meme,(0,0),meme)

        buffer = io.BytesIO()
        fundo.save(buffer,format="PNG")
        buffer.seek(0)
        await interaction.followup.send(file=discord.File(fp=buffer,filename="braixen says.png"))

    except Exception as e:
        await Res.erro_brix_embed(interaction,str="message_erro_apimemes",e=e,comando="braixensays")
























#criador de memes Braixen Sleep
  @meme.command(name="braixen-drake",description='🤡⠂Braixen ao melhor estilo drake')
  @app_commands.describe(img_1="Anexe uma imagem para virar meme", img_2="Anexe uma imagem para virar meme",url_1="URL de uma imagem", avatar_1="Use o avatar de um usuário",url_2="URL de uma imagem", avatar_2="Use o avatar de um usuário")
  async def braixendrake(self,interaction: discord.Interaction, img_1: discord.Attachment = None, url_1: str = None, avatar_1: discord.User = None,img_2: discord.Attachment = None, url_2: str = None, avatar_2: discord.User = None):
    if await Res.print_brix(comando="braixensleep",interaction=interaction):
        return

    try:
        await interaction.response.defer()
        fundo = Image.new("RGB",(534,534),"white")
        meme = Image.open("src/assets/imagens/memes/braixen_drake_meme.png")
        img1 = await pegar_imagem(interaction, img_1, url_1, avatar_1,0)
        img2 = await pegar_imagem(interaction, img_2, url_2, avatar_2,1)
        if not img1 or not img2:
            await interaction.followup.send(Res.trad(interaction=interaction,str="message_erro_apimemes_notmidia"), ephemeral=True)
            return
        img1 = img1.resize((265,264))
        img2 = img2.resize((265,264))
        fundo.paste(meme,(0,0))
        fundo.paste(img1,(269,0))
        fundo.paste(img2,(269,270))
        
        buffer = io.BytesIO()
        fundo.save(buffer,format="PNG")
        buffer.seek(0)
        await interaction.followup.send(file=discord.File(fp=buffer,filename="braixen Drake.png"))
    except Exception as e:
        await Res.erro_brix_embed(interaction,str="message_erro_apimemes",e=e,comando="braixendrake")



















#criador de memes LOONA FOTO
#  @meme.command(name="loona",description='🤡⠂Oque Loona viu?')
#  @app_commands.describe(imagem="Anexe uma imagem para virar meme...",variante="Selecione uma variante...")
#  @app_commands.choices(variante=[app_commands.Choice(name="normal", value="normal"),app_commands.Choice(name="raiva", value="raiva"),])
#  async def loonaimg(self,interaction: discord.Interaction, imagem: discord.Attachment, variante:app_commands.Choice[str]):
#    if await Res.print_brix(comando="loonaimg",interaction=interaction):
        #return
#    if interaction.guild is None:
#        await interaction.response.send_message(Res.trad(interaction,str="message_erro_onlyservers"),delete_after=10,ephemeral=True)
#    else:
#        try:
##            await interaction.response.defer()
 #           if (variante.value == 'normal'):
 #               fundo = Image.new("RGB",(500,563),"white")
 #               arquivo = await imagem.read()
 #               imagem = Image.open(io.BytesIO(arquivo))
  #              imagem = imagem.resize((195,144))
   #             meme = Image.open("src/assets/imagens/memes/loona foto.png")
  #              fundo.paste(imagem,(278,84))
  #              fundo.paste(meme,(0,0),meme)
  #              buffer = io.BytesIO()
  #              fundo.save(buffer,format="PNG")
  #              buffer.seek(0)
  #              await interaction.followup.send(file=discord.File(fp=buffer,filename="Loona Foto.png"))
  #          elif (variante.value == 'raiva'):
  #              fundo = Image.new("RGB",(502,310),"white")
  #              arquivo = await imagem.read()
  #              imagem = Image.open(io.BytesIO(arquivo))
  #              imagem = imagem.resize((227,185))
  #              imagem = imagem.rotate(-2.73)
  #              meme = Image.open("src/assets/imagens/memes/loona angry foto.png")
  #              fundo.paste(imagem,(260,74))
  #              fundo.paste(meme,(0,0),meme)
  #              buffer = io.BytesIO()
  #              fundo.save(buffer,format="PNG")
  #              buffer.seek(0)
  #              await interaction.followup.send(file=discord.File(fp=buffer,filename="Loona angry Foto.png"))
  #      except Exception as e:
  #          await Res.erro_brix_embed(interaction,str="message_erro_apimemes",e=e)








async def setup(client:commands.Bot) -> None:
  await client.add_cog(diversao(client))