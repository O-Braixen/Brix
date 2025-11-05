import os , datetime , pytz
from pymongo import MongoClient, UpdateOne
from dotenv import load_dotenv
from typing import Dict






# ======================================================================
#CARREGA E LE O ARQUIVO .env na raiz
load_dotenv()
mongo_uri = os.getenv("MONGO_URI")





# ======================================================================
# Configuração da conexão com o MongoDB
client = MongoClient(mongo_uri,serverSelectionTimeoutMS=3000)
db_connection = client["brix"] # NOME DO BANCO DE DADOS








# ======================================================================
# =========================== COLEÇÃO DOS USUARIOS =====================


usercollection = db_connection.get_collection("users")  # A COLEÇÃO DA CONEXÃO

class BancoUsuarios: # Classe da coleção de usuarios

    # INSERIR REGISTROS
    def insert_document( membro ):
        membro_id = membro.id if hasattr(membro, 'id') else membro
        if usercollection.find_one({"_id" : membro_id}) is None:
            document = {"_id": membro_id,"braixencoin": 0,"graveto": 0, "nascimento": "00/00/0000", "rep": 0 ,"xpg": 0,"descricao": "brix é top, edite sua descrição usando /perfil sobremim","dm-notification":True , "backgroud": "braixen-house-2023","backgrouds": {"braixen-house-2023" : "braixen-house-2023"}}
            usercollection.insert_one(document)
        else:
            document = usercollection.find_one({"_id" : membro_id})
        return document
    

    # ATUALIZAR REGISTROS
    def update_document(membro,item):
        membro_id = membro.id if hasattr(membro, 'id') else membro
        BancoUsuarios.insert_document(membro_id)
        document = usercollection.update_one({"_id" : membro_id},{"$set": item })
        return document
  
    
    # INCREMENTAR VALORES
    def update_inc(membro, item):
        membro_id = membro.id if hasattr(membro, 'id') else membro
        # Primeiro faz o inc normal
        document = usercollection.update_one({"_id": membro_id},{"$inc": item})
        # Depois garante que existe o campo date-daily
        datacheck = datetime.datetime.now() - datetime.timedelta(days=60)
        today_str = datacheck.astimezone(pytz.timezone('America/Sao_Paulo')).strftime("%d/%m/%Y")
        usercollection.update_one({"_id": membro_id, "date-daily": {"$exists": False}},{"$set": {"date-daily": today_str}})
        return document
    

    # REALIZAR UM SELECT COM FILTRO
    def select_many_document( filtro):
        document = usercollection.find(filtro)
        return document
    

    # DELETAR UM ITEM DE UM REGISTRO
    def delete_field(membro,item): #deletando um item a partir de um deteminado item
        membro_id = membro.id if hasattr(membro, 'id') else membro
        BancoUsuarios.insert_document(membro)
        document = usercollection.update_one({"_id" : membro_id},{"$unset": item })
        return document
    

    # DELETAR UM DOCUMENTO INTEIRO
    def delete_document(membro): #deletando um item a partir de um deteminado item
        membro_id = membro.id if hasattr(membro, 'id') else membro
        document = usercollection.delete_one({"_id": membro_id})
        return document

       

    #CODIGO NOVO PARA ATUALIZAÇÂO EM LOTE
    @staticmethod
    def bulk_update(data_list):
        """
        Recebe uma lista de dicionários com as informações para atualizar.
        Cada item deve ter '_id' e 'update' (update pode ser $set, $unset, etc).
        """
        operations = [UpdateOne({"_id": data["_id"]}, data["update"])for data in data_list]
        
        if operations:
            result = usercollection.bulk_write(operations)
            return result
        return None

















# ======================================================================
# =========================== COLEÇÃO DOS SERVIDORES ===================

serverscollection = db_connection.get_collection("servers")

class BancoServidores: # Classe da coleção de servidores
    
    def insert_document( id ): #inserindo um item no banco de dados
        if serverscollection.find_one({"_id" : id}) is None:
            document = {"_id": id}
            serverscollection.insert_one(document)
        else:
            document = serverscollection.find_one({"_id" : id})
        return document
    
    def update_document(id,item): #atualizando um item no banco de dados
        BancoServidores.insert_document(id)
        document = serverscollection.update_one({"_id" : id},{"$set": item })
        return document

    def select_many_document( filtro): #dando select em um deteminado filtro no banco de dados
        document = serverscollection.find(filtro)
        return document
    
    def delete_field(id,item): #deletando um item a partir de um deteminado item
        BancoServidores.insert_document(id)
        document = serverscollection.update_one({"_id" : id},{"$unset": item })
        return document

    def delete_document(id): #deletando um item a partir de um deteminado item
        document = serverscollection.delete_one({"_id": id})
        return document
    
    def bot_in_guild (id , status):
        BancoServidores.insert_document(id)
        document = serverscollection.update_one({"_id" : id},{"$set": {"bot_in_guild" : status} })
        return document





















