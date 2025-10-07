import discord,os,json,asyncio,re
from discord import app_commands
from google import genai
from deep_translator import GoogleTranslator
from dotenv import load_dotenv


load_dotenv()
GOOGLE_AI_KEY = os.getenv("GOOGLE_AI_KEY")


genaitradutor = None


#Lista de idiomas compartiveis
# "Portuguese": "pt", "English": "en", "Spanish": "es", "French": "fr", "German": "de", "Italian": "it",
# "Russian": "ru", "Japanese": "ja", "Korean": "ko", "Arabic": "ar", "Hindi": "hi",
# "Bengali": "bn", "Urdu": "ur", "Turkish": "tr", "Dutch": "nl", "Swedish": "sv", "Polish": "pl",
# "Romanian": "ro", "Hungarian": "hu", "Greek": "el", "Czech": "cs", "Danish": "da", "Finnish": "fi",
# "Norwegian": "no"
    


# ======================================================================
# CARREGANDO A API DO GEMINI PARA TRADUZIR AS COISAS
try:
    if not GOOGLE_AI_KEY:
        raise ValueError("API KEY ausente.")
    genaitradutor = genai.Client(api_key=GOOGLE_AI_KEY)
except Exception as e:
    print(f"❌  -  Erro ao inicializar GenAI: {e}")
    print("❌  -  Tradução por IA desativada.")













# ======================================================================
#sistema para traduzir para qualquer idioma que eu queira

class BrixTradutor(app_commands.Translator):
    def __init__(self, dir_name='src/core/traducoes', response_dir='src/core/responses'):
        print("🌐  -  Iniciando Traduções Automáticas!")
        # Criar diretórios, se não existirem
        self.dir_name = dir_name
        self.response_dir = response_dir

        for directory in [self.dir_name, self.response_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)

        # Lista de idiomas suportados e nomes dos arquivos JSON
        self.allowed_locales = {
            discord.Locale.american_english: 'en-US',
            #discord.Locale.spain_spanish: 'es-ES',
            discord.Locale.polish :'pl',
            #discord.Locale.japanese: 'ja',
            #discord.Locale.french: 'fr',
        }

        # Carregar traduções de comandos
        self.translations = self.load_translations(self.dir_name)

        # Carregar mensagens de resposta da pasta response/
        self.response_translations = self.load_translations(self.response_dir)











# ======================================================================
    def load_translations(self, directory):
        """Carrega ou cria arquivos de tradução para cada idioma."""
        translations = {}

        for locale, file_name in self.allowed_locales.items():
            file_path = os.path.join(directory, f"{file_name}.json")

            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    translations[locale] = json.load(f)
            else:
                translations[locale] = {}

        return translations

















# ======================================================================
    async def translate(self, string: app_commands.locale_str, locale: discord.Locale, context: app_commands.TranslationContext):
        message_str = string.message

        # Garante que sempre vai ter pt-BR salvo também
        file_path_ptbr = os.path.join(self.dir_name, "pt-BR.json")
        if "pt-BR" not in self.translations:
            self.translations["pt-BR"] = {}

        # Salva o texto original em pt-BR.json se ainda não estiver lá
        if message_str not in self.translations["pt-BR"]:
            self.translations["pt-BR"][message_str] = message_str
            with open(file_path_ptbr, 'w', encoding='utf-8') as f:
                json.dump(self.translations["pt-BR"], f, ensure_ascii=False, indent=4)


        # Se for português, retorna o texto original
        if locale == discord.Locale.brazil_portuguese:
            return message_str

        # Se o idioma não estiver na lista permitida, retorna o texto original
        if locale not in self.allowed_locales:
            return message_str

        # Nome do arquivo JSON correspondente
        file_name = self.allowed_locales[locale]
        file_path = os.path.join(self.dir_name, f"{file_name}.json")

        # Se a tradução já existir, retorna ela
        if message_str in self.translations[locale]:
            return self.translations[locale][message_str]

        await asyncio.sleep(2)
        # Traduzir a mensagem e armazenar
        target_lang = file_name.split('-')[0]    
        response = genaitradutor.models.generate_content(model="gemini-2.0-flash" , contents=f"você é um tradutor e deve retornar apenas a tradução do texto enviado, mantendo qualquer emoji junto com seu ponto de separação caso tenha e qualquer indicação em seu respectivo lugar, caso a mensagem já esteja no respectivo idioma mantem oque foi enviado, faça isso em {target_lang} para a seguinte mensagem: {message_str}") 
        translated_text = response.text
        #translated_text = GoogleTranslator(source='pt', target=target_lang).translate(message_str)

        # Ajustar formatação da tradução (se for nome de comando)
        if " " in message_str:
            translated_text = translated_text.strip().lower()
        else:
            translated_text = translated_text.strip().replace(" ", "").lower()

        # Armazena a nova tradução
        self.translations[locale][message_str] = translated_text

        # Salvar no JSON correspondente
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.translations[locale], f, ensure_ascii=False, indent=4)

        print(f"✅ - Traduzido comando para {file_name}: {translated_text}")
        return translated_text














