import discord,os,asyncio,time,datetime,pytz,random
from discord.ext import commands,tasks
from functools import partial
from discord import app_commands
from typing import List
from modulos.connection.database import BancoUsuarios
from modulos.essential.respostas import Res
from modulos.essential.exibirTops import exibirtops
from PIL import Image, ImageFont, ImageDraw, ImageOps #IMPORTAÇÂO Py PIL IMAGEM
from dotenv import load_dotenv


#importação
BH_id = int(os.getenv('id_servidor_bh'))






#CLASSE

class financeiro(commands.Cog):
  def __init__(self, client: commands.Bot):
    self.client = client

# CARREGANDO COISAS PADROES DE USO NO SISTEMA DE TOPS DO BOT
    self.tops_recorte_mascara = Image.open("imagens/icons/recorte-redondo.png").resize((44, 44))
    self.bccoin_tops_background = Image.open("imagens/financeiro/backgroud-top-braixencoin.png")
    self.tops_font = ImageFont.truetype("font/PoetsenOne-Regular.ttf", 15)
    self.tops_font_numero = ImageFont.truetype("font/Quick-Fox.ttf", 18)
    self.default_avatar = Image.open("imagens/financeiro/icondefault.png").resize((44, 44))
    





  @commands.Cog.listener()
  async def on_ready(self):
    print("💲  -  Modúlo Financeiro carregado.")
   # fuso = pytz.timezone('America/Sao_Paulo')
    #now = datetime.datetime.now().astimezone(fuso)
   # target_time = now.replace(hour=21, minute=0, second=0, microsecond=0)

   # if now > target_time:
          #  target_time += datetime.timedelta(days=1)
        # Calcula o tempo até o horário alvo
    #time_until_target = target_time - now
        # Agendar a tarefa para iniciar no horário alvo
   # await asyncio.sleep(time_until_target.total_seconds())

    if not self.verificar_daily.is_running():
        self.verificar_daily.start()





    #FUNÇÂO DE VERIFICAÇÃO DE RESGATE DO DAILY
  #@tasks.loop(hours=24) #24H loop
  @tasks.loop(time=datetime.time(hour=21, minute= 0, tzinfo=datetime.timezone(datetime.timedelta(hours=-3))))
  async def verificar_daily(self): 
    try:
        data_verificacao = datetime.datetime.now() - datetime.timedelta(days=30) #30
        print(f"data de verificação daily: {data_verificacao.strftime('%d/%m/%Y')}\n\n")
        filtro = {"date-daily": {"$exists":True}}
        dado = BancoUsuarios.select_many_document(filtro)
        updates = []  # Lista para armazenar dados de atualização
        TotalTaxas = 0
        for membro in dado:
            try:
                if datetime.datetime.strptime(membro['date-daily'],'%d/%m/%Y') < data_verificacao:
                    if membro['date-daily'] == data_verificacao.strftime('%d/%m/%Y'):
                        
                        #fuso = pytz.timezone('America/Sao_Paulo')
                        datanova = datetime.datetime.now() + datetime.timedelta(days=1)
                        try:
                            user = await self.client.fetch_user(membro['_id'])
                            resposta = discord.Embed(
                            colour=discord.Color.yellow(),
                            title=Res.trad(user=user, str='message_daily_impostodm_title'),
                            description=Res.trad(user=user, str='message_daily_impostodm').format(user.mention,membro['braixencoin'],int(datanova.timestamp()))
                            )
                            resposta.set_thumbnail(url="https://i.imgur.com/rsG9pNp.png")
                            resposta.set_footer(text=datetime.datetime.now().strftime('%d/%m/%Y ás %H:%M'))
                            await user.send(embed=resposta)
                            print(f"notificando: {user.id} - {user.name}")
                        except:
                            print(f"dm do usuario {user.name} está fechada ou não foi encontrado")
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
                        print(f"cobrança aplicada: {membro['_id']} tinha {saldo} taxa de {taxa} ficou com {saldonovo}")
            except Exception as e:
                print(f"problemas ao localizar o usuario: {membro['_id']}")
                print(f"Error: {e}")
        
        try:
            #CUSTO APARTAMENTO DO BRIX
            brix = BancoUsuarios.insert_document(self.client.user)
            apartamento = brix['braixencoin'] - 2000
            updates.append({"_id": brix['_id'],"update": {"$set": {"braixencoin": apartamento}}})
            print(f"Um total de {TotalTaxas} BC Foram tirados dos usuarios.")
            print(f"Brix pagou o aluguel do ap com o vini, brix tinha {brix['braixencoin']} e agora ficou com {apartamento}")
        except Exception as e:
            print(f"Error na cobrança do apartamento de brix: {e}")
        # Executa as atualizações em lote
        if updates:
            try:
                result = BancoUsuarios.bulk_update(updates)
                print(f"Atualizações realizadas: {result.modified_count}")
            except Exception as e:
                print(f"Erro ao executar operações em lote: {e}")

    except Exception as e:
        print(f"Error no verificar daily: {e}")
    







