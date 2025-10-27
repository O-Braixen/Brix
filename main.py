import discord, os  , datetime , pytz ,platform , asyncio, hashlib , json
from discord.ext import commands
from dotenv import load_dotenv
from src.services.essential.shardsname import NOME_DOS_SHARDS
from src.services.essential.translator import BrixTradutor



load_dotenv()
token_bot = os.getenv("DISCORD_TOKEN")
SYNC_FILE = "last_sync.json"







class Client(commands.AutoShardedBot): 
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(command_prefix='-', intents=intents, shard_count=3)
        self.synced = False  # Isso é usado para que o bot não sincronize os comandos mais de uma vez
        self.cogslist = [
            f"src.services.modules.{os.path.splitext(cog)[0]}"
            for cog in os.listdir("src/services/modules")
            if cog.endswith(".py") and not cog.startswith("__")
        ]



    async def setup_hook(self):

        self.brixtradutor = BrixTradutor() #Define o modulo de tradução
        await asyncio.gather(
            self.tree.set_translator(self.brixtradutor),
            self.brixtradutor.translate_responses(),
            *[self.load_extension(ext) for ext in self.cogslist]
        )


    async def on_shard_ready(self, shard_id):
        print(f"Shard {shard_id} ({NOME_DOS_SHARDS.get(shard_id, 'Desconhecido')}) pronto!")


    async def on_ready(self):

        await self.try_sync_commands()
        await asyncio.sleep(10)
        
        fuso = pytz.timezone('America/Sao_Paulo')
        now = datetime.datetime.now().astimezone(fuso)
        print("\n============================= STATUS DO BOT ==============================")
        print(f"🐍  -  Versão do python: {platform.python_version()}")
        print(f"🦊  -  O Bot {self.user} já está online e disponível")
        print(f"🤖  -  Número de Shards: {self.shard_count}") 
        print(f"🍕  -  Estou em {len(self.guilds)} comunidades com um total de {len(self.users)} membros")
        print(f"⏰  -  A hora no sistema é {now.strftime('%d/%m/%Y às %H:%M:%S')}\n\n")
        print("                                                                            ")
        print("                                                                            ")
        print("BBBBBBBBBBBBBBBBB   RRRRRRRRRRRRRRRRR   IIIIIIIIIIXXXXXXX       XXXXXXX     ")
        print("B::::::::::::::::B  R::::::::::::::::R  I::::::::IX:::::X       X:::::X     ")
        print("B::::::BBBBBB:::::B R::::::RRRRRR:::::R I::::::::IX:::::X       X:::::X     ")
        print("BB:::::B     B:::::BRR:::::R     R:::::RII::::::IIX::::::X     X::::::X     ")
        print("  B::::B     B:::::B  R::::R     R:::::R  I::::I  XXX:::::X   X:::::XXX     ")
        print("  B::::B     B:::::B  R::::R     R:::::R  I::::I     X:::::X X:::::X        ")
        print("  B::::BBBBBB:::::B   R::::RRRRRR:::::R   I::::I      X:::::X:::::X         ")
        print("  B:::::::::::::BB    R:::::::::::::RR    I::::I       X:::::::::X          ")
        print("  B::::BBBBBB:::::B   R::::RRRRRR:::::R   I::::I       X:::::::::X          ")
        print("  B::::B     B:::::B  R::::R     R:::::R  I::::I      X:::::X:::::X         ")
        print("  B::::B     B:::::B  R::::R     R:::::R  I::::I     X:::::X X:::::X        ")
        print("  B::::B     B:::::B  R::::R     R:::::R  I::::I  XXX:::::X   X:::::XXX     ")
        print("BB:::::BBBBBB::::::BRR:::::R     R:::::RII::::::IIX::::::X     X::::::X     ")
        print("B:::::::::::::::::B R::::::R     R:::::RI::::::::IX:::::X       X:::::X     ")
        print("B::::::::::::::::B  R::::::R     R:::::RI::::::::IX:::::X       X:::::X     ")
        print("BBBBBBBBBBBBBBBBB   RRRRRRRR     RRRRRRRIIIIIIIIIIXXXXXXX       XXXXXXX     ")
        print("                                                                            ")
        print("                                                                            ")
        print("                                                                            ")
        print("==========================================================================\n")
    



    # Syncronizador da arvore de comandos, só roda caso exista algum comando que realmente precise ser syncronizado
    async def try_sync_commands(self):
        # Gera hash do conteúdo dos comandos atuais
        command_data = "".join(sorted([c.qualified_name for c in self.tree.walk_commands()]))
        current_hash = hashlib.md5(command_data.encode()).hexdigest()

        # Lê o hash anterior
        last_hash = None
        if os.path.exists(SYNC_FILE):
            with open(SYNC_FILE, "r", encoding="utf-8") as f:
                last_hash = json.load(f).get("hash")

        # Só sincroniza se o hash mudou
        if current_hash != last_hash:
            try:
                await self.tree.sync()
                self.synced = True
                with open(SYNC_FILE, "w", encoding="utf-8") as f:
                    json.dump({"hash": current_hash, "timestamp": datetime.datetime.now().isoformat()}, f, indent=2)
                print("✅  Comandos atualizados e sincronizados com o Discord.")
            except Exception as e:
                print(f"❌  Erro ao sincronizar comandos: {e}")
        else:
            print("⚡  Nenhuma mudança detectada — comandos já sincronizados.")






        
# COISA DO MAIN NÃO MEXER
client = Client()

# LIGA O BOT
client.run(token_bot)