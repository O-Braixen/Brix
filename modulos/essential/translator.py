import discord,os,json,asyncio,re
from discord import app_commands
from google import genai
from dotenv import load_dotenv


load_dotenv()
GOOGLE_AI_KEY = os.getenv("GOOGLE_AI_KEY")
genaitradutor = genai.Client(api_key=GOOGLE_AI_KEY)


 #sistema para traduzir para qualquer idioma que eu queira

class BrixTradutor(app_commands.Translator):
    def __init__(self, dir_name='traduçãocomandos', response_dir='responses'):
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
            #discord.Locale.french: 'fr',
        }

        # Carregar traduções de comandos
        self.translations = self.load_translations(self.dir_name)

        # Carregar mensagens de resposta da pasta response/
        self.response_translations = self.load_translations(self.response_dir)

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

    async def translate(self, string: app_commands.locale_str, locale: discord.Locale, context: app_commands.TranslationContext):
        message_str = string.message

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

        await asyncio.sleep(5)
        # Traduzir a mensagem e armazenar
        target_lang = file_name.split('-')[0]    
        response = genaitradutor.models.generate_content(model="gemini-2.0-flash" , contents=f"você é um tradutor e deve retornar apenas a tradução do texto enviado, mantendo qualquer emoji junto com seu ponto de separação caso tenha e qualquer indicação em seu respectivo lugar, caso a mensagem já esteja no respectivo idioma mantem oque foi enviado, faça isso em {target_lang} para a seguinte mensagem: {message_str}") 
        translated_text = response.text

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

        print(f"Traduzido comando para {file_name}: {translated_text}")
        return translated_text



    # TRADUTOR DAS RESPOSTAS DO BOT COM BASE NO ARQUIVO PRINCIPAL pt-BR
    async def translate_responses(self):
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
                    await asyncio.sleep(10)  # Evitar limites de taxa
                    response = genaitradutor.models.generate_content(model="gemini-2.0-flash" , contents=f"Você é um tradutor e deve retornar apenas a tradução do texto enviado, mantendo qualquer emoji e formatação. Se a mensagem já estiver em {target_lang}, mantenha o texto original. Traduza para {target_lang}: {cleaned_message}")
                    #response = text_model.generate_content( f"Você é um tradutor e deve retornar apenas a tradução do texto enviado, mantendo qualquer emoji e formatação. Se a mensagem já estiver em {target_lang}, mantenha o texto original. Traduza para {target_lang}: {cleaned_message}")
                    translated_text =  response.text.rstrip("\n") 

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

        print("🌐  -  Traduções concluídas!")

    def remove_custom_emojis(self, message):
        """Remove emojis personalizados da mensagem e retorna o texto limpo e as posições dos emojis encontrados."""
        # Regex para identificar emojis personalizados
        emoji_pattern = r'(<:[a-zA-Z0-9_]+:[0-9]+>)'
        
        # Encontrar todos os emojis personalizados e suas posições
        emojis = re.findall(emoji_pattern, message)
        emoji_positions = []

        # Substituir os emojis por um marcador temporário e manter o emoji original (nome e ID)
        for i, emoji in enumerate(emojis):
            emoji_positions.append((i, emoji, message.find(emoji)))  # Armazenar o emoji e sua posição
            message = message.replace(emoji, f"E{i}", 1)  # Substitui o emoji por um marcador único
        
        return message, emoji_positions

    def restore_emojis(self, translated_text, emoji_positions):
        """Restaurar os emojis personalizados nas posições corretas da tradução."""
        # Restaurar os emojis nas posições corretas
        for i, emoji, position in reversed(emoji_positions):  # Coloca os emojis na posição original
            translated_text = translated_text[:position] + emoji + translated_text[position:]

        # Agora removemos os marcadores temporários
        translated_text = re.sub(r'[Ee]\d+', '', translated_text)  # Remove qualquer marcador EMOJI{i}

        return translated_text































    """async def translate_responses(self):
        #Lê o arquivo pt-BR.json em response/ e gera as traduções para os outros idiomas.
        pt_br_file = os.path.join(self.response_dir, "pt-BR.json")

        if not os.path.exists(pt_br_file):
            print("Arquivo pt-BR.json não encontrado em response/.")
            return

        with open(pt_br_file, 'r', encoding='utf-8') as f:
            pt_br_messages = json.load(f)

        for key, message in pt_br_messages.items():
            if isinstance(message, str):
                messages_to_translate = [message]
            elif isinstance(message, list):
                messages_to_translate = message
            else:
                continue

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

                # Filtra mensagens que ainda não foram traduzidas
                messages_to_process = [
                    msg for msg in messages_to_translate 
                    if msg not in translated_messages_dict[key]
                ]

                print(messages_to_process)
                if not messages_to_process:
                    print(f"Todas as traduções para '{key}' já existem em {file_name}, pulando...")
                    continue  # Pula para a próxima chave

                for msg in messages_to_process:

                    
                    # Remove e armazena emojis personalizados
                    cleaned_message, emoji_positions = self.remove_custom_emojis(msg)

                    # Tradução
                    await asyncio.sleep(5)  # Evitar limites de taxa

                    #response = text_model.generate_content(                        f"Você é um tradutor e deve retornar apenas a tradução do texto enviado, mantendo qualquer emoji e formatação. Se a mensagem já estiver em {target_lang}, mantenha o texto original. Traduza para {target_lang}: {cleaned_message}")
                    translated_text = cleaned_message# response.text

                    # Restaurar emojis
                    final_translated_text = self.restore_emojis(translated_text, emoji_positions)

                    # Adiciona a resposta traduzida na lista
                    translated_messages_dict[key].append(final_translated_text)
                    print(f"Traduzido {key} para {file_name}: {final_translated_text}")

                # Salvar o arquivo atualizado
                with open(response_file, 'w', encoding='utf-8') as f:
                    json.dump(translated_messages_dict, f, ensure_ascii=False, indent=4)

        print("Traduções de respostas concluídas!")"""


