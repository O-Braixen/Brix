import discord, os  , datetime , pytz ,platform , asyncio
from os import listdir
from discord.ext import commands
from dotenv import load_dotenv
from src.services.essential.shardsname import NOME_DOS_SHARDS
from src.services.essential.translator import BrixTradutor


load_dotenv()
token_bot = os.getenv("DISCORD_TOKEN")







class Client(commands.AutoShardedBot): 
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(command_prefix='-', intents=intents, shard_count=2)
        self.synced = False  # Isso é usado para que o bot não sincronize os comandos mais de uma vez
        self.cogslist = []
        for cog in listdir("src/services/modules"):
            if cog.endswith(".py"):
                cog = os.path.splitext(cog)[0]
                self.cogslist.append('src.services.modules.' + cog)



    async def setup_hook(self):
        #await self.load_extension("jishaku")

        self.brixtradutor =  BrixTradutor() #Define o modulo de tradução
        await self.tree.set_translator(self.brixtradutor) #Define o tradutor padrão para os comandos
        await self.brixtradutor.translate_responses() #inicia o tradutor das respostas do bot 

        for ext in self.cogslist:
            await self.load_extension(ext)


    async def on_shard_ready(self, shard_id):
        print(f"Shard {shard_id} ({NOME_DOS_SHARDS.get(shard_id, 'Desconhecido')}) pronto!")


    async def on_ready(self):
        await self.wait_until_ready()
        fuso = pytz.timezone('America/Sao_Paulo')
        now = datetime.datetime.now().astimezone(fuso)

        if not self.synced:  # Checar se os comandos slash foram sincronizados
            try:
                await self.tree.sync()
                self.synced = True
                print(f"\n\n💻  -  Comandos sincronizados: {self.synced}")
            except discord.DiscordServerError:
                print("\n\n⚠️  -  Discord API está indisponível (503). Tentará sincronizar depois.")
            except Exception as e:
                print(f"\n\n❌  -  Erro ao sincronizar comandos: {e}")
                
        print(f"🐍  -  Versão do python: {platform.python_version()}")
        print(f"🦊  -  O Bot {self.user} já está online e disponível")
        print(f"🤖  -  Número de Shards: {self.shard_count}") 
        print(f"🍕  -  Estou em {len(self.guilds)} comunidades com um total de {len(self.users)} membros")
        print(f"⏰  -  A hora no sistema é {now.strftime('%d/%m/%Y às %H:%M:%S')}\n\n")
        
        


        
# COISA DO MAIN NÃO MEXER
client = Client()

# LIGA O BOT
client.run(token_bot)