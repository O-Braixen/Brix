from pymongo import MongoClient, UpdateOne
import os
from dotenv import load_dotenv
from typing import Dict

#CARREGA E LE O ARQUIVO .env na raiz
load_dotenv()
mongo_uri = os.getenv("MONGO_URI")


# Configuração da conexão com o MongoDB
client = MongoClient(mongo_uri,serverSelectionTimeoutMS=3000)
db_connection = client["brix"] # Substitua "meu_banco_de_dados" pelo nome do seu banco de dados


usercollection = db_connection.get_collection("users")  # Substitua "minha_colecao" pelo nome da sua coleção


class BancoUsuarios: # Classe da coleção de usuarios
    #def __init__(self, db_connection) -> None:
    #    self.__collection_name = "users"
     #   self.__db_connection = db_connection

    def insert_document( membro ):
        membro_id = membro.id if hasattr(membro, 'id') else membro
        if usercollection.find_one({"_id" : membro_id}) is None:
            document = {"_id": membro_id,"braixencoin": 0,"graveto": 0, "nascimento": "00/00/0000", "rep": 0 ,"xpg": 0,"descricao": "brix é top, edite sua descrição usando /perfil sobremim","dm-notification":True}
            usercollection.insert_one(document)
        else:
            document = usercollection.find_one({"_id" : membro_id})
        return document
    
    def update_document(membro,item):
        membro_id = membro.id if hasattr(membro, 'id') else membro
        BancoUsuarios.insert_document(membro_id)
        document = usercollection.update_one({"_id" : membro_id},{"$set": item })
        return document
    
    def update_inc(membro,item):
        membro_id = membro.id if hasattr(membro, 'id') else membro
        BancoUsuarios.insert_document(membro_id)
        document = usercollection.update_one({"_id" : membro_id},{"$inc": item })
        return document
    
    def select_many_document( filtro):
        document = usercollection.find(filtro)
        return document
    
    def delete_field(membro,item): #deletando um item a partir de um deteminado item
        membro_id = membro.id if hasattr(membro, 'id') else membro
        BancoUsuarios.insert_document(membro)
        document = usercollection.update_one({"_id" : membro_id},{"$unset": item })
        return document
    
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








serverscollection = db_connection.get_collection("servers")

class BancoServidores: # Classe da coleção de servidores
   # def __init__(self, db_connection) -> None:
    #    self.__collection_name = "servers"
     #   self.__db_connection = db_connection
    
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







lojacollection = db_connection.get_collection("loja")

class BancoLoja:
   # def __init__(self, db_connection) -> None:
   #     self.__collection_name = "loja"
    #    self.__db_connection = db_connection
    
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










botconfigcollection = db_connection.get_collection("botconfig")

class BancoBot:
   # def __init__(self, db_connection) -> None:
    #    self.__collection_name = "botconfig"
    #    self.__db_connection = db_connection
    
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










"""
correiocollection = db_connection.get_collection("data-correio")

class BancoCorreio:
   # def __init__(self, db_connection) -> None:
   #     self.__collection_name = "data-correio"
   #     self.__db_connection = db_connection
    
    def insert_document( registro, remetente , destinatario , data , mensagem , anonimo): #inserindo um novo registro
        if correiocollection.find_one({"_id" : "brixthebraixen"}) is None:
            document = {"_id": registro,"remetente": remetente,"destinatario": destinatario,"data": data,"mensagem":mensagem,"anonimo" : anonimo}
            correiocollection.insert_one(document)
        else:
            document = correiocollection.find_one({"_id" : registro})
        return document

    def select_one(registro):
        document = correiocollection.find_one({"_id" : registro})
        return document
    


"""







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