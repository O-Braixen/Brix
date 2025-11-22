import discord, os  , datetime , pytz ,platform , asyncio, hashlib , json
from discord.ext import commands
from dotenv import load_dotenv
from src.services.essential.shardsname import NOME_DOS_SHARDS
from src.services.essential.translator import BrixTradutor



load_dotenv()
token_bot = os.getenv("DISCORD_TOKEN")
SYNC_FILE = "last_sync.json"






#CLASSE DO MEU CLIENTE PRINCIPAL
class Client(commands.AutoShardedBot): 
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        #MEU INICIALIZADOR SUPER COM A PRÉ DEFINIÇÃO DE INICIAÇÃO
        super().__init__(command_prefix='-', intents=intents , chunk_guilds_at_startup= False ) #, shard_count= 1
        self.ready_tasks_done = False  # Isso é usado para que o bot não sincronize os comandos mais de uma vez
        self.cogslist = [
            f"src.services.modules.{os.path.splitext(cog)[0]}"
            for cog in os.listdir("src/services/modules")
            if cog.endswith(".py") and not cog.startswith("__")
        ]







    #SETUP HOOK PARA INICIAR O CARREGAMENTO DO TRADUDOR E DAS COGS
    async def setup_hook(self):       
        self.brixtradutor = BrixTradutor()
        # Carregar cogs de forma sequencial (evita overload no startup)
        for ext in self.cogslist:
            try:
                await self.load_extension(ext)
            except Exception as e:
                print(f"Erro ao carregar cog {ext}: {e}")

        # Criar tarefa assíncrona para inicialização pesada
        self.loop.create_task(self.start_background_initializers())







    #INCIALIZADOR DE TAREFAS PESADAS EM BACKGROUND
    async def start_background_initializers(self):
        #ESSE INICIALIZADOR FAZ AS TAREFAS PESADAS DEPOIS QUE O BOT ESTEJA COMPLETAMENTE CONECTADO AO DISCORD
        await self.wait_until_ready()

        #SÓ RODO ESSA TAREFA UMA UNICA VEZ
        if self.ready_tasks_done:
            print("🦊  -  Tarefas de inicialização já concluídas. Ignorando.")
            return
        # 1. TRADUÇÕES (Chamamos de novo, mas se for a primeira vez, é rápido)
        try:
            await self.tree.set_translator(self.brixtradutor)
            await self.brixtradutor.translate_responses()
        except Exception as e:
            print(f"Erro nas traduções: {e}")

        # 2. SINCRONIZAÇÃO DE COMANDOS
        await self.try_sync_commands()
        
        # 3. LÓGICA DE on_bot_ready DAS COGS (Tarefas de primeira vez)
        print("⚙️  -  Iniciando lógica de inicialização das Cogs (on_ready centralizado)...")
        for cog_name in self.cogslist:
            cog_instance = self.get_cog(cog_name.split('.')[-1].replace('Modúlo', '')) 
            if hasattr(cog_instance, 'on_bot_ready'):
                # Você precisará renomear os on_ready nas cogs para on_bot_ready
                await cog_instance.on_bot_ready() 
        # 4. PRINTS FINAIS DE STATUS (Apenas na primeira vez)
        self.ready_tasks_done = True
        print("🦊  -  Inicialização pós-login concluída.")
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



    #CARREGADOR DE MEMBROS CONTROLADO, PARA EVITAR LIMIT RATE
    async def _load_all_members_controlled(self, shard_id):
        
        # 💡 Damos um tempo extra para a conexão se estabilizar antes do chunking pesado
        print(f"⏳ Shard {shard_id}: Aguardando 5s antes de iniciar o chunking de membros.")
        await asyncio.sleep(5)
        MAX_CONCURRENCY = 30 
        semaphore = asyncio.Semaphore(MAX_CONCURRENCY)

        async def chunk_guild(guild):
            async with semaphore:
                try:
                    # Verifica se a guild pertence a este shard
                    if guild.shard_id == shard_id:
                        await guild.chunk()
                except Exception as e:
                    print(f"❌ Erro ao carregar membros para a Guild {guild.id}: {e}")

        print(f"⚡ Shard {shard_id}: Iniciando carregamento assíncrono de membros...")
        
        # Cria uma lista de tarefas para TODAS as guilds
        tasks = [chunk_guild(guild) for guild in self.guilds]
        
        # Executa as tarefas limitando a concorrência
        await asyncio.gather(*tasks)

        print(f"🏁 Shard {shard_id}: Carregamento de membros em segundo plano concluído. Cache total com {len(self.users)} usuários.")


    #ON_READY PARA QUANDO O SHARD FICA PRONTO, AO FICAR PRONTO ELE CHAMA A LOAD MEMBERS PARA CARREGAR TUDO DEVAGAR
    async def on_shard_ready(self, shard_id):
        print(f"Shard {shard_id} ({NOME_DOS_SHARDS.get(shard_id, 'Desconhecido')}) pronto!")
        self.loop.create_task(self._load_all_members_controlled(shard_id))


    #SYNCRONIZADOR DA ARVORE DE COMANDOS, SÓ RODA CASO PRECISE ATUALIZAR ALGUM COMANDO
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
                self.ready_tasks_done = True
                with open(SYNC_FILE, "w", encoding="utf-8") as f:
                    json.dump({"hash": current_hash, "timestamp": datetime.datetime.now().isoformat()}, f, indent=2)
                print("✅  Comandos atualizados e sincronizados com o Discord.")
            except Exception as e:
                print(f"❌  Erro ao sincronizar comandos: {e}")
        else:
            print("⚡  Nenhuma mudança detectada — comandos já sincronizados.")






# -------------------------------------------------------------------------
## 💡 NOVO BLOCO DE INICIALIZAÇÃO ASSÍNCRONA
async def main():
    await client.start(token_bot)

# COISA DO MAIN NÃO MEXER
client = Client()

# LIGA O BOT usando asyncio.run()
if __name__ == "__main__":
    try:
        # Define o loop de eventos principal e executa a função main.
        asyncio.run(main())
    except Exception as e:
        print(f"Erro fatal: {e}")