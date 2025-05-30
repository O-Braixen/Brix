import discord,os,asyncio,time,datetime,pytz,random
from discord.ext import commands,tasks
from discord import app_commands
from modulos.connection.database import BancoUsuarios,BancoServidores
from modulos.essential.respostas import Res
from modulos.essential.usuario import useraniversario,aniversariodefinir
from modulos.admin import addtemproleusuario




class aniversario(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        # CARREGANDO COISAS PADROES DE USO NO SISTEMA DE TOPS DO BOT

        self.fusohorario = pytz.timezone('America/Sao_Paulo')
        #Carrega os menu e adiciona eles
        #foi comentado devido a limitação de 5 menucontext na porra do discord
        self.menu_aniversarioconsulta = app_commands.ContextMenu(name="Aniversário consultar",callback=self.useraniversariomenu,type=discord.AppCommandType.user,allowed_installs=app_commands.AppInstallationType(guild=True,user=True),allowed_contexts=app_commands.AppCommandContext(guild=True, dm_channel=True, private_channel=True))
        self.client.tree.add_command(self.menu_aniversarioconsulta)







      #Remove os menu se necessario
    async def cog_unload(self) -> None:
        self.client.tree.remove_command(self.menu_aniversarioconsulta, type=self.menu_aniversarioconsulta.type)






    @commands.Cog.listener()
    async def on_ready(self):
        print("🎂  -  Modúlo Aniversário carregado.")

        if not self.verificar_aniversariantes.is_running():
            self.verificar_aniversariantes.start()




    #@tasks.loop(hours=24)
    @tasks.loop(time=datetime.time(hour=9 , minute= 0, tzinfo=datetime.timezone(datetime.timedelta(hours=-3))))
    async def verificar_aniversariantes(self):
        # Obtenha a data atual e o ano
        data_atual = datetime.datetime.now().strftime("%d/%m")
        ano_atual = datetime.datetime.now().year
        datadaily = datetime.datetime.now() - datetime.timedelta(days=1)

        # Busque aniversariantes e servidores uma vez
        filtro_aniversario = {"nascimento": {"$regex": data_atual} , "ban": {"$exists": False} }
        aniversariantes = BancoUsuarios.select_many_document(filtro_aniversario)
        
        filtro_servidores = {"aniversario": {"$exists": True}}
        servidores = BancoServidores.select_many_document(filtro_servidores)

        print("🎂 - Iniciando verificação de aniversariantes")

        listaaniversariante = []

        # Processar cada aniversariante (Envio de DMs)
        for membro in aniversariantes:
            aniversariante_id = membro['_id']
            partes_data = membro['nascimento'].split("/")
            ano_nascimento = int(partes_data[2])
            idade = ano_atual - ano_nascimento
            listaaniversariante.append(aniversariante_id)

            try:
                # Enviar DM ao usuário aniversariante
                user = await self.client.fetch_user(aniversariante_id)
                saldodado = 250000
                usuario = BancoUsuarios.insert_document(user)
                saldo = usuario['braixencoin'] + saldodado
                BancoUsuarios.update_document(user, {"braixencoin": saldo, "date-daily": datadaily.strftime("%d/%m/%Y")})

                # Enviar mensagens de parabéns na DM
                mensagem_completa = (Res.trad(user=user, str='message_aniversario_anuncio_dm').format(idade) + "\n\n" + Res.trad(user=user, str='message_aniversario_recompensa_dm').format(saldodado, saldo))
                #dm_tasks = [user.send(Res.trad(user=user, str='message_aniversario_anuncio_dm').format(idade)),  user.send(Res.trad(user=user, str='message_aniversario_recompensa_dm').format(saldodado, saldo))]
                #await asyncio.gather(*dm_tasks)
                await user.send(mensagem_completa)
                print(f"Enviando DM para: {aniversariante_id}")

            except Exception as e:
                print(f"Não foi possível enviar DM para {aniversariante_id}: {str(e)}")

        if listaaniversariante:
            print("🎂 - Iniciando envio para servidores")
            # Enviar mensagens para os servidores com aniversariantes acumulados

            for servidor_info in servidores:
                servidor_id = servidor_info['_id']
                servidor = self.client.get_guild(servidor_id)
                canal = self.client.get_channel(servidor_info['aniversario']['canal'])

                if not servidor or not canal:
                    print(f"Servidor ou canal inválido: {servidor_id}")
                    continue

                # Lista para acumular aniversariantes desse servidor
                aniversariantes_servidor = []

                for membro in listaaniversariante:
                    aniversariante_id = membro
                    membro_servidor = servidor.get_member(aniversariante_id)

                    if membro_servidor:
                        aniversariantes_servidor.append(aniversariante_id)

                # Se houver aniversariantes no servidor, envia uma mensagem acumulada
                if aniversariantes_servidor:
                    try:
                        descricao = ", ".join(f"<@{aniversariante}>" for aniversariante in aniversariantes_servidor)

                        embed = discord.Embed(
                            colour=discord.Color.yellow(),
                            description=random.choice(Res.trad(guild=servidor.id, str='message_aniversario_mensagem_random_server')).format(descricao)
                        )
                        embed.set_thumbnail(url="https://d.furaffinity.net/art/kitsunekotaro/1669349629/1669349629.kitsunekotaro_vesta_is_back.jpg")
                        embed.set_footer(text=Res.trad(guild=servidor.id, str='message_aniversario_mensagem_footer_server'))
                        cargoping = servidor.get_role(servidor_info['aniversario']['cargo'])
                        if cargoping == servidor.default_role:  # Verifica se é @everyone
                            cargo_ping_str = '@everyone'
                        else:
                            cargo_ping_str = cargoping.mention

                        # Enviar a mensagem no canal com os aniversariantes acumulados
                        mensagem_servidor = await canal.send(Res.trad(guild=servidor.id,str='message_aniversario_message_ping').format(descricao,cargo_ping_str),#.format(len(aniversariantes_servidor)),
                            embed=embed
                        )
                        await mensagem_servidor.add_reaction('🎂')

                        # Adicionar cargo temporário, se aplicável, para cada aniversariante
                        if 'destaque' in servidor_info['aniversario']:
                            cargo = servidor.get_role(servidor_info['aniversario']['destaque'])
                            for aniversariante in aniversariantes_servidor:
                                membro_servidor = servidor.get_member(aniversariante)
                                if membro_servidor:
                                    await addtemproleusuario(self, None, membro_servidor, cargo, 15*60*60)

                        print(f"Mensagem acumulada enviada no servidor {servidor.name} para {len(aniversariantes_servidor)} aniversariantes")

                    except Exception as e:
                        print(f"Erro ao enviar mensagem acumulada no servidor {servidor_id}: {str(e)}")
        else:
            print("Nenhum aniversariante encontrado hoje.")
        print("Verificação de aniversariantes finalizada")







    #GRUPO ANIVERSARIO
    aniversario=app_commands.Group(name="aniversário",description="Comandos de aniversario do brix.",allowed_installs=app_commands.AppInstallationType(guild=True,user=True),allowed_contexts=app_commands.AppCommandContext(guild=True, dm_channel=False, private_channel=False))





     #COMANDO DEFINIR ANIVERSARIO
    @aniversario.command(name="definir",description='🎂⠂Defina seu aniversário.')
    @app_commands.describe(dia="2 digitos para o dia",mes="2 digitos para o mês",ano="4 digitos para o ano")
    async def aniversariodefinir(self,interaction: discord.Interaction,dia: int, mes:int, ano:int):
        await interaction.response.defer(ephemeral=True) 
        await aniversariodefinir(interaction,dia,mes,ano)
          



    #COMANDO USUARIO ANIVERSARIO MENU
    async def useraniversariomenu(self,interaction: discord.Interaction, membro: discord.Member):
        if await Res.print_brix(comando="useraniversariomenu",interaction=interaction):
            return
        await interaction.response.defer(ephemeral=True)
        menu = True
        await useraniversario(interaction,membro,menu)




     #COMANDO USUARIO ANIVERSARIO SLASH
    @aniversario.command(name="consultar",description='🎂⠂Consulte o aniversário de alguém.')
    @app_commands.describe(membro="informe um membro")
    async def useraniversarioslash(self,interaction: discord.Interaction,membro: discord.User=None):
        if await Res.print_brix(comando="useraniversarioslash",interaction=interaction):
            return
        await interaction.response.defer()
        menu = False
        await useraniversario(interaction,membro,menu)

















    #GRUPO ANIVERSARIO DE SERVIDOR
    aniversarioservidor=app_commands.Group(name="servidor",description="Comandos de aniversario do brix.",parent=aniversario)




    #Comando Aniversario servidor definir
    @aniversarioservidor.command(name="ativar", description="🎂⠂Defina um canal para lembretes de aniversários.")
    @app_commands.describe(canal="Selecione um canal...",cargoping="Selecione um cargo que será pingado...",cargodestaque = "Selecione um cargo de destaque dos aniversáriantes...")#,idioma = "Selecione um idioma")
    #@app_commands.choices(idioma=[app_commands.Choice(name="Portugues", value="pt-BR"),app_commands.Choice(name="English", value="en-US")])
    async def aniversarioserveranuncioativar(self, interaction: discord.Interaction,canal:discord.TextChannel,cargoping:discord.Role,cargodestaque:discord.Role = None):#,idioma:app_commands.Choice[str]):
        if await Res.print_brix(comando="aniversarioserveranuncioativar",interaction=interaction):
            return
        if interaction.guild is None:
            await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyservers"),delete_after=30,ephemeral=True)
            return
        elif interaction.permissions.manage_guild:
            try:
                if cargodestaque is not None:
                    item = {"aniversario.canal": canal.id,"aniversario.cargo":cargoping.id,"aniversario.destaque" : cargodestaque.id}
                else:
                    item = {"aniversario.canal": canal.id,"aniversario.cargo":cargoping.id}#,"language":idioma.value}
                BancoServidores.update_document(interaction.guild.id,item)
                embed = discord.Embed( colour=discord.Color.yellow(),  title=Res.trad(interaction=interaction,str="message_aniversario_server_title"),  description=Res.trad(interaction=interaction,str="message_aniversario_server_description") )
                embed.set_thumbnail(url="https://d.furaffinity.net/art/kitsunekotaro/1669349629/1669349629.kitsunekotaro_vesta_is_back.jpg")
                mensagemteste = await canal.send(embed=embed)
                await interaction.response.send_message(Res.trad(interaction=interaction,str="message_aniversario_notificacao_ativo"))
                await asyncio.sleep(10)
                await mensagemteste.delete()
            except:
                await interaction.response.send_message(Res.trad(interaction=interaction,str="message_aniversario_notificacao_erro"),delete_after=30,ephemeral=True)
        else:
            await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro"),delete_after=30,ephemeral=True)





#Comando Aniversario servidor definir
    @aniversarioservidor.command(name="desativar", description="🎂⠂Desative o envio de lembretes de aniversários.")
    async def aniversarioserveranunciodesativar(self, interaction: discord.Interaction):
        if await Res.print_brix(comando="aniversarioserveranunciodesativar",interaction=interaction):
            return
        if interaction.guild is None:
            await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyservers"),delete_after=30)
            return
        elif interaction.permissions.manage_guild:
            try:
                item = {"aniversario": 0}
                BancoServidores.delete_field(interaction.guild.id,item)
                await interaction.response.send_message(Res.trad(interaction=interaction,str="message_aniversario_notificacao_desativado"))
            except:
                await interaction.response.send_message(Res.trad(interaction=interaction,str="message_aniversario_notificacao_erro"),delete_after=30,ephemeral=True)
        else:
            await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro"),delete_after=30,ephemeral=True)
    



        #Comando Aniversario servidor definir
    @aniversarioservidor.command(name="status", description="🎂⠂Saiba o Status de aviso desta comunidade.")
    async def aniversarioserveranunciostatus(self, interaction: discord.Interaction):
        if await Res.print_brix(comando="aniversarioserveranunciostatus",interaction=interaction):
            return
        if interaction.guild is None:
            await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyservers"),delete_after=30,ephemeral=True)
            return
        try:
            filtro_servidores = {"_id": interaction.guild.id}
            servidor = BancoServidores.select_many_document(filtro_servidores)
            if 'aniversario' in servidor[0]:
                aniversario = servidor[0]['aniversario']
                # Verifica se os valores existem antes de formatar
                canal = f"<#{aniversario['canal']}>" if 'canal' in aniversario else "-"
                cargo = f"<@&{aniversario['cargo']}>" if 'cargo' in aniversario else "-"
                destaque = f"<@&{aniversario['destaque']}>" if 'destaque' in aniversario else "-"
                resposta = Res.trad(interaction=interaction,str="message_aniversario_server_statusativo").format(canal,cargo,destaque)
            else:
                resposta = Res.trad(interaction=interaction,str="message_aniversario_server_dica")

            embed = discord.Embed( colour=discord.Color.yellow(),  description=resposta )
            embed.set_thumbnail(url="https://d.furaffinity.net/art/kitsunekotaro/1669349629/1669349629.kitsunekotaro_vesta_is_back.jpg")
            await interaction.response.send_message(embed=embed)

        except Exception as e:
            await Res.erro_brix_embed(interaction, str="message_erro_brixsystem", e=e,comando="aniversarioserveranunciostatus")




    #Comando Aniversario servidor definir
    @aniversarioservidor.command(name="aniversáriantes", description="🎂⠂Consulte os proximos aniversáriantes da comunidade.")
    async def aniversarioserverconsultaraniversariantes(self, interaction: discord.Interaction):
        if await Res.print_brix(comando="aniversarioserverconsultaraniversariantes",interaction=interaction):
            return
        if interaction.guild is None:
            await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyservers"),delete_after=30)
            return
        await interaction.response.defer()
        # Obter a data atual
        hoje = datetime.datetime.now().astimezone(self.fusohorario)
        #consulta rapída no sistema de servidores
        servidor = BancoServidores.insert_document(interaction.guild.id)
        if 'aniversario' in servidor:
            dicabrix = Res.trad(interaction=interaction,str="message_aniversario_server_sistemaativo")
        else:
            dicabrix = Res.trad(interaction=interaction,str="message_aniversario_server_dica")
        # Buscar todos os usuários com datas de nascimento válidas
        filtro_aniversario = {"nascimento": {"$ne": "00/00/0000"}}
        aniversariantes = BancoUsuarios.select_many_document(filtro_aniversario)
        # Criar uma lista para os próximos aniversariantes
        proximos_aniversariantes = []
        # Iterar sobre os aniversariantes
        for usuario in aniversariantes:
            aniversario = datetime.datetime.strptime(usuario.get("nascimento"), "%d/%m/%Y").replace(tzinfo=self.fusohorario)
            proximo_aniversario = aniversario.replace(year=hoje.year)
            # Caso o aniversário já tenha passado este ano, ajustar para o próximo ano
            if proximo_aniversario < hoje:
                proximo_aniversario = proximo_aniversario.replace(year=hoje.year + 1)
            # Verificar se o usuário está no servidor
            membro = interaction.guild.get_member(usuario.get("_id"))
            if membro:
                proximos_aniversariantes.append({ "nome": membro.mention, "data": proximo_aniversario  })
        # Ordenar os aniversariantes por data
        proximos_aniversariantes.sort(key=lambda x: x["data"])

        # Formatar a mensagem de resposta
        if proximos_aniversariantes:
            mensagem = f"{Res.trad(interaction=interaction,str='message_aniversario_server_consulta')}\n"
            for aniversariante in proximos_aniversariantes[:12]:  # Limitar aos 12 próximos
                Res.trad(interaction=interaction, str="padrao_data")
                mensagem += f"- 🎂 {aniversariante['data'].strftime(Res.trad(interaction=interaction, str='padrao_data')[:5])} - {aniversariante['nome']}\n"
        else:
            mensagem = Res.trad(interaction=interaction,str="message_aniversario_server_sem_aniversariantes")
        embed = discord.Embed(description=f"{mensagem}\n{dicabrix}", color=discord.Color.yellow())
        # Enviar a mensagem
        await interaction.edit_original_response(embed=embed)


    @aniversarioservidor.command(name="ajuda", description="🎂⠂Ajuda sobre lembretes de aniversários.")
    async def aniversarioserveranunciodesativar(self, interaction: discord.Interaction):
        if await Res.print_brix(comando="aniversarioserveranunciodesativar",interaction=interaction):
            return
        if interaction.guild is None:
            await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_onlyservers"),delete_after=30)
        else:
            await interaction.response.send_message(Res.trad(interaction=interaction,str="message_aniversario_help"),delete_after=30,ephemeral=True)




async def setup(client:commands.Bot) -> None:
  await client.add_cog(aniversario(client))

