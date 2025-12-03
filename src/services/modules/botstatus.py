import discord, os , asyncio , datetime , pytz
from discord.ext import commands, tasks
from src.services.essential.host import informação , status
from src.services.connection.database import BancoBot , BancoUsuarios , BancoLogs , BancoServidores
from src.services.essential.respostas import listapegadinha
from src.services.essential.shardsname import NOME_DOS_SHARDS
from src.services.essential.diversos import calcular_saldo , set_guild_profile
from dotenv import load_dotenv





# ======================================================================

load_dotenv()
mes = int(os.getenv("mes_Braixen_day"))
dia = int(os.getenv("dia_Braixen_day"))
token_bot = os.getenv("DISCORD_TOKEN")










# ======================================================================
#FUNÇÂO PARA PUXAR OS COMANDOS DO BOT
def extrair_comandos_grupo(grupo, prefixo=""):
    comandos = []
    for cmd in sorted(grupo.commands, key=lambda c: c.name):
        if isinstance(cmd, discord.app_commands.Group):
            comandos.extend(extrair_comandos_grupo(cmd, prefixo=f"{prefixo}{grupo.name} "))
        else:
            comandos.append({
                "nome": f"{prefixo}{grupo.name} {cmd.name}",
                "descricao": getattr(cmd, "description", "Sem descrição"),
                "opcoes": [
                    {
                        "nome": opt.name,
                        "tipo": str(opt.type),
                        "descricao": opt.description,
                        "obrigatorio": opt.required
                    }
                    for opt in getattr(cmd, "parameters", [])
                ]
            })
    return comandos















# ======================================================================

