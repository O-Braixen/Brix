import discord,os,asyncio,time,random
from discord.ext import commands
from discord import app_commands
from typing import List
from modulos.connection.database import BancoUsuarios,BancoServidores
from modulos.essential.respostas import Res








# PAINEL DE ESCOLHA DE CORES
class menucores(discord.ui.Select):
    def __init__(self, interaction: discord.Interaction,item):
        options = []

        for item_id, valor in item.items():
        #for i in range(0, len(cores), 2):
            #cargo = interaction.guild.get_role(int(cores[i]))
            cargo = interaction.guild.get_role(int(item_id))
            #options.append(discord.SelectOption(value=cargo.id,label=cargo.name,description="{:,.0f} - BraixenCoin".format(int(cores[i+1])), emoji="🎨"))
            options.append(discord.SelectOption(value=cargo.id,label=cargo.name,description="{:,.0f} - BraixenCoin".format(int(valor)), emoji="🎨"))
        super().__init__(
            placeholder=Res.trad(interaction=interaction,str="lojacor_dropdown"),
            min_values=1,
            max_values=1,
            options=options,
        )
    async def callback(self, interaction: discord.Interaction): #Retorno seleção Dropdown
        #coleta os dados do membro no banco de dados
        await interaction.response.defer()
        filtro = {"_id": interaction.guild.id}
        resultado = BancoServidores.select_many_document(filtro)
        item = resultado[0]['itensloja']
        dados_do_membro = BancoUsuarios.insert_document(interaction.user)
        for item_id, valor in item.items():
        #for i in range(0, len(cores), 2):
            if self.values[0] == item_id:
                custo = valor
        if dados_do_membro['braixencoin'] < int(custo): #verifica se o membro tem saldo o suficiente para pagar
                await interaction.followup.send(Res.trad(interaction=interaction,str="message_financeiro_saldo_insuficiente"))
                return
        saldo = dados_do_membro['braixencoin'] - int(custo)
        try:
            for item_id, valor in item.items():
            #for i in range(0, len(cores), 2):
                cargo = interaction.guild.get_role(int(item_id))
                if cargo in interaction.user.roles:
                    await interaction.user.remove_roles(cargo)
            cargo = interaction.guild.get_role(int(self.values[0]))
            await interaction.user.add_roles(cargo)
            BancoUsuarios.update_document(interaction.user,{"braixencoin": saldo})
            await interaction.followup.send(Res.trad(interaction=interaction,str='message_financeiro_compracor') .format(cargo.name,saldo))
        except Exception or discord.Forbidden as e:
            await interaction.followup.send(Res.trad(interaction=interaction,str='message_erro_permissao'))
            await interaction.followup.send(e)









#PAINEL PERSISTENTE CORES
class DropdownCores(discord.ui.View):
    def __init__(self, interaction: discord.Interaction,item): 
        super().__init__(timeout=60)
        self.add_item(menucores(interaction,item))