#-----------------COMANDOS----------------------



  #GRUPO SERVIDOR
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
                await interaction.followup.send(f"{messagem}\n{messagepremium}")
                return
            else:
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







  #Comando Pagamento
  @braixencoin.command(name="pagar", description='💰⠂Pague um valor em BraixenCoin para alguém.')
  @app_commands.checks.cooldown(4,3600)
  @app_commands.describe(membro = "Informe um membro",quantidade = "quantidade de BraixenCoin")
  async def pay(self, interaction: discord.Interaction,membro:discord.User,quantidade:int):
        if await Res.print_brix(comando="bcpagar",interaction=interaction):
            return
        #await interaction.response.defer()
        if interaction.user == membro: #verifica se o membro que interagil é o mesmo que foi passado
            await interaction.response.send_message(Res.trad(interaction= interaction, str="message_erro_autopagar"),delete_after=30,ephemeral=True)
            return
        elif quantidade == 0 : # verifica se passaram 0 como valor
            await interaction.response.send_message(Res.trad(interaction= interaction, str="message_erro_pagarzero"),delete_after=30,ephemeral=True)
            return
        else: #Roda o restante do codigo
            try:
                quantidade = int(quantidade)
            except:
                await interaction.response.send_message(Res.trad(interaction= interaction, str='message_financeiro_pagamento_invalido').format(interaction.user.id),delete_after=30,ephemeral=True)
                return
            try: #tentativa de coleta de informações no banco de dados
                dados_do_membro = BancoUsuarios.insert_document(interaction.user)
                saldo1 = dados_do_membro['braixencoin']
                if quantidade > saldo1: #verifica se o membro tem saldo o suficiente para pagar
                    await interaction.response.send_message(Res.trad(interaction= interaction, str="message_financeiro_saldo_insuficiente"),delete_after=30,ephemeral=True)
                    return

                botão = discord.ui.View()
                botãoconfirmação = discord.ui.Button(label=Res.trad(interaction=interaction, str='botão_confirmartransacao'),style=discord.ButtonStyle.green,emoji="<:Braix_Glass:1272664403296260126>")
                botão.add_item(item=botãoconfirmação)
                botãoconfirmação.callback = partial(self.confirmacao_transferencia,membro= membro,quantidade = quantidade,originaluser = interaction.user)
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

        sugestao = [
                app_commands.Choice(
                    name=f"{int(valor):_} BraixenCoin".replace("_", "."),
                    value=int(valor),
                )
        ]
        return sugestao
  
  @pay.error
  async def on_test_error(self, interaction:discord.Integration, error: app_commands.AppCommandError):
    if isinstance(error,app_commands.CommandOnCooldown):
        await interaction.response.send_message(Res.trad(interaction= interaction, str='message_erro_cooldown').format(int(time.time() + error.retry_after)),delete_after=15, ephemeral= True)


  # COMANDO PARA COMFIRMAR A COMPRAR DE UM ITEM
  @commands.Cog.listener()
  async def confirmacao_transferencia(self,interaction, membro, quantidade, originaluser):
    if interaction.user != originaluser:
        await interaction.response.send_message(Res.trad(interaction=interaction, str="message_erro_interacaoalheia"), delete_after=20, ephemeral=True)
        return
    try:
        view = discord.ui.View.from_message(interaction.message)
        for button in view.children:
                button.disabled = True

            # Atualiza a resposta original para refletir os botões desativados
        await interaction.response.edit_message(view=view)
        dados_do_membro = BancoUsuarios.insert_document(interaction.user)
        saldo1 = dados_do_membro['braixencoin']
        dados_do_membro2 = BancoUsuarios.insert_document(membro)
        saldo2 = dados_do_membro2['braixencoin']
               #calculo dos novos valores
        novosaldo1 = saldo1 - quantidade
        novosaldo2 = saldo2 + quantidade
    except:
        await interaction.followup.send(Res.trad(interaction= interaction, str='message_erro_mongodb').format(interaction.user.id),ephemeral=True)
        return
    if membro.id == self.client.user.id: #verifica se tão pagando para o bot
        if saldo2 < 100000: #verifica o saldo do bot é dá retorno diferente
            try:
                BancoUsuarios.update_document(interaction.user,{"braixencoin": novosaldo1})
                BancoUsuarios.update_document(membro,{"braixencoin": novosaldo2})
            except:await interaction.followup.send(Res.trad(interaction= interaction, str='message_erro_mongodb').format(interaction.user.id),ephemeral=True)
            await interaction.followup.send(f"{Res.trad(interaction= interaction, str='message_financeiro_pagamento_sucesso').format(membro.mention,quantidade,novosaldo1,membro.mention,novosaldo2)}\n{random.choice(Res.trad(interaction= interaction, str='message_financeiro_brix_agradecimento_-30k'))}")
        else: #retorno abusivo de brix no saldo
            saldoexigido = saldo2 * 0.1
            print(saldoexigido)
            if saldoexigido > quantidade: #se for menor que o bot deseja ele nega
                await interaction.followup.send(random.choice(Res.trad(interaction= interaction, str="message_financeiro_brix_negative")).format(membro.mention))
                return
            else:
                try: # Registro dos valores no bot
                    BancoUsuarios.update_document(interaction.user,{"braixencoin": novosaldo1})
                    BancoUsuarios.update_document(membro,{"braixencoin": novosaldo2})
                except:await interaction.followup.send(Res.trad(interaction= interaction, str='message_erro_mongodb').format(interaction.user.id),ephemeral=True)
                await interaction.followup.send(f"{Res.trad(interaction= interaction, str='message_financeiro_pagamento_sucesso').format(membro.mention,quantidade,novosaldo1,membro.mention,novosaldo2)}\n{random.choice(Res.trad(interaction= interaction, str='message_financeiro_brix_agradecimento_+30k'))}")

    else: #else para salvar direto nos membros normais
        try:
            BancoUsuarios.update_document(interaction.user,{"braixencoin": novosaldo1})
            BancoUsuarios.update_document(membro,{"braixencoin": novosaldo2})
        except:await interaction.followup.send(Res.trad(interaction= interaction, str='message_erro_mongodb').format(interaction.user.id),ephemeral=True)
        await interaction.followup.send(Res.trad(interaction= interaction, str="message_financeiro_pagamento_sucesso").format(membro.mention,quantidade,novosaldo1,membro.mention,novosaldo2))
                    
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
                    description=random.choice(Res.trad(user= membro, str="message_financeiro_pagamento_sucesso_dm")).format(interaction.user.mention,quantidade,novosaldo2)
                )
                resposta.set_author(name=f"{interaction.user.name}",icon_url=f"{interaction.user.avatar.url}")
                resposta.set_thumbnail(url="https://cdn.discordapp.com/emojis/1182695452731265126")
                await membro.send(embed=resposta)
            except:
                print("erro no envio de dm para informar pagamento")
                return
        else:
            print("membro não recebe notificações via DM")
            return
  














  #COMANDO USUARIO TOP REP
  @braixencoin.command(name="tops",description='💰⠂veja o Rank dos mais ricos!')
  async def braixencointops(self,interaction: discord.Integration):
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
  async def braixencoinahelp(self,interaction: discord.Integration):
    if await Res.print_brix(comando="bchelp",interaction=interaction):
      return
    resposta = discord.Embed(   colour=discord.Color.yellow(),  description=Res.trad(interaction=interaction,str="message_financeiro_help")    )
    resposta.set_thumbnail(url="https://cdn.discordapp.com/emojis/1182695452731265126")
    await interaction.response.send_message(embed=resposta)
  













  aposta = app_commands.Group(name="apostas", description="Comandos de aposta do sistema financeiro de Brix",parent=braixencoin,allowed_installs=app_commands.AppInstallationType(guild=True,user=True),allowed_contexts=app_commands.AppCommandContext(guild=True, dm_channel=True, private_channel=True))








  #COMANDO CARA/COROA DE APOSTA
  @aposta.command(name="girarmoeda",description="💰⠂Aposte sua sorte na moeda e ganhe BraixenCoin.")
  @app_commands.describe(moeda="Selecione o lado da moeda...",valor="Indique o valor da aposta...")
  @app_commands.checks.cooldown(2,60)
  @app_commands.choices(moeda=[app_commands.Choice(name="cara", value="cara"),app_commands.Choice(name="coroa", value="coroa"),])
  async def coinflipbet(self, interaction:discord.Interaction,valor:int,moeda:app_commands.Choice[str]):
      if await Res.print_brix(comando="coinflipbet",interaction=interaction):
        return
      await interaction.response.defer()
      try:
        dados_do_membro = BancoUsuarios.insert_document(interaction.user)
        saldo = dados_do_membro['braixencoin']
        if saldo < valor:
            await interaction.followup.send(Res.trad(interaction= interaction, str='message_financeiro_saldo_insuficiente'))
            return
        elif valor > 5000:
            await interaction.followup.send(Res.trad(interaction= interaction, str='message_financeiro_aposta_limite'))
            return
        else:
            sorteiobot = ["cara","coroa"]
            moedasorteada = random.choice(sorteiobot)
            print(f"sorteou: {moedasorteada}")
            if moeda.value == moedasorteada:
                valor = valor * 2
                saldonovo = saldo + valor
                mensagem = random.choice(Res.trad(interaction= interaction, str='message_financeiro_aposta_acerto')).format(valor,saldonovo)
                await asyncio.sleep(0.1)
            else:
                saldonovo = saldo - valor
                mensagem = random.choice(Res.trad(interaction= interaction, str='message_financeiro_aposta_erro')).format(moedasorteada,saldonovo)
                await asyncio.sleep(0.1)
            item = {"braixencoin": saldonovo}
            BancoUsuarios.update_document(interaction.user,item)
            embed = discord.Embed(colour=discord.Color.yellow(),
                description=mensagem
            )
            if moedasorteada == "cara":
                embed.set_thumbnail(url="https://i.imgur.com/rsG9pNp.png")
            else:
                embed.set_thumbnail(url="https://i.imgur.com/5shod8h.png")
            await interaction.followup.send(embed=embed)

      except:await interaction.followup.send(Res.trad(interaction= interaction, str='message_erro_mongodb').format(interaction.user.id),ephemeral=True)

  @coinflipbet.error
  async def on_test_error(self, interaction:discord.Integration, error: app_commands.AppCommandError):
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
  @app_commands.checks.cooldown(6,120)
  async def braixenloteria(self, interaction:discord.Interaction):
    if await Res.print_brix(comando="braixenloteria",interaction=interaction):
        return
    await interaction.response.defer()
    try:
        dados_do_membro = BancoUsuarios.insert_document(interaction.user)
        saldo = dados_do_membro['braixencoin']
        if saldo < 150:
            await interaction.followup.send(Res.trad(interaction= interaction, str='message_financeiro_saldo_insuficiente'))
            return
        else:
            chancedevitoria = random.randint(1,10) # controle de chance de vitoria, variavel vai de 1 a 10
            if chancedevitoria <= 9: # verifica se a variavel chance de vitoria é maior ou igual a 8 fazendo isso garante apenas 15% de sucesso
                sorteador = random.randint(0,5)
            else:
                sorteador = random.randint(5,10)
            lista = []
            for i in range(10):
                if sorteador >= i + 1:
                    lista.append("||<:BH_Braix:1154338509839143023>||")
                else:
                    lista.append("||<:BH_Braix_derp:1154338588062908436>||")
            #calcula o valor que será atualizado no banco de dados igual ou menor que 5 só desconta o custo do ticket
            if sorteador <= 5:
                saldonovo = saldo - 150
            elif sorteador == 6:
                saldonovo = saldo + 100
            elif sorteador == 7:
                saldonovo = saldo + 500
            elif sorteador == 8:
                saldonovo = saldo + 1000
            elif sorteador == 9:
                saldonovo = saldo + 10000
            elif sorteador == 10:
                saldonovo = saldo + 50000
            item = {"braixencoin": saldonovo}
            BancoUsuarios.update_document(interaction.user,item)
            random.shuffle(lista)
            mensagem = ''.join(lista)
            await interaction.followup.send(Res.trad(interaction= interaction, str='message_financeiro_braixenloteria').format(mensagem))
            print(f"Usuario {interaction.user.name} liberou o sorteador {sorteador} com chance de vitoria {chancedevitoria} e o saldo foi para {saldonovo}")
    except:await interaction.followup.send(Res.trad(interaction= interaction, str='message_erro_mongodb').format(interaction.user.id),ephemeral=True)        

  @braixenloteria.error
  async def on_test_error(self, interaction:discord.Integration, error: app_commands.AppCommandError):
    if isinstance(error,app_commands.CommandOnCooldown):
        await interaction.response.send_message(Res.trad(interaction= interaction, str='message_erro_cooldown').format(int(time.time() + error.retry_after)),delete_after=15, ephemeral= True)






