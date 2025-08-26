from flask import Flask, send_from_directory, jsonify , redirect , render_template , request, session
from flask_session import Session
from pymongo import MongoClient
import threading , os , discord.app_commands , re , time , secrets , requests,asyncio , logging 
from src.services.connection.database import BancoUsuarios ,BancoServidores , BancoLoja , BancoBot
from src.services.essential.diversos import calcular_saldo 
from flask import request
from dotenv import load_dotenv


# ======================================================================
# LOADS DAS INFORMAÇÕES IMPORTANTES DO .ENV

load_dotenv(os.path.join(os.path.dirname(__file__), '.env')) #load .env da raiz
CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")




# ======================================================================
# CONEXÂO COM MONGODB PARA SESSÔES

mongo_uri = os.getenv("MONGO_URI")
mongo_client = MongoClient(mongo_uri)
db_connection = mongo_client["brix"]
db_connection['sessions'].create_index('expiration', expireAfterSeconds=0)





# ======================================================================
#PARTE DO INICIO DA SESSÂO FLASK COM MONGODB
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=os.path.join(BASE_DIR) , template_folder=".")
app.config['SESSION_TYPE'] = 'mongodb'
app.config['SESSION_MONGODB'] = mongo_client
app.config['SESSION_MONGODB_DB'] = 'brix'
app.config['SESSION_MONGODB_COLLECT'] = 'sessions'
app.config['SECRET_KEY'] = secrets.token_hex(32)
app.config['PERMANENT_SESSION_LIFETIME'] = 345600  # 4 dias em segundos






# ======================================================================
# CRIANDO A SESSÃO E OS CACHES NECESSARIOS
Session(app)
client = None  # vai ser definido depois pelo main.py
status_cache = {} # vai armazenar os dados do bot
loja_cache = {} # vai armazenar os itens da loja







# ======================================================================
#PARTE DA SOLICITAÇÂO DO DISCORD PARA DASHBOARD
CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
REDIRECT_URI = os.getenv("REDIRECT_URI")
SCOPES = "identify guilds"
DISCORD_AUTH_URL = f"https://discord.com/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope={SCOPES}"












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
#FUNÇÃO PARA ATUALIZAR O CACHE DA LOJA
def atualizar_loja_cache():
    global loja_cache
    try:
        filtro = {"braixencoin": {"$exists": True}}
        pymongo = BancoLoja.select_many_document(filtro)
    except Exception as e:
        print(f"[ERRO] Falha ao atualizar cache dos itens da loja: {e}")
        return  # Sai e tenta de novo na próxima chamada
    
    loja_cache = []
    dados = list(pymongo)[::-1]
    for item in dados:
        loja_cache.append({
            "_id": item.get("_id", "Sem id"),
            "name": item.get("name", "Sem nome"),
            "descricao": item.get("descricao", "Sem descrição"),
            "url": item.get("url", ""),  # URL da imagem
            "braixencoin": f"{item.get('braixencoin', 0):,}".replace(",", "."),
            "graveto": f"{item.get('graveto', 0):,}".replace(",", "."),
            "raridade": item.get("raridade", 0),
            "font_color": item.get("font_color", 0)
        })












# ======================================================================
#FUNÇÃO PARA ATUALIZAR O CACHE DOS COMANDOS
def atualizar_status_cache():
    global status_cache
    if client and client.is_ready():
        try:
            filtro = {"braixencoin": {"$exists": True}}
            usuarios = BancoUsuarios.select_many_document(filtro)
        except Exception as e:
            print(f"[ERRO] Falha ao atualizar cache: {e}")
            return  # Sai e tenta de novo na próxima chamada

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

        total_moeda = sum(usuario.get("braixencoin", 0) for usuario in usuarios)
        total_moeda = calcular_saldo(total_moeda)

        dadosbot = BancoBot.insert_document()

        status_cache = {
            "hora_atualização": time.strftime("%d/%m/%Y - %H:%M:%S", time.localtime()),
            "servidores": calcular_saldo(len(client.guilds)), 
            "usuarios": f"+{calcular_saldo(len(client.users))}", 
            "braixencoin": f"+{total_moeda}",
            "shards": f"{client.shard_count:,}".replace(",", "."),
            "nome": str(client.user.name),
            "nome_completo": str(client.application.name),
            "num_comandos_normais": len(comandos_normais),
            "num_comandos_slash": f"{len(comandos_slash):,}".replace(",", "."),
            "total_comandos": f"{len(comandos_normais) + len(comandos_slash):,}".replace(",", "."),
            "lista_comandos_normais": comandos_normais,
            "lista_comandos_slash": comandos_slash,
            "status_dashboard": dadosbot["status_dashboard"]
        }