class cogcores(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client




    @commands.Cog.listener()
    async def on_ready(self):
        print("🎨  -  Modúlo Sistema de cores carregado.")
  








   #GRUPO DE LOJA  DE CORES
    cor=app_commands.Group(name="cores",description="Comandos de compra de cores do Brix.",allowed_installs=app_commands.AppInstallationType(guild=True,user=False),allowed_contexts=app_commands.AppCommandContext(guild=True, dm_channel=False, private_channel=False))





    # COMANDO EXIBIR LOJA DE CORES
    @cor.command(name="loja", description="🖌️⠂Exibe a loja de cores da comunidade.")
    async def lojacor(self, interaction:discord.Interaction):
        if await Res.print_brix(comando="lojacor",interaction=interaction):
            return
        await interaction.response.defer()
        filtro = {"_id": interaction.guild.id}
        resultado = BancoServidores.select_many_document(filtro)
        try:
            item = resultado[0]['itensloja']
        except:
            await interaction.followup.send(Res.trad(interaction=interaction,str='message_financeiro_compracor_lojanaoexistente'))
            return
        if not item or item is None:
            await interaction.followup.send(Res.trad(interaction=interaction,str='message_financeiro_compracor_lojanaoexistente'))
            return
        lista = ""
        for item_id, valor in item.items():

            lista += "<@&{}> - **{:,.0f}** <:BraixenCoin:1272655353108103220>\n".format(item_id,int(valor))
            #lista += "**{:,.0f}** <:BraixenCoin:1272655353108103220> <@&{}>\n".format(int(valor),item_id)
            #itens += "**{:,.0f}** <:BraixenCoin:1272655353108103220> <@&{}> | ".format(int(cores[i+1]),cores[i])
        embedcores = discord.Embed(
            colour=discord.Color.yellow(),
            title=Res.trad(interaction=interaction,str='lojacor_title'),
            description=Res.trad(interaction=interaction,str='lojacor_description').format(lista)
        )
        try:
            embedcores.set_image(url=resultado[0]['lojabanner'])
        except:embedcores.set_image(url="https://cdn.discordapp.com/attachments/1067789510097768528/1146086919462207620/cores.png")
        await interaction.followup.send(embed=embedcores,view=DropdownCores(interaction,item))






   # COMANDO ADICIONAR ITEM A LOJA DE CORES
    @cor.command(name="adicionar", description="🖌️⠂Adicione uma cor na loja.")
    @app_commands.describe(cargo="informe um cargo de cor",valor="informe um valor em BraixenCoin")
    async def lojaadd(self,interaction:discord.Interaction,cargo:discord.Role,valor:int):
        if await Res.print_brix(comando="lojaadd",interaction=interaction):
            return
        if interaction.guild is None:
            await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyservers"),delete_after=10,ephemeral=True)
            return
        elif interaction.permissions.manage_guild:
            await interaction.response.defer(ephemeral=True)
            filtro = {"_id": interaction.guild.id}
            resultado = BancoServidores.select_many_document(filtro)
            try:
                item = resultado[0]['itensloja']
            except:
                item = [0]
            if len(item)>= 25:
                await interaction.followup.send(Res.trad(interaction=interaction,str="message_financeiro_compracor_Limite"),ephemeral=True)
            else:
                item = {f"itensloja.{cargo.id}": str(valor)}
                BancoServidores.update_document(interaction.guild.id,item)
                await interaction.followup.send(Res.trad(interaction=interaction,str="message_financeiro_compracor_item_adicionado").format(cargo.name,valor))
        else: await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro"),delete_after=10,ephemeral=True)
    
    @lojaadd.autocomplete("valor")
    async def valor_autocomplete(self, interaction: discord.Interaction, current: str ) -> List[app_commands.Choice[int]]:
        valor = 0
        if current.lower().endswith('k'):
            valor = int(current[:-1]) * 1000
        elif current.lower().endswith('m'):
            valor = int(current[:-1]) * 1000000
        elif current.isdigit():
            valor = current

        sugestao = [
                app_commands.Choice(
                    name=f"{int(valor):_} BraixenCoin".replace("_", "."),
                    value=int(valor),
                )
        ]
        return sugestao





   # COMANDO REMOVER ITEM A LOJA DE CORES
    @cor.command(name="remover", description="🖌️⠂Retire uma cor na loja.")
    @app_commands.describe(cargo="informe um cargo de cor")
    async def lojarem(self,interaction:discord.Interaction,cargo:discord.Role):
        if await Res.print_brix(comando="lojarem",interaction=interaction):
            return
        if interaction.guild is None:
            await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyservers"),delete_after=10,ephemeral=True)
        elif interaction.permissions.manage_guild:
            await interaction.response.defer(ephemeral=True)
            filtro = {"_id": interaction.guild.id}
            resultado = BancoServidores.select_many_document(filtro)
            try:
                item = resultado[0]['itensloja']
            except:
                await interaction.response.send_message(Res.trad(interaction=interaction,str="message_financeiro_compracor_lojanaoexistente"),delete_after=10)
                return
            if str(cargo.id) in item:
                item = {f"itensloja.{cargo.id}": 0}
                BancoServidores.delete_field(interaction.guild.id,item)                                                              #.replace("['","").replace("']","").split("', '")
                await interaction.followup.send(random.choice(Res.trad( interaction, str="message_financeiro_compracor_item_removido")).format(cargo.name))
            else:
                await interaction.followup.send(Res.trad(interaction=interaction,str="message_financeiro_compracor_item_notfound"))
        else: await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro"),delete_after=10,ephemeral=True)



   # COMANDO DEFINIR ARTE PARA A LOJA DE CORES
    @cor.command(name="arteloja", description="🖌️⠂Adicione uma arte personalizada na loja de cores.")
    @app_commands.describe(link="envie o link da imagem")
    async def artloja(self,interaction:discord.Interaction,link:str):
        if await Res.print_brix(comando="artloja",interaction=interaction):
            return
        if interaction.guild is None:
            await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyservers"),delete_after=10,ephemeral=True)
        elif interaction.permissions.manage_guild:
            await interaction.response.defer()
            item = {f"lojabanner": link}
            BancoServidores.update_document(interaction.guild.id,item)
            await interaction.followup.send(Res.trad(interaction=interaction,str="message_financeiro_compracor_banner"))
        else: await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro"),delete_after=10,ephemeral=True)















async def setup(client:commands.Bot) -> None:
  await client.add_cog(cogcores(client))