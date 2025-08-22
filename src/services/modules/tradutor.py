import discord,os,asyncio,time,requests,aiohttp
from discord.ext import commands
from discord import app_commands
from deep_translator import GoogleTranslator
from src.services.essential.respostas import Res


language_dict = {
            "Portuguese": "pt", "English": "en", "Spanish": "es", "French": "fr", "German": "de", "Italian": "it",
            "Russian": "ru", "Japanese": "ja", "Korean": "ko", "Arabic": "ar", "Hindi": "hi",
            "Bengali": "bn", "Urdu": "ur", "Turkish": "tr", "Dutch": "nl", "Swedish": "sv", "Polish": "pl",
            "Romanian": "ro", "Hungarian": "hu", "Greek": "el", "Czech": "cs", "Danish": "da", "Finnish": "fi",
            "Norwegian": "no"
    }


##FUNÇÂO DE TRADUÇÂO DE TEXTOS
async def comandotradutor(self):
  if await Res.print_brix(comando="traduzirmensagem",interaction=self.interaction,condicao=self.message.content):
    return
  try:
    await self.interaction.original_response()
    translated_text = GoogleTranslator(source='auto', target=self.selected_language).translate(self.message.content)
    if len(translated_text) < 1900:
      resposta = discord.Embed(colour=discord.Color.yellow(), description=Res.trad(interaction=self.interaction,str="message_traducao").format(translated_text))
      await self.interaction.edit_original_response(embed=resposta,view=LanguageSelectView(self.message,self.interaction))
    else:
      while len(translated_text) > 1900:
        await self.interaction.followup.send(content=translated_text[:1900],ephemeral = True)
        translated_text = translated_text[1900:]
      await self.interaction.followup.send(content=translated_text,ephemeral = True)
  except Exception as e:
    await Res.erro_brix_embed(self.interaction,str="message_erro_brixsystem",e=e,comando="traduzirmensagem")







class LanguageSelect(discord.ui.Select):
    def __init__(self, message, interaction):
        self.message = message
        self.interaction = interaction
        options = [discord.SelectOption(label=lang, value=code) for lang, code in language_dict.items()]
        super().__init__(placeholder=Res.trad(str="message_tradutor_dropdown", interaction=self.interaction), min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
      self.selected_language = self.values[0]
      await interaction.response.defer(ephemeral=True)
      await comandotradutor(self)
       




class LanguageSelectView(discord.ui.View):
    def __init__(self, message, interaction):
        super().__init__()
        self.add_item(LanguageSelect(message, interaction))






class tradutor(commands.Cog):
  def __init__(self, client: commands.Bot):
    self.client = client

    self.menu_traduzir = app_commands.ContextMenu(name="Traduzir mensagem",callback=self.traduzirmenu,type=discord.AppCommandType.message,allowed_installs=app_commands.AppInstallationType(guild=True,user=True),allowed_contexts=app_commands.AppCommandContext(guild=True, dm_channel=True, private_channel=True))
    self.client.tree.add_command(self.menu_traduzir)
    





    #Remove os menu se necessario
  async def cog_unload(self) -> None:
    self.client.tree.remove_command(self.menu_traduzir, type=self.menu_traduzir.type)





  @commands.Cog.listener()
  async def on_ready(self):
    print("🌟  -  Modúlo Tradutor carregado.")

  


#COMANDO TRADUZIR 
  @app_commands.command(name="traduzir",description='🌐⠂Traduza alguma coisa.')
  @app_commands.allowed_installs(guilds=True, users=True)
  @app_commands.allowed_contexts(guilds=True,dms=True,private_channels=True)
  @app_commands.describe(texto="Insira o texto que deseja traduzir...",idioma="Selecione para qual idioma devo traduzir...")
  async def traduzirmensagem(self,interaction: discord.Interaction,texto:str,idioma:str):
    if await Res.print_brix(comando="traduzirmensagem",interaction=interaction,condicao=texto):
       return
    await interaction.response.defer()
    try:
        print(f"Comando /tradutor - User {interaction.user.name} , Conteúdo {texto}")
        ans =  GoogleTranslator(source='auto', target=idioma).translate(texto)
        if len(ans) < 1900:
          await interaction.followup.send(ans, suppress_embeds=True)
        else:
          while len(ans) > 1900:
            ans_text = ans[:1900]
            await interaction.followup.send(ans_text, suppress_embeds=True)
            ans = ans[1900:]
          await interaction.followup.send(ans, suppress_embeds=True)
    except Exception as e:
        await Res.erro_brix_embed(interaction,str="message_erro_brixsystem",e=e,comando="traduzirmensagem")

  @traduzirmensagem.autocomplete("idioma")
  async def language_autocomplete(self, interaction: discord.Interaction, current: str):
    
    choices = [
            app_commands.Choice(name=name, value=code) 
            for name, code in language_dict.items() 
            if current.lower() in name.lower() or current.lower() in code.lower()
    ]
    return choices





#COMANDO DE TRADUZIR VIA CONTEXT MENU MENSAGEM
  async def traduzirmenu(self,interaction: discord.Interaction, message: discord.Message):
    if message.content:
      self.interaction = interaction
      self.message = message
      self.selected_language = interaction.locale.value[:2]
      await interaction.response.defer(ephemeral=True)
      await comandotradutor(self)
    else:
      await interaction.response.send_message(Res.trad(str="message_erro_tradutor", interaction=interaction),ephemeral=True,delete_after=15)
       




async def setup(client:commands.Bot) -> None:
  await client.add_cog(tradutor(client))