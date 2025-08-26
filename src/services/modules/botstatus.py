import discord, os , asyncio , datetime , pytz 
from discord.ext import commands, tasks
from src.services.essential.host import informação
from src.services.connection.database import BancoBot
from src.services.essential.respostas import listapegadinha
from dotenv import load_dotenv





# ======================================================================

load_dotenv()
mes = int(os.getenv("mes_Braixen_day"))
dia = int(os.getenv("dia_Braixen_day"))












# ======================================================================

class BotStatus(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.isbraixenday = False
        self.isnatalday = False
        self.isanonovoday = False
        self.abrilfools = False





# ======================================================================

    @commands.Cog.listener()
    async def on_ready(self):
        print("🤖  -  Modúlo BotStatus carregado.")
        await self.client.wait_until_ready() #Aguardando o bot ficar pronto
         #Ligando tasks
        if not self.verificar_datas_comemorativas.is_running():
            await asyncio.sleep(20)
            self.verificar_datas_comemorativas.start()
        
        if not self.update_status_loop.is_running():
            await asyncio.sleep(20)
            self.update_status_loop.start()
       







# ======================================================================

    @tasks.loop(minutes=10)
    async def update_status_loop(self):
        dadosbot = BancoBot.insert_document()
        if self.isbraixenday: # Dia do Braixen
            await self.client.change_presence(activity=discord.CustomActivity(name="🦊 Braixen Day!!!"),  status=discord.Status.online)
            await asyncio.sleep(900)
            await self.client.change_presence(activity=discord.CustomActivity(name="🔥 Celebrando Braixen Day!"),  status=discord.Status.online)
            await asyncio.sleep(900)
            await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"Braixen's em Kalos TV"),  status=discord.Status.do_not_disturb)
            await asyncio.sleep(900)

        elif self.isnatalday: # Natal
            await self.client.change_presence(activity=discord.CustomActivity(name="🎄 Feliz Natal!!!") ,  status=discord.Status.online)
            await asyncio.sleep(900)
            await self.client.change_presence(activity=discord.CustomActivity(name="🎄 Natal com magia de fogo!") ,  status=discord.Status.online)
            await asyncio.sleep(900)
            await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"Especial de Natal na Globo") ,  status=discord.Status.online)
            await asyncio.sleep(900)

        elif self.isanonovoday: # Ano novo
            await self.client.change_presence(activity=discord.CustomActivity(name="Feliz Ano Novo!!!"), status=discord.Status.online)
            await asyncio.sleep(900)
            await self.client.change_presence(activity=discord.CustomActivity(name="🔥 Um Próspero Ano Novo!!!"), status=discord.Status.online)
            await asyncio.sleep(900)
            await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"🎆 Fogos de Artifício"), status=discord.Status.online)
            await asyncio.sleep(900)
        
        elif self.abrilfools: # 1 de abril
            await self.client.change_presence(activity=discord.CustomActivity(name=f"{len(listapegadinha)} Raposas cairam na pegadinha de primeiro de abril!"), status=discord.Status.dnd)
            await asyncio.sleep(900)
            await self.client.change_presence(activity=discord.CustomActivity(name="🔥 Braixen agora é um Pokémon Lendário!"), status=discord.Status.dnd)
            await asyncio.sleep(900)
            await self.client.change_presence(activity=discord.CustomActivity(name="🔨 Todos Foram Banidos ~kyuuuu!!!"), status=discord.Status.dnd)
            await asyncio.sleep(900)
            await self.client.change_presence(activity=discord.CustomActivity(name="Primeiro de Abril ~kyuuuu!!!"), status=discord.Status.dnd)
            await asyncio.sleep(900)

        else: # sem data especifica
            await self.client.change_presence(activity=discord.CustomActivity(name="🦊 Minha casa discord.gg/braixen"), status=discord.Status.online)
            await asyncio.sleep(900)
            await self.client.change_presence(activity=discord.CustomActivity(name=f"✨ visitando {len(self.client.guilds)} servidores kyuuuuu!"), status=discord.Status.online)
            await asyncio.sleep(900)
            await self.client.change_presence(activity=discord.CustomActivity(name="🍕📱 Pedindo uma pizza com @obraixen"), status=discord.Status.dnd)
            await asyncio.sleep(900)
            await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"Braixen's House 🦊"), status=discord.Status.do_not_disturb)
            await asyncio.sleep(900)
            await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="Pokémon X em dsc.gg/braixen"), status=discord.Status.do_not_disturb)
            await asyncio.sleep(900)
            await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(self.client.users)} usuários!"), status=discord.Status.online)
            await asyncio.sleep(900)
            await self.client.change_presence(activity=discord.CustomActivity(name=f"🦊 {len(self.client.guilds)} guildas confiando na sabedoria de Brix!"), status=discord.Status.online)
            await asyncio.sleep(900)
            await self.client.change_presence(activity=discord.CustomActivity(name=f"🦊 Sendo um bom Braixen, kyuu!"), status=discord.Status.online)
            await asyncio.sleep(900)
            await self.client.change_presence(activity=discord.CustomActivity(name=f"Versão {dadosbot['version']} Brix!"), status=discord.Status.online)
            await asyncio.sleep(900)
            try:
                res_information , host = await informação(self.client.user.name)
                if host == "squarecloud":
                    await self.client.change_presence(activity=discord.CustomActivity(name=f"🖥️ Squarecloud - {res_information['response']['cluster']}"), status=discord.Status.online)
                if host == "discloud":
                    await self.client.change_presence(activity=discord.CustomActivity(name=f"🖥️ Discloud - Melhor Host de todas"), status=discord.Status.online)
            except:
                print("❌ falha ao coletar dados da square para status")
            await asyncio.sleep(900)











# ======================================================================

    #VERIFICADOR DE DATAS COMEMORATIVAS PARA USAR DE STATUS NO BOT
    @tasks.loop(minutes=10)
    async def verificar_datas_comemorativas(self):
        
        now = datetime.datetime.now().astimezone(pytz.timezone('America/Sao_Paulo'))
        databraixenday = datetime.date(now.year , mes , dia) # sequencia Ano , Mes , Dia
        natalday = datetime.date(now.year , 12 , 25 )
        anonovoday = datetime.date(now.year , 1 , 1 )
        primeiroabril = datetime.date(now.year , 4 , 1 )


        if now.date() == databraixenday:
            self.isbraixenday = True
        elif now.date() == natalday:
            self.isnatalday = True
        elif now.date() == anonovoday:
            self.isanonovoday = True
        elif now.date() == primeiroabril:
            self.abrilfools = True
        else:
            self.isbraixenday = False
            self.isnatalday = False
            self.isanonovoday = False
            self.abrilfools = False


















# ======================================================================

async def setup(client: commands.Bot) -> None:
    await client.add_cog(BotStatus(client))