import discord,os,asyncio,requests,random,io,textwrap,time
from discord.ext import commands,tasks
from discord import app_commands
from discord.voice_client import VoiceClient 
from typing import List
import e621py_wrapper as e621 #IMPORTAÇÂO E621
from modulos.connection.database import BancoServidores
from modulos.essential.respostas import Res
from modulos.essential.usuario import userpremiumcheck , verificar_cooldown
from modulos.essential.gasmii import generate_response_with_text
from modulos.essential.imagem import pegar_imagem
from PIL import Image, ImageFont, ImageDraw, ImageOps #IMPORTAÇÂO Py PIL IMAGEM
Image.MAX_IMAGE_PIXELS = None

id_chatBH = int(os.getenv('id_chatBH'))


try:
    #login e621
    time.sleep(5)  # Espera de 5 segundos
    e621api = e621.client()
    e621api.login(os.getenv("E621_Login"), os.getenv("E621_Api"))
    print("🦊  -  Login e621 bem-sucedido!")
except:
    print(f"❌ - Falha no login do e621")




#API E621 VIA SLASH
async def buscae621slash(interaction,quantidade,item):
    if await Res.print_brix(comando="buscare621slash",interaction=interaction,condicao=item):
        return
    permitido, tempo_restantante = await verificar_cooldown(interaction, "buscae621slash", 1)
    if not permitido:
        await interaction.response.send_message( Res.trad(interaction=interaction, str="message_erro_cooldown").format(tempo_restantante),  ephemeral=True  )
        return
    try:
        await interaction.response.defer()
        #await asyncio.sleep(0.1)
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
                    filtro = "rating:s,urine,gore,feces"
                    messagefooter = Res.trad(interaction=interaction,str='message_APIE621_footer')
                else:
                    busca = f"{item} rating:s"
                    filtro = "rating:e,rating:q,urine,gore,feces,breasts,genitals,butt,diaper"
                    messagefooter = Res.trad(interaction=interaction,str='message_APIE926_footer')
            except:
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
                view = discord.ui.View()
                button = discord.ui.Button(style=discord.ButtonStyle.blurple,label=Res.trad(interaction=interaction,str="botão_abrir_navegador"),url=f"https://e621.net/posts/{post['id']}")
                view.add_item(item=button)
                await interaction.followup.send(f"[{item} - {post['tags']['artist'][0] if post['tags']['artist'] else '-'}]({post['file']['url']})\n-# {messagefooter}",view=view)
        else:await interaction.followup.send(Res.trad(interaction=interaction,str="message_erro_E621_limit").format(quantidade),ephemeral = True)    
    except Exception as e:
        print(e)
        await interaction.followup.send(Res.trad(interaction=interaction,str="message_erro_APIE621"),ephemeral = True)


#API ANIMAL RANDOMICO VIA SLASH
async def animalrandomico(interaction, quantidade, apirandom):
    try:
        await interaction.response.defer()
        if quantidade is None:
            quantidade = 1
        if quantidade <= 5:
            for _ in range(quantidade):
                r = requests.get(apirandom)
                res_list = r.json()
                for res in res_list:
                    if 'url' in res:
                        image_url = res['url']
                        if quantidade > 1:
                            await asyncio.sleep(1)
                            await interaction.followup.send(image_url)
                        else:
                            await interaction.followup.send(image_url)
                    else:
                        await interaction.followup.send(Res.trad(interaction=interaction,str="message_erro_apirandomica_url"), ephemeral=True)
        else:
            await interaction.followup.send(Res.trad(interaction=interaction,str="message_erro_apirandomica_limit").format(quantidade), ephemeral=True)
    except:
        await interaction.followup.send(Res.trad(interaction=interaction,str="message_erro_apirandomica"), ephemeral=True)









