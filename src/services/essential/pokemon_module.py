import discord , requests , json , os , re , asyncio
from discord import app_commands
from icalendar import Calendar


# ======= CORES POR TIPO ==========
tipos_cores = [{"tipo": "Normal", "cor": "#d7d69f"},{"tipo": "Fire", "cor": "#EE8130"},    {"tipo": "Water", "cor": "#6390F0"},    {"tipo": "Electric", "cor": "#d2ba55"},    {"tipo": "Grass", "cor": "#7AC74C"},    {"tipo": "Ice", "cor": "#a3fcf8"},    {"tipo": "Fighting", "cor": "#ea514a"},    {"tipo": "Poison", "cor": "#a74fa5"},    {"tipo": "Ground", "cor": "#E2BF65"},    {"tipo": "Flying", "cor": "#988ff3"},    {"tipo": "Psychic", "cor": "#fd6593"},    {"tipo": "Bug", "cor": "#A6B91A"},    {"tipo": "Rock", "cor": "#a89223"},    {"tipo": "Ghost", "cor": "#7e56b1"},    {"tipo": "Dragon", "cor": "#753dfe"},    {"tipo": "Dark", "cor": "#705746"},    {"tipo": "Steel", "cor": "#B7B7CE"},    {"tipo": "Fairy", "cor": "#e375ab"}]


# ======= INSTÂNCIAS GLOBAIS ==========
pokemon_cache = None
jogos_cache = None










# ======================================================================
# ======= FUNÇÕES ==========
#PROCURADOR DE COR COM BASE NA TIPAGEM
def encontrar_cor_tipo(nome_tipo):
    # Converte o nome do tipo recebido para capitalizado (ex.: "fire" -> "Fire")
    nome_tipo = nome_tipo.capitalize()
    # Itera sobre a lista para encontrar a cor correspondente
    for tipo in tipos_cores:
        if tipo["tipo"] == nome_tipo:
            return tipo["cor"]
    return None  # Caso o tipo não seja encontrado











# ======================================================================
#VERIFICA E BUSCA UM POKÉMON OU DATA NO CALENDARIO
async def verificar_calendario_pokemon(data_atual=None, pokemon_nome=None):
    with open('src/services/caches/pokedaycalendar.ics', 'rb') as f:
        cal = Calendar.from_ical(f.read())
    
    # Busca por data
    if data_atual:
        dia_procurado = data_atual.day
        mes_procurado = data_atual.month
        listapokemon = []
        
        print(f"Verificando pokeday para hoje: {data_atual}")
        for component in cal.walk('VEVENT'):
            dtstart = component.get('dtstart').dt
            if dtstart.day == dia_procurado and dtstart.month == mes_procurado:
                pokemon = re.sub(r" Day.*", "", component.get('summary'))
                listapokemon.append(pokemon)
        
        return listapokemon if listapokemon else None
    
    # Busca por nome
    if pokemon_nome:
        nome_normalizado = pokemon_nome.lower()
        for component in cal.walk('VEVENT'):
            summary = component.get('summary', '').lower()
            if nome_normalizado in summary:
                dtstart = component.get('dtstart').dt
                return dtstart
        
        return None
















# ======================================================================
class PokemonCache:
    def __init__(self, cache_file='src/services/caches/pokemon_cache.json'):
        self.cache_file = cache_file
        self.pokemon_data = []  # lista de dicts
        self.loaded = False





