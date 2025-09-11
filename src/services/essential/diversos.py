import discord,random,string
from discord.ext import commands
from discord import app_commands
from functools import partial
from src.services.essential.respostas import Res



# ======================================================================
#Calculador de saldo em casas
def calcular_saldo(cash):
    if abs(cash) >= 1_000_000_000_000:
        return "{:,.1f}T".format(int(cash / 1_000_000_000_000 * 10) / 10)
    elif abs(cash) >= 1_000_000_000:
        return "{:,.1f}B".format(int(cash / 1_000_000_000 * 10) / 10)
    elif abs(cash) >= 1_000_000:
        return "{:,.1f}M".format(int(cash / 1_000_000 * 10) / 10)
    else:
        return "{:,.0f}".format(cash)








# ======================================================================
#Calculador de XP do usuario
def calcular_nivel(xp):
    # Defina a relação entre XP e nível
    xp_por_nivel = 500  # Por exemplo, 300 XP para cada nível
    # Calcula o nível baseado no XP
    nivel = xp // xp_por_nivel
    
    return nivel









# ======================================================================
#Gerador de ID de 6 digitos
def gerar_id_unica(tamanho=6):
    caracteres = string.ascii_letters + string.digits  # Letras maiúsculas, minúsculas e números
    return ''.join(random.choice(caracteres) for _ in range(tamanho))










# ======================================================================
#SISTEMA DE PAGINADOR GLOBAL
async def Paginador_Global(self, interaction, blocos, pagina, originaluser, descrição,  thumbnail_url : str = None):
    await interaction.original_response()
    try:
        res = discord.Embed(
            colour=discord.Color.yellow(),
            description=descrição + "\n\n".join(blocos[pagina])
        )
        res.set_thumbnail(url=thumbnail_url)

        view = discord.ui.View()

        botao_primeira = discord.ui.Button(emoji="<:setaduplaesquerda:1318716104474099722>", style=discord.ButtonStyle.gray, disabled=(pagina == 0))
        botao_primeira.callback = partial(trocar_pagina, self, blocos=blocos, pagina=0, originaluser=originaluser, descrição=descrição, thumb=thumbnail_url)
        view.add_item(botao_primeira)

        botao_voltar = discord.ui.Button(emoji="<:setaesquerda:1318698827422765189>", style=discord.ButtonStyle.gray, disabled=(pagina == 0))
        botao_voltar.callback = partial(trocar_pagina, self, blocos=blocos, pagina=pagina - 1, originaluser=originaluser, descrição=descrição,  thumb=thumbnail_url)
        view.add_item(botao_voltar)

        botão_page = discord.ui.Button(label=f"{pagina+1}/{len(blocos)}", style=discord.ButtonStyle.gray, disabled=True)
        view.add_item(botão_page)

        botao_avancar = discord.ui.Button(emoji="<:setadireita:1318698789225369660>", style=discord.ButtonStyle.gray, disabled=(pagina+1 == len(blocos)))
        botao_avancar.callback = partial(trocar_pagina, self, blocos=blocos, pagina=pagina + 1, originaluser=originaluser, descrição=descrição,  thumb=thumbnail_url)
        view.add_item(botao_avancar)

        botao_ultima = discord.ui.Button(emoji="<:setadupladireita:1318715892242190419>", style=discord.ButtonStyle.gray, disabled=(pagina+1 == len(blocos)))
        botao_ultima.callback = partial(trocar_pagina, self, blocos=blocos, pagina=len(blocos)-1, originaluser=originaluser, descrição=descrição,  thumb=thumbnail_url)
        view.add_item(botao_ultima)

        await interaction.edit_original_response(content = "",embed=res, view=view)

    except Exception as e:
        await Res.erro_brix_embed(interaction, str="message_erro_brixsystem", e=e, comando="Paginador")

async def trocar_pagina(self, interaction, blocos, pagina, originaluser, descrição, thumb):
    if interaction.user != originaluser:
        await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_interacaoalheia"),delete_after=10,ephemeral=True)
        return
    view = discord.ui.View.from_message(interaction.message)
    for button in view.children:
        button.disabled = True
        # Atualiza a resposta original para refletir os botões desativados
    await interaction.response.edit_message(view=view)
    await Paginador_Global(self,interaction, blocos, pagina, originaluser, descrição, thumb)














# ======================================================================
#SISTEMA DE FORMATAÇÃO DE TEMPO CONVERTENDO SEGUNDOS EM TEXTO
def formatar_tempo(segundos: int , interaction) -> str:
    if isinstance(segundos, str) and segundos == "perm":
        return Res.trad(interaction=interaction,str='permanente')
    
    # Se vier como string de número, converte
    if isinstance(segundos, str) and segundos.isdigit():
        segundos = int(segundos)
    
    if segundos < 3600:  # menos de 1h → minutos
        minutos = segundos // 60
        return f"{minutos} {Res.trad(interaction=interaction,str='minutos')}"
    elif segundos < 86400:  # menos de 1 dia → horas
        horas = segundos // 3600
        return f"{horas} {Res.trad(interaction=interaction,str='horas')}"
    else:  # 1 dia ou mais → dias
        dias = segundos // 86400
        return f"{dias} {Res.trad(interaction=interaction,str='dias')}"