# ======================================================================
# =========================== COLEÇÃO DA LOJA ==========================

lojacollection = db_connection.get_collection("loja")

class BancoLoja:
   
    def insert_document(id,name,braixencoin,graveto,raridade,url,descricao,fontcor): #inserindo um novo registro
        if lojacollection.find_one({"_id" : id}) is None:
            document = {"_id": id,"name": name,"braixencoin": braixencoin,"graveto": graveto,"raridade": raridade,"url": url,"descricao": descricao,"font_color":fontcor}
            lojacollection.insert_one(document)
        else:
            document = lojacollection.find_one({"_id" : id})
        return document

    def update_one(id,item): #atualizando um item no banco de dados
        document = lojacollection.update_one({"_id" : id},{"$set": item })
        return document
    
    def update_document(id,name,braixencoin,graveto,raridade,url,descricao,fontcor): #atualizando um item no banco de dados
        BancoLoja.insert_document(id,name,braixencoin,graveto,raridade,url,descricao,fontcor)
        item = {"name": name,"braixencoin": braixencoin,"graveto": graveto,"raridade": raridade,"url": url,"descricao": descricao,"font_color":fontcor}
        document = lojacollection.update_one({"_id" : id},{"$set": item })
        return document
    
    def select_one(id):
        document = lojacollection.find_one({"_id" : id})
        return document
    
    def select_many_document( filtro): #dando select em um deteminado filtro no banco de dados
        document = lojacollection.find(filtro)
        return document




    def insert_loja(id):
        botconfigcollection.insert_one({"_id" : id})

    def update_loja(id,item): #atualizando um item no banco de dados
        document = botconfigcollection.replace_one({"_id" : id}, item  , upsert =True)
        return document

    def select_loja( filtro): #dando select em um deteminado filtro no banco de dados
        document = botconfigcollection.find(filtro)
        return document









# ======================================================================
# =================== COLEÇÃO DE CONFIGURAÇÃO DO BOT ===================

botconfigcollection = db_connection.get_collection("botconfig")

class BancoBot:
    
    def insert_document(): #inserindo um novo registro
        if botconfigcollection.find_one({"_id" : "brixthebraixen"}) is None:
            document = {"_id": "brixthebraixen","name": "nome","premiumsys": True,"version": 0.0,"notasupdate":"-","rotacaoloja" : True}
            botconfigcollection.insert_one(document)
        else:
            document = botconfigcollection.find_one({"_id" : "brixthebraixen"})
        return document
    
    def update_one(item): #atualizando um item no banco de dados
        document = botconfigcollection.update_one({"_id" : "brixthebraixen"},{"$set": item })
        return document













# ======================================================================
# ==================== COLEÇÃO DE TRANSAÇÕE FINANCEIRAS ================

# Conexão com a coleção
bottransacoes = db_connection.get_collection("brix-transacoes")

class BancoFinanceiro:

    @staticmethod
    def registrar_transacao(user_id, tipo, origem, valor, moeda="", descricao=""):
        
        transacao = {   "user_id": str(user_id),"tipo": tipo,"origem": origem,"valor": valor,"moeda": moeda,"descricao": descricao,"timestamp":  datetime.datetime.now().replace(tzinfo=None) }
        bottransacoes.insert_one(transacao)

    @staticmethod
    def buscar_historico(user_id, limite, moeda=None):
        
        filtro = {"user_id": str(user_id)}
        if moeda:
            filtro["moeda"] = moeda

        return bottransacoes.find(filtro).sort("timestamp", -1).limit(limite)

    @staticmethod
    def buscar_por_filtro(filtro):
        return bottransacoes.find(filtro)

    @staticmethod
    def deletar_transacoes_user(user_id):
        bottransacoes.delete_many({"user_id": str(user_id)})

    @staticmethod
    def bulk_registrar_transacoes(lista):
        if not lista:
            return
        bottransacoes.insert_many(lista)














# ======================================
# COLEÇÃO DE LOGS GERAIS DO BRIX
# ======================================

bancologs = db_connection.get_collection("logs_brix")

