import discord,os,asyncio,datetime,pytz,re
from discord.ext import commands,tasks
from discord import app_commands
from src.services.essential.respostas import Res
from dotenv import load_dotenv







# ======================================================================

#Dia do braixen é comemorado todo dia 7/10 - month=10,day=7
load_dotenv(os.path.join(os.path.dirname(__file__), '.env')) #load .env da raiz
id_chatBH = int(os.getenv('id_chatBH'))
mes = int(os.getenv("mes_Braixen_day"))
dia = int(os.getenv("dia_Braixen_day"))










# ======================================================================

class braixenday(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
    







# ======================================================================

    @commands.Cog.listener()
    async def on_message(self,message:discord.Message):

        if message.author == self.client.user or message.author.bot:
            return
        
        elif message.guild is None:
            return

        # RETORNA UMA MENSAGEM DO BRIX SOBRE O DIA DO BRAIXEN
        elif "feliz dia do braixen brix" in message.content.lower() and message.author != self.client.user and message.channel.id != id_chatBH:
            #async with message.channel.typing():
            #    await asyncio.sleep(0.5)
            #defini as datas para realizar a consulta
            fuso = pytz.timezone('America/Sao_Paulo')
            now = datetime.datetime.now(pytz.utc).astimezone(fuso).replace(hour=0, minute=0, second=0, microsecond=0)  # Garante que estamos pegando UTC e convertendo
            
            databraixenday = datetime.date(now.year, mes, dia)  # Ano, Mês, Dia

            # Verifica se a data já passou
            if now.date() > databraixenday:
                databraixenday = datetime.date(now.year + 1, mes, dia)  # Ajusta para o próximo ano

            # Converte a data para datetime com o fuso correto
            databraixenday = fuso.localize(datetime.datetime(databraixenday.year, databraixenday.month, databraixenday.day, 0, 0, 0))

            if now.date() == databraixenday.date():
                await message.reply(Res.trad(str='message_brixday_positivo').format(message.author))
            else:
                await message.reply(Res.trad(str='message_brixday_negativo').format(int(databraixenday.timestamp())))
        
         # RETORNO DO BRIX CASO ALGUEM ESCREVA "BRIX" OU SUAS VARIAÇÕES
        elif message.author != self.client.user and not message.author.bot:
            conteudo = message.content.strip().lower()

            # Caso seja só "brix" ou variantes "-brix !brix"
            if re.search(r"^[\W_]?brix(?:\W.*)?$", conteudo.strip(), re.IGNORECASE):
                await message.reply(Res.trad(user=message.author,str="onwer_help_apresentação") , delete_after = 60)






# ======================================================================

    @commands.Cog.listener()
    async def on_ready(self):
        print("🦊  -  Modúlo Braixen Day carregado.")
        await self.client.wait_until_ready() #Aguardando o bot ficar pronto
        if not self.diadobraixen.is_running():
            await asyncio.sleep(20)
            self.diadobraixen.start()










# ======================================================================

    #Verificador do dia do braixen para postagem dedicada na BH
    @tasks.loop(time=datetime.time(hour=8 , minute= 30, tzinfo=datetime.timezone(datetime.timedelta(hours=-3))))
    async def diadobraixen(self):
        fuso = pytz.timezone('America/Sao_Paulo')
        now = datetime.datetime.now().astimezone(fuso)
        databraixenday = now.replace(month=mes,day=dia)
        if databraixenday.date() != now.date():
            print("🦊 - Hoje não é dia do Braixen")
            return
        print("🦊🦊🦊🦊 - Dia do Braixen!!!")
        channel_id = 888567677784829982 #888567677784829982
        channel = self.client.get_channel(channel_id)
        embed = discord.Embed(
                    colour=discord.Color.yellow(),
                    title="Dia do Braixen!!!",
                    description ="Eiii, **Humanos e Raposas!!** 🦊🔥\n Eu sou o **Brix, o Braixen**, e hoje é um dia muito especial...\n**O Dia do Braixen!!!** 🎉\n\nQuero **celebrar** com todos vocês esse momento incrível, então me **tratem como um rei** 👑 porque eu mereço, kyuuu~!\n\n💡 **Surpresa de raposa:** Deseje *'feliz dia do braixen brix'* e descubra o que eu preparei pra você! Kyuuuu~"
        )
        embed.set_image(url="https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/6864594f-c529-49c2-9678-777a37591fc1/de6hy2q-b5edf92d-1e6c-47e3-8a62-68d179934d89.png?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7InBhdGgiOiJcL2ZcLzY4NjQ1OTRmLWM1MjktNDljMi05Njc4LTc3N2EzNzU5MWZjMVwvZGU2aHkycS1iNWVkZjkyZC0xZTZjLTQ3ZTMtOGE2Mi02OGQxNzk5MzRkODkucG5nIn1dXSwiYXVkIjpbInVybjpzZXJ2aWNlOmZpbGUuZG93bmxvYWQiXX0.BoD1eu1dCBdSTpd0iU3CYXpX9Van8kYnBJ3ZSCoclXU")
        mensagem = f"<:BH_Braix_Happy2:1154418208925823067> - Dia Do Braixen!!!! ||Ping: <@&1081023728206495804>||"
        await channel.send(mensagem,embed=embed)
    



















# ======================================================================

async def setup(client:commands.Bot) -> None:
  await client.add_cog(braixenday(client))