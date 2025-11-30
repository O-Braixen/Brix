import discord,os,json,asyncio,re,time
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
# INICIALIZA GEMINI (SINCRONO) → SERÁ USADO EM THREADPOOL
try:
    if not GOOGLE_AI_KEY:
        raise ValueError("API KEY ausente.")
    genaitradutor = genai.Client(api_key=GOOGLE_AI_KEY)
except Exception as e:
    print(f"❌ Erro ao inicializar GenAI: {e}")
    print("❌ Tradução por IA desativada.")





# ======================================================================
# FUNÇÃO SEGURA PARA CHAMAR GEMINI SEM TRAVAR O EVENT LOOP
async def gemini_translate(text: str, target_lang: str):
    loop = asyncio.get_running_loop()

    def _call():
        response = genaitradutor.models.generate_content(
            model="gemini-2.0-flash",
            contents=(
                f"Você é um tradutor e deve retornar apenas a tradução. "
                f"Mantenha emojis e formatação. "
                f"Se já estiver em {target_lang}, devolva igual. "
                f"Traduza para {target_lang}: {text}"
            )
        )
        return response.text.strip()

    return await loop.run_in_executor(None, _call)







# ======================================================================
#sistema para traduzir para qualquer idioma que eu queira

class BrixTradutor(app_commands.Translator):
    def __init__(self, dir_name='src/core/traducoes', response_dir='src/core/responses'):
        print("🌐  -  Iniciando Traduções Automáticas!")

        self.dir_name = dir_name
        self.response_dir = response_dir

        os.makedirs(self.dir_name, exist_ok=True)
        os.makedirs(self.response_dir, exist_ok=True)

        self.allowed_locales = {
            discord.Locale.american_english: 'en-US',
            discord.Locale.polish: 'pl',
            #discord.Locale.spain_spanish: 'es-ES',
        }

        self.translations = self.load_translations(self.dir_name)
        self.response_translations = self.load_translations(self.response_dir)










# ==================================================================
    def load_translations(self, directory):
        translations = {}
        for locale, file_name in self.allowed_locales.items():
            file_path = os.path.join(directory, f"{file_name}.json")
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    translations[locale] = json.load(f)
            else:
                translations[locale] = {}
        return translations















    # ==================================================================
    async def translate(self, string: app_commands.locale_str, locale: discord.Locale, context):
        message_str = string.message

        # Garante pt-BR.json
        file_path_ptbr = os.path.join(self.dir_name, "pt-BR.json")
        if "pt-BR" not in self.translations:
            self.translations["pt-BR"] = {}

        if message_str not in self.translations["pt-BR"]:
            self.translations["pt-BR"][message_str] = message_str
            with open(file_path_ptbr, 'w', encoding='utf-8') as f:
                json.dump(self.translations["pt-BR"], f, ensure_ascii=False, indent=4)

        # Se destino = pt → retorna original
        if locale == discord.Locale.brazil_portuguese:
            return message_str

        if locale not in self.allowed_locales:
            return message_str

        file_name = self.allowed_locales[locale]
        file_path = os.path.join(self.dir_name, f"{file_name}.json")

        # Se já existe tradução → retorna
        if message_str in self.translations[locale]:
            return self.translations[locale][message_str]

        target_lang = file_name.split('-')[0]

        # Pequena espera segura
        await asyncio.sleep(1)

        # Traduz usando GoogleTranslator síncrono em threadpool
        loop = asyncio.get_running_loop()
        translated_text = await loop.run_in_executor(
            None,
            lambda: GoogleTranslator(source='pt', target=target_lang).translate(message_str)
        )

        # Ajuste
        if " " in message_str:
            translated_text = translated_text.strip().lower()
        else:
            translated_text = translated_text.strip().replace(" ", "").lower()

        # Salva em memória + arquivo
        self.translations[locale][message_str] = translated_text
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.translations[locale], f, ensure_ascii=False, indent=4)

        print(f"✅ Traduzido comando para {file_name}: {translated_text}")
        return translated_text













# ==================================================================
    def remove_custom_emojis(self, message):
        emoji_pattern = r'(<a?:[a-zA-Z0-9_]+:[0-9]+>)'
        emojis = re.findall(emoji_pattern, message)
        emoji_positions = []

        for i, emoji in enumerate(emojis):
            emoji_positions.append((i, emoji))
            message = message.replace(emoji, f"%{i}", 1)

        return message, emoji_positions

    # ==================================================================
    def restore_emojis(self, translated_text, emoji_positions):
        for i, emoji in emoji_positions:
            translated_text = translated_text.replace(f"%{i}", emoji)
        return translated_text

    # ==================================================================
    # TRADUÇÃO DAS RESPOSTAS EXTENSAS (opcional)
    async def translate_responses(self):
        pt_br_file = os.path.join(self.response_dir, "pt-BR.json")

        if not os.path.exists(pt_br_file):
            print("Arquivo pt-BR.json não encontrado.")
            return

        with open(pt_br_file, 'r', encoding='utf-8') as f:
            pt_br_messages = json.load(f)

        async def process_message(msg, target_lang):
            if isinstance(msg, str):
                cleaned, emojis = self.remove_custom_emojis(msg)
                translated = await gemini_translate(cleaned, target_lang)
                return self.restore_emojis(translated, emojis)

            elif isinstance(msg, list):
                return [await process_message(m, target_lang) for m in msg]

            elif isinstance(msg, dict):
                new_dict = {}
                for k, v in msg.items():
                    new_dict[k] = await process_message(v, target_lang)
                return new_dict

            return msg

        for key, msg in pt_br_messages.items():
            for locale, file_name in self.allowed_locales.items():
                target_lang = file_name.split('-')[0]
                output_path = os.path.join(self.response_dir, f"{file_name}.json")

                if os.path.exists(output_path):
                    with open(output_path, 'r', encoding='utf-8') as f:
                        existing = json.load(f)
                else:
                    existing = {}

                if key in existing and existing[key]:
                    continue

                translated_msg = await process_message(msg, target_lang)
                await asyncio.sleep(1)

                existing[key] = translated_msg

                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(existing, f, ensure_ascii=False, indent=4)

                print(f"🌐 Traduzido {key} → {file_name}")

        print("🌐  -  Traduções concluídas!")