# ======================================================================
    # TRADUTOR DAS RESPOSTAS DO BOT COM BASE NO ARQUIVO PRINCIPAL pt-BR
    """async def translate_responses(self):
        # Lê o arquivo pt-BR.json em response/ e gera as traduções para os outros idiomas.
        pt_br_file = os.path.join(self.response_dir, "pt-BR.json")

        if not os.path.exists(pt_br_file):
            print("Arquivo pt-BR.json não encontrado em response/.")
            return

        with open(pt_br_file, 'r', encoding='utf-8') as f:
            pt_br_messages = json.load(f)

        for key, message in pt_br_messages.items():
            # Verifica se a mensagem é uma lista
            if isinstance(message, list):
                messages_to_translate = message  # Se for uma lista, mantém como está
            elif isinstance(message, str):
                messages_to_translate = [message]  # Se for uma string, transforma em lista de 1 item
            else:
                continue  # Pula casos que não são nem string nem lista

            for locale, file_name in self.allowed_locales.items():
                target_lang = file_name.split('-')[0]
                response_file = os.path.join(self.response_dir, f"{file_name}.json")

                # Carrega as traduções existentes, se o arquivo já existir
                if os.path.exists(response_file):
                    with open(response_file, 'r', encoding='utf-8') as f:
                        translated_messages_dict = json.load(f)
                else:
                    translated_messages_dict = {}

                # Se a chave ainda não existe, cria uma lista vazia
                if key not in translated_messages_dict:
                    translated_messages_dict[key] = []

                # Garantir que o valor para a chave seja uma lista
                if not isinstance(translated_messages_dict[key], list):
                    translated_messages_dict[key] = [translated_messages_dict[key]]

                # Verifica se a chave já existe e, se sim, pula a tradução para ela
                if key in translated_messages_dict and translated_messages_dict[key]:
                    continue  # Pula para a próxima chave

                for msg in messages_to_translate:
                    # Remove e armazena emojis personalizados
                    cleaned_message, emoji_positions = self.remove_custom_emojis(msg)
                    # Tradução
                    await asyncio.sleep(0.5)  # Evitar limites de taxa
                    #response = genaitradutor.models.generate_content(model="gemini-2.0-flash" , contents=f"Você é um tradutor e deve retornar apenas a tradução do texto enviado, mantendo qualquer emoji e formatação. Se a mensagem já estiver em {target_lang}, mantenha o texto original. Traduza para {target_lang}: {cleaned_message}")
                    #translated_text =  response.text.rstrip("\n") 
                    translated_text = GoogleTranslator(source='pt', target=target_lang).translate(cleaned_message)
                    # Restaurar emojis
                    final_translated_text = self.restore_emojis(translated_text, emoji_positions)

                    # Adiciona a resposta traduzida na lista
                    if isinstance(message, list):
                        translated_messages_dict[key].append(final_translated_text)

                    elif isinstance(message, str):
                        # Se for uma string única, armazena diretamente sem a lista
                        translated_messages_dict[key] = final_translated_text  # Não usa append, armazena diretamente
                    print(f"Traduzido {key} para {file_name}")

                # Salvar o arquivo atualizado
                with open(response_file, 'w', encoding='utf-8') as f:
                    json.dump(translated_messages_dict, f, ensure_ascii=False, indent=4)

        print("🌐  -  Traduções concluídas!")"""



    # ======================================================================
    # TRADUTOR DAS RESPOSTAS DO BOT COM BASE NO ARQUIVO PRINCIPAL pt-BR
    async def translate_responses(self):
        pt_br_file = os.path.join(self.response_dir, "pt-BR.json")

        if not os.path.exists(pt_br_file):
            print("Arquivo pt-BR.json não encontrado em response/.")
            return

        with open(pt_br_file, 'r', encoding='utf-8') as f:
            pt_br_messages = json.load(f)

        # Função auxiliar para processar string/lista/dict
        def process_message(msg, target_lang):
            """Processa mensagens que podem ser string, lista ou dicionário."""
            if isinstance(msg, str):
                cleaned_message, emoji_positions = self.remove_custom_emojis(msg)
                response = genaitradutor.models.generate_content(model="gemini-2.0-flash" , contents=f"Você é um tradutor e deve retornar apenas a tradução do texto enviado, mantendo qualquer emoji e formatação. Se a mensagem já estiver em {target_lang}, mantenha o texto original. Traduza para {target_lang}: {cleaned_message}")
                translated_text =  response.text.rstrip("\n") 
                return self.restore_emojis(translated_text, emoji_positions)

            elif isinstance(msg, list):
                return [process_message(item, target_lang) for item in msg]

            elif isinstance(msg, dict):
                return {k: process_message(v, target_lang) for k, v in msg.items()}

            else:
                return msg  # qualquer outro tipo, retorna sem mexer

        # Itera sobre cada chave do pt-BR.json
        for key, message in pt_br_messages.items():
            for locale, file_name in self.allowed_locales.items():
                target_lang = file_name.split('-')[0]
                response_file = os.path.join(self.response_dir, f"{file_name}.json")

                # Carrega traduções existentes, se houver
                if os.path.exists(response_file):
                    with open(response_file, 'r', encoding='utf-8') as f:
                        translated_messages_dict = json.load(f)
                else:
                    translated_messages_dict = {}

                # Se a chave já existe e tem conteúdo, pula
                if key in translated_messages_dict and translated_messages_dict[key]:
                    continue

                # Traduz a mensagem (string/list/dict)
                translated_result = process_message(message, target_lang)

                # Garante consistência no tipo de saída
                if isinstance(message, list):
                    translated_messages_dict[key] = translated_result
                elif isinstance(message, str):
                    translated_messages_dict[key] = translated_result
                elif isinstance(message, dict):
                    translated_messages_dict[key] = translated_result

                print(f"Traduzido {key} para {file_name}")

                # Salva o arquivo atualizado
                with open(response_file, 'w', encoding='utf-8') as f:
                    json.dump(translated_messages_dict, f, ensure_ascii=False, indent=4)

        print("🌐  -  Traduções concluídas!")