class diversao(commands.Cog):
  def __init__(self, client: commands.Bot):
    self.client = client
     # Cache para contar erros de cada registro: chave = ID do servidor, valor = contador
    self.autophox_error_count = {}
    



  @commands.Cog.listener()
  async def on_ready(self):
    print("🎲  -  Modúlo Diversao carregado.")
    if not self.autophox.is_running():
        await asyncio.sleep(300) #300
        self.autophox.start()
  




  @commands.Cog.listener()
  async def on_message(self,message):

        if message.author == self.client.user or message.author.bot:
            return
        
        elif message.guild is None:
            return

        elif "kyu" in message.content.lower() and message.author != self.client.user and message.channel.id != id_chatBH:
            async with message.channel.typing():
                await asyncio.sleep(0.5)
            #await message.reply(random.choice(responsekyu))
            await message.reply(random.choice(Res.trad(guild=message.guild.id,str='responsekyu')))
        





    #LOOP DE POSTAGEM DO AUTOPHOX
  @tasks.loop(hours=1) # hours=1
  async def autophox(self):
    print("🦊 - rodando Auto Phox")
    try:
        pesquisa = ['fennekin','braixen','delphox']
        item = random.choice(pesquisa)
        page = random.randint(1,5)
        r=e621api.posts.search(tags=f"{item} rating:s -breasts -genitals -butt -diaper",blacklist="rating:e,rating:q,urine,gore,feces,breasts,genitals,butt,diaper" ,limit=200 ,page=page,ignorepage=True)
        #post = r[random.randint(1,20)] #default 1,20
        post = random.choice(r)
        filtro = {"autophox": {"$exists":True}}
        canais = BancoServidores.select_many_document(filtro)
        for linha in canais:
            try:
                servidor = await self.client.fetch_guild(linha['_id'])
                canal = await self.client.fetch_channel(linha['autophox'])
                print(f"enviando autophox em {servidor.name}") 
                view = discord.ui.View()
                button = discord.ui.Button(style=discord.ButtonStyle.blurple,label=Res.trad(guild=servidor.id,str="botão_abrir_navegador"),url=f"https://e621.net/posts/{post['id']}")
                view.add_item(item=button)
                await canal.send(f"[{post['tags']['artist'][0]}]({post['file']['url']})\n-# {Res.trad(guild=servidor.id,str='message_autophox_footer')}",view=view)

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
                
                #item = {"autophox":linha['autophox']}
                #BancoServidores.delete_field(linha['_id'],item)

    except Exception as e:
        print(f"erro na api, tentarei novamente depois, confira o erro gerado: {e}")
      







#------------------COMANDOS-------------------------------

  #Comando AutoPhox 
  @app_commands.command(name="autophox", description="🦊⠂Ative a postagem automática de imagens.")
  @app_commands.describe(opcao="Selecione uma opção...")
  @app_commands.choices(opcao=[app_commands.Choice(name="ativado",value="Ativou"),app_commands.Choice(name="desativado", value="Desativou"),])
  async def optionautophox(self, interaction: discord.Interaction,opcao:app_commands.Choice[str]):
    if await Res.print_brix(comando="autophox",interaction=interaction):
        return
    await interaction.response.defer()
    if interaction.guild is None:
        await interaction.followup.send(Res.trad(interaction=interaction,str="message_erro_onlyservers"))
    elif interaction.permissions.manage_guild:
        if (opcao.value == "Ativou"):
            item = {"autophox": interaction.channel.id}
            BancoServidores.update_document(interaction.guild.id,item)
        elif (opcao.value == "Desativou"):
            item = {"autophox":interaction.channel.id}
            BancoServidores.delete_field(interaction.guild.id,item)
        await interaction.followup.send(Res.trad(interaction=interaction,str="message_autophox_notificacao").format(opcao.name))
    else:
        await interaction.followup.send(Res.trad(interaction=interaction,str="message_erro"),ephemeral=True)













#GRUPO DE COMANDOS DE KYU DO BOT 
  kyu=app_commands.Group(name="kyu",description="Comandos de voz do Brix.")

#COMANDO JOIN CANAL DE VOZ
  @kyu.command(name="conectar",description='🔈⠂Faz Brix se conectar a um canal.')
  async def join(self,interaction:discord.Integration):
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
  async def leave(self,interaction:discord.Integration):
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
  @app_commands.choices(quantidade=[app_commands.Choice(name=f"{i}", value=i) for i in range(1, 16)])
  @app_commands.describe(quantidade="quantidade de imagens, limite 15")
  async def braixen(self,interaction: discord.Interaction,quantidade:app_commands.Choice[int]=None):
    item = "braixen"
    await buscae621slash(interaction,quantidade,item)