# ======================================================================


# ================================== DIRECIONADORES DE ROTAS =========================

#CAMINHO DE ORIGEM DA PAGINA
@app.route('/')
def index():
    user = session.get("user")
    if isinstance(user, dict) and user.get("message") == "401: Unauthorized":
        user = None
        session["user"] = None
    guilds = session.get("guilds", [])
    if not user or not guilds:
        return render_template("index.html")
    return render_template("index.html", user=user, guilds=guilds)









# ======================================================================
#CAMINHO PARA PAGINA DE COMANDOS
@app.route('/comandos')
def comandos():
    user = session.get("user")
    if isinstance(user, dict) and user.get("message") == "401: Unauthorized":
        user = None
        session["user"] = None
    guilds = session.get("guilds", [])
    if not user or not guilds:
        return render_template("comandos.html")
    return render_template("comandos.html", user=user, guilds=guilds)










# ======================================================================
#CAMINHO PARA PAGINA DA LOJA DE ITENS DO BRIX
@app.route('/loja')
def loja():
    user = session.get("user")
    if isinstance(user, dict) and user.get("message") == "401: Unauthorized":
        user = None
        session["user"] = None
    guilds = session.get("guilds", [])
    if not user or not guilds:
        return render_template("loja.html")
    return render_template("loja.html", user=user, guilds=guilds )











# ======================================================================
#CAMINHO PARA PAGINA DE ASSINATURA PREMIUM (NÃO FEITO AINDA)
#@app.route('/premium')
#def premium():
   # user = session.get("user")
   # guilds = session.get("guilds", [])
   # if not user or not guilds:
   #     return render_template("premium.html")
   # return render_template("premium.html", user=user, guilds=guilds)









# ======================================================================
# ESSE CARA AQUI DIRECIONA PARA A ORIGEM EM CASO DE PROBLEMAS
@app.route('/<path:path>')
def serve_file(path):
    return send_from_directory(BASE_DIR, path)











# ======================================================================
#CALLBACK DO LOGIN RELACIONADO AO RETORNO DO DISCORD
@app.route("/login")
def login():
    user = session.get("user")
    if isinstance(user, dict) and user.get("message") == "401: Unauthorized":
        user = None
        session["user"] = None
    access_token = session.get("access_token")

    if not user or not access_token:
        return redirect(DISCORD_AUTH_URL)
    
    return redirect("/dashboard")












# ======================================================================
#CAMINHO PARA A PAGINA DE DASHBOARD DO BRIX QUE TAMBÉM FAZ TODA A VERIFICAÇÃO
@app.route("/dashboard")
def dashboard():
    if status_cache.get("status_dashboard",False) is not True:
        return render_template("manutencao.html")

    user = session.get("user")
    access_token = session.get("access_token")
    guilds = session.get("guilds")
    guilds_last_update = session.get("guilds_last_update", 0)

    if not user or not access_token:
        return render_template("dashlogin.html")
    
    # SE PASSAR MAIS DE 1 hora (3600 SEGUNDOS) RECARREGA TODAS AS ONFORMAÇÕES DO USUARIO
    if time.time() - guilds_last_update > 3600:
        try:            
            # 👉 ATUALIZA OS DADOS DO DISCORD
            all_guilds = requests.get("https://discord.com/api/users/@me/guilds",  headers={"Authorization": f"Bearer {access_token}"}).json()
            user = requests.get("https://discord.com/api/users/@me", headers={"Authorization": f"Bearer {access_token}"}).json()

            # 👉 Verifica se está banido antes de tudo
            user_doc = BancoUsuarios.insert_document(int(user["id"]))
            ban = user_doc.get("ban")
            if ban:
                session.clear()
                return render_template("banned.html")
        except:
            session.clear()
            return render_template("dashlogin.html")
        
        session["guilds"] = all_guilds
        session["guilds_last_update"] = time.time()
        session["user"] = user
        session["user_last_update"] = time.time()
        
    else:
        all_guilds = guilds #ELSE RETORNA OQUE JÁ ESTA NO CACHE DO BOT

    #REALIZA O FILTRO PARA SABER QUAIS COMUNIDADES DEVEM SER LISTADAS E ONDE DE FATO O BOT ESTÁ
    filtered_guilds = []
    for guild in all_guilds:
        user_is_owner = guild.get("owner", False)
        permissions = int(guild.get("permissions", 0))
        user_is_admin = (permissions & 0x8) != 0
        user_can_manage_server = (permissions & 0x20) != 0
        #VERIFICA SE O USUARIO É DONO OU PODE GERENCIAR A COMUNIDADE COMO ADMIN OU MANAGE-SERVER
        if user_is_owner or user_is_admin or user_can_manage_server:
            guild['bot_in_guild'] = client.get_guild(int(guild["id"])) is not None
            filtered_guilds.append(guild)
    # Ordena para exibir primeiro as comunidades onde o bot está
    filtered_guilds.sort(key=lambda g: not g.get('bot_in_guild', False))
    return render_template("dashboard.html", user=user, guilds=filtered_guilds)