"""
    # PARTE DE TRADUZIR OS RESPONSES DO BOT
    async def translate_responses(self):
        #Lê o arquivo pt-BR.json em response/ e gera as traduções para os outros idiomas.
        pt_br_file = os.path.join(self.response_dir, "pt-BR.json")

        # Se o arquivo pt-BR não existir, não há o que traduzir
        if not os.path.exists(pt_br_file):
            print("Arquivo pt-BR.json não encontrado em response/.")
            return

        # Carrega o conteúdo do pt-BR.json
        with open(pt_br_file, 'r', encoding='utf-8') as f:
            pt_br_messages = json.load(f)

        # Para cada chave e mensagem em pt-BR
        for key, message in pt_br_messages.items():
            # Verificar se a mensagem é válida (string simples)
            if isinstance(message, str):
                # Remove e armazena emojis personalizados com suas posições
                cleaned_message, emoji_positions = self.remove_custom_emojis(message)

                for locale, file_name in self.allowed_locales.items():
                    target_lang = file_name.split('-')[0]  # Ex: 'en' de 'en-US'
                    response_file = os.path.join(self.response_dir, f"{file_name}.json")

                    # Se já existir um arquivo para esse idioma, carregamos as traduções existentes
                    if os.path.exists(response_file):
                        with open(response_file, 'r', encoding='utf-8') as f:
                            translated_messages = json.load(f)
                    else:
                        translated_messages = {}

                    # Se a mensagem ainda não foi traduzida, traduz
                    if key not in translated_messages:
                        # Traduzir a mensagem limpa (sem emojis)
                        #translated_text = GoogleTranslator(source='pt', target=target_lang).translate(cleaned_message)
                        await asyncio.sleep(5)

                        response = text_model.generate_content(f"você é um tradutor e deve retornar apenas a tradução do texto enviado, mantendo qualquer emoji junto com seu ponto de separação caso tenha e qualquer indicação em seu respectivo lugar, caso a mensagem já esteja no respectivo idioma mantem oque foi enviado, faça isso em {target_lang} para a seguinte mensagem: {cleaned_message}")
                        translated_text = response.text

                        # Restaurar os emojis nas posições corretas
                        final_translated_text = self.restore_emojis(translated_text, emoji_positions)
                        
                        # Armazena a tradução
                        translated_messages[key] = final_translated_text
                        print(f"Traduzido {key} para {file_name}: {final_translated_text}")

                    # Salva o arquivo atualizado
                    with open(response_file, 'w', encoding='utf-8') as f:
                        json.dump(translated_messages, f, ensure_ascii=False, indent=4)

        print("Traduções de respostas concluído!")

    def remove_custom_emojis(self, message):
        #Remove emojis personalizados da mensagem e retorna o texto limpo e as posições dos emojis encontrados.
        # Regex para identificar emojis personalizados
        emoji_pattern = r'(<:[a-zA-Z0-9_]+:[0-9]+>)'
        
        # Encontrar todos os emojis personalizados e suas posições
        emojis = re.findall(emoji_pattern, message)
        emoji_positions = []

        # Substituir os emojis por um marcador temporário e manter o emoji original (nome e ID)
        for i, emoji in enumerate(emojis):
            emoji_positions.append((i, emoji, message.find(emoji)))  # Armazenar o emoji e sua posição
            message = message.replace(emoji, f"E{i}", 1)  # Substitui o emoji por um marcador único
        
        return message, emoji_positions

    def restore_emojis(self, translated_text, emoji_positions):
        #Restaurar os emojis personalizados nas posições corretas da tradução.
        # Restaurar os emojis nas posições corretas
        for i, emoji, position in reversed(emoji_positions):  # Coloca os emojis na posição original
            translated_text = translated_text[:position] + emoji + translated_text[position:]

        # Agora removemos os marcadores temporários
        #translated_text = re.sub(r'E\d+', '', translated_text)  
        translated_text = re.sub(r'[Ee]\d+', '', translated_text)# Remove qualquer marcador EMOJI{i}


        return translated_text


"""


#  async def translate(self, string: app_commands.locale_str, locale: discord.Locale, context: app_commands.TranslationContext):
 #   message_str = string.message
 #   if locale == discord.Locale.brazil_portuguese:
  #     return message_str
    
  #  if locale == discord.Locale.american_english:
   #     translated_text = GoogleTranslator(source='pt', target='en').translate(message_str)
  #      if " " in message_str:  # Supondo que você tenha uma variável/flag que indica que é um nome de comando
  #          translated_text = translated_text.strip()  # Para nomes de comando, sem espaços
    #    else:
   #         translated_text = translated_text.strip().replace(" ", "_")
    #    print(translated_text)
   #     return translated_text
        

