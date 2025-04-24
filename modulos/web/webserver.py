from flask import Flask, send_from_directory, jsonify
import threading , os , discord.app_commands , logging , time  


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=os.path.join(BASE_DIR))
client = None  # vai ser definido depois pelo main.py
status_cache = None






def atualizar_status_cache():
    global status_cache
    if client and client.is_ready():
        def contar_comandos_slash():
            total = 0
            for cmd in client.tree.get_commands():
                if isinstance(cmd, discord.app_commands.Group):
                    total += len(cmd.commands)
                else:
                    total += 1
            return total

        comandos_normais = [cmd.name for cmd in client.commands]
        comandos_slash = []
        for cmd in client.tree.get_commands():
            if isinstance(cmd, discord.app_commands.Group):
                for sub in cmd.commands:
                    comandos_slash.append(f"{cmd.name} {sub.name}")
            else:
                comandos_slash.append(cmd.name)

        status_cache = {
            "servidores": f"{len(client.guilds):,}".replace(",", "."),
            "usuarios": f"{len(client.users):,}".replace(",", "."),
            "shards": f"{client.shard_count:,}".replace(",", "."),
            "nome": str(client.user.name),
            "nome_completo": str(client.application.name),
            "comandos_normais": comandos_normais,
            "comandos_slash": f"{contar_comandos_slash():,}".replace(",", "."),
            "total_comandos": f"{len(comandos_normais) + len(comandos_slash):,}".replace(",", ".")
        }








@app.route('/')
def index():
    return send_from_directory(BASE_DIR, 'index.html')





@app.route('/<path:path>')
def serve_file(path):
    return send_from_directory(BASE_DIR, path)






@app.route('/api/status')
def status():
    if status_cache:
        return jsonify(status_cache)
    else:
        return jsonify({"status": "bot ainda iniciando..."})

  #  if client and client.is_ready():
     #   def contar_comandos_slash():
     #       total = 0
      #      for cmd in client.tree.get_commands():
      ##          if isinstance(cmd, discord.app_commands.Group):
        #            total += len(cmd.commands)
       #         else:
       #             total += 1
       #     return total
#
      #  comandos_normais = [cmd.name for cmd in client.commands]
      #  comandos_slash = []
       # for cmd in client.tree.get_commands():
      #      if isinstance(cmd, discord.app_commands.Group):
      #          for sub in cmd.commands:
      #              comandos_slash.append(f"{cmd.name} {sub.name}")
       #     else:
       #         comandos_slash.append(cmd.name)

       # return jsonify({
     #       "servidores": f"{len(client.guilds):,}".replace(",", "."),
       #     "usuarios": f"{len(client.users):,}".replace(",", "."),
       #     "shards": f"{client.shard_count:,}".replace(",", "."),
       #     "nome": str(client.user.name),
       #     "nome_completo": str(client.application.name),
       ##     "comandos_normais": comandos_normais,
      #      "comandos_slash": f"{contar_comandos_slash():,}".replace(",", "."),
       #     "total_comandos": f"{len(comandos_normais) + len(comandos_slash):,}".replace(",", ".")
     #   })
    #else:
      #  return jsonify({"status": "bot ainda iniciando..."})






def iniciar_webserver(bot_client):
    global client
    client = bot_client
    threading.Thread(target=_run_web).start()






def _run_web():
    time.sleep(120)  # espera 3 minutos
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.logger.disabled = True
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