class BancoLogs:
    """
    Sistema unificado de registro de eventos do bot Brix.
    Tipo:
      1 = entrada/saída de servidor
      2 = comando executado
      3 = usuários / contagens gerais
      4 = métricas externas (ping, RAM, CPU, etc)
      5 = Assinaturas Premium
    """

    @staticmethod
    def registrar_evento(tipo: int, dados: dict):
        now = datetime.datetime.now().astimezone(pytz.timezone('America/Sao_Paulo'))

        log_doc = {
            "tipo": tipo,
            "timestamp": now,
            "dados": dados
        }

        try:
            bancologs.insert_one(log_doc)
        except Exception as e:
            print(f"Falha ao salvar log: {e}")
            print(log_doc)

    # ---------------------------------------------------------------------
    # COMANDO EXECUTADO
    # ---------------------------------------------------------------------
    @staticmethod
    def registrar_comando(interaction, comando, condicao=None):
        dados = {
            "user_id": interaction.user.id,
            "user_name": interaction.user.name,
            "guild_id": interaction.guild.id if interaction.guild else None,
            "guild_name": interaction.guild.name if interaction.guild else None,
            "comando": comando,
            "condicao": condicao
        }
        BancoLogs.registrar_evento(2, dados)

    # ---------------------------------------------------------------------
    # ENTRADA / SAÍDA DE SERVIDOR
    # ---------------------------------------------------------------------
    @staticmethod
    def registrar_guild_evento(guild, tipo_entrada=True):
        dados = {
            "guild_id": guild.id,
            "guild_name": guild.name,
            "membros": guild.member_count,
            "acao": "entrada" if tipo_entrada else "saida"
        }
        BancoLogs.registrar_evento(1, dados)

    # ---------------------------------------------------------------------
    # SNAPSHOT DE USUÁRIOS E SERVIDORES (diário ou horário)
    # ---------------------------------------------------------------------
    @staticmethod
    async def registrar_estatisticas_gerais(bot):
        total_guilds = len(bot.guilds)
        total_users = len(set(u.id for g in bot.guilds for u in g.members))

        dados = {
            "total_servidores": total_guilds,
            "total_usuarios": total_users
        }
        BancoLogs.registrar_evento(3, dados)

    # ---------------------------------------------------------------------
    # DADOS EXTERNOS (ping, memória, CPU)
    # ---------------------------------------------------------------------
    @staticmethod
    def registrar_metricas_externas(latencia, uso_ram, uso_cpu):
        dados = {
            "latencia_ms": latencia,
            "uso_ram_mb": uso_ram,
            "uso_cpu_percent": uso_cpu
        }
        BancoLogs.registrar_evento(4, dados)
    

    # ---------------------------------------------------------------------
    # DADOS ASSINATURA (ENTREGA DE PREMIUM)
    # ---------------------------------------------------------------------
    @staticmethod
    def registrar_assinatura_premium(userid , tempo):
        dados = {
            "usuario_recebimento_id": userid,
            "tempo_assinatura": tempo
        }
        BancoLogs.registrar_evento(5, dados)

    # ---------------------------------------------------------------------
    # CONSULTAS
    # ---------------------------------------------------------------------
    @staticmethod
    def listar(tipo=None, limite=50):
        filtro = {"tipo": tipo} if tipo else {}
        try:
            cursor = bancologs.find(filtro).sort("timestamp", -1).limit(limite)
            return list(cursor)
        except Exception as e:
            print(f"Erro ao listar logs: {e}")
            return []

    @staticmethod
    def contar_registros(filtro={}, limite=None):
        try:
            query = filtro.copy()
            if limite:
                return bancologs.count_documents(query, limit=limite)
            return bancologs.count_documents(query)
        except Exception as e:
            print(f"Falha ao contar logs: {e}")
            return 0










# ======================================================================
# ====================== COLEÇÃO DE TROCAS POKÉMON =====================

# Conexão com a coleção de trocas de pokémon
trocas_collection = db_connection.get_collection("trocas_pokemon")

