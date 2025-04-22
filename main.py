import discord, os  , datetime , pytz , modulos.essential.translator,platform
from os import listdir
from discord.ext import commands
from dotenv import load_dotenv
from modulos.web import webserver


load_dotenv()
token_bot = os.getenv("DISCORD_TOKEN")



#class Client(commands.Bot): #no furuto usar AutoShardedBot
class Client(commands.AutoShardedBot): 
    def __init__(self) -> None:
        intençoes = discord.Intents.default()
        intençoes.message_content = True
        intençoes.members = True

        super().__init__(command_prefix='-', intents=intençoes, shard_count=1)
        self.synced = False  # Nós usamos isso para o bot não sincronizar os comandos mais de uma vez
        self.cogslist = []
        for cog in listdir("modulos"):
            if cog.endswith(".py"):
                cog = os.path.splitext(cog)[0]
                self.cogslist.append('modulos.' + cog)



    async def setup_hook(self):
        await self.load_extension("jishaku")
        await self.tree.set_translator(modulos.essential.translator.BrixTradutor())

        for ext in self.cogslist:
            await self.load_extension(ext)





    async def on_ready(self):
        await self.wait_until_ready()
        fuso = pytz.timezone('America/Sao_Paulo')
        now = datetime.datetime.now().astimezone(fuso)

        if not self.synced:  # Checar se os comandos slash foram sincronizados
            await self.tree.sync()
            self.synced = True
            print(f"\n\n💻  -  Comandos sincronizados: {self.synced}")
        print(f"🐍  -  Versão do python: {platform.python_version()}")
        print(f"🦊  -  O Bot {self.user} já está online e disponível")
        print(f"🤖  -  Número de Shards: {self.shard_count}")  # Mostra a quantidade de shards (será 1)
        print(f"🍕  -  Estou em {len(self.guilds)} comunidades com um total de {len(self.users)} membros")
        print(f"⏰  -  A hora no sistema é {now.strftime('%d/%m/%Y às %H:%M:%S')}\n\n")
        


        
# COISA DO MAIN NÃO MEXER
client = Client()

# INICIA O SITE
webserver.iniciar_webserver(client)

# LIGA O BOT
client.run(token_bot)