# ======================================================================
    async def load_pokemon_data(self):
        if self.loaded:
            return

        cache_existente = {}
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                try:
                    self.pokemon_data = json.load(f)
                    cache_existente = { p['name']: p for p in self.pokemon_data }
                except Exception as e:
                    print(f"[WARN] Falha ao ler cache local: {e}")
                    self.pokemon_data = []
                    cache_existente = {}

        try:
            response = requests.get("https://pokeapi.co/api/v2/pokemon?limit=10000", timeout=10) #10000
            response.raise_for_status()
            data = response.json()

            nova_lista = []
            novos_count = 0  # contador de novos pokémon carregados

            for p in data['results']:
                nome = p['name']
                url = p['url']

                precisa_atualizar = False
                if nome in cache_existente:
                    poke_local = cache_existente[nome]
                    if (poke_local.get('front_default') is None 
                        or poke_local.get('front_shiny') is None
                        or poke_local.get('species') is None
                        or poke_local.get('abilities') is None
                        or poke_local.get('stats') is None
                        or not poke_local.get('types')):
                        precisa_atualizar = True
                    else:
                        nova_lista.append(poke_local)
                        continue
                else:
                    precisa_atualizar = True

                if precisa_atualizar:
                    try:
                        detalhe = requests.get(url, timeout=5).json()
                        front_default = detalhe['sprites']['other']['home']['front_default']
                        front_shiny = detalhe['sprites']['other']['home']['front_shiny']
                        poke_id = detalhe['id']
                        types = detalhe['types']
                        height = detalhe['height']
                        weight = detalhe['weight']
                        abilities = detalhe['abilities']
                        stats = detalhe['stats']
                        species = detalhe['species']['url'] #requests.get(species_url, timeout=5).json()
                    except Exception as e:
                        print(f"[WARN] Falha ao buscar dados de {nome}: {e}")
                        front_default, front_shiny, poke_id, types = None, None, None, []
                        abilities, stats, species = None, None, None

                    novo_poke = {
                        "id": poke_id, "name": nome,
                        "front_default": front_default, "front_shiny": front_shiny,
                        "types": types, "height": height, "weight": weight,
                        "abilities": abilities, "stats": stats, "species": species
                    }
                    nova_lista.append(novo_poke)
                    novos_count += 1
                    await asyncio.sleep(0.1)

                    # salva a cada 20 novos pokémon
                    if novos_count % 40 == 0:
                        with open(self.cache_file, 'w', encoding='utf-8') as f:
                            json.dump(nova_lista, f, ensure_ascii=False, indent=2)
                        print(f"Cache parcial salvo após {novos_count} novos pokémon.")

            # salva cache final completo
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(nova_lista, f, ensure_ascii=False, indent=2)
            self.pokemon_data = nova_lista
            print(f"Cache final salvo após {novos_count} novos pokémon.")
        except Exception as e:
            print(f"[AVISO] Falha ao consultar lista geral da API: {e}")
            if not self.pokemon_data:
                print("[ERRO] Nenhum dado disponível. Lista vazia.")

        self.loaded = True

    def get_pokemon_data(self):
        return self.pokemon_data
    
















# ======================================================================
class JogosCache:
    def __init__(self, cache_file='src/services/caches/jogos_cache.json'):
        self.cache_file = cache_file
        self.jogos_data = []
        self.loaded = False

    async def load_jogos_data(self):
        if self.loaded:
            return

        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.jogos_data = json.load(f)
            except Exception as e:
                print(f"[ERRO] Falha ao carregar o cache: {e}")
                self.jogos_data = []
        else:
            print("[AVISO] Cache não encontrado. Lista de jogos vazia.")
            self.jogos_data = []

        self.loaded = True

    def get_jogos_data(self):
        return self.jogos_data
    
















# ======================================================================
# ======= FUNÇÕES PÚBLICAS ==========
#COLETA UM POKÈMON 
async def get_pokemon(key):
    await inicializar_caches_se_preciso()
    key = str(key).lower()
    for p in pokemon_cache.get_pokemon_data():
        if str(p['id']) == key or p['name'].lower() == key:
            return p
    return None





# ======================================================================
#COLETA TODOS OS POKÉMON
async def get_all_pokemon():
    await inicializar_caches_se_preciso()
    return pokemon_cache.get_pokemon_data()








# ======================================================================
#COLETA OS DADOS DE UM JOGO BASEADO NA ID
async def get_jogo_nome(jogo_id):
    await inicializar_caches_se_preciso()
    for j in jogos_cache.get_jogos_data():
        if j['id'] == jogo_id:
            return j['name'], j['plataforma']
    return None, None












# ======================================================================
#SISTEMA DE AUTOCOMPLETE PARA NOME DE POKÉMON
async def pokemon_autocomplete(interaction, current):
    await inicializar_caches_se_preciso()
    cache = pokemon_cache.get_pokemon_data()
    filtrado = [p for p in cache if current.lower() in p['name'].lower()]
    return [app_commands.Choice(name=f"{p['id']} - {p['name']}", value=p['name']) for p in filtrado][:25]













# ======================================================================
#SISTEMA DE AUTOCOMPLETE PARA JOGOS POKÉMON
async def jogos_autocomplete(interaction, current):
    await inicializar_caches_se_preciso()
    cache = jogos_cache.get_jogos_data()
    filtrado = [j for j in cache if current.lower() in j['name'].lower()]
    return [app_commands.Choice(name=f"{j['name']} ({j['plataforma']})", value=j['id']) for j in reversed(filtrado)][:25]














# ======================================================================
#SISTEMA QUE INICIA O SISTEMA DE CACHE LOCAL
async def inicializar_caches_se_preciso():
    global pokemon_cache, jogos_cache
    if pokemon_cache is None:
        pokemon_cache = PokemonCache()
        await pokemon_cache.load_pokemon_data()
    if jogos_cache is None:
        jogos_cache = JogosCache()
        await jogos_cache.load_jogos_data()