class BancoTrocas:
    
    @staticmethod
    def insert_document(id_troca,user_id, username, pokemon, jogo, shiny):
        # Verifica se o mesmo user já tem esse pokémon registrado     # 3 - concluido, 4 - cancelado
        existe = trocas_collection.find_one({"user_id": user_id, "pokemon": pokemon, "status": {"$nin": [3, 4]} })
        if existe:
            return False , existe  # ou raise Exception ou retorna algo que diga que já existe

        document = {
            "id_troca": id_troca,
            "user_id": user_id,
            "username": username,
            "pokemon": pokemon,
            "shiny": shiny,
            "jogo": jogo,
            "data_registro": datetime.datetime.now(),
            "status": 1, # (1 - disponivel → 2 - aceito → 3 - concluido ou 4 - cancelado)
            "user_id_aceitou": None,
            "username_aceitou": None,
            "data_aceitou": None,
            "data_conclusao": None
        }
        trocas_collection.insert_one(document)
        return True, document

    @staticmethod
    def update_document(document_id, item):  # item = dict com campos pra atualizar
        result = trocas_collection.update_one({"_id": document_id}, {"$set": item})
        return result

    @staticmethod
    def select_many_document(filtro):
        documentos = trocas_collection.find(filtro)
        return list(documentos)



















# ======================================================================
# =============== COLEÇÃO DE PAGAMENTOS MERCADO PAGO ===================

# Conexão com a coleção de pagamentos
payments_collection = db_connection.get_collection("payments")

class BancoPagamentos:
    
    @staticmethod
    def insert_payment(mp_payment_id, mp_status, qr_code_base64, ticket_url, plano, user_id , quant_meses):
        doc = {
            "mp_payment_id": mp_payment_id,
            "mp_status": mp_status,
            "qr_code_base64": qr_code_base64,
            "ticket_url": ticket_url,
            "plano": plano,   
            "quant_meses": quant_meses,  
            "user_id": user_id,  
            "created_at": datetime.datetime.now(),
            "ativado":False
        }
        payments_collection.insert_one(doc)
        return doc

    @staticmethod
    def update_payment(mp_payment_id, data):
        return payments_collection.update_one({"mp_payment_id": mp_payment_id}, {"$set": data})

    @staticmethod
    def select_by_filter(filtro):
        return list(payments_collection.find(filtro))
    

    @staticmethod
    def get_pending_payment(user_id, validade_hours=24):
        """
        Retorna um pagamento pendente não expirado para user_id ou None.
        Considera 'pending' e 'in_process' como pendentes.
        Usa created_at + validade_hours para expirar.
        """
        agora = datetime.datetime.now()
        limite = agora - datetime.timedelta(hours=validade_hours)
        filtro = {
            "user_id": user_id,
            "mp_status": {"$in": ["pending", "in_process", "pending_waiting_transfer"]},
            "created_at": {"$gte": limite}
        }
        return payments_collection.find_one(filtro)
    
    @staticmethod
    def delete_by_mp_id(mp_payment_id):
        """
        Deleta um pagamento pelo mp_payment_id.
        Retorna True se deletou 1 documento, False caso contrário.
        """
        res = payments_collection.delete_one({"mp_payment_id": mp_payment_id})
        return res.deleted_count == 1

























# ======================================================================
# ============= COLEÇÃO PARA O SISTEMA DE APOSTAS DE POKÉMON ===========
apostascollection = botconfigcollection

class BancoApostasPokemon:

    @staticmethod
    def insert_document():
        """Garante que exista o documento base para apostas"""
        if apostascollection.find_one({"_id": "aposta_pokemon"}) is None:
            document = {
                "_id": "aposta_pokemon",
                "valor_acumulado": 0,
                "ultimo_sorteado": None
            }
            apostascollection.insert_one(document)
        else:
            document = apostascollection.find_one({"_id": "aposta_pokemon"})
        return document
    
    
    
    @staticmethod
    def get_document():
        """Retorna o documento completo"""
        BancoApostasPokemon.insert_document()
        return apostascollection.find_one({"_id": "aposta_pokemon"})



    @staticmethod
    def get_aposta_usuario(user_id:int):
        """Retorna a aposta do usuário (ou None se não apostou)"""
        BancoApostasPokemon.insert_document()
        doc = BancoApostasPokemon.get_document()
        for aposta in doc.get("apostas", []):
            if aposta["user_id"] == user_id:
                return aposta
        return None
    


    @staticmethod
    def add_aposta(user_id:int, pokemon:str, valor:int):
        """Adiciona uma aposta para o usuário"""
        BancoApostasPokemon.insert_document()
        aposta_existente = BancoApostasPokemon.get_aposta_usuario(user_id)
        if aposta_existente:
            return aposta_existente  # já existe → retorna aposta atual

        apostascollection.update_one(
            {"_id": "aposta_pokemon"},
            {"$push": {"apostas": {
                "user_id": user_id,
                "pokemon": pokemon,
                "valor": valor
            }}}
        )
        return None  # None indica que foi inserida com sucesso

    @staticmethod
    def update_valor_acumulado(valor:int):
        """Atualiza o valor acumulado do pote"""
        apostascollection.update_one(
            {"_id": "aposta_pokemon"},
            {"$inc": {"valor_acumulado": valor}}
        )

    @staticmethod
    def set_ultimo_sorteado(pokemon:str):
        """Define o último pokémon sorteado"""
        apostascollection.update_one(
            {"_id": "aposta_pokemon"},
            {"$set": {"ultimo_sorteado": pokemon}}
        )

    @staticmethod
    def limpar_apostas():
        """Limpa as apostas (após o sorteio)"""
        BancoApostasPokemon.insert_document()
        apostascollection.update_one( {"_id": "aposta_pokemon"}, {"$unset": {"apostas": ""}} )

   