# ======================================================================
#CALLBACK DO LOGIN RELACIONADO AO RETORNO DO DISCORD QUE PEGA TUDO E DIRECIONA PARA DASHBOARD
@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return redirect("/")

    data = {"client_id": CLIENT_ID,"client_secret": CLIENT_SECRET,"grant_type": "authorization_code","code": code,"redirect_uri": REDIRECT_URI,"scope": SCOPES,    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    token = requests.post("https://discord.com/api/oauth2/token", data=data, headers=headers).json()
    session.permanent = True
    access_token = token["access_token"]
    session["access_token"] = access_token
    # COLETAÇÃO DOS DADOS DO USUARIO E DE SUAS GUILDAS.
    user = requests.get("https://discord.com/api/users/@me", headers={"Authorization": f"Bearer {access_token}"}).json()
    guilds = requests.get("https://discord.com/api/users/@me/guilds", headers={"Authorization": f"Bearer {access_token}"}).json()
    session["user"] = user
    session["guilds"] = guilds
    session["guilds_last_update"] = time.time() #SALVO O HORARIO DO REGISTRO DOS DADOS
    session["user_last_update"] = time.time() #SALVO O HORARIO DO REGISTRO DOS DADOS
    return redirect("/dashboard")














# ======================================================================
#FERRAMENTA DE LOGOUT PARA FINALIZAR O LOGIN DO USUARIO
@app.route("/logout")
def logout():
    session.clear()  # REMOVE TODOS OS DADOS DA SESSÃO INDICADA
    return redirect("/") 














# ======================================================================
#PAGINA DO USUARIO DA DASHBOARD
@app.route("/user")
def user_dash():
    try:
        if status_cache.get("status_dashboard",False) is not True:
            return render_template("manutencao.html")
    
        user = session.get("user")
        if not user:
            return redirect("/dashboard")
        usuario = BancoUsuarios.insert_document(int(user["id"]))
        usuario.get('premium', False)
        perfil = {
            "premium": usuario['premium'].strftime('%d/%m/%Y') if usuario.get('premium', False) else False,
            "xpg": f"{usuario.get('xpg', 0):,}".replace(",", "."),
            "graveto": f"{usuario.get('graveto', 0):,}".replace(",", "."),
            "braixencoin": f"{usuario.get('braixencoin', 0):,}".replace(",", "."),
            "descricao": usuario.get("descricao", ""),
            "aniversario": usuario.get('nascimento', '00/00/0000'),
            "notificacoes": usuario["dm-notification"], 
            "backgroud": usuario.get("backgroud", ""),          
            "backgrouds": usuario.get("backgrouds", [])   
            
        }
        # USANDO A LOJA_CACHE GLOBAL DIRETAMENTE PARA EVITAR REQUESTS 
        backgrounds_usuario = [  item for item in loja_cache if item["_id"] in perfil["backgrouds"]]
        # GARANTO QUE O ITEM ATUAL DO USUARIO VIRÁ PRIMEIRO NA LISTA
        backgroud_atual = perfil["backgroud"]
        if backgroud_atual and backgroud_atual not in [item["_id"] for item in backgrounds_usuario]:
            item_atual = next((item for item in loja_cache if item["_id"] == backgroud_atual), None)
            if item_atual:
                backgrounds_usuario.append(item_atual)
        backgrounds_usuario.sort(key=lambda x: (x["_id"] != backgroud_atual, -x["raridade"]))
        return render_template("user.html", user=user, perfil=perfil, backgrounds=backgrounds_usuario)
    except: return redirect("/login")















# ======================================================================
#SALVA DADOS DA PAGINA DO USUARIO
@app.route("/dashboard/save-user", methods=["POST"])
def salvar_perfil_usuario():
    try:
        user = session.get("user")
        if not user:
            return redirect("/dashboard")

        descricao = request.form.get("descricao", "").strip()[:150]  # limita a 150
        arte_perfil = request.form.get("arte_perfil", "").strip()

        updates = {}
        if descricao:
            updates["descricao"] = descricao  # INCLUI DESCRIÇÃO NOVA NO UPDATE
        if arte_perfil:
            updates["backgroud"] = arte_perfil  # INCLUI ARTE DO PERFIL NO UPDATE

        updates["dm-notification"] = "ativar_notificacoes" in request.form
        if updates:
            BancoUsuarios.update_document(int(user["id"]), updates) # REALIZO O UPDATE NO BANCO DE DADOS
        return redirect("/user")
    except: return redirect("/login")
















# ======================================================================
# PÁGINA DE CONTROLE DO SERVIDOR
@app.route("/server/<guild_id>")
def guild_dashboard(guild_id):
    try:
        if status_cache.get("status_dashboard",False) is not True:
            return render_template("manutencao.html")
    
        user = session.get("user")
        guild = next((g for g in session.get("guilds", []) if g["id"] == str(guild_id)), None)
        if not user or not guild:
            return redirect("/dashboard")
        
        user_is_owner = guild.get("owner", False)
        permissions = int(guild.get("permissions", 0))
        user_is_admin = (permissions & 0x8) != 0
        user_can_manage_server = (permissions & 0x20) != 0

        if user_is_owner or user_is_admin or user_can_manage_server:
            guild = client.get_guild(int(guild_id))
            if guild is None:
                return redirect("/dashboard")
            # DADOS PROVENIENTES DO BANCO DE DADOS
            text_channels = [c for c in guild.text_channels]
            retbanco = BancoServidores.insert_document(int(guild_id))
            return render_template("server.html", user=user, retbanco=retbanco, guild=guild , text_channels=text_channels)
        
        return redirect("/dashboard")
    except: return redirect("/login")

















# ======================================================================
#SALVA DADOS DA PAGINA DE CONTROLE DO SERVIDOR
@app.route("/dashboard/save-guild", methods=["POST"])
def salvar_configuracoes():
    user = session.get("user")
    if not user:
        return redirect("/dashboard")
    guild_id = request.form.get("guild_id")
    if not guild_id:
        return "ID do servidor ausente", 400

    # Verifica se o user tem acesso ao servidor
    guilds = session.get("guilds", [])
    if not any(str(g["id"]) == guild_id for g in guilds):
        return "Acesso negado", 403

    updates = {}
    unset_fields = {}

    # ---------------- ANIVERSÁRIO ----------------
    if "ativar_aniversario" in request.form:
        destaque = request.form.get("cargo_temp_aniversario")
        aniversario = {
            "canal": int(request.form.get("canal_aniversario")),
            "cargo": int(request.form.get("cargo_ping_aniversario")),
        }
        if destaque and destaque.isdigit() and int(destaque) > 0:
            aniversario["destaque"] = int(destaque)

        updates["aniversario"] = aniversario
    else:
        unset_fields["aniversario"] = 1

    # ---------------- BOAS-VINDAS ----------------
    if "ativar_boasvindas" in request.form:
        updates["boasvindas"] = {
            "canal": int(request.form.get("canal_boasvindas")),
            "mensagem": request.form.get("mensagem_boasvindas", "").replace('\r\n', '\n').replace('\r', '\n').strip(),
            "deletar": int(request.form.get("boasvindas_deletar", 0))
        }
    else:
        unset_fields["boasvindas"] = 1

    # ---------------- AUTOPHOX ----------------
    if "ativar_autophox" in request.form:
        updates["autophox"] = int(request.form.get("canal_autophox"))
    else:
        unset_fields["autophox"] = 1

    # ---------------- LOJA DE CORES ----------------
    if "ativar_loja_cores" in request.form:
        from bs4 import BeautifulSoup
        html = request.form.get("lista-itens-loja-html", "")
        soup = BeautifulSoup(html, "html.parser")
        itensloja = {}
            
        for item in soup.find_all(attrs={"data-id": True}):
            cargo_id = item["data-id"]
            texto = item.get_text()
            match = re.findall(r"\b\d+\b", texto)
            valor = int(match[-1]) if match else 0
            itensloja[str(cargo_id)] = str(valor)

        updates["itensloja"] = itensloja
        link_arte = request.form.get("link_arte_loja", "").strip()
        if link_arte:
            updates["lojabanner"] = link_arte
    else:
        unset_fields["itensloja"] = 1
        unset_fields["lojabanner"] = 1

    # ---------------- BUMP ----------------
    if "ativar_bump" in request.form:
        updates["bump-message"] = request.form.get("mensagem_bump", "").replace('\r\n', '\n').replace('\r', '\n').strip()
    else:
        unset_fields["bump-message"] = 1

    # ---------------- POKÉDAY ----------------
    if "ativar_pokeday" in request.form:
        ping_val = request.form.get("cargo_pokeday", "").strip()
        updates["pokeday"] = {
            "canal": int(request.form.get("canal_pokeday")),
            "ping": int(ping_val) if ping_val.isdigit() else None
        }
    else:
        unset_fields["pokeday"] = 1

    
    # ---------------- TROCAS POKÉMON ----------------
    if "ativar_trocas" in request.form:
        ping_val = request.form.get("cargo_trocas", "").strip()
        updates["trocas_aviso"] = {
            "canal": int(request.form.get("canal_trocas")),
            "cargo": int(ping_val) if ping_val.isdigit() else None
        }
    else:
        unset_fields["trocas_aviso"] = 1


    
    # ---------------- SEGURANÇA ----------------
    if "ativar_seguranca" in request.form:
        tempo_valor = request.form.get("tempo_antialt")
        unidade = request.form.get("unidade_antialt")  # minutos, horas ou dias
        acao = request.form.get("acao_antialt", "kick")
        notificar = "notificar_antialt" in request.form

        # Converte tempo pra segundos
        try:
            tempo_num = int(tempo_valor)
            if unidade == "minutos":
                tempo_segundos = tempo_num * 60
            elif unidade == "horas":
                tempo_segundos = tempo_num * 3600
            elif unidade == "dias":
                tempo_segundos = tempo_num * 86400
            else:
                tempo_segundos = tempo_num  # fallback, caso venha vazio
        except (TypeError, ValueError):
            tempo_segundos = 432000 # valor padrão para 5 dias em caso de erro
        
        if tempo_segundos > 2592000:
            tempo_segundos = 2592000
        antialt = {
            "seguranca.antialt.tempo": tempo_segundos,
            "seguranca.antialt.acao": acao,
            "seguranca.antialt.notificacao": notificar
        }
        updates.update(antialt)
    else:
        unset_fields["seguranca"] = 1



    # Aplica updates de uma vez só
    if updates:
        BancoServidores.update_document(int(guild_id), updates)
    if unset_fields:
        BancoServidores.delete_field(int(guild_id), unset_fields)

    return redirect(f"/server/{guild_id}")





















# ======================================================================
# =============================== RESPOSTAS DE API =====================
# RETORNO DE STATUS DO BOT, COM COMANDOS E OUTROS DETALHES
@app.route('/api/status')
def status():
    if status_cache:
        return jsonify(status_cache)
    else:
        return jsonify({"status": "bot ainda iniciando..."})








# ======================================================================
# RETORNO PARA EXIBIR TODOS OS ITENS DA LOJA DO BOT NO SITE
@app.route('/api/loja')
def statusloja():
    if loja_cache:
        return jsonify(loja_cache)
    else:
        return jsonify({"status": "bot ainda iniciando..."})








# ======================================================================
# RETORNO DE UMA VENDA PELO SISTEMA MERCADO PAGO
@app.route('/comprapremium', methods=['POST'])
def webhook_mercadopago():
    data = request.json
    print("Webhook recebido:", data)
    
    return "OK", 200











# ======================================================================
# Caminho absoluto até a pasta all-itens
CAMINHO_ITENS = os.path.join(os.getcwd(), 'src' , 'assets' ,  'imagens', 'backgroud', 'all-itens')

@app.route('/src/assets/imagens/backgroud/all-itens/<path:filename>')
def servir_all_itens(filename):
    return send_from_directory(CAMINHO_ITENS, filename)








# ======================================================================
# INICIA O WEBSERVER PARA RODAR TODA A PARTE DO SITE

def iniciar_webserver(bot_client):
    global client
    client = bot_client
    threading.Thread(target=_run_web).start()
    




# ======================================================================
# REALIZA O LOOP PARA ATUALIZAR OS DADOS DE CACHE
async def loop_dados_site():
    while True:
        atualizar_status_cache()
        atualizar_loja_cache()
        await asyncio.sleep(600) #10 Minutos










# ======================================================================
#RODA O WEBSERVER DE VEZ OCULTANDO OS LOGS EXAGERADOS
def _run_web():
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.logger.disabled = True
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
