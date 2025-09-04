import discord,os,asyncio,time,datetime,pytz,random , requests , io
from discord.ext import commands,tasks
from functools import partial
from discord import app_commands
from typing import List
from src.services.connection.database import BancoUsuarios , BancoFinanceiro
from src.services.essential.respostas import Res
from src.services.essential.funcoes_usuario import exibirtops , userpremiumcheck, verificar_cooldown
from src.services.essential.diversos import calcular_saldo, Paginador_Global
#from modulos.premium import liberarpremium
from src.services.essential.pokemon_module import get_all_pokemon , get_pokemon , get_pokemon_sprite
from PIL import Image, ImageFont, ImageDraw, ImageOps #IMPORTAÇÂO Py PIL IMAGEM
from dotenv import load_dotenv


#importação
BH_id = int(os.getenv('id_servidor_bh'))






#CLASSE

class financeiro(commands.Cog):
  def __init__(self, client: commands.Bot):
    self.client = client

# CARREGANDO COISAS PADROES DE USO NO SISTEMA DE TOPS DO BOT
    self.tops_recorte_mascara = Image.open("src/assets/imagens/icons/recorte-redondo.png").resize((44, 44))
    self.bccoin_tops_background = Image.open("src/assets/imagens/financeiro/backgroud-top-braixencoin.png")
    self.tops_font = ImageFont.truetype("src/assets/font/PoetsenOne-Regular.ttf", 15)
    self.tops_font_numero = ImageFont.truetype("src/assets/font/Quick-Fox.ttf", 18)
    self.default_avatar = Image.open("src/assets/imagens/financeiro/icondefault.png").resize((44, 44))
    
    #ANDAMENTO DE JOGOS DE APOSTA
    self.jogos_em_andamento = {}





  @commands.Cog.listener()
  async def on_ready(self):
    print("💲  -  Modúlo Financeiro carregado.")
    await self.client.wait_until_ready() #Aguardando o bot ficar pronto
    if not self.verificar_daily.is_running():
        self.verificar_daily.start()
    if not self.lembretes_cacar.is_running():
        self.lembretes_cacar.start()











    #FUNÇÂO DE VERIFICAÇÃO DE RESGATE DO DAILY hour=21, minute= 0,
  @tasks.loop(time=datetime.time(hour=21, minute= 0, tzinfo=datetime.timezone(datetime.timedelta(hours=-3))))
  async def verificar_daily(self): 
    try:
        data_verificacao = datetime.datetime.now() - datetime.timedelta(days=30) #30
        fuso = pytz.timezone('America/Sao_Paulo')
        print(f"💲  -  data de verificação daily: {data_verificacao.strftime('%d/%m/%Y')}\n\n")
        filtro = {"date-daily": {"$exists":True} , "braixencoin": {"$gt": 0} }
        dado = BancoUsuarios.select_many_document(filtro)
        updates = []  # Lista para armazenar dados de atualização
        transacoes = []
        TotalTaxas = 0
        for membro in dado:
            try:
                if datetime.datetime.strptime(membro['date-daily'],'%d/%m/%Y') < data_verificacao:
                    if membro['date-daily'] == data_verificacao.strftime('%d/%m/%Y'):
                        datanova = datetime.datetime.now() + datetime.timedelta(days=1)
                        try:
                            user = await self.client.fetch_user(membro['_id'])
                            resposta = discord.Embed(
                            colour=discord.Color.yellow(),
                            title=Res.trad(user=user, str='message_daily_impostodm_title'),
                            description=Res.trad(user=user, str='message_daily_impostodm').format(user.mention,membro['braixencoin'],int(datanova.timestamp()))
                            )
                            resposta.set_thumbnail(url="https://i.imgur.com/rsG9pNp.png")
                            
                            resposta.set_footer(text=datetime.datetime.now().astimezone(fuso).strftime('%d/%m/%Y ás %H:%M'))
                            await user.send(embed=resposta)
                            print(f"✉️  -  notificando: {user.id} - {user.name}")
                        except:
                            print(f"❌  -  dm do usuario {user.name} está fechada ou não foi encontrado")
                    else:
                        saldo = membro['braixencoin']
                        taxa = saldo * 0.05
                        if saldo < 20:
                            saldonovo = 0
                            updates.append({"_id": membro['_id'],"update": {"$unset": {"date-daily": ""}}})
                        else:
                            saldonovo = saldo - int(taxa)
                            TotalTaxas = TotalTaxas + int(taxa)
                        updates.append({"_id": membro['_id'],"update": {"$set": {"braixencoin": saldonovo}}})
                        transacoes.append({    "user_id": str(membro['_id']),    "tipo": "gasto",    "origem": "Daily Taxa",    "valor": int(taxa),    "moeda": "braixencoin",    "descricao": f"Cobrança de 5% por inatividade no daily.",    "timestamp": datetime.datetime.now()})

            except Exception as e:
                print(f"problemas ao localizar o usuario: {membro['_id']}")
                print(f"Error: {e}")
        
        try:
            #CUSTO APARTAMENTO DO BRIX
            brix = BancoUsuarios.insert_document(self.client.user)
            custobrix = brix['braixencoin'] * 0.05
            apartamento = brix['braixencoin'] - int(custobrix)
            updates.append({"_id": brix['_id'],"update": {"$set": {"braixencoin": apartamento , "date-daily": datetime.datetime.now().strftime("%d/%m/%Y") }}})
            transacoes.append({    "user_id": str(brix['_id']),    "tipo": "gasto",    "origem": "Aluguel Ap",    "valor": custobrix,    "moeda": "braixencoin",    "descricao": "Taxa apartamento do Brix.",    "timestamp": datetime.datetime.now()})
            print(f"Brix pagou o aluguel do ap com o vini, brix tinha {brix['braixencoin']} e agora ficou com {apartamento}")
        except Exception as e:
            print(f"Error na cobrança do apartamento de brix: {e}")
        # Executa as atualizações em lote
        
        if updates:
            try:
                result = BancoUsuarios.bulk_update(updates)
                print(f"💲  -  Atualizações realizadas: {result.modified_count}")
            except Exception as e:
                print(f"Erro ao executar operações em lote: {e}")
        if transacoes:
            try:
                BancoFinanceiro.bulk_registrar_transacoes(transacoes)
                print(f"💲  -  Transações registradas")
            except Exception as e:
                print(f"Erro ao registrar transações em lote: {e}")
        print(f"💲  -  Um total de {TotalTaxas:,.0f} BC Foram tirados dos usuarios.")
        print(f"💲  -  Fim da Checagem do Daily")
    except Exception as e:
        print(f"Error no verificar daily: {e}")
    














  async def mostrar_transações(self,interaction,  moeda): 
    await interaction.response.send_message("https://cdn.discordapp.com/emojis/1370974233588404304.gif")
    try:
        transacoes = BancoFinanceiro.buscar_historico(interaction.user.id, limite=1000,moeda=moeda)
        lista = []
        for t in transacoes:
            timestamp = int(t["timestamp"].timestamp())
            tipo = "🟢 +" if t["tipo"] == "ganho" else "🔴 -"
            origem = t.get("origem", "desconhecido")
            emoji = "<:BraixenCoin:1272655353108103220>" if t["moeda"] == "braixencoin" else "<:Graveto:1318962131567378432>"
            descricao = t.get("descricao", "desconhecido")
            linha = f"**{tipo} {t['valor']:,.0f}** {emoji} <t:{timestamp}:R> - {origem}\n*{descricao}*"
            lista.append(linha)

        url = "https://i.imgur.com/rsG9pNp.png" if moeda == "braixencoin" else "https://cdn.discordapp.com/emojis/1318962131567378432"
        textomoeda = "Braixen Coin" if moeda == "braixencoin" else "Graveto"
        if not lista:
            lista =[f"{Res.trad(interaction= interaction, str='message_financeiro_sem_transções')}"]
        blocos = [lista[i:i + 10] for i in range(0, len(lista), 10)] 
        descrição = Res.trad(interaction= interaction, str="message_financeiro_extrato").format(textomoeda)
        await Paginador_Global(self, interaction, blocos, pagina=0, originaluser=interaction.user,descrição=descrição, thumbnail_url=url)

    except:
        await interaction.edit_original_response(content=Res.trad(interaction=interaction,str='message_erro_mongodb').format(interaction.user.id))  
















