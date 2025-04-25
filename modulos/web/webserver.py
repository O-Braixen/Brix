from flask import Flask, send_from_directory, jsonify
import threading , os , discord.app_commands , logging , time  


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=os.path.join(BASE_DIR))
client = None  # vai ser definido depois pelo main.py
status_cache = None
loja_cache = None



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




#FUNÇÃO PARA ATUALIZAR O CACHE DA LOJA
def atualizar_loja_cache(pymongo):
    global loja_cache
    loja_cache = []
    dados = list(pymongo)[::-1]
    for item in dados:
        loja_cache.append({
                    "name": item.get("name", "Sem nome"),
                    "descricao": item.get("descricao", "Sem descrição"),
                    "url": item.get("url", ""),  # URL da imagem
                    "braixencoin": f"{item.get('braixencoin', 0):,}".replace(",", "."),
                    "graveto": f"{item.get('graveto', 0):,}".replace(",", "."),
                    "raridade": item.get("raridade", 0),
                    "font_color": item.get("font_color", 0)
                })







#FUNÇÃO PARA ATUALIZAR O CACHE DOS COMANDOS
def atualizar_status_cache():
    global status_cache
    if client and client.is_ready():
 
        comandos_normais = [cmd.name for cmd in client.commands]
        comandos_slash = []

        for cmd in sorted(client.tree.get_commands(), key=lambda c: c.name):
            if isinstance(cmd, discord.app_commands.Group):
                comandos_slash.extend(extrair_comandos_grupo(cmd))
            elif isinstance(cmd, discord.app_commands.ContextMenu):
                continue
            else:
                comandos_slash.append({
                    "nome": cmd.name,
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
        
        status_cache = {
            "servidores": f"{len(client.guilds):,}".replace(",", "."),
            "usuarios": f"{len(client.users):,}".replace(",", "."),
            "shards": f"{client.shard_count:,}".replace(",", "."),
            "nome": str(client.user.name),
            "nome_completo": str(client.application.name),
            "num_comandos_normais": len(comandos_normais),
            "num_comandos_slash": f"{len(comandos_slash):,}".replace(",", "."),
            "total_comandos": f"{len(comandos_normais) + len(comandos_slash):,}".replace(",", "."),
            "lista_comandos_normais": comandos_normais,
            "lista_comandos_slash": comandos_slash
        }




#DIRECIONADORES DE ROTAS

@app.route('/')
def index():
    return send_from_directory(BASE_DIR, 'index.html')


@app.route('/comandos')
def comandos():
    return send_from_directory(BASE_DIR, 'comandos.html')

@app.route('/loja')
def loja():
    return send_from_directory(BASE_DIR, 'loja.html')

#@app.route('/premium')
#def premium():
#    return send_from_directory(BASE_DIR, 'premium.html')


@app.route('/<path:path>')
def serve_file(path):
    return send_from_directory(BASE_DIR, path)




#RESPOSTAS PARA SOLICITAÇÃO DE API

@app.route('/api/status')
def status():
    if status_cache:
        return jsonify(status_cache)
    else:
        return jsonify({"status": "bot ainda iniciando..."})



@app.route('/api/loja')
def statusloja():
    if loja_cache:
        return jsonify(loja_cache)
    else:
        return jsonify({"status": "bot ainda iniciando..."})





#INICIA O WEBSERVER

def iniciar_webserver(bot_client):
    global client
    client = bot_client
    threading.Thread(target=_run_web).start()





#RODA O WEBSERVER

def _run_web():
    #time.sleep(120)  # espera 3 minutos
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.logger.disabled = True
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
