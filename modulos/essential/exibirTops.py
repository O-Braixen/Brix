import discord,os,io,asyncio
from discord.ext import commands
from discord import app_commands
from functools import partial
#from modulos.connection.database import BancoServidores
from modulos.essential.respostas import Res
from PIL import Image, ImageFont, ImageDraw, ImageOps #IMPORTAÇÂO Py PIL IMAGEM





async def exibirtops(self, interaction, bloco_classificacao,pagina,originaluser,background):
    await interaction.original_response()
    try:
            # Obtendo IDs dos membros no bloco
        bloco_atual = bloco_classificacao[pagina-1]
        ids_membros = [membro[1] for membro in bloco_atual]

            # Buscando os usuários e carregando os avatares
        membros = await asyncio.gather(*[self.client.fetch_user(membro_id) for membro_id in ids_membros])

            # Processando avatares de forma assíncrona
        avatares = await asyncio.gather(*[process_avatar(self,membro) for membro in membros])

            # Configurações de imagem
        fundo = Image.new("RGB", (600, 400), "yellow")
        fundo.paste(background, (0, 0))

        avatar_positions = [(382, 86), (380, 148), (382, 212), (381, 277), (379, 337)]
        for avatar, pos in zip(avatares, avatar_positions):
            fundo.paste(avatar, pos, self.tops_recorte_mascara)

        fundodraw = ImageDraw.Draw(fundo)

        text_positions = [(434, 91), (434, 153), (434, 218), (434, 281), (434, 341)]
        saldo_positions = [(450, 114), (450, 176), (450, 240), (450, 304), (450, 364)]

        for i, ((classificacao, membro_id, saldo), membro, pos_text, pos_saldo) in enumerate(zip(bloco_atual, membros, text_positions, saldo_positions)):
            try:
                fundodraw.text(pos_text, f"{classificacao} - {membro.name[:12]}", font=self.tops_font)
            except:
                fundodraw.text(pos_text, "semnome", font=self.tops_font)
            fundodraw.text(pos_saldo, "{:,.0f}".format(saldo), font=self.tops_font_numero)

        fundodraw.text((10,10), f"{Res.trad(interaction=interaction,str='botão_pagina')} {pagina}/{len(bloco_classificacao)}", font=self.tops_font_numero)

        buffer = io.BytesIO()
        fundo.save(buffer, format="PNG")
        buffer.seek(0)
        view = discord.ui.View()

            # Botoões
        botaovoltarfast = discord.ui.Button(emoji="<:setaduplaesquerda:1318716104474099722>", style=discord.ButtonStyle.gray, disabled=(pagina == 1))
        view.add_item(item=botaovoltarfast)
        botaovoltarfast.callback = partial(trocarpaginatops, self, blocos_classificacao=bloco_classificacao, pagina=1,originaluser=originaluser , background = background)

        botaovoltar = discord.ui.Button(emoji="<:setaesquerda:1318698827422765189>", style=discord.ButtonStyle.gray, disabled=(pagina == 1))
        view.add_item(item=botaovoltar)
        botaovoltar.callback = partial(trocarpaginatops, self, blocos_classificacao=bloco_classificacao, pagina=pagina-1,originaluser=originaluser , background = background)

        #botaopagina = discord.ui.Button(label=f"{pagina}/{len(bloco_classificacao)}", style=discord.ButtonStyle.gray, disabled=True)
        #view.add_item(item=botaopagina)

        botaoavancar = discord.ui.Button(emoji="<:setadireita:1318698789225369660>", style=discord.ButtonStyle.gray, disabled=(pagina == len(bloco_classificacao)))
        view.add_item(item=botaoavancar)
        botaoavancar.callback = partial(trocarpaginatops, self, blocos_classificacao=bloco_classificacao, pagina=pagina+1,originaluser=originaluser , background = background)

        botaoavancarfast = discord.ui.Button(emoji="<:setadupladireita:1318715892242190419>", style=discord.ButtonStyle.gray, disabled=(pagina == len(bloco_classificacao)))
        view.add_item(item=botaoavancarfast)
        botaoavancarfast.callback = partial(trocarpaginatops, self, blocos_classificacao=bloco_classificacao, pagina=len(bloco_classificacao),originaluser=originaluser , background = background)

            # Botão para buscar a página do usuário original
        botaobuscar = discord.ui.Button(label=Res.trad(interaction=interaction,str="botão_buscarpaginausuario"),emoji="<:lupa:1318713789872603187>", style=discord.ButtonStyle.primary)
        view.add_item(item=botaobuscar)
        botaobuscar.callback = partial(buscar_pagina_usuario, self, blocos_classificacao=bloco_classificacao, originaluser=originaluser , background = background)

        await interaction.edit_original_response(attachments={discord.File(fp=buffer, filename="Rank.png")},view=view)

    except Exception as e:
        await Res.erro_brix_embed(interaction, str="message_erro_brixsystem", e=e,comando="exibirtops")

async def process_avatar(self, membro):
        try:
            avatar = await membro.avatar.read()
            avatar = Image.open(io.BytesIO(avatar)).resize((44, 44))
        except:
            avatar = self.default_avatar
        return avatar

@commands.Cog.listener()
async def trocarpaginatops(self,interaction,blocos_classificacao,pagina,originaluser,background):

  if interaction.user != originaluser:
    await interaction.response.send_message(Res.trad(interaction=interaction,str="message_erro_interacaoalheia"),delete_after=10,ephemeral=True)
  else:
    view = discord.ui.View.from_message(interaction.message)
    for item in view.children:
            item.disabled = True

        # Atualiza a resposta original para refletir os botões desativados
    await interaction.response.edit_message(view=view)
    #await interaction.response.defer()
    await exibirtops(self,interaction,blocos_classificacao,pagina,originaluser,background)

@commands.Cog.listener()
async def buscar_pagina_usuario(self, interaction, blocos_classificacao, originaluser,background):
    # Verifica se o botão foi clicado pelo usuário correto
    if interaction.user != originaluser:
        await interaction.response.send_message(Res.trad(interaction=interaction, str="message_erro_interacaoalheia"), delete_after=20, ephemeral=True)
        return

    # Busca a página onde o usuário está
    for idx, bloco in enumerate(blocos_classificacao):
        for classificacao, membro_id, saldo in bloco:
            if membro_id == originaluser.id:
                view = discord.ui.View.from_message(interaction.message)
                for item in view.children:
                        item.disabled = True

                    # Atualiza a resposta original para refletir os botões desativados
                await interaction.response.edit_message(view=view)
                # Usuário encontrado, exibir página
                await exibirtops(self, interaction, blocos_classificacao, idx + 1, originaluser,background)
                return

    # Caso o usuário não seja encontrado
    await interaction.response.send_message(Res.trad(interaction=interaction, str="message_financeiro_ausentelista"), ephemeral=True)