#-----------------COMANDOS----------------------

  #GRUPO DE COMANDOS BRAIXENCOIN
  gravetocoin = app_commands.Group(name="gravetos",description="Comandos de gravetos do Brix.",allowed_installs=app_commands.AppInstallationType(guild=True,user=True),allowed_contexts=app_commands.AppCommandContext(guild=True, dm_channel=True, private_channel=True))


  #comando transações de braixencoin do usuario
  @gravetocoin.command(name="transações", description='🪵⠂Extrato de uso dos Gravetos.')
  async def gravetocointransacoes(self, interaction: discord.Interaction):
    if await Res.print_brix(comando="gravetocointransacoes",interaction=interaction):
        return
    
    await self.mostrar_transações(interaction=interaction,moeda="graveto")












  #GRUPO DE COMANDOS BRAIXENCOIN
  braixencoin = app_commands.Group(name="bc",description="Comandos de braixencoin do Brix.",allowed_installs=app_commands.AppInstallationType(guild=True,user=True),allowed_contexts=app_commands.AppCommandContext(guild=True, dm_channel=True, private_channel=True))




  #Comando Daily
  @braixencoin.command(name="daily", description='💰⠂Colete sua BraixenCoin diaria!')
  async def daily(self, interaction: discord.Interaction):
    if await Res.print_brix(comando="bcdaily",interaction=interaction):
        return
    if interaction.guild is None:
        await interaction.response.send_message(Res.trad(interaction=interaction,str="message_daily_errodm"),delete_after=20)
        return
    else:
        membro = interaction.user
        await interaction.response.defer()
        fuso = pytz.timezone('America/Sao_Paulo')
        now = datetime.datetime.now().astimezone(fuso)
        datahoje = now.strftime("%d/%m/%Y")
        try:
            dados_do_membro = BancoUsuarios.insert_document(membro)
            gravetosaldo = dados_do_membro['graveto']
        except:
            await interaction.followup.send(Res.trad(interaction= interaction, str='message_erro_mongodb').format(interaction.user.id),ephemeral=True)
            return
        try:
            daily = dados_do_membro['date-daily']
        except:
            daily = None
        try:
            premium = dados_do_membro['premium']
        except:
            premium = False
        if daily is None or daily != datahoje:
            saldo = dados_do_membro['braixencoin']
            saldoganho = random.randint(700,2200)
            if premium != False:
                saldoganho = saldoganho *4
                gravetoganho = random.randint(120,350)
                graveto = gravetoganho + gravetosaldo
                messagepremium = Res.trad(interaction= interaction, str='message_premium_daily').format(gravetoganho,graveto)
            else:
                graveto = gravetosaldo

            if interaction.guild.id == BH_id:
                vip = interaction.guild.get_role(970848984669233162)
                boost = interaction.guild.get_role(899819290503573515)
                                    
                if boost in membro.roles:
                    saldoganho = saldoganho + 10000
                    saldonovo = saldo + saldoganho
                    messagem = Res.trad(interaction= interaction, str='message_daily_confirmacao_bonus').format(saldoganho,saldonovo,10000,boost.name)
                elif vip in membro.roles:
                    saldoganho = saldoganho + 4000
                    saldonovo = saldo + saldoganho
                    messagem = Res.trad(interaction= interaction, str='message_daily_confirmacao_bonus').format(saldoganho,saldonovo,4000,vip.name)
                else:
                    saldonovo = saldo + saldoganho
                    messagem = Res.trad(interaction= interaction, str='message_daily_confirmacao').format(saldoganho,saldonovo)
            else:
                saldonovo = saldo + saldoganho
                messagem = Res.trad(interaction= interaction, str='message_daily_confirmacao').format(saldoganho,saldonovo)
            item = {"braixencoin": saldonovo,"date-daily": datahoje,"graveto": graveto}
            try:
                BancoUsuarios.update_document(membro,item)
            except:
                await interaction.followup.send(Res.trad(interaction= interaction, str='message_erro_mongodb').format(interaction.user.id),ephemeral=True)
                return
            if premium != False:
                BancoFinanceiro.registrar_transacao(user_id=membro.id,tipo="ganho",origem="daily",valor=gravetoganho,moeda="graveto",descricao="Recompensa diária premium")
                BancoFinanceiro.registrar_transacao(user_id=membro.id,tipo="ganho",origem="daily",valor=saldoganho,moeda="braixencoin",descricao="Recompensa diária premium")
                await interaction.followup.send(f"{messagem}\n{messagepremium}")
                return
            else:
                BancoFinanceiro.registrar_transacao(user_id=membro.id,tipo="ganho",origem="daily",valor=saldoganho,moeda="braixencoin",descricao="Recompensa diária")
                await interaction.followup.send(messagem)
                return
        else:
            data_coleta_daily = datetime.datetime.now().astimezone(fuso).replace(hour=0, minute=0, second=0) + datetime.timedelta(days=1)
            await interaction.followup.send(Res.trad(interaction= interaction, str='message_daily_negacao').format(int(data_coleta_daily.timestamp())),ephemeral=True)
            return

  

















  #comando saldo de usuario
  @braixencoin.command(name="saldo", description='💰⠂Consulte quantas BraixenCoin você ou alguém tem.')
  @app_commands.describe(membro="informe um membro")
  async def usersaldo(self, interaction: discord.Interaction,membro: discord.User = None):
    if await Res.print_brix(comando="bcsaldo",interaction=interaction):
        return
    await interaction.response.defer()
    if membro is None:
        membro = interaction.user
    try:
        dado = BancoUsuarios.insert_document(membro)
        await interaction.followup.send(Res.trad(interaction= interaction, str="message_financeiro_saldo").format(membro.mention,dado['braixencoin'],dado['graveto']))    
    except:
        await interaction.followup.send(Res.trad(interaction= interaction, str='message_erro_mongodb').format(interaction.user.id),ephemeral=True)












  #comando transações de braixencoin do usuario
  @braixencoin.command(name="transações", description='💰⠂Extrato de uso da BraixenCoin.')
  async def bctransacoes(self, interaction: discord.Interaction):
    if await Res.print_brix(comando="bctransacoes",interaction=interaction):
        return
    
    await self.mostrar_transações(interaction=interaction,moeda="braixencoin")














  #Comando Pagamento
  @braixencoin.command(name="pagar", description='💰⠂Pague um valor em BraixenCoin para alguém.')
  @app_commands.checks.cooldown(4,3600)
  @app_commands.describe(membro = "Informe um membro",quantidade = "quantidade de BraixenCoin")
  async def pay(self, interaction: discord.Interaction,membro:discord.User,quantidade:int):
        if await Res.print_brix(comando="bcpagar",interaction=interaction , condicao=f"{membro.name} - {membro.id}  -  {quantidade}"):
            return
        #await interaction.response.defer()
        if interaction.user == membro: #verifica se o membro que interagil é o mesmo que foi passado
            await interaction.response.send_message(Res.trad(interaction= interaction, str="message_erro_autopagar"),delete_after=30,ephemeral=True)
            return
        if quantidade <= 0 : # verifica se passaram 0 como valor
            await interaction.response.send_message(Res.trad(interaction= interaction, str="message_erro_pagarzero"),delete_after=30,ephemeral=True)
            return
        #Roda o restante do codigo
        try:
            quantidade = int(quantidade)
        except:
            await interaction.response.send_message(Res.trad(interaction= interaction, str='message_financeiro_pagamento_invalido').format(interaction.user.id),delete_after=30,ephemeral=True)
            return
        try: #tentativa de coleta de informações no banco de dados
            dados_do_membro = BancoUsuarios.insert_document(interaction.user)
            saldo_pagante = dados_do_membro['braixencoin']
            if quantidade > saldo_pagante: #verifica se o membro tem saldo o suficiente para pagar
                await interaction.response.send_message(Res.trad(interaction= interaction, str="message_financeiro_saldo_insuficiente"),delete_after=30,ephemeral=True)
                return

            botão = discord.ui.View()
            botãoconfirmação = discord.ui.Button(label=Res.trad(interaction=interaction, str='botão_confirmartransacao'),style=discord.ButtonStyle.green,emoji="<:Braix_Glass:1272664403296260126>")
            botão.add_item(item=botãoconfirmação)
            botãoconfirmação.callback = partial(self.confirmacao_transferencia,membro= membro,quantidade = quantidade,saldo_pagante = saldo_pagante ,originaluser = interaction.user)
            await interaction.response.send_message(Res.trad(interaction=interaction, str='message_financeiro_confirmacao_pagamento').format(quantidade,membro.mention),view=botão,delete_after=60)
        except:
            await interaction.response.send_message(Res.trad(interaction= interaction, str='message_erro_mongodb').format(interaction.user.id),ephemeral=True)
            

  @pay.autocomplete("quantidade")
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
  
  @pay.error
  async def on_test_error(self, interaction:discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error,app_commands.CommandOnCooldown):
        await interaction.response.send_message(Res.trad(interaction= interaction, str='message_erro_cooldown').format(int(time.time() + error.retry_after)),delete_after=15, ephemeral= True)


  # COMANDO PARA COMFIRMAR A COMPRAR DE UM ITEM
  @commands.Cog.listener()
  async def confirmacao_transferencia(self,interaction, membro, quantidade, saldo_pagante, originaluser):
    if interaction.user != originaluser:
        await interaction.response.send_message(Res.trad(interaction=interaction, str="message_erro_interacaoalheia"), delete_after=20, ephemeral=True)
        return
    try:
        view = discord.ui.View.from_message(interaction.message)
        for button in view.children:
                button.disabled = True

            # Atualiza a resposta original para refletir os botões desativados
        await interaction.response.edit_message(view=view)
        dados_do_membro2 = BancoUsuarios.insert_document(membro)
        saldomembro2 = dados_do_membro2['braixencoin']

    except:
        await interaction.followup.send(Res.trad(interaction= interaction, str='message_erro_mongodb').format(interaction.user.id),ephemeral=True)
        return
    if membro.id == self.client.user.id: #verifica se tão pagando para o bot
        
        if saldomembro2 < 1000000: #verifica o saldo do bot é dá retorno diferente
            try:
                BancoUsuarios.update_inc(interaction.user, {"braixencoin" : - quantidade })
                BancoFinanceiro.registrar_transacao(user_id=interaction.user.id,tipo="gasto",origem="bc pagar",valor=quantidade,moeda="braixencoin",descricao=f"Pagamento feito para {membro.name} - {membro.id}")

                BancoUsuarios.update_inc(membro, {"braixencoin" : quantidade })
                BancoFinanceiro.registrar_transacao(user_id=membro.id,tipo="ganho",origem="bc pagar",valor=quantidade,moeda="braixencoin",descricao=f"Pagamento recebido por {interaction.user.name} - {interaction.user.id}")

            except:await interaction.followup.send(Res.trad(interaction= interaction, str='message_erro_mongodb').format(interaction.user.id),ephemeral=True)
            await interaction.followup.send(f"{Res.trad(interaction= interaction, str='message_financeiro_pagamento_sucesso').format(membro.mention,quantidade,saldo_pagante-quantidade,membro.mention,saldomembro2+quantidade)}\n{random.choice(Res.trad(interaction= interaction, str='message_financeiro_brix_agradecimento_-30k'))}")
            return
        else: #retorno abusivo de brix no saldo
            saldoexigido = saldomembro2 * 0.1
            if saldoexigido > quantidade: #se for menor que o bot deseja ele nega
                await interaction.followup.send(random.choice(Res.trad(interaction= interaction, str="message_financeiro_brix_negative")).format(membro.mention))
                return
            else:
                try: # Registro dos valores no bot
                    BancoUsuarios.update_inc(interaction.user, {"braixencoin" : - quantidade })
                    BancoFinanceiro.registrar_transacao(user_id=interaction.user.id,tipo="gasto",origem="bc pagar",valor=quantidade,moeda="braixencoin",descricao=f"Pagamento feito para {membro.name} - {membro.id}")

                    BancoUsuarios.update_inc(membro, {"braixencoin" : quantidade })
                    BancoFinanceiro.registrar_transacao(user_id=membro.id,tipo="ganho",origem="bc pagar",valor=quantidade,moeda="braixencoin",descricao=f"Pagamento recebido por {interaction.user.name} - {interaction.user.id}")

                except:await interaction.followup.send(Res.trad(interaction= interaction, str='message_erro_mongodb').format(interaction.user.id),ephemeral=True)
                await interaction.followup.send(f"{Res.trad(interaction= interaction, str='message_financeiro_pagamento_sucesso').format(membro.mention,quantidade,saldo_pagante-quantidade , membro.mention , saldomembro2+quantidade)}\n{random.choice(Res.trad(interaction= interaction, str='message_financeiro_brix_agradecimento_+30k'))}")
                return
    else: #else para salvar direto nos membros normais
        try:
            BancoUsuarios.update_inc(interaction.user, {"braixencoin" : - quantidade })
            BancoFinanceiro.registrar_transacao(user_id=interaction.user.id,tipo="gasto",origem="bc pagar",valor=quantidade,moeda="braixencoin",descricao=f"Pagamento feito para {membro.name} - {membro.id}")

            BancoUsuarios.update_inc(membro, {"braixencoin" : quantidade })
            BancoFinanceiro.registrar_transacao(user_id=membro.id,tipo="ganho",origem="bc pagar",valor=quantidade,moeda="braixencoin",descricao=f"Pagamento recebido por {interaction.user.name} - {interaction.user.id}")

        except:await interaction.followup.send(Res.trad(interaction= interaction, str='message_erro_mongodb').format(interaction.user.id),ephemeral=True)
        await interaction.followup.send(Res.trad(interaction= interaction, str="message_financeiro_pagamento_sucesso").format(membro.mention,quantidade,saldo_pagante-quantidade ,membro.mention,saldomembro2+quantidade))
                    
        try:
            dm_notification = dados_do_membro2['dm-notification']
        except:
            dm_notification = True
            item = {"dm-notification": dm_notification}
            BancoUsuarios.update_document(membro,item)
        if dm_notification is True:
            try:
                resposta = discord.Embed(
                    colour=discord.Color.yellow(),
                    description=random.choice(Res.trad(user= membro, str="message_financeiro_pagamento_sucesso_dm")).format(interaction.user.mention,quantidade,saldomembro2+quantidade)
                )
                resposta.set_author(name=f"{interaction.user.name}",icon_url=f"{interaction.user.avatar.url}")
                resposta.set_thumbnail(url="https://i.imgur.com/rsG9pNp.png")
                await membro.send(embed=resposta)
            except:
                print("erro no envio de dm para informar pagamento")
                return
        else:
            print("membro não recebe notificações via DM")
            return
  














  #COMANDO BRAIXENCOIN TOPS
  @braixencoin.command(name="tops",description='💰⠂veja o Rank dos mais ricos!')
  async def braixencointops(self,interaction: discord.Interaction):
        if await Res.print_brix(comando="bctops",interaction=interaction):
            return
        await interaction.response.defer()
        filtro = {  "braixencoin": {"$exists": True, "$gt": 0}, "ban": {"$exists": False} }
        dados_ordenados = BancoUsuarios.select_many_document(filtro).sort('braixencoin',-1)[:500]
        classificacao_dados = [(index + 1, int(dados['_id']), int(dados['braixencoin'])) for index, dados in enumerate(dados_ordenados)]
        blocos_classificacao = [classificacao_dados[i:i + 5] for i in range(0, len(classificacao_dados), 5)]
        await exibirtops(self,interaction,blocos_classificacao,1,originaluser=interaction.user,background=self.bccoin_tops_background)














  #COMANDO DE AJUDA SOBRE AS BRAIXENCOIN
  @braixencoin.command(name="ajuda",description='💰⠂Ajuda sobre a BraixenCoin!')
  async def braixencoinahelp(self,interaction: discord.Interaction):
    if await Res.print_brix(comando="bchelp",interaction=interaction):
      return
    resposta = discord.Embed(   colour=discord.Color.yellow(),  description=Res.trad(interaction=interaction,str="message_financeiro_help")    )
    resposta.set_thumbnail(url="https://i.imgur.com/rsG9pNp.png")
    await interaction.response.send_message(embed=resposta)
  
















