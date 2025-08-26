import os,requests
from dotenv import load_dotenv


load_dotenv()
square_token = os.getenv("square_token") #acessa e define o token da square cloud
discloud_token = os.getenv("discloud_token") #acessa e define o token da square cloud

appid = None
host = None


if square_token:
    host = "squarecloud"
if discloud_token:
    host = "discloud"

def obter_nome_bot():
    global host
    if host == "discloud":
        caminho = "discloud.config"
        return ler_arquivo(caminho, host)
    elif host == "squarecloud":
        caminho = "squarecloud.app"
        return ler_arquivo(caminho, host)
    else:
        raise ValueError("Host desconhecido.")

def ler_arquivo(caminho , host):
    with open(caminho, "r", encoding="utf-8") as f:
        for linha in f:
            if host == "squarecloud":
                if linha.startswith("DISPLAY_NAME="):
                    return linha.strip().split("=", 1)[1]
            if host == "discloud":
                if linha.startswith("NAME="):
                    return linha.strip().split("=", 1)[1]
    return None


async def appname(nome):
    global appid
    global host
    if appid is None:
        if host == None:
            print("🤖 - Nenhum token de Host encontrado. Verifique o .env")
            return
        
        print(f"🤖 - Usando a hospedagem da {host}")
        if host == "squarecloud":
            busca =  requests.get(f"https://api.squarecloud.app/v2/users/me", headers={"Authorization": square_token})
            aplicativos = busca.json().get("response", {}).get("applications", [])
            # Filtrar e retornar apenas os IDs dos aplicativos com nome igual ou similar ao fornecido
            for app in aplicativos:
                if nome.lower() in app.get("name", "").lower():
                    appid = app["id"]
                    return app["id"]
        if host == "discloud":
            busca =  requests.get(f"https://api.discloud.app/v2/user", headers={"api-token": discloud_token})
            aplicativos = busca.json().get("user", {}).get("apps", [])
            for app in aplicativos:
                app =  requests.get(f"https://api.discloud.app/v2/app/{app}", headers={"api-token": discloud_token})
                if nome.lower() in app.json().get("apps", {}).get("name", "").lower():
                    appid = app.json().get("apps", {}).get("id", "")
                    return appid
    else:
        return appid

async def informação(nome):
    global host
    retorno = await appname(nome)
    if host == "squarecloud":
        res_information =  requests.get(f"https://api.squarecloud.app/v2/apps/{retorno}", headers={"Authorization": square_token})
        return res_information.json()  , host
    if host == "discloud":
        res_information =  requests.get(f"https://api.discloud.app/v2/app/{retorno}", headers={"api-token": discloud_token})
        return res_information.json() , host

async def status(nome):
    global host
    retorno = await appname(nome)
    if host == "squarecloud":
        res_status =  requests.get(f"https://api.squarecloud.app/v2/apps/{retorno}/status", headers={"Authorization": square_token})
        return res_status.json()  , host
    if host == "discloud":
        res_status =  requests.get(f"https://api.discloud.app/v2/app/{retorno}/status", headers={"api-token": discloud_token})
        return res_status.json()  , host


async def restart(nome):
    global host
    retorno = await appname(nome)
    if host == "squarecloud":
        res_status =  requests.post(f"https://api.squarecloud.app/v2/apps/{retorno}/restart",headers={"Authorization": square_token})
        return res_status.json() , host
    if host == "discloud":
        res_status =  requests.put(f"https://api.discloud.app/v2/app/{retorno}/restart",headers={"api-token": discloud_token})
        return res_status.json() , host