"""
  @aposta.command(name="quem-e-esse-pokemon", description="💰⠂Aposte sua sorte e tente adivinhar o Pokémon!")
  @app_commands.describe(valor="Indique o valor da aposta...")
  @app_commands.checks.cooldown(2, 60)
  async def quem_e_esse_pokemon(self, interaction: discord.Interaction, valor: int):
        await interaction.response.defer()
        dados_do_membro = BancoUsuarios.insert_document(interaction.user)
        saldo = dados_do_membro['braixencoin']
        if saldo < valor:
            await interaction.followup.send(Res.trad(interaction= interaction, str='message_financeiro_saldo_insuficiente'))
            return
        
        await self.start_game(interaction, valor, interaction.user)

  async def start_game(self, interaction: discord.Interaction, aposta: int, original_user: discord.User):
        
        response = requests.get("https://pokeapi.co/api/v2/pokemon?limit=10000").json()
        pokemon_data = [pokemon['name'] for pokemon in response['results']]  # Lista de nomes de Pokémon (não um conjunto)
        pokemon = random.choice(pokemon_data)  # Escolhe um nome de Pokémon aleatório
        
        dex = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon}/").json()

        imagempokemon = dex['sprites']['other']['home']['front_default']
        nome_oculto = self.ocultar_letras(pokemon)
        view = discord.ui.View()

        botao_tentar = discord.ui.Button(label="Tentar", style=discord.ButtonStyle.primary)
        botao_tentar.callback = partial(self.tentar_adivinhar, original_user=original_user, pokemon=pokemon, aposta=aposta)
        view.add_item(botao_tentar)

        botao_cancelar = discord.ui.Button(label="Cancelar", style=discord.ButtonStyle.danger)
        botao_cancelar.callback = partial(self.cancelar_jogo, original_user=original_user)
        view.add_item(botao_cancelar)

        await interaction.followup.send(f"Quem é esse [Pokémon?]({imagempokemon})\n**{nome_oculto}**", view=view)

  async def tentar_adivinhar(self, interaction: discord.Interaction, original_user: discord.User, pokemon: str, aposta: int):
        if interaction.user != original_user:
            await interaction.response.send_message("Apenas o jogador original pode interagir!", ephemeral=True)
            return

        resposta = interaction.message.content.split("? ")[-1]  # Simples verificação da resposta
        if resposta.lower() == pokemon.lower():
            await interaction.response.send_message(f"Parabéns! Você acertou! Ganhou {aposta * 3} BraixenCoin.")
        else:
            await interaction.response.send_message(f"Errado! O Pokémon era {pokemon}.")

        view = discord.ui.View.from_message(interaction.message)
        for item in view.children:
            item.disabled = True
        await interaction.edit_original_response(view=view)

  async def cancelar_jogo(self, interaction: discord.Interaction, original_user: discord.User):
        if interaction.user != original_user:
            await interaction.response.send_message("Apenas o jogador original pode cancelar!", ephemeral=True)
            return

        view = discord.ui.View.from_message(interaction.message)
        for item in view.children:
            item.disabled = True
        await interaction.edit_original_response(content="Jogo cancelado.", view=view)

  def ocultar_letras(self, nome: str):
        oculto = list(nome)
        indices = random.sample(range(len(nome)), max(1, len(nome) // 2))
        for i in indices:
            oculto[i] = "-"
        return " ".join(oculto)

"""










async def setup(client:commands.Bot) -> None:
  await client.add_cog(financeiro(client))