#COMANDO DE CAÇADA POKÉMON ONDE O USUARIO INICIA A CAÇADA E AGUARDA 3 HORAS PARA RESGATAR
  @braixencoin.command(name="caçar", description="🦊⠂Inicie ou resgate sua caçada especial!")
  @app_commands.checks.cooldown(1, 10)
  async def cacar(self, interaction: discord.Interaction):
    if await Res.print_brix(comando="bccacar", interaction=interaction):
        return
    if interaction.guild is None:
        await interaction.response.send_message(
            Res.trad(interaction=interaction, str="message_erro_onlyservers"),
            delete_after=20
        )
        return

    now = datetime.datetime.now()
    try:
        dados_do_membro = BancoUsuarios.insert_document(interaction.user)
        data_resgate = dados_do_membro.get('resgate-cacar')
    except Exception:
        await interaction.response.send_message(
            Res.trad(interaction=interaction, str='message_erro_mongodb'),
            ephemeral=True
        )
        return

    view = discord.ui.View()

    if not data_resgate:
        # Estado inicial: botão de iniciar
        botao = discord.ui.Button( label=Res.trad(interaction=interaction, str='message_botão_iniciar_caçada'), style=discord.ButtonStyle.green )
        view.add_item(botao)
        resposta = discord.Embed( colour=discord.Color.yellow(), description=Res.trad(interaction=interaction, str='message_financeiro_iniciar_caçada') )
        resposta.set_thumbnail(url="https://64.media.tumblr.com/94ba1db8eeb3f9e9b2ee8a883da22f8a/d28975f772fd9d9f-f7/s540x810/987e2c9d6855bdffeccd60c2edeae8fa8924038c.pnj")
        await interaction.response.send_message(embed=resposta, view=view)
        botao.callback = partial(self.gerenciar_cacar_callback, membro=interaction.user)

    elif now >= data_resgate:
        # Tempo passou, botão de concluir
        botao = discord.ui.Button( label=Res.trad(interaction=interaction, str='message_botão_concluir_caçada'), style=discord.ButtonStyle.primary )
        view.add_item(botao)
        resposta = discord.Embed( colour=discord.Color.yellow(), description=Res.trad(interaction=interaction, str='message_financeiro_Concluir_caçada') )
        resposta.set_thumbnail(url="https://64.media.tumblr.com/94ba1db8eeb3f9e9b2ee8a883da22f8a/d28975f772fd9d9f-f7/s540x810/987e2c9d6855bdffeccd60c2edeae8fa8924038c.pnj")
        await interaction.response.send_message(embed=resposta, view=view)
        botao.callback = partial(self.gerenciar_cacar_callback, membro=interaction.user)

    else:
        # Ainda não chegou a hora do resgate
        botao_tempo = discord.ui.Button( label=Res.trad(interaction=interaction, str='message_botão_andamento_caçada'), style=discord.ButtonStyle.blurple, disabled=True )
        view.add_item(botao_tempo)
        resposta = discord.Embed( colour=discord.Color.yellow(), description=Res.trad(interaction=interaction, str='message_financeiro_andamento_caçada').format(int(data_resgate.timestamp())) )
        resposta.set_thumbnail(url="https://64.media.tumblr.com/94ba1db8eeb3f9e9b2ee8a883da22f8a/d28975f772fd9d9f-f7/s540x810/987e2c9d6855bdffeccd60c2edeae8fa8924038c.pnj")
        await interaction.response.send_message(embed=resposta, view=view)


  async def gerenciar_cacar_callback(self, interaction: discord.Interaction, membro: discord.Member):
    now = datetime.datetime.now()

    if interaction.user != membro:
        await interaction.response.send_message( content=Res.trad(interaction=interaction, str='message_erro_interacaoalheia'), ephemeral=True )
        return

    dados_do_membro = BancoUsuarios.insert_document(membro)
    data_resgate = dados_do_membro.get('resgate-cacar')

    if not data_resgate:
        # ESTADO 0: VERIFICA SE O USUARIO É PREMIUM
        if not await userpremiumcheck(interaction):
            await interaction.response.send_message(  Res.trad(interaction=interaction, str="message_premium_erro"),  ephemeral=True  )
            return  
        
        # ESTADO 1: INICIAR A CAÇADA
        tempo_espera = datetime.timedelta(hours=3)
        tempo_para_resgate = now + tempo_espera
        BancoUsuarios.update_document(membro, {"resgate-cacar": tempo_para_resgate})

        view_espera = discord.ui.View()
        botao_tempo = discord.ui.Button( label=Res.trad(interaction=interaction, str='message_botão_andamento_caçada'), style=discord.ButtonStyle.blurple, disabled=True )
        view_espera.add_item(botao_tempo)
        resposta = discord.Embed( colour=discord.Color.yellow(), description=Res.trad(interaction=interaction, str='message_financeiro_andamento_caçada').format(int(tempo_para_resgate.timestamp())) )
        resposta.set_thumbnail(url="https://64.media.tumblr.com/94ba1db8eeb3f9e9b2ee8a883da22f8a/d28975f772fd9d9f-f7/s540x810/987e2c9d6855bdffeccd60c2edeae8fa8924038c.pnj")
        await interaction.response.edit_message(embed=resposta, view=view_espera)

    elif now >= data_resgate:
        # TEMPO SUFICIENTE: ENTREGAR RECOMPENSA
        await interaction.response.defer()

        moedas_ganhas = random.randint(1500, 5000)
        gravetos_ganhos = random.randint(120, 400)

        try:
            BancoUsuarios.update_document(membro, { "braixencoin": dados_do_membro.get('braixencoin', 0) + moedas_ganhas, "graveto": dados_do_membro.get('graveto', 0) + gravetos_ganhos })
            BancoUsuarios.delete_field(membro,{"resgate-cacar": 0})
        except Exception:
            await interaction.followup.send( Res.trad(interaction=interaction, str='message_erro_mongodb'), ephemeral=True )
            return

        BancoFinanceiro.registrar_transacao( user_id=membro.id, tipo="ganho", origem="cacar", valor=moedas_ganhas, moeda="braixencoin", descricao="Recompensa de caçada" )
        BancoFinanceiro.registrar_transacao( user_id=membro.id, tipo="ganho", origem="cacar", valor=gravetos_ganhos, moeda="graveto", descricao="Recompensa de caçada" )

        resposta = discord.Embed( colour=discord.Color.yellow(), description=Res.trad(interaction=interaction, str='message_financeiro_resgate_caçada').format(moedas_ganhas, gravetos_ganhos) )
        resposta.set_thumbnail(url="https://64.media.tumblr.com/94ba1db8eeb3f9e9b2ee8a883da22f8a/d28975f772fd9d9f-f7/s540x810/987e2c9d6855bdffeccd60c2edeae8fa8924038c.pnj")
        await interaction.edit_original_response(embed=resposta, view=None)


  @cacar.error
  async def on_test_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message( Res.trad(interaction=interaction, str='message_erro_cooldown').format(int(time.time() + error.retry_after)), delete_after=15, ephemeral=True )