# ======================================================================
# =================== COLEÇÃO DE CÓDIGOS DE RESGATE =====================
# ======================================================================

codigoscollection = db_connection.get_collection("codigos_resgate")

class BancoCodigosResgate:
    
    @staticmethod
    def insert_document(codigo: str, recompensa: dict, max_usos: int = None,  expira_em: str = None, ativa_em: str = None):
        """Cria um novo código de resgate"""
        if codigoscollection.find_one({"_id": codigo}):
            return None  # já existe

        doc = {
            "_id": codigo.lower().strip(),
            "recompensa": recompensa,     # Ex: {"tipo": "premium", "valor": 30} ou {"tipo": "braixencoin", "valor": 500}
            "usados_por": [],             # lista de user_ids que já usaram
            "max_usos": max_usos,         # limite global de usos (None = ilimitado)
            "ativo": True,
            "criado_em": datetime.datetime.now(),
            "expira_em": expira_em,       # data limite em ISO (ou None)
            "ativa_em": ativa_em,          # data que o código se torna ativo (ou None)
        }
        codigoscollection.insert_one(doc)
        return doc

    @staticmethod
    def get_codigo(codigo: str):
        """Busca um código"""
        codigo = codigo.lower().strip()
        return codigoscollection.find_one({"_id": codigo})
    
    @staticmethod
    def get_all_codigo():
        """Busca todos os código"""
        return codigoscollection.find({})

    @staticmethod
    def set_inativo(codigo: str, ativo: bool):
        """Ativa/desativa um código"""
        codigo = codigo.lower().strip()
        return codigoscollection.update_one({"_id": codigo}, {"$set": {"ativo": ativo}})
    
    @staticmethod
    def add_uso(codigo: str, user_id: int):
        """Registra o uso de um código"""
        codigo = codigo.lower().strip()
        return codigoscollection.update_one(
            {"_id": codigo},
            {"$addToSet": {"usados_por": user_id}}
        )


    @staticmethod
    def delete_codigo(codigo: str):
        """Remove um código do sistema"""
        codigo = codigo.lower().strip()
        return codigoscollection.delete_one({"_id": codigo})














# ======================================================================
# =========================== COLEÇÃO DE EVENTOS ==========================


#BANDO DE DAODS DEDICADO A EVENTOS
"""
eventocollection = db_connection.get_collection("evento-natalxen")

class BancoEventos:
    def __init__(self, db_connection) -> None:
        self.__collection_name = "evento-natalxen"
        self.__db_connection = db_connection

    #ADICIONANDO USUARIO OU BUSCANDO
    def insert_document( membro ):
        membro_id = membro.id if hasattr(membro, 'id') else membro
        if eventocollection.find_one({"_id" : membro_id}) is None:
            document = {"_id": membro_id,"giftscoletados": 0 , "giftspresentes": 0 , "totalcoletados" : 0, "brinde-entregue": False}
            eventocollection.insert_one(document)
        else:
            document = eventocollection.find_one({"_id" : membro_id})
        return document

    #ATUALIZANDO UM REGISTRO
    def update_document(membro,item):
        membro_id = membro.id if hasattr(membro, 'id') else membro
        BancoEventos.insert_document(membro_id)
        document = eventocollection.update_one({"_id" : membro_id},{"$set": item })
        return document
    
    #INCREMENTANDO UM CADASTRO
    def update_inc(membro,item):
        membro_id = membro.id if hasattr(membro, 'id') else membro
        BancoEventos.insert_document(membro_id)
        document = eventocollection.update_one({"_id" : membro_id},{"$inc": item })
        return document
    
    #BUSCANDO
    def select_many_document( filtro):
        document = eventocollection.find(filtro)
        return document


"""