# ======================================================================
    def remove_custom_emojis(self, message):
        """Remove emojis personalizados (estáticos e animados) da mensagem e retorna o texto limpo e as posições."""
        # Regex para identificar emojis personalizados (estáticos <:...:...> e animados <a:...:...>)
        emoji_pattern = r'(<a?:[a-zA-Z0-9_]+:[0-9]+>)'
        
        # Encontrar todos os emojis personalizados e suas posições
        emojis = re.findall(emoji_pattern, message)
        emoji_positions = []

        # Substituir os emojis por um marcador temporário e manter o emoji original (nome e ID)
        for i, emoji in enumerate(emojis):
            emoji_positions.append((i, emoji, message.find(emoji)))  # (índice, emoji, posição no texto)
            message = message.replace(emoji, f"%{i}", 1)  # Substitui por marcador único
        
        return message, emoji_positions













# ======================================================================
    """def restore_emojis(self, translated_text, emoji_positions):
        # Restaurar os emojis nas posições corretas
        for i, emoji, position in reversed(emoji_positions):  # Coloca os emojis na posição original
            translated_text = translated_text[:position] + emoji + translated_text[position:]

        # Agora removemos os marcadores temporários
        translated_text = re.sub(r'[%]\d+', '', translated_text)  # Remove qualquer marcador EMOJI{i}
        return translated_text"""
    
# ======================================================================
    def restore_emojis(self, translated_text, emoji_positions):
        """Restaura os emojis personalizados substituindo os marcadores %i pelos emojis originais."""
        for i, emoji, _ in emoji_positions:  # posição original não é mais necessária
            translated_text = translated_text.replace(f"%{i}", emoji)

        return translated_text