class botstatus(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.isbraixenday = False
        self.isnatalday = False
        self.isanonovoday = False
        self.abrilfools = False





# ======================================================================

    @commands.Cog.listener()
    async def on_bot_ready(self):
        print("🤖  -  Modúlo botstatus carregado.")
        #Ligando tasks
        if not self.salvar_estatisticas_gerais.is_running():
            self.salvar_estatisticas_gerais.start()
        
        if not self.salvar_metricas.is_running():
            self.salvar_metricas.start()

        #await asyncio.sleep(300)
        if not self.atualizar_status_cache.is_running():
            self.atualizar_status_cache.start()

        if not self.verificar_datas_comemorativas.is_running():
            self.verificar_datas_comemorativas.start()
        
        if not self.update_status_loop.is_running():
            self.update_status_loop.start()
        
        if not self.atualizar_BOT_AVATAR.is_running():
            self.atualizar_BOT_AVATAR.start()
        
        
       






# ======================================================================

    @tasks.loop(minutes=10)
    async def update_status_loop(self):
        await self.client.member_cache_ready_event.wait() 
        # evita escrever no socket enquanto ele está caindo/reconectando
        if self.client.is_closed():
            return
        
        dadosbot = BancoBot.insert_document()

        status_list = []

        if self.isbraixenday:  # Dia do Braixen
            status_list = [
                (discord.CustomActivity(name="🦊 Braixen Day!!!"), discord.Status.online),
                (discord.CustomActivity(name="🔥 Celebrando Braixen Day!"), discord.Status.online),
                (discord.Activity(type=discord.ActivityType.watching, name="Braixen's em Kalos TV"), discord.Status.do_not_disturb),
                (discord.CustomActivity(name="Feliz Braixen Day para mim!"), discord.Status.online),
            ]

        elif self.isnatalday:  # Natal
            status_list = [
                (discord.CustomActivity(name="🎄 Feliz Natal!!!"), discord.Status.online),
                (discord.CustomActivity(name="🎄 Natal com magia de fogo!"), discord.Status.online),
                (discord.Activity(type=discord.ActivityType.watching, name="Especial de Natal na Globo"), discord.Status.online),
            ]

        elif self.isanonovoday:  # Ano novo
            status_list = [
                (discord.CustomActivity(name="Feliz Ano Novo!!!"), discord.Status.online),
                (discord.CustomActivity(name="🔥 Um Próspero Ano Novo!!!"), discord.Status.online),
                (discord.Activity(type=discord.ActivityType.watching, name="🎆 Fogos de Artifício"), discord.Status.online),
            ]

        elif self.abrilfools:  # 1 de abril
            status_list = [
                (discord.CustomActivity(name=f"{len(listapegadinha)} Raposas cairam na pegadinha de primeiro de abril!"), discord.Status.dnd),
                (discord.CustomActivity(name="🔥 Braixen agora é um Pokémon Lendário!"), discord.Status.dnd),
                (discord.CustomActivity(name="🔨 Todos Foram Banidos ~kyuuuu!!!"), discord.Status.dnd),
                (discord.CustomActivity(name="Primeiro de Abril ~kyuuuu!!!"), discord.Status.dnd),
            ]

        else:  # sem data especifica
            try:
                res_information, host = await informação(self.client.user.name)
                if host == "squarecloud":
                    status_list.append((discord.CustomActivity(name=f"🖥️ Square Cloud - {res_information['response']['cluster']}"), discord.Status.online))
                elif host == "discloud":
                    status_list.append((discord.CustomActivity(name=f"🖥️ Discloud - CLUSTER {res_information['apps']['clusterName']}"), discord.Status.online))
            except:
                print("❌ - falha ao coletar dados da hospedagem para status")

            status_list.extend([
                (discord.CustomActivity(name="🦊 Minha casa dsc.gg/braixen"), discord.Status.online),
                (discord.CustomActivity(name=f"✨ visitando {len(self.client.guilds)} servidores kyuuuuu!"), discord.Status.online),
                (discord.CustomActivity(name="🍕📱 Pedindo uma pizza com @obraixen"), discord.Status.dnd),
                (discord.Activity(type=discord.ActivityType.watching, name="Braixen's House 🦊"), discord.Status.do_not_disturb),
                (discord.Activity(type=discord.ActivityType.playing, name="Pokémon X em dsc.gg/braixen"), discord.Status.do_not_disturb),
                (discord.Activity(type=discord.ActivityType.watching, name=f"{len(self.client.users)} usuários!"), discord.Status.online),
                (discord.CustomActivity(name=f"🦊 {len(self.client.guilds)} guildas confiando na sabedoria de Brix!"), discord.Status.online),
                (discord.CustomActivity(name="🦊 Sendo um bom Braixen, kyuu!"), discord.Status.online),
                (discord.CustomActivity(name=f"Versão {dadosbot['version']} Brix!"), discord.Status.online),
                (discord.CustomActivity(name=f"💎 Personalize meu perfil na Dashboard"), discord.Status.online),
                (discord.CustomActivity(name="🦊 Adquira sua assinatura Premium agora mesmo!"), discord.Status.online),
                #(discord.CustomActivity(name=f"{shard_nome} ({shard_id}) em uso"), discord.Status.online),
                (discord.CustomActivity(name="✨ Magia Pokémon em cada servidor!"), discord.Status.online),
            ])
        try:
            # loop principal para trocar os status
            for activity, status in status_list:
                if self.client.is_closed():
                    return  # evita erro no meio da sequência
                await self.client.change_presence(activity=activity, status=status)
                await asyncio.sleep(900)  # apenas uma vez aqui
        except Exception as e:
            print(f"❌ -  Falha ao atualizar o status: {e}")










# ======================================================================

    #VERIFICADOR DE DATAS COMEMORATIVAS PARA USAR DE STATUS NO BOT
    @tasks.loop(minutes=10)
    async def verificar_datas_comemorativas(self):
        
        now = datetime.datetime.now().astimezone(pytz.timezone('America/Sao_Paulo'))
        databraixenday = datetime.date(now.year , mes , dia) # sequencia Ano , Mes , Dia
        natalday = datetime.date(now.year , 12 , 25 )
        anonovoday = datetime.date(now.year , 1 , 1 )
        primeiroabril = datetime.date(now.year , 4 , 1 )


        if now.date() == databraixenday:
            self.isbraixenday = True
        elif now.date() == natalday:
            self.isnatalday = True
        elif now.date() == anonovoday:
            self.isanonovoday = True
        elif now.date() == primeiroabril:
            self.abrilfools = True
        else:
            self.isbraixenday = False
            self.isnatalday = False
            self.isanonovoday = False
            self.abrilfools = False


















    



#FUNÇÃO PARA ATUALIZAR O CACHE DOS COMANDOS
    @tasks.loop(minutes=10)
    async def atualizar_status_cache(self):
        await self.client.member_cache_ready_event.wait() 
        try:
            filtro = {"braixencoin": {"$exists": True}}
            usuarios = BancoUsuarios.select_many_document(filtro)
            total_moeda = sum(usuario.get("braixencoin", 0) for usuario in usuarios)
            total_moeda = calcular_saldo(total_moeda)
            item = { "name": str(self.client.user.name), "braixencoin": total_moeda,"usuarios": calcular_saldo(len(self.client.users))}
            BancoBot.update_one(item)

        except Exception as e:
            print(f"🔴 - [ERRO] Falha ao atualizar cache: {e}")


        











    #FUNÇÃO PARA ATUALIZAR AVATAR DO BOT NAS GUILDAS
    @tasks.loop(minutes=2)
    async def atualizar_BOT_AVATAR(self):
        try:
            filtro = {"custom": {"$exists": True}}
            servidores = BancoServidores.select_many_document(filtro)
            for servidor in servidores:
            
                guild_id = servidor["_id"]
                custom = servidor.get("custom", {})

                # ============================
                # 1) SE TIVER delete = True → RESETAR
                # ============================
                if custom.get("delete") is True:
                    print(f"🗑️ Limpando customização da guild {guild_id}")
                    status, resp = await set_guild_profile( bot_token=token_bot, guild_id=guild_id, avatar_path=None, banner_path=None, nick=None, bio=None )
                    # limpa no BD
                    BancoServidores.delete_field(guild_id,{"custom": 0})
                    await asyncio.sleep(10)  # apenas uma vez aqui
                    continue

                # ============================
                # 2) SE NÃO ESTIVER ATIVO → IGNORA
                # ============================
                if custom.get("ativo") is True:
                    continue

                # ============================
                # 3) Preparar dados para aplicar
                # ============================
                nome = custom.get("nome")
                bio = custom.get("bio")
                avatar_filename = custom.get("avatar")
                banner_filename = custom.get("banner")

                avatar_path = f"https://brixbot.xyz/cdn/{avatar_filename}" if avatar_filename else None
                banner_path = f"https://brixbot.xyz/cdn/{banner_filename}" if banner_filename else None

                # ============================
                # 4) Aplicar no Discord
                # ============================
                print(f"🦊  -  Aplicando customização na guild {guild_id}")

                try:
                    status, resp = await set_guild_profile( bot_token=token_bot, guild_id=guild_id, avatar_path=avatar_path, banner_path=banner_path, nick=nome, bio=bio )
                    BancoServidores.update_document(guild_id,{"custom.ativo": True})
                    print(f"✔️  -  Guild {guild_id} atualizada — Status: {status}")
                    await asyncio.sleep(30)  # apenas uma vez aqui
                except Exception as e:
                    print(f"🔴  -  Falha ao aplicar na guild {guild_id}: {e}")
                    continue
                

        except Exception as e:
            print(f"🔴  -  Erro inesperado ao processar guild: {e}")
            


















#TASKS PARA SALVAR ESTATISTICAS DE METRICAS DO BOT

    @tasks.loop(time=datetime.time(hour=0 , minute= 0, tzinfo=datetime.timezone(datetime.timedelta(hours=-3))))
    async def salvar_estatisticas_gerais(self):
        await BancoLogs.registrar_estatisticas_gerais(self.client)
    

    @tasks.loop(minutes=1)
    async def salvar_metricas(self):
        agora = datetime.datetime.now(pytz.timezone("America/Sao_Paulo"))
        minuto = agora.minute

        # Executa de 5 em 5 minutos (00, 05, 10, 15, ...)
        if minuto % 5 == 0:
            try:
                res_status, host = await status(self.client.user.name)
                latencia = round(self.client.latency * 1000, 2)
                uso_ram = float(res_status['response']['ram'].replace("MB", ""))
                uso_cpu = float(res_status['response']['cpu'].replace("%", ""))

                BancoLogs.registrar_metricas_externas(latencia, uso_ram, uso_cpu)
            except Exception as e:
                print(f"Erro ao salvar métricas: {e}")
                


















# ======================================================================

async def setup(client: commands.Bot) -> None:
    await client.add_cog(botstatus(client))