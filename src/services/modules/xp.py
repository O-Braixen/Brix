import discord, os, asyncio, time, datetime, functools
from discord.ext import commands, tasks
from discord import app_commands
from src.services.connection.database import BancoUsuarios







class xp(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.xp_cache = {}  # Dicionário para acumular XP
        self.cache_lock = asyncio.Lock()  # Lock para evitar conflito de acesso
        self.save_xp.start()  # Inicia a task para salvar o XP periodicamente






    @commands.Cog.listener()
    async def on_bot_ready(self):
        print("🎮  -  Modúlo XP carregado.")








    @commands.Cog.listener()
    async def on_message(self, message):
        #await asyncio.sleep(1)  # Delay para evitar spam
        if message.author != self.client.user and not message.author.bot:
            user_id = str(message.author.id)
            async with self.cache_lock:
                # Acumula o XP no cache com segurança
                if user_id not in self.xp_cache:
                    self.xp_cache[user_id] = 0
                self.xp_cache[user_id] += 1









    @tasks.loop(minutes=5)
    async def save_xp(self):
        await asyncio.sleep(5)
        async with self.cache_lock:
            if self.xp_cache:
                loop = asyncio.get_running_loop()
                for user_id, xp in list(self.xp_cache.items()):
                    try:
                        await loop.run_in_executor(
                            None,
                            functools.partial(BancoUsuarios.update_inc, int(user_id), {"xpg": xp})
                        )
                    except Exception as e:
                        print(f"Falha ao salvar o XP de {user_id}: {e}")
                self.xp_cache.clear()










    @save_xp.before_loop
    async def before_save_xp(self):
        await self.client.wait_until_ready()







async def setup(client: commands.Bot) -> None:
    await client.add_cog(xp(client))