#COMANDO FENNEKIN SLASH
  @img.command(name="fennekin",description='🎨⠂imagem de Fennekin.')
  @app_commands.choices(quantidade=[app_commands.Choice(name=f"{i}", value=i) for i in range(1, 16)])
  @app_commands.describe(quantidade="quantidade de imagens, limite 15")
  async def fennekin(self,interaction: discord.Interaction,quantidade:app_commands.Choice[int]=None):
    item = "fennekin"
    await buscae621slash(interaction,quantidade,item)


#COMANDO DELPHOX SLASH
  @img.command(name="delphox",description='🎨⠂imagem de Delphox.')
  @app_commands.choices(quantidade=[app_commands.Choice(name=f"{i}", value=i) for i in range(1, 16)])
  @app_commands.describe(quantidade="quantidade de imagens, limite 15")
  async def delphox(self,interaction: discord.Interaction,quantidade:app_commands.Choice[int]=None):
    item = "delphox"
    await buscae621slash(interaction,quantidade,item)


#COMANDO LUCARIO SLASH
  @img.command(name="lucario",description='🎨⠂imagem de Lucario.')
  @app_commands.choices(quantidade=[app_commands.Choice(name=f"{i}", value=i) for i in range(1, 16)])
  @app_commands.describe(quantidade="quantidade de imagens, limite 15")
  async def lucario(self,interaction: discord.Interaction,quantidade:app_commands.Choice[int]=None):
    item = "lucario"
    await buscae621slash(interaction,quantidade,item)


#COMANDO MEOWSCARADA SLASH
  @img.command(name="meowscarada",description='🎨⠂imagem de Meowscarada.')
  @app_commands.choices(quantidade=[app_commands.Choice(name=f"{i}", value=i) for i in range(1, 16)])
  @app_commands.describe(quantidade="quantidade de imagens, limite 15")
  async def meowscarada(self,interaction: discord.Interaction,quantidade:app_commands.Choice[int]=None):
    item = "meowscarada"
    await buscae621slash(interaction,quantidade,item)


#COMANDO GARDEVOIR SLASH
  @img.command(name="gardevoir",description='🎨⠂imagem de Gardevoir.')
  @app_commands.choices(quantidade=[app_commands.Choice(name=f"{i}", value=i) for i in range(1, 16)])
  @app_commands.describe(quantidade="quantidade de imagens, limite 15")
  async def gardevoir(self,interaction: discord.Interaction,quantidade:app_commands.Choice[int]=None):
    item = "gardevoir"
    await buscae621slash(interaction,quantidade,item)


#COMANDO CINDERACE SLASH
  @img.command(name="cinderace",description='🎨⠂imagem de Cinderace.')
  @app_commands.choices(quantidade=[app_commands.Choice(name=f"{i}", value=i) for i in range(1, 16)])
  @app_commands.describe(quantidade="quantidade de imagens, limite 15")
  async def cinderace(self,interaction: discord.Interaction,quantidade:app_commands.Choice[int]=None):
    item = "cinderace"
    await buscae621slash(interaction,quantidade,item)


#COMANDO PRIMARINA SLASH
  @img.command(name="primarina",description='🎨⠂imagem de Primarina.')
  @app_commands.choices(quantidade=[app_commands.Choice(name=f"{i}", value=i) for i in range(1, 16)])
  @app_commands.describe(quantidade="quantidade de imagens, limite 15")
  async def cinderace(self,interaction: discord.Interaction,quantidade:app_commands.Choice[int]=None):
    item = "primarina"
    await buscae621slash(interaction,quantidade,item)

  

  #COMANDO PRIMARINA SLASH
  @img.command(name="e621",description='🎨⠂Procure algo no e621.')
  @app_commands.choices(quantidade=[app_commands.Choice(name=f"{i}", value=i) for i in range(1, 16)])
  @app_commands.describe(tag="indique uma tag",quantidade="quantidade de imagens, limite 15")
  async def e621(self,interaction: discord.Integration,tag:str,quantidade:app_commands.Choice[int]=None):
    await buscae621slash(interaction,quantidade,tag)
     

  @e621.autocomplete("tag")
  async def valor_autocomplete(self, interaction: discord.Interaction, current: str ) -> List[app_commands.Choice[int]]:
    #FAZ O REQUESTS DA PESQUISA DO USUARIO
    r = requests.get(        "https://e621.net/tags/autocomplete.json",        params={"search[name_matches]": current},        headers={"User-Agent": "DiscordBot/1.0 (by YourUsername on e621)"}    , timeout=1).json()
    if "error" in r: #CASO APRESENTE ERRO RETORNA UMA LISTA GENERICA
      r =  e621api.tags.search(current)
    sugestao = [] #MONTADOR DE SUGESTÔES
    try:
      for tag in r:
        sugestao.append(
            app_commands.Choice(
                name=f"{tag['name']} ({tag['post_count']})",  # Acessando o nome da tag
                value=tag['name'],   # Acessando o ID da tag
            )
        )
    except:
        sugestao = [] #MONTADOR DE SUGESTÔES
    return sugestao [:25]















  #GRUPO DE COMANDOS DE IMAGENS RANDOMICAS BOT 
  gruporand=app_commands.Group(name="randomico",description="Comandos de imagens randomicos.",allowed_installs=app_commands.AppInstallationType(guild=True,user=True),allowed_contexts=app_commands.AppCommandContext(guild=True, dm_channel=False, private_channel=False))


