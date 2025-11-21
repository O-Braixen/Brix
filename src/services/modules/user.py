import discord,asyncio,pytz
from discord.ext import commands
from discord import app_commands
from src.services.connection.database import BancoUsuarios
from src.services.essential.respostas import Res
from src.services.essential.funcoes_usuario import userperfil,userrepavaliar,userrepconsulta , exibirtops
from PIL import Image, ImageFont #IMPORTAÇÂO Py PIL IMAGEM




class user(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        # CARREGANDO COISAS PADROES DE USO NO SISTEMA DE TOPS DO BOT
        self.reps_tops_background = Image.open("src/assets/imagens/financeiro/backgroud-top-reps.png")
        self.tops_recorte_mascara = Image.open("src/assets/imagens/icons/recorte-redondo.png").resize((44, 44))
        self.tops_font = ImageFont.truetype("src/assets/font/PoetsenOne-Regular.ttf", 15)
        self.tops_font_numero = ImageFont.truetype("src/assets/font/Quick-Fox.ttf", 18)
        self.default_avatar = Image.open("src/assets/imagens/financeiro/icondefault.png").resize((44, 44))

        self.fusohorario = pytz.timezone('America/Sao_Paulo')

        #Carrega os menu e adiciona eles
        self.menu_perfil = app_commands.ContextMenu(name="Perfil Ver no Brix",callback=self.uservermenu,type=discord.AppCommandType.user,allowed_installs=app_commands.AppInstallationType(guild=True,user=True),allowed_contexts=app_commands.AppCommandContext(guild=True, dm_channel=True, private_channel=True))
        self.client.tree.add_command(self.menu_perfil)
        self.menu_repconsulta = app_commands.ContextMenu(name="Rep Consultar",callback=self.userrapconsultarmenu,type=discord.AppCommandType.user,allowed_installs=app_commands.AppInstallationType(guild=True,user=True),allowed_contexts=app_commands.AppCommandContext(guild=True, dm_channel=True, private_channel=True))
        self.client.tree.add_command(self.menu_repconsulta)      
        
    
    @commands.Cog.listener()
    async def on_bot_ready(self):
        print("🙍  -  Modúlo Usuario database carregado.")







    #GRUPO REPUTAÇÃO
    rep=app_commands.Group(name="rep",description="Comandos de reputação do brix.")


    #COMANDO USUARIO REP AVALIAR #SLASH
    @rep.command(name="ajuda",description='👤⠂Ajuda sobre o sistema de reputação.')
    async def helprep(self,interaction: discord.Interaction):
        if await Res.print_brix(comando="rephelp",interaction=interaction):
            return
        await interaction.response.send_message(Res.trad(interaction=interaction,str="message_help_rep"))


    #COMANDO USUARIO REP AVALIAR #SLASH
    @rep.command(name="avaliar",description='👤⠂dé reputação a um membro')
    @app_commands.describe(membro="informe um membro")
    async def repavaliarslash(self,interaction: discord.Interaction,membro: discord.Member):
        if await Res.print_brix(comando="repavaliarslash",interaction=interaction,condicao=f"membro:{membro}"):
            return
        menu = False
        await userrepavaliar(interaction,membro,menu)


    #COMANDO USUARIO REP MENU
    async def userrapconsultarmenu(self,interaction: discord.Interaction, membro: discord.Member):
        if await Res.print_brix(comando="userrapconsultarmenu",interaction=interaction,condicao=f"membro:{membro}"):
            return
        menu = True
        await userrepconsulta(interaction,membro,menu)


    #COMANDO USUARIO REP SLASH
    @rep.command(name="consultar",description='👤⠂Consulte a reputaçao de um membro')
    @app_commands.describe(membro="informe um membro")
    async def repconsulta(self,interaction: discord.Interaction,membro: discord.Member=None):
        if await Res.print_brix(comando="repconsulta",interaction=interaction):
            return
        await interaction.response.defer()
        menu = False
        await userrepconsulta(interaction,membro,menu)


    #COMANDO USUARIO TOP REP
    @rep.command(name="tops",description='👤⠂veja os top reps')
    async def reptops(self,interaction: discord.Interaction):
        if await Res.print_brix(comando="reptops",interaction=interaction):
            return
        await interaction.response.defer()
        filtro = {"rep": {"$exists": True, "$gt": 0}, "ban": {"$exists": False} }
        dados_ordenados = BancoUsuarios.select_many_document(filtro).sort('rep',-1)[:500]
        classificacao_dados = [(index + 1, int(dados['_id']), int(dados['rep'])) for index, dados in enumerate(dados_ordenados)]
        blocos_classificacao = [classificacao_dados[i:i + 5] for i in range(0, len(classificacao_dados), 5)]
        await exibirtops(self,interaction,blocos_classificacao,1,originaluser=interaction.user,background=self.reps_tops_background)
    







     #Grupo perfil
    perfil=app_commands.Group(name='perfil',description="Comandos de perfil de usuario.",allowed_installs=app_commands.AppInstallationType(guild=True,user=True),allowed_contexts=app_commands.AppCommandContext(guild=True, dm_channel=True, private_channel=True))

     #Comando Mudar descrição perfil
    @perfil.command(name="sobremim", description='🦊⠂Edite sua descrição de exibição no /perfil.',)
    @app_commands.describe(frase="informe uma nova frase")
    async def usersobremin(self, interaction: discord.Interaction,frase: str):
        if await Res.print_brix(comando="usersobremin",interaction=interaction):
            return
        await interaction.response.defer()
        await interaction.original_response()
        if len(frase) <= 150:
            try:
                item = {"descricao": frase}
                BancoUsuarios.update_document(interaction.user,item)
            except:await interaction.edit_original_response(content=Res.trad(interaction=interaction,str="message_erro_mongodb").format(interaction.user.id))
            await interaction.edit_original_response(content=Res.trad(interaction=interaction,str="message_sobremim").format(frase))
            await asyncio.sleep(3)
            await userperfil(interaction,interaction.user)
        else:
            await interaction.edit_original_response(content=Res.trad(interaction=interaction,str="message_sobremim_limit"))
        


    #COMANDO Perfil de usuario MENU
    async def uservermenu(self,interaction: discord.Interaction, membro: discord.Member):
        menu = True
        await interaction.response.defer(ephemeral=menu)
        await userperfil(interaction,membro)


     #comando Perfil de usuario SLASH
    @perfil.command(name="ver", description='🦊⠂Consulte o seu perfil ou o de alguém.')
    @app_commands.describe(usuario="informe um usuario")
    async def userver(self, interaction: discord.Interaction,usuario: discord.User = None):
        if await Res.print_brix(comando="userver",interaction=interaction):
            return
        menu = False
        await interaction.response.defer(ephemeral=menu)
        await userperfil(interaction,usuario)
    





async def setup(client:commands.Bot) -> None:
  await client.add_cog(user(client))

