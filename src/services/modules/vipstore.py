import discord, random , asyncio , datetime
from discord.ext import commands
from discord import app_commands
from typing import List
from src.services.connection.database import BancoUsuarios, BancoServidores, BancoFinanceiro
from src.services.essential.respostas import Res
from src.services.modules.admin import addtemproleusuario
from src.services.essential.diversos import gerar_id_unica , formatar_tempo












# ======================================================================

# SELECT MENU LOJA VIP
class menuvip(discord.ui.Select):
    def __init__(self, interaction: discord.Interaction, itens):
        options = []
        for registro_id, dados in itens.items():
            cargo_id = dados["cargo"]
            valor = int(dados["valor"])
            tempo = formatar_tempo(dados["tempo"], interaction)

            cargo = interaction.guild.get_role(int(cargo_id))
            if not cargo:
                continue

            descricao = f"{valor:,} BraixenCoin - {tempo}".replace(",", ".")
            options.append( discord.SelectOption( value=registro_id, label=cargo.name, description=descricao, emoji="⭐" ) )

        super().__init__(
            placeholder=Res.trad(interaction=interaction, str="viploja_dropdown"),
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):  # Retorno seleção
        await interaction.response.defer()

        filtro = {"_id": interaction.guild.id}
        resultado = BancoServidores.select_many_document(filtro)
        itens = resultado[0]['lojavip']

        dados_membro = BancoUsuarios.insert_document(interaction.user)

        # Agora o value do select é o registro_id
        registro_id = self.values[0]
        if registro_id not in itens:
            return interaction.edit_original_response(content= Res.trad(interaction=interaction, str="viploja_erro_item") , embed =None , view=None)

        dados = itens[registro_id]
        cargo_id = int(dados["cargo"])
        custo = int(dados["valor"])
        
        tempo = formatar_tempo(dados["tempo"], interaction)

        guild = interaction.guild
        member = guild.get_member(interaction.user.id)
        vendedor = guild.get_member(dados["registrado"])

        # Verificar se o cargo já está aplicado
        cargo = guild.get_role(cargo_id)
        if cargo in member.roles:
            return await interaction.edit_original_response(content= Res.trad(interaction=interaction, str="viploja_erro_ja_existente") , embed =None , view=None)
        consulta = BancoServidores.insert_document(interaction.guild.id)
        if 'temprole' in consulta:
            for registro, info in consulta['temprole'].items():
                if info['usuario'] == interaction.user.id and info['cargo'] == cargo.id:
                    await interaction.edit_original_response(content=Res.trad(interaction=interaction, str="viploja_erro_registro_existente") , embed =None , view=None)
                    await interaction.user.add_roles(cargo)
                    return
          
        # Verifica saldo
        if dados_membro['braixencoin'] < custo:
            return await interaction.edit_original_response(content= Res.trad(interaction=interaction, str="message_financeiro_saldo_insuficiente") , embed =None , view=None )

        saldo = dados_membro['braixencoin'] - custo
        BancoUsuarios.update_inc(member, {"braixencoin": - custo})
        BancoFinanceiro.registrar_transacao( user_id=member.id, tipo="gasto", origem="Loja VIP", valor=custo, moeda="braixencoin", descricao=f"Compra de cargo {cargo.name} ({tempo}) em {interaction.guild.name}" )

        BancoUsuarios.update_inc(vendedor, {"braixencoin" : custo })
        BancoFinanceiro.registrar_transacao( user_id=vendedor.id, tipo="ganho", origem="Loja VIP", valor=custo, moeda="braixencoin", descricao=f"Venda de cargo {cargo.name} ({tempo}) em {interaction.guild.name}" )


        try:
            if dados["tempo"] == "perm":
                await interaction.user.add_roles(cargo)
            else:
                await addtemproleusuario(self, interaction, interaction.user, cargo, dados["tempo"])


            await interaction.edit_original_response(content= Res.trad(interaction=interaction, str="message_financeiro_compracor").format(f"{cargo.name} ({tempo})",saldo)  , embed =None , view=None)
        except Exception as e:
            await interaction.edit_original_response(content=Res.trad(interaction=interaction, str="message_erro_permissao")  , embed =None , view=None)
            await interaction.followup.send(str(e))


















# ======================================================================
# VIEW LOJA VIP
class DropdownVip(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, itens, client):
        super().__init__(timeout=120)
        self.client = client
        self.add_item(menuvip(interaction, itens))





