#COMANDO RAPOSA RANDOMICA SLASH
  @gruporand.command(name="raposa",description='🎨⠂imagem aleatoria de uma raposa.')
  @app_commands.describe(quantidade="quantidade de imagens, limite 5")
  async def randraposa(self,interaction: discord.Interaction,quantidade:int=None):
    if await Res.print_brix(comando="randraposa",interaction=interaction):
        return
    try:
        if quantidade == None:
            quantidade = 1
        if quantidade <= 5:
            i = 0
            while (i<quantidade):
                r= requests.get("https://randomfox.ca/floof/")
                res = r.json()
                i=i+1
                if i >1:
                    await asyncio.sleep(1)
                    await interaction.followup.send(res['image'])
                else:await interaction.response.send_message(res['image'])
        else:await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_apirandomica_limit").format(quantidade),delete_after=10,ephemeral = True)    
    except:
        await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_apirandomica"),delete_after=10,ephemeral = True)


#COMANDO GATO RANDOMICO SLASH
  @gruporand.command(name="gato",description='🎨⠂imagem aleatoria de um gato.')
  @app_commands.describe(quantidade="quantidade de imagens, limite 5")
  async def randgato(self,interaction: discord.Interaction,quantidade:int=None):
    if await Res.print_brix(comando="randgato",interaction=interaction):
        return
    apirandom = "https://api.thecatapi.com/v1/images/search"
    await animalrandomico(interaction,quantidade,apirandom)

#COMANDO CACHORRO RANDOMICO SLASH
  @gruporand.command(name="cachorro",description='🎨⠂imagem aleatoria de um cachorro.')
  @app_commands.describe(quantidade="quantidade de imagens, limite 5")
  async def randcachorro(self,interaction: discord.Interaction,quantidade:int=None):
    if await Res.print_brix(comando="randcachorro",interaction=interaction):
        return
    apirandom = "https://api.thedogapi.com/v1/images/search"
    await animalrandomico(interaction,quantidade,apirandom)

















#--------------------------------  SETOR DOS MEMES ------------------------------------
  

#GRUPO DE COMANDOS DE MEMES DO BOT 
  meme=app_commands.Group(name="meme",description="Comandos de geração de imangens do Brix.",allowed_installs=app_commands.AppInstallationType(guild=True,user=True),allowed_contexts=app_commands.AppCommandContext(guild=True, dm_channel=True, private_channel=True))

