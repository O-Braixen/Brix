import discord, os , asyncio , datetime , pytz 
from discord.ext import commands, tasks
from src.services.essential.host import informação
from src.services.connection.database import BancoBot
from src.services.essential.respostas import listapegadinha
from src.services.essential.shardsname import NOME_DOS_SHARDS
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

        status_list = []

        if self.isbraixenday:  # Dia do Braixen
            status_list = [
                (discord.CustomActivity(name="🦊 Braixen Day!!!"), discord.Status.online),
                (discord.CustomActivity(name="🔥 Celebrando Braixen Day!"), discord.Status.online),
                (discord.Activity(type=discord.ActivityType.watching, name="Braixen's em Kalos TV"), discord.Status.do_not_disturb),
            ]

        elif self.isnatalday:  # Natal
            status_list = [
                (discord.CustomActivity(name="🎄 Feliz Natal!!!"), discord.Status.online),
                (discord.CustomActivity(name="🎄 Natal com magia de fogo!"), discord.Status.online),
                (discord.Activity(type=discord.ActivityType.watching, name="Especial de Natal na Globo"), discord.Status.online),
            ]

        elif self.isanonovoday:  # Ano novo
            status_list = [
                (discord.CustomActivity(name="Feliz Ano Novo!!!"), discord.Status.online),
                (discord.CustomActivity(name="🔥 Um Próspero Ano Novo!!!"), discord.Status.online),
                (discord.Activity(type=discord.ActivityType.watching, name="🎆 Fogos de Artifício"), discord.Status.online),
            ]

        elif self.abrilfools:  # 1 de abril
            status_list = [
                (discord.CustomActivity(name=f"{len(listapegadinha)} Raposas cairam na pegadinha de primeiro de abril!"), discord.Status.dnd),
                (discord.CustomActivity(name="🔥 Braixen agora é um Pokémon Lendário!"), discord.Status.dnd),
                (discord.CustomActivity(name="🔨 Todos Foram Banidos ~kyuuuu!!!"), discord.Status.dnd),
                (discord.CustomActivity(name="Primeiro de Abril ~kyuuuu!!!"), discord.Status.dnd),
            ]

        else:  # sem data especifica
            try:
                res_information, host = await informação(self.client.user.name)
                if host == "squarecloud":
                    status_list.append((discord.CustomActivity(name=f"🖥️ Squarecloud - {res_information['response']['cluster']}"), discord.Status.online))
                elif host == "discloud":
                    status_list.append((discord.CustomActivity(name=f"🖥️ Discloud - CLUSTER {res_information['apps']['clusterName']}"), discord.Status.online))
            except:
                print("❌ falha ao coletar dados da square para status")

            status_list.extend([
                (discord.CustomActivity(name="🦊 Minha casa discord.gg/braixen"), discord.Status.online),
                (discord.CustomActivity(name=f"✨ visitando {len(self.client.guilds)} servidores kyuuuuu!"), discord.Status.online),
                (discord.CustomActivity(name="🍕📱 Pedindo uma pizza com @obraixen"), discord.Status.dnd),
                (discord.Activity(type=discord.ActivityType.watching, name="Braixen's House 🦊"), discord.Status.do_not_disturb),
                (discord.Activity(type=discord.ActivityType.playing, name="Pokémon X em dsc.gg/braixen"), discord.Status.do_not_disturb),
                (discord.Activity(type=discord.ActivityType.watching, name=f"{len(self.client.users)} usuários!"), discord.Status.online),
                (discord.CustomActivity(name=f"🦊 {len(self.client.guilds)} guildas confiando na sabedoria de Brix!"), discord.Status.online),
                (discord.CustomActivity(name="🦊 Sendo um bom Braixen, kyuu!"), discord.Status.online),
                (discord.CustomActivity(name=f"Versão {dadosbot['version']} Brix!"), discord.Status.online),
                #(discord.CustomActivity(name=f"{shard_nome} ({shard_id}) em uso"), discord.Status.online),
                (discord.CustomActivity(name="✨ Magia Pokémon em cada servidor!"), discord.Status.online),
            ])

        # loop principal para trocar os status
        for activity, status in status_list:
            await self.client.change_presence(activity=activity, status=status)
            await asyncio.sleep(900)  # apenas uma vez aqui











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