# TAREFA DE LEMBRETE DE CAÇADAS CONCLUIDAS
  @tasks.loop(minutes=5)
  async def lembretes_cacar(self):
    while True:
        agora = datetime.datetime.now().replace(tzinfo=None)
        usuarios = BancoUsuarios.select_many_document({ "resgate-cacar": {"$gt": agora} })

        # Monta a lista de proximos
        proximos = [  (u["resgate-cacar"].timestamp(), u)  for u in usuarios  if isinstance(u.get("resgate-cacar"), datetime.datetime)  ]

        if not proximos:  # se não tem nada, espera e volta
            await asyncio.sleep(300)
            continue

        proximos.sort(key=lambda x: x[0])
        ts_proximo, _ = proximos[0]

        espera = max(ts_proximo - agora.timestamp(), 5)
        print(f"[caçada] Próximo lembrete em {espera:.0f}s")
        await asyncio.sleep(espera)

        agora_ts = datetime.datetime.now().timestamp()
        for ts, usuario in proximos:
            if ts > agora_ts:
                continue

            user_id = usuario["_id"]
            try:
                membro = self.client.get_user(user_id)
                if membro:
                    resposta = discord.Embed( colour=discord.Color.yellow(), description=Res.trad(user=membro, str='message_financeiro_resgate_avisodm') )
                    resposta.set_thumbnail(url="https://64.media.tumblr.com/94ba1db8eeb3f9e9b2ee8a883da22f8a/d28975f772fd9d9f-f7/s540x810/987e2c9d6855bdffeccd60c2edeae8fa8924038c.pnj")
        
                    await membro.send( embed= resposta)
            except:
                pass

















