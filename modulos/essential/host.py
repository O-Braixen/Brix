import os,requests
from dotenv import load_dotenv


load_dotenv()
square_token = os.getenv("square_token") #acessa e define o token da square cloud

appid = None

async def appname(nome):
    global appid
    if appid is None:
        busca =  requests.get(f"https://api.squarecloud.app/v2/users/me", headers={"Authorization": square_token})
        aplicativos = busca.json().get("response", {}).get("applications", [])
        # Filtrar e retornar apenas os IDs dos aplicativos com nome igual ou similar ao fornecido
        for app in aplicativos:
            if nome.lower() in app.get("name", "").lower():
                appid = app["id"]
                return app["id"]
    else:
        return appid

async def informação(nome):
    retorno = await appname(nome)
    res_information =  requests.get(f"https://api.squarecloud.app/v2/apps/{retorno}", headers={"Authorization": square_token})
    return res_information.json()

async def status(nome):
    retorno = await appname(nome)
    res_status =  requests.get(f"https://api.squarecloud.app/v2/apps/{retorno}/status", headers={"Authorization": square_token})
    return res_status.json()

async def restart(nome):
    retorno = await appname(nome)
    res_status =  requests.post(f"https://api.squarecloud.app/v2/apps/{retorno}/restart",headers={"Authorization": square_token})
    return res_status