# ======================================================================
# COG VIP
class vipstore(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.Cog.listener()
    async def on_bot_ready(self):
        print("⭐  -  Módulo Sistema de cargos VIP carregado.")




    # Grupo VIP
    vip = app_commands.Group( name="vip", description="Comandos da loja de cargos VIP do Brix.", allowed_installs=app_commands.AppInstallationType(guild=True, user=False),        allowed_contexts=app_commands.AppCommandContext(guild=True, dm_channel=False, private_channel=False)    )






    # Comando exibir loja
    @vip.command(name="loja", description="⭐⠂Exibe a loja de cargos VIP da comunidade.")
    async def lojavipexibir(self, interaction: discord.Interaction):
        if await Res.print_brix(comando="lojavipexibir", interaction=interaction):
            return
        await interaction.response.defer()

        filtro = {"_id": interaction.guild.id}
        resultado = BancoServidores.select_many_document(filtro)
        try:
            itens = resultado[0]['lojavip']
        except:
            await interaction.edit_original_response(content=Res.trad(interaction=interaction, str="viploja_lojanaoexistente"))
            return

        if not itens:
            await interaction.edit_original_response(content=Res.trad(interaction=interaction, str="viploja_lojanaoexistente"))
            return

        lista = ""
        for registro_id, dados in itens.items():
            cargo_id = dados["cargo"]
            valor = int(dados["valor"])
            tempo = formatar_tempo(dados["tempo"], interaction)

            lista += f"<@&{cargo_id}> ({tempo}) - **{valor:,}** <:BraixenCoin:1272655353108103220>\n".replace(",", ".")

        embed = discord.Embed(
            colour=discord.Color.gold(),
            description=f"{Res.trad(interaction=interaction , str='viploja_title').format(interaction.guild.name)}\n {Res.trad(interaction=interaction , str='viploja_description').format(lista)}"
        )

        try:
            embed.set_image(url=resultado[0]['lojavipbanner'])
        except:
            embed.set_image(url="https://i.imgur.com/FnmoqCr.png")

        await interaction.edit_original_response(content="", embed=embed, view=DropdownVip(interaction, itens, self.client))
        await asyncio.sleep(120)
        await interaction.edit_original_response(content=Res.trad(interaction=interaction, str='message_erro_interacaoexpirada'), embed = None, view = None)

































    # Comando adicionar item
    @vip.command(name="adicionar", description="⭐⠂Adicione um cargo VIP na loja.")
    @app_commands.describe(cargo="Cargo VIP", valor="Custo em BraixenCoin", tempo="Tempo da assinatura (opcional)")
    async def lojavipadd(self, interaction: discord.Interaction, cargo: discord.Role, valor: int, tempo: int = None):
        if await Res.print_brix(comando="lojavipadd", interaction=interaction):
            return
        if not interaction.permissions.manage_guild:
            await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro"),delete_after=10,ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        filtro = {"_id": interaction.guild.id}
        resultado = BancoServidores.select_many_document(filtro)
        try:
            itens = resultado[0]['lojavip']
        except:
            itens = []

        if len(itens) >= 25:
            await interaction.followup.send(Res.trad(interaction=interaction, str="viploja_Limite"), ephemeral=True)
            return

        # se não foi informado tempo → perm
        if tempo is None:
            tempo = "perm"
        else:
            # transforma em horas, caso precise (ajuste conforme sua unidade)
            tempo_final = datetime.datetime.now() + datetime.timedelta(seconds=tempo)
            # limite de 5 meses (aprox. 3650 horas)
            limite = datetime.datetime.now() + datetime.timedelta(hours=3650)
            if tempo_final > limite:
                await interaction.followup.send( Res.trad(interaction=interaction, str='cargo_temporario_limit'), ephemeral=True )
                return
        # atualiza no banco
        BancoServidores.update_document(interaction.guild.id, {f"lojavip.{gerar_id_unica()}": {"cargo": cargo.id, "valor": valor, "tempo": tempo , "registrado": interaction.user.id}})
        await interaction.followup.send(Res.trad(interaction=interaction, str="viploja_item_adicionado").format(cargo.name,valor,formatar_tempo(tempo, interaction)) , ephemeral=True)




    @lojavipadd.autocomplete("valor")
    async def valor_autocomplete(self, interaction: discord.Interaction, current: str ) -> List[app_commands.Choice[int]]:
            valor = 0
            if current.lower().endswith('k'):
                valor = int(current[:-1]) * 1000
            elif current.lower().endswith('m'):
                valor = int(current[:-1]) * 1000000
            elif current.isdigit():
                valor = current

            sugestao = [ app_commands.Choice(  name=f"{int(valor):_} BraixenCoin".replace("_", "."),  value=int(valor),  )]
            return sugestao


    @lojavipadd.autocomplete("tempo")
    async def tipo_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        valor = 0
        if current.isdigit():
            valor = int(current)  
        sugestoes = [
        app_commands.Choice(
            name=f"{int(valor):_} {Res.trad(interaction=interaction,str='minutos')}",
            value=int(valor)*60,
        ),
        app_commands.Choice(
            name=f"{int(valor):_} {Res.trad(interaction=interaction,str='horas')}",
            value=int(valor)*60*60,
        ),
        app_commands.Choice(
            name=f"{int(valor):_} {Res.trad(interaction=interaction,str='dias')}",
            value=int(valor)*86400,
        )
        ]
        return sugestoes




















    # Comando remover item
    @vip.command(name="remover", description="⭐⠂Remova um cargo VIP da loja.")
    @app_commands.describe(idregistro="informe a ID do registro que deseja remover")
    async def lojaviprem(self, interaction: discord.Interaction, idregistro: str):
        if await Res.print_brix(comando="lojaviprem", interaction=interaction):
            return
        if not interaction.permissions.manage_guild:
            await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro"),delete_after=10,ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        filtro = {"_id": interaction.guild.id}
        resultado = BancoServidores.select_many_document(filtro)
        try:
            itens = resultado[0]['lojavip']
        except:
            await interaction.response.send_message(Res.trad(interaction=interaction, str="viploja_lojanaoexistente"), ephemeral=True)
            return

        if str(idregistro) in itens:
            item = {f"lojavip.{idregistro}": 0}
            BancoServidores.delete_field(interaction.guild.id, item)
            await interaction.followup.send(Res.trad(interaction=interaction,str="viploja_item_removido").format(itens[idregistro]['cargo']) )
        else:
            await interaction.followup.send(Res.trad(interaction=interaction,str="viploja_item_notfound"))

# Autocomplete para ID de registro
    @lojaviprem.autocomplete("idregistro")
    async def temproleremover_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        # Consulta no banco de dados para obter registros de cargos temporários
        consulta = BancoServidores.insert_document(interaction.guild.id)
        sugestoes = []

        if 'lojavip' in consulta:
            # Adiciona os registros encontrados como sugestões para o autocomplete
            for registro_id, info in consulta['lojavip'].items():
                if current.lower() in registro_id.lower():  # Filtra sugestões com base no texto do usuário
                    try:
                        cargo = interaction.guild.get_role(int(info['cargo']))
                        sugestoes.append(app_commands.Choice(name=f"ID: {registro_id} - {cargo.name} - {info['valor']} - {info['tempo']}", value=registro_id))
                    except:
                        sugestoes.append(app_commands.Choice(name=f"ID: {registro_id} - {info['cargo']} - {info['valor']} - {info['tempo']}", value=registro_id))
                    
        # Caso não haja sugestões, adiciona a mensagem de "sem registros"
        if not sugestoes:
            mensagem_sem_registros = Res.trad(interaction=interaction, str="viploja_notlist")
            sugestoes.append(app_commands.Choice(name=mensagem_sem_registros, value=""))

        return sugestoes























    # Comando definir arte
    @vip.command(name="arteloja", description="⭐⠂Defina a arte da loja VIP.")
    @app_commands.describe(link="Link da imagem")
    async def lojaviparte(self, interaction: discord.Interaction, link: str):
        if await Res.print_brix(comando="lojaviparte", interaction=interaction):
            return
        if not interaction.permissions.manage_guild:
            await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro"),delete_after=10,ephemeral=True)
            return

        await interaction.response.defer()
        item = {"lojavipbanner": link}
        BancoServidores.update_document(interaction.guild.id, item)
        await interaction.followup.send(Res.trad(interaction=interaction,str="viploja_banner"))











    # Comando definir arte
    @vip.command(name="ajuda", description="⭐⠂Ajuda sobre a loja VIP.")
    async def lojavipajuda(self, interaction: discord.Interaction):
        if await Res.print_brix(comando="lojavipajuda", interaction=interaction):
            return
        
        await interaction.response.send_message(Res.trad(interaction=interaction,str="viploja_ajuda"))
        










# ======================================================================
async def setup(client: commands.Bot) -> None:
    await client.add_cog(vipstore(client))