#GRUPO DE COMANDOS DE APOSTAS VINCULADO A BRAIXENCOIN
  aposta = app_commands.Group(name="apostas", description="Comandos de aposta do sistema financeiro de Brix",parent=braixencoin,allowed_installs=app_commands.AppInstallationType(guild=True,user=True),allowed_contexts=app_commands.AppCommandContext(guild=True, dm_channel=True, private_channel=True))








  #COMANDO CARA/COROA DE APOSTA
  @aposta.command(name="girarmoeda",description="💰⠂Aposte sua sorte na moeda e ganhe BraixenCoin.")
  @app_commands.describe(moeda="Selecione o lado da moeda...",valor="Indique o valor da aposta...")
  @app_commands.checks.cooldown(1,180)
  @app_commands.choices(moeda=[app_commands.Choice(name="cara", value="cara"),app_commands.Choice(name="coroa", value="coroa"),])
  async def coinflipbet(self, interaction:discord.Interaction,valor:int,moeda:app_commands.Choice[str]):
      if await Res.print_brix(comando="coinflipbet",interaction=interaction):
        return
      await interaction.response.defer()
      try:
        dados_do_membro = BancoUsuarios.insert_document(interaction.user)
        saldo = dados_do_membro['braixencoin']
        
        # Determinar limite
        limite = 20000 if await userpremiumcheck(interaction) else 10000

        # Ajustar valor para o limite se necessário
        if valor > limite:
            valor = limite

        if saldo < valor:
            await interaction.followup.send(Res.trad(interaction= interaction, str='message_financeiro_saldo_insuficiente'))
            return
        if valor <= 0:
            await interaction.followup.send(Res.trad(interaction= interaction, str='message_financeiro_zero'))
            return
        #if valor > 10000:
        #    await interaction.followup.send(Res.trad(interaction= interaction, str='message_financeiro_aposta_limite'))
        #    return
        sorteiobot = ["cara","coroa"]
        moedasorteada = random.choice(sorteiobot)
        if moeda.value == moedasorteada:
            saldonovo = valor * 2
            mensagem = random.choice(Res.trad(interaction= interaction, str='message_financeiro_aposta_acerto')).format(saldonovo , saldonovo+saldo)
            BancoFinanceiro.registrar_transacao(user_id=interaction.user.id,tipo="ganho",origem="aposta coinflip",valor=saldonovo,moeda="braixencoin",descricao=f"aposta feita no brix")
            await asyncio.sleep(0.1)
        else:
            saldonovo = - valor
            mensagem = random.choice(Res.trad(interaction= interaction, str='message_financeiro_aposta_erro')).format(moedasorteada,saldonovo+saldo)
            BancoFinanceiro.registrar_transacao(user_id=interaction.user.id,tipo="gasto",origem="aposta coinflip",valor=valor,moeda="braixencoin",descricao=f"aposta feita no brix")
            await asyncio.sleep(0.1)
        
        BancoUsuarios.update_inc(interaction.user, {"braixencoin" : saldonovo })

        embed = discord.Embed(colour=discord.Color.yellow(), description=mensagem )
        if moedasorteada == "cara":
            embed.set_thumbnail(url="https://i.imgur.com/rsG9pNp.png")
        else:
            embed.set_thumbnail(url="https://i.imgur.com/5shod8h.png")
        await interaction.followup.send(embed=embed)

      except:await interaction.followup.send(Res.trad(interaction= interaction, str='message_erro_mongodb').format(interaction.user.id),ephemeral=True)

  @coinflipbet.error
  async def on_test_error(self, interaction:discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error,app_commands.CommandOnCooldown):
        await interaction.response.send_message(Res.trad(interaction= interaction, str='message_erro_cooldown').format(int(time.time() + error.retry_after)),delete_after=15, ephemeral= True)
  















  #COMANDO Braixen Loteria Help
  @aposta.command(name="braixenloteria-ajuda",description="💰⠂veja ajuda sobre o BraixenLoteria.")
  async def braixenloteriahelp(self, interaction:discord.Interaction):
      if await Res.print_brix(comando="braixenloteriahelp",interaction=interaction):
        return
      await interaction.response.send_message(Res.trad(interaction= interaction, str='message_financeiro_braixenloteria_help'),delete_after=30)
      return
      











  #COMANDO Braixen Loteria
  @aposta.command(name="braixenloteria",description="💰⠂Compre uma raspadinha e tente a sorte de ganhar algo.")
  @app_commands.checks.cooldown(1,60)
  async def braixenloteria(self, interaction:discord.Interaction):
    if await Res.print_brix(comando="braixenloteria",interaction=interaction):
        return
    await interaction.response.defer()
    try:
        dados_do_membro = BancoUsuarios.insert_document(interaction.user)
        saldo = dados_do_membro['braixencoin']
        if saldo < 600:
            await interaction.followup.send(Res.trad(interaction= interaction, str='message_financeiro_saldo_insuficiente'))
            return
        chancedevitoria = random.randint(1,20) # controle de chance de vitoria, variavel vai de 1 a 20
        if chancedevitoria != 1: # verifica se a variavel chance de vitoria é igual a 1 fazendo isso garante apenas 5% de sucesso
            sorteador = random.randint(0,5)
        else:
            sorteador = random.randint(6,10)
        lista = []
        for i in range(10):
            if sorteador >= i + 1:
                lista.append("<:BH_Braix:1154338509839143023>")
            else:
                lista.append("<:BH_Braix_derp:1154338588062908436>")
        #calcula o valor que será atualizado no banco de dados igual ou menor que 5 só desconta o custo do ticket
        if sorteador <= 5:
            saldonovo = - 600
        elif sorteador == 6:
            saldonovo =  + 100
        elif sorteador == 7:
            saldonovo =  + 500
        elif sorteador == 8:
            saldonovo =  + 1000
        elif sorteador == 9:
            saldonovo =  + 10000
        elif sorteador == 10:
            saldonovo =  + 50000
        
        if sorteador <= 5:
            tipo="gasto"
        else:
            tipo="ganho"
        BancoUsuarios.update_inc(interaction.user, {"braixencoin" : saldonovo })
        BancoFinanceiro.registrar_transacao(user_id=interaction.user.id,tipo=tipo,origem="aposta braixenloteria",valor=abs(saldonovo),moeda="braixencoin",descricao=f"aposta feita no brix")
        random.shuffle(lista)
        mensagem = ''.join(lista)
        await interaction.followup.send(Res.trad(interaction= interaction, str='message_financeiro_braixenloteria').format(mensagem))
    except:await interaction.followup.send(Res.trad(interaction= interaction, str='message_erro_mongodb').format(interaction.user.id),ephemeral=True)        

  @braixenloteria.error
  async def on_test_error(self, interaction:discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error,app_commands.CommandOnCooldown):
        await interaction.response.send_message(Res.trad(interaction= interaction, str='message_erro_cooldown').format(int(time.time() + error.retry_after)),delete_after=15, ephemeral= True)















  @aposta.command(name="quem-e-esse-pokemon", description="💰⠂Aposte sua sorte e tente adivinhar o Pokémon!")
  @app_commands.describe(valor="Indique o valor da aposta...")
  @app_commands.checks.cooldown(1, 500)
  async def quem_e_esse_pokemon(self, interaction: discord.Interaction, valor: int):
    if await Res.print_brix(comando="quem-e-esse-pokemon",interaction=interaction):
        return
    await interaction.response.defer()
    dados_do_membro = BancoUsuarios.insert_document(interaction.user)
    saldo = dados_do_membro['braixencoin']

    # Determinar limite
    limite = 20000 if await userpremiumcheck(interaction) else 10000
    # Ajustar valor para o limite se necessário
    if valor > limite:
        valor = limite

    if saldo < valor:
        await interaction.followup.send(Res.trad(interaction= interaction, str='message_financeiro_saldo_insuficiente'))
        return
    if valor <= 0:
        await interaction.followup.send(Res.trad(interaction= interaction, str='message_financeiro_zero'))
        return
    
    saldoatual = saldo - valor
    await self.start_game(interaction, valor, saldoatual ,  interaction.user)




    # INICIAR JOGO QUEM È ESSE POKÈMON    
  async def start_game(self, interaction: discord.Interaction, aposta: int, saldoatual: int, original_user: discord.User):
    todos_pokemon = await get_all_pokemon()
    while True:
        p = random.choice(todos_pokemon)
        imagempokemon = p.get('front_default')
        if imagempokemon:
            try:
                # Usa o helper com cache
                img = get_pokemon_sprite( url=imagempokemon, pokemon=p['id'], shiny=False )

                # converte pra bytes (igual você fazia com requests.content)
                buffer = io.BytesIO()
                img.save(buffer, format="PNG")
                res = buffer.getvalue()
                break

            except Exception as e:
                print(f"[ERRO] Falha ao carregar sprite com cache: {e}")
                continue

    nome_correto = p['name']

    # Criar alternativas
    alternativas = [nome_correto]
    while len(alternativas) < 4:
        fake = random.choice(todos_pokemon)['name']
        if fake != nome_correto and fake not in alternativas:
            alternativas.append(fake)
    random.shuffle(alternativas)

    buffer = await self.criar_art(res, True)

    # Criar view com botões
    view = discord.ui.View()
    for nome in alternativas:
        botao = discord.ui.Button(label=nome.capitalize(), style=discord.ButtonStyle.secondary)
        botao.callback = partial(self.verificar_resposta, original_user=original_user, resposta_usuario=nome, resposta_correta=nome_correto, aposta=aposta, saldoatual=saldoatual, res=res)
        view.add_item(botao)

    temporesposta = datetime.datetime.now() + datetime.timedelta(seconds=15)
    mensagem = await interaction.followup.send(
        content=Res.trad(interaction=interaction, str='message_financeiro_pokemon_inicio').format(int(temporesposta.timestamp())),
        files=[discord.File(fp=buffer, filename=f"quem-é-esse-pokémon.png")],
        view=view
    )
    BancoUsuarios.update_inc(interaction.user, {"braixencoin": -aposta})
    BancoFinanceiro.registrar_transacao( user_id=interaction.user.id, tipo="gasto", origem="aposta Quem é o Pokémon", valor=aposta, moeda="braixencoin",        descricao=f"aposta feita no brix" )
    task = asyncio.create_task(self.timeout_jogo(mensagem, original_user, nome_correto, res))
    self.jogos_em_andamento[mensagem.id] = task

  # VERIFICAR RESPOSTA JOGO QUEM È ESSE POKÈMON
  async def verificar_resposta(self, interaction: discord.Interaction, original_user: discord.User, resposta_usuario: str, resposta_correta: str, aposta: int , saldoatual: int , res):
    if interaction.user != original_user:
        await interaction.response.send_message(content=Res.trad(interaction=interaction, str='message_erro_interacaoalheia'), ephemeral=True)
        return
    task = self.jogos_em_andamento.pop(interaction.message.id, None)
    if task:
        task.cancel()
    await interaction.response.defer()
    #self.jogos_em_andamento[interaction.message.id].cancel()
    #del self.jogos_em_andamento[interaction.message.id]
    
    buffer = await self.criar_art(res, False)
    if resposta_usuario.lower() == resposta_correta.lower():
        saldoganho = aposta*2
        BancoUsuarios.update_inc(interaction.user, {"braixencoin" : saldoganho })
        BancoFinanceiro.registrar_transacao(user_id=interaction.user.id,tipo="ganho",origem="aposta Quem è o Pokémon",valor=saldoganho,moeda="braixencoin",descricao=f"aposta feita no brix")

        await interaction.edit_original_response(content=Res.trad(interaction=interaction, str='message_financeiro_pokemon_acerto').format(saldoganho) , attachments=[discord.File(fp=buffer,filename=f"é-o-{resposta_correta}.png")], view = None)
    else:
        await interaction.edit_original_response(content=Res.trad(interaction=interaction, str='message_financeiro_pokemon_erro').format(resposta_correta.capitalize()) , attachments=[discord.File(fp=buffer,filename=f"é-o-{resposta_correta}.png")] , view = None)

  # TIME OUT JOGO QUEM È ESSE POKÈMON
  async def timeout_jogo(self, mensagem: discord.Message, original_user: discord.User, pokemon:str, res):
    await asyncio.sleep(15)
    try:
        buffer = await self.criar_art(res, False)
        await mensagem.edit(content=Res.trad(user=original_user, str='message_financeiro_pokemon_timeout').format(pokemon),attachments=[discord.File(fp=buffer,filename=f"é-o-{pokemon}.png")], view = None)
        self.jogos_em_andamento.pop(mensagem.id, None)

    except Exception as e:
        print(f"Erro ao encerrar o jogo: {e}")
  

  async def criar_art(self, res, black):
    fundo = Image.new("RGBA", (595, 448), "#ffffff")
    artfundo = Image.open("src/assets/imagens/financeiro/art-aposta-queméessepokémon.png").convert("RGBA")
    fundo.paste(artfundo, (0, 0), artfundo)
    artpokemon = Image.open(io.BytesIO(res)).convert("RGBA")

    if black:
        preto = Image.new("RGBA", artpokemon.size, (0, 0, 0, 255))
        alpha = artpokemon.split()[3]
        artpokemon = Image.composite(preto, Image.new("RGBA", artpokemon.size, (0, 0, 0, 0)), mask=alpha)

    artpokemon = artpokemon.resize((290, 290))
    fundo.paste(artpokemon, (10, 65), artpokemon)

    buffer = io.BytesIO()
    fundo.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

  @quem_e_esse_pokemon.error
  async def on_test_error(self, interaction:discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error,app_commands.CommandOnCooldown):
        await interaction.response.send_message(Res.trad(interaction= interaction, str='message_erro_cooldown').format(int(time.time() + error.retry_after)),delete_after=15, ephemeral= True)



 








































async def setup(client:commands.Bot) -> None:
  await client.add_cog(financeiro(client))