#criador de memes Braixen REAL
  @meme.command(name="braixen-real",description='🤡⠂Oque Vinicius está segurando?')
  @app_commands.describe(imagem="Anexe uma imagem para virar meme", url_imagem="URL de uma imagem", avatar_usuario="Use o avatar de um usuário")
  async def braixenrealmeme(self,interaction: discord.Interaction, imagem: discord.Attachment = None, url_imagem: str = None, avatar_usuario: discord.User = None):
    if await Res.print_brix(comando="braixenrealmeme",interaction=interaction):
        return
    print(f"Comando /meme braixenreal - User {interaction.user.name}")
    if interaction.guild is None:
        await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyservers"),delete_after=10,ephemeral=True)
    else:
        try:
            await interaction.response.defer()
            imagem_pil = await pegar_imagem(interaction, imagem, url_imagem, avatar_usuario)
            if not imagem_pil:
                await interaction.followup.send(Res.trad(interaction=interaction,str="message_erro_apimemes_notmidia"), ephemeral=True)
                return

            fundo = Image.new("RGB",(362,480),"white")

            imagem_pil  = imagem_pil.resize((224,153))
            meme = Image.open("imagens/memes/Vinicius_Segurando_Cartao_Sem_Fundo.png")
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
    if interaction.guild is None:
        await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyservers"),delete_after=10,ephemeral=True)
    else:
        try:
            await interaction.response.defer()
            fundo = Image.new("RGB",(800,751),"white")
            imagem_pil = await pegar_imagem(interaction, imagem, url_imagem, avatar_usuario)
            if not imagem_pil:
                await interaction.followup.send(Res.trad(interaction=interaction,str="message_erro_apimemes_notmidia"), ephemeral=True)
                return
            
            imagem_pil = imagem_pil.resize((345,245))
            meme = Image.open("imagens/memes/braixen monitor.png")
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
    if interaction.guild is None:
        await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyservers"),delete_after=10,ephemeral=True)
    else:
        try:
            await interaction.response.defer()
            
            
            if not interaction.user.avatar or not rival.avatar:
                await interaction.followup.send(Res.trad(interaction=interaction,str="message_erro_apimemes_notavatar")) 
                return
            
            interaction_image_data = await interaction.user.avatar.replace(size=512, format="png").read()
            rival_image_data = await rival.avatar.replace(size=512, format="png").read()

            mascaraavatar = Image.open(f"imagens/icons/recorte-redondo.png")
            mascaraavatar = mascaraavatar.resize((75,75))

            membro_bytesio = io.BytesIO(interaction_image_data)
            avatar1 = Image.open(membro_bytesio)
            avatar1 = avatar1.resize((75,75))
            
            membro_bytesio = io.BytesIO(rival_image_data)
            avatar2 = Image.open(membro_bytesio)
            avatar2 = avatar2.resize((75,75))

            fundo = Image.new("RGB",(440,550),"white")
            meme = Image.open("imagens/memes/don_t_touch_her.png")
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
    if interaction.guild is None:
        await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyservers"),delete_after=10,ephemeral=True)
    else:
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
            meme = Image.open("imagens/memes/3-caras-e-uma-braixen.png")

            mascaraavatar = Image.open(f"imagens/icons/recorte-redondo.png")
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
                mascara4 = Image.open(f"imagens/icons/recorte-redondo.png")
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
    if interaction.guild is None:
        await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyservers"),delete_after=10,ephemeral=True)
    else:
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
            meme = Image.open("imagens/memes/braixen-hug.png")
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
    if interaction.guild is None:
        await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyservers"),delete_after=10,ephemeral=True)
    else:
        try:
            await interaction.response.defer()
            fundo = Image.new("RGB",(593,900),"white")
            imagem_pil = await pegar_imagem(interaction, imagem, url_imagem, avatar_usuario)
            if not imagem_pil:
                await interaction.followup.send(Res.trad(interaction=interaction,str="message_erro_apimemes_notmidia"), ephemeral=True)
                return
            
            imagem_pil = imagem_pil.resize((495,380))
            meme = Image.open("imagens/memes/braixen tablet.png")
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
    if interaction.guild is None:
        await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyservers"),delete_after=10,ephemeral=True)
    else:
        try:
            await interaction.response.defer()
            fundo = Image.new("RGB",(460,281),"white")
            imagem_pil = await pegar_imagem(interaction, imagem, url_imagem, avatar_usuario)
            if not imagem_pil:
                await interaction.followup.send(Res.trad(interaction=interaction,str="message_erro_apimemes_notmidia"), ephemeral=True)
                return
            imagem_pil = imagem_pil.resize((460,281))
            meme = Image.open("imagens/memes/braixen-sad.png")
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
    if interaction.guild is None:
        await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyservers"),delete_after=10,ephemeral=True)
    else:
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
            meme = Image.open("imagens/memes/braixen-smash.png")
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
    if interaction.guild is None:
        await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyservers"),delete_after=10,ephemeral=True)
    else:
        try:
            await interaction.response.defer()
            fundo = Image.new("RGB",(558,787),"white")
            imagem_pil = await pegar_imagem(interaction, imagem, url_imagem, avatar_usuario)
            if not imagem_pil:
                await interaction.followup.send(Res.trad(interaction=interaction,str="message_erro_apimemes_notmidia"), ephemeral=True)
                return
           
            imagem_pil = imagem_pil.resize((243,274))
            meme = Image.open("imagens/memes/braixen-sleep.png")
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
    if frase is None and ia is None:
        await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_notargument").format("escreva uma frase ou peça uma para a IA"),ephemeral = True)
    else:
        try:
            await interaction.response.defer()
            if frase is not None:
                if len(frase) > 72:
                    await interaction.followup.send(f"Limite de caracteres atingido, você enviou {len(frase)} caracteres", ephemeral = True)
                    return
                
            if ia is not None:
                Check = await userpremiumcheck(interaction)
                if Check == True:
                    frase = await generate_response_with_text(f"{ia} que braixen diria limite 60 caracteres totais")
                    frase.replace('"','')
                else:
                    await interaction.followup.send(Res.trad(interaction=interaction,str='message_ia_only_premium'))
                    return
            if (variante.value == 'gun'):
                    meme = Image.open("imagens/memes/braixen-citacao-gun.png")
            if (variante.value == 'gun2'):
                    meme = Image.open("imagens/memes/braixen-citacao-gun-olhoaberto.png")
            fonte = ImageFont.truetype("font/Hey Comic.ttf",30)
            fontegrande = ImageFont.truetype("font/Hey Comic.ttf",50)
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
                if Check == True:
                    frase = await generate_response_with_text(f"{ia} que braixen diria limite 68 caracteres totais")
                else:
                    await interaction.followup.send(Res.trad(interaction=interaction,str='message_ia_only_premium'))
                    return
            if ignoreimage is True:
                meme = Image.open("imagens/memes/braixen-says.png")
                fundo = Image.new("RGBA", meme.size, (0, 0, 0, 0))
                fundo.paste(meme,(0,0),meme)
                fonte = ImageFont.truetype("font/Hey Comic.ttf",24)

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
                meme = Image.open("imagens/memes/braixen-says-imagem.png")
                mask = Image.open("imagens/memes/braixen-says-imagem-mask.png")
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
    if interaction.guild is None:
        await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyservers"),delete_after=10,ephemeral=True)
    else:
        try:
            await interaction.response.defer()
            fundo = Image.new("RGB",(534,534),"white")
            meme = Image.open("imagens/memes/braixen_drake_meme.png")
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
#  async def loonaimg(self,interaction: discord.Integration, imagem: discord.Attachment, variante:app_commands.Choice[str]):
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
   #             meme = Image.open("imagens/memes/loona foto.png")
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
  #              meme = Image.open("imagens/memes/loona angry foto.png")
  #              fundo.paste(imagem,(260,74))
  #              fundo.paste(meme,(0,0),meme)
  #              buffer = io.BytesIO()
  #              fundo.save(buffer,format="PNG")
  #              buffer.seek(0)
  #              await interaction.followup.send(file=discord.File(fp=buffer,filename="Loona angry Foto.png"))
  #      except Exception as e:
  #          await Res.erro_brix_embed(interaction,str="message_erro_apimemes",e=e)














#GRUPO DE COMANDOS DE DIVERSÂO DO BOT 
  diver=app_commands.Group(name="diversao",description="Comandos de diversão do Brix.",allowed_installs=app_commands.AppInstallationType(guild=True,user=True),allowed_contexts=app_commands.AppCommandContext(guild=True, dm_channel=True, private_channel=True))

#COMANDO GIRAR MOEDA
  @diver.command(name='girarmoeda',description='🪙⠂Veja se a moeda cai cara ou coroa.')
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
  @diver.command(name='d20',description='🪙⠂Rode o D20.')
  async def d20(self, interaction:discord.Interaction):
    if await Res.print_brix(comando="d20",interaction=interaction):
        return
    moedasorteada = random.randint(1,20)
    await interaction.response.send_message(f"🎲 - `{moedasorteada}`")

#COMANDO 8BALL
  @diver.command(name='8ball',description='🎱⠂Pergunte algo de sim/não ao Brix.')
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
    await interaction.followup.send(embed=resposta)













async def setup(client:commands.Bot) -> None:
  await client.add_cog(diversao(client))