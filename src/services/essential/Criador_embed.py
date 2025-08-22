from typing import Dict, Optional, Union, List, Any, Union, Callable
import discord , json
from discord import Embed, ButtonStyle, utils, Interaction, Colour, HTTPException, SelectOption, TextStyle , ChannelType , CategoryChannel , ForumChannel , StageChannel , Message, InteractionMessage, WebhookMessage
from discord.ui import View, button, Button , TextInput , ChannelSelect, Modal, Select, select , Item
from discord.ext.commands import Context
from contextlib import suppress
from src.services.essential.respostas import Res




class Paginador(View):
    
    message: Optional[Message] = None

    def __init__(
        self,
        pages: List[Any],
        *,
        timeout: Optional[float] = 180.0,
        delete_message_after: bool = False,
        per_page: int = 1,
    ):
        super().__init__(timeout=timeout)
        self.delete_message_after: bool = delete_message_after
        self.current_page: int = 0

        self.ctx: Optional[Context] = None
        self.interaction: Optional[Interaction] = None
        self.per_page: int = per_page
        self.pages: Any = pages
        total_pages, left_over = divmod(len(self.pages), self.per_page)
        if left_over:
            total_pages += 1

        self.max_pages: int = total_pages
        self.next_page.disabled = self.current_page >= self.max_pages - 1

    def stop(self) -> None:
        self.message = None
        self.ctx = None
        self.interaction = None

        super().stop()

    def get_page(self, page_number: int) -> Any:
        if page_number < 0 or page_number >= self.max_pages:
            self.current_page = 0
            return self.pages[self.current_page]

        if self.per_page == 1:
            return self.pages[page_number]
        else:
            base = page_number * self.per_page
            return self.pages[base: base + self.per_page]

    def format_page(self, page: Any) -> Any:
        return page

    async def get_page_kwargs(self, page: Any) -> Dict[str, Any]:
        formatted_page = await utils.maybe_coroutine(self.format_page, page)

        kwargs = {"content": None, "embeds": [], "view": self}
        if isinstance(formatted_page, str):
            kwargs["content"] = formatted_page
        elif isinstance(formatted_page, Embed):
            kwargs["embeds"] = [formatted_page]
        elif isinstance(formatted_page, list):
            if not all(isinstance(embed, Embed) for embed in formatted_page):
                raise TypeError(
                    "Todos os elementos na lista devem ser do tipo Embed")

            kwargs["embeds"] = formatted_page
        elif isinstance(formatted_page, dict):
            return formatted_page

        return kwargs

    async def update_page(self, interaction: Interaction) -> None:
        if self.message is None:
            self.message = interaction.message

        kwargs = await self.get_page_kwargs(self.get_page(self.current_page))
        self.previous_page.disabled = self.current_page <= 0
        self.next_page.disabled = self.current_page >= self.max_pages - 1
        await interaction.response.edit_message(**kwargs)

    @button(label="<", style=ButtonStyle.gray)
    async def previous_page(self, interaction: Interaction, button: Button) -> None:
        self.current_page -= 1
        await self.update_page(interaction)

    @button(label=">", style=ButtonStyle.gray)
    async def next_page(self, interaction: Interaction, button: Button) -> None:
        self.current_page += 1
        await self.update_page(interaction)

    async def start(
        self, obj: Union[Context, Interaction]
    ) -> Optional[Union[Message, InteractionMessage, WebhookMessage]]:
        if isinstance(obj, Context):
            self.ctx = obj
            self.interaction = None
        else:
            self.ctx = None
            self.interaction = obj

        if self.message is not None and self.interaction is not None:
            await self.update_page(self.interaction)
        else:
            self.previous_page.disabled = self.current_page <= 0
            kwargs = await self.get_page_kwargs(self.get_page(self.current_page))
            if self.ctx is not None:
                self.message = await self.ctx.send(**kwargs)
            elif self.interaction is not None:
                if self.interaction.response.is_done():
                    self.message = await self.interaction.followup.send(**kwargs, view=self)
                else:
                    await self.interaction.response.send_message(**kwargs, view=self)
                    self.message = await self.interaction.original_response()
            else:
                raise RuntimeError(
                    "Não é possível iniciar um paginador sem um contexto ou interação.")

        return self.message


class ModalInput(Modal):
    
    def __init__( self, *, title: str, timeout: Optional[float] = None, custom_id: str = "modal_input", ephemeral: bool = False) -> None:
        super().__init__(title=title, timeout=timeout, custom_id=custom_id)
        self.ephemeral = ephemeral

    async def on_submit(self, interaction: Interaction) -> None:
        with suppress(Exception):
            await interaction.response.defer(ephemeral=self.ephemeral)


class PromptDeSelecao(View):
    
    def __init__(
        self, interaction: Interaction, placeholder_str: str, options: List[SelectOption], max_values: int = 1, ephemeral: bool = False
    ) -> None:
        super().__init__()
        self.children[0].placeholder, self.children[0].max_values, self.children[0].options = Res.trad(interaction=interaction, str=placeholder_str), max_values, options 
        self.values = None
        self.ephemeral = ephemeral

    @select()
    async def select_callback(self, interaction: Interaction, select: Select):
        await interaction.response.defer(ephemeral=self.ephemeral)
        if self.ephemeral:
            await interaction.delete_original_response()
        else:
            with suppress(Exception):
                await interaction.message.delete() 
        self.values = select.values
        self.stop()

class PromptDeSelecaoDeCanal(View):

    def __init__(
        self, interaction: Interaction, placeholder_str: str, ephemeral: bool = False, max_values: int = 1
    ) -> None:
        super().__init__()
        self.values = None
        self.ephemeral = ephemeral
        self.children[0].placeholder, self.children[0].max_values = Res.trad(interaction=interaction, str=placeholder_str), max_values

    @select(cls=ChannelSelect, channel_types=[ChannelType.text, ChannelType.private_thread, ChannelType.public_thread])
    async def callback(self, interaction: Interaction, select: ChannelSelect):
        await interaction.response.defer(ephemeral=self.ephemeral)
        if self.ephemeral:
            await interaction.delete_original_response()
        else:
            with suppress(Exception):
                await interaction.message.delete()
        self.values = [interaction.guild.get_channel(i.id) for i in select.values] 
        self.stop()


class CriadorDeEmbed(View):

    def __init__( self, *, interacao: Union[Interaction, Context], embed: Optional[Embed] = None, timeout: Optional[float] = None, **kwargs: Any, ) -> None:
        super().__init__(timeout=timeout)
        self.interacao = interacao

        if not embed:
            embed = self.get_default_embed
        self.embed, self.timeout, self._creator_methods = ( embed, timeout, CreatorMethods(self.interacao, embed), )

        self.options_data = [
            {
                "label": kwargs.get("author_label", Res.trad(interaction=self.interacao, str="author_label")),
                "description": kwargs.get("author_description", Res.trad(interaction=self.interacao, str="author_description")),
                "emoji": kwargs.get("author_emoji", "✨"),
                "value": "author",
            },
            {
                "label": kwargs.get("message_label", Res.trad(interaction=self.interacao, str="message_label")),
                "description": kwargs.get("message_description", Res.trad(interaction=self.interacao, str="message_description")),
                "emoji": kwargs.get("message_emoji", "📝"),
                "value": "message",
            },
            {
                "label": kwargs.get("thumbnail_label", Res.trad(interaction=self.interacao, str="thumbnail_label")),
                "description": kwargs.get("thumbnail_description", Res.trad(interaction=self.interacao, str="thumbnail_description")),
                "emoji": kwargs.get("thumbnail_emoji", "🖼️"),
                "value": "thumbnail",
            },
            {
                "label": kwargs.get("image_label", Res.trad(interaction=self.interacao, str="image_label")),
                "description": kwargs.get("image_description", Res.trad(interaction=self.interacao, str="image_description")),
                "emoji": kwargs.get("image_emoji", "📸"),
                "value": "image",
            },
            {
                "label": kwargs.get("footer_label", Res.trad(interaction=self.interacao, str="footer_label")),
                "description": kwargs.get("footer_description", Res.trad(interaction=self.interacao, str="footer_description")),
                "emoji": kwargs.get("footer_emoji", "📜"),
                "value": "footer",
            },
            {
                "label": kwargs.get("color_label", Res.trad(interaction=self.interacao, str="color_label")),
                "description": kwargs.get("color_description", Res.trad(interaction=self.interacao, str="color_description")),
                "emoji": kwargs.get("color_emoji", "🎨"),
                "value": "color",
            },
            {
                "label": kwargs.get("addfield_label", Res.trad(interaction=self.interacao, str="addfield_label")),
                "description": kwargs.get("addfield_description", Res.trad(interaction=self.interacao, str="addfield_description")),
                "emoji": kwargs.get("addfield_emoji", "➕"),
                "value": "addfield",
            },
            {
                "label": kwargs.get("removefield_label", Res.trad(interaction=self.interacao, str="removefield_label")),
                "description": kwargs.get("removefield_description", Res.trad(interaction=self.interacao, str="removefield_description")),
                "emoji": kwargs.get("removefield_emoji", "➖"),
                "value": "removefield",
            },
        ]

        self.children[0].options = [SelectOption( **option) for option in self.options_data]
        self.children[0].placeholder = Res.trad(interaction=self.interacao, str="edit_section_placeholder")
        self.children[1].label, self.children[1].emoji, self.children[1].style = kwargs.get("send_label", Res.trad(interaction=self.interacao, str="send_label")), kwargs.get("send_emoji", "<a:Brix_Check:1371215835653210182>"), kwargs.get("send_style", ButtonStyle.gray)
        self.children[2].label, self.children[2].emoji, self.children[2].style = kwargs.get("cancel_label", Res.trad(interaction=self.interacao, str="cancel_label")), kwargs.get("cancel_emoji", "<a:Brix_Negative:1371215873637093466>"), kwargs.get("cancel_style", ButtonStyle.gray) 
        
    async def on_error(self, interaction: Interaction, error: Exception, item: Item[Any]) -> None:
        if isinstance(error, HTTPException) and error.code == 50035:
            self.embed.description = f"_ _"
            await self.update_embed(interaction)

    async def update_embed(self, interaction: Interaction):
        return await interaction.message.edit(embed=self.embed, view=self) 

    @property
    def get_default_embed(self) -> Embed:
        client = self.interacao.client

        title = Res.trad(interaction=self.interacao, str='default_embed_title')
        description = Res.trad(interaction=self.interacao, str='default_embed_description')
        author_name = Res.trad(interaction=self.interacao, str='default_embed_author_name')
        footer_text = Res.trad(interaction=self.interacao, str='default_embed_footer_text')

        embed = Embed(title=title, description=description, colour=discord.Color.yellow()) 
        embed.set_author(name=author_name, icon_url=client.user.avatar.url if client.user.avatar else None)
        embed.set_thumbnail( url=client.user.avatar.url if client.user.avatar else None)
        embed.set_footer( text=footer_text, icon_url=client.user.avatar.url if client.user.avatar else None)
        return embed

    @select(placeholder="Editar uma seção")
    async def edit_select_callback( self, interaction: Interaction, select: Select ) -> None:
        self.interacao = interaction
        await self._creator_methods.callbacks[select.values[0]](interaction)
        await self.update_embed(interaction)

    @button()
    async def send_callback(self, interaction: Interaction, button: Button) -> None:
        prompt = PromptDeSelecaoDeCanal(
            interaction=interaction, placeholder_str="send_channel_prompt", ephemeral=True, max_values=1)
        await interaction.response.send_message(view=prompt, ephemeral=True)
        await prompt.wait()
        if prompt.values:
            if not isinstance(prompt.values[0], (StageChannel, ForumChannel, CategoryChannel)):
                await prompt.values[0].send(embed=self.embed) 
                await interaction.message.delete() 

    @button()
    async def cancel_callback(self, interaction: Interaction, button: Button) -> None:
        await interaction.message.delete()
        self.stop()


class CreatorMethods:

    def __init__(self, interaction: Interaction, embed: Embed) -> None:
        self.interaction = interaction
        self.embed = embed
        self.callbacks: Dict[str, Callable] = { 
            "author": self.edit_author, 
            "message": self.edit_message, 
            "thumbnail": self.edit_thumbnail, 
            "image": self.edit_image, 
            "footer": self.edit_footer, 
            "color": self.edit_colour, 
            "addfield": self.add_field, 
            "removefield": self.remove_field, 
        }

    async def edit_author(self, interaction: Interaction) -> None:
        modal = ModalInput(title=Res.trad(interaction=self.interaction, str="edit_author_modal_title"))
        modal.add_item( TextInput( label=Res.trad(interaction=self.interaction, str="author_name_input_label"), max_length=100, default=self.embed.author.name, placeholder=Res.trad(interaction=self.interaction, str="author_name_input_placeholder"), required=False, ) )
        modal.add_item( TextInput( label=Res.trad(interaction=self.interaction, str="author_icon_url_input_label"), default=self.embed.author.icon_url, placeholder=Res.trad(interaction=self.interaction, str="author_icon_url_input_placeholder"), required=False, ) )
        modal.add_item( TextInput( label=Res.trad(interaction=self.interaction, str="author_url_input_label"), default=self.embed.author.url, placeholder=Res.trad(interaction=self.interaction, str="author_url_input_placeholder"), required=False, ) )
        await interaction.response.send_modal(modal)
        await modal.wait()
        try:
            self.embed.set_author(
                name=str(modal.children[0]),
                icon_url=str(modal.children[1]),
                url=str(modal.children[2]),
            )
        except HTTPException:
            self.embed.set_author(
                name=str(modal.children[0])
            )

    async def edit_message(self, interaction: Interaction) -> None:
        modal = ModalInput(title=Res.trad(interaction=self.interaction, str="edit_message_modal_title"))
        modal.add_item(
            TextInput(
                label=Res.trad(interaction=self.interaction, str="title_input_label"),
                max_length=255,
                default=self.embed.title,
                placeholder=Res.trad(interaction=self.interaction, str="title_input_placeholder"),
                required=False,
            )
        )
        modal.add_item(
            TextInput(
                label=Res.trad(interaction=self.interaction, str="description_input_label"),
                default=self.embed.description,
                placeholder=Res.trad(interaction=self.interaction, str="description_input_placeholder"),
                style=TextStyle.paragraph,
                required=False,
                max_length=2000,
            )
        )
        await interaction.response.send_modal(modal)
        await modal.wait()
        self.embed.title, self.embed.description = str(modal.children[0]), str(
            modal.children[1]
        )

    async def edit_thumbnail(self, interaction: Interaction) -> None:
        modal = ModalInput(title=Res.trad(interaction=self.interaction, str="edit_thumbnail_modal_title"))
        modal.add_item(
            TextInput(
                label=Res.trad(interaction=self.interaction, str="thumbnail_url_input_label"),
                default=self.embed.thumbnail.url,
                placeholder=Res.trad(interaction=self.interaction, str="thumbnail_url_input_placeholder"),
                required=False,
            )
        )
        await interaction.response.send_modal(modal)
        await modal.wait()
        self.embed.set_thumbnail(url=str(modal.children[0]))

    async def edit_image(self, interaction: Interaction) -> None:
        modal = ModalInput(title=Res.trad(interaction=self.interaction, str="edit_image_modal_title"))
        modal.add_item(
            TextInput(
                label=Res.trad(interaction=self.interaction, str="image_url_input_label"),
                default=self.embed.image.url,
                placeholder=Res.trad(interaction=self.interaction, str="image_url_input_placeholder"),
                required=False,
            )
        )
        await interaction.response.send_modal(modal)
        await modal.wait()
        self.embed.set_image(url=str(modal.children[0]))

    async def edit_footer(self, interaction: Interaction) -> None:
        modal = ModalInput(title=Res.trad(interaction=self.interaction, str="edit_footer_modal_title"))
        modal.add_item(
            TextInput(
                label=Res.trad(interaction=self.interaction, str="footer_text_input_label"),
                max_length=255,
                required=False,
                default=self.embed.footer.text,
                placeholder=Res.trad(interaction=self.interaction, str="footer_text_input_placeholder"),
            )
        )
        modal.add_item(
            TextInput(
                label=Res.trad(interaction=self.interaction, str="footer_icon_url_input_label"),
                required=False,
                default=self.embed.footer.icon_url,
                placeholder=Res.trad(interaction=self.interaction, str="footer_icon_url_input_placeholder"),
            )
        )
        await interaction.response.send_modal(modal)
        await modal.wait()
        self.embed.set_footer(
            text=str(modal.children[0]), icon_url=str(modal.children[1])
        )

    async def edit_colour(self, interaction: Interaction) -> None:
        modal = ModalInput(title=Res.trad(interaction=self.interaction, str="edit_color_modal_title"))
        modal.add_item(
            TextInput(
                label=Res.trad(interaction=self.interaction, str="color_input_label"),
                placeholder=Res.trad(interaction=self.interaction, str="color_input_placeholder"),
                max_length=20
            )
        )
        await interaction.response.send_modal(modal)
        await modal.wait()
        try:
            colour = Colour.from_str(str(modal.children[0]))
        except:
            await interaction.followup.send(
                Res.trad(interaction=self.interaction, str="invalid_hex_color_error"), ephemeral=True
            )
        else:
            self.embed.color = colour

    async def add_field(self, interaction: Interaction) -> None:
        if len(self.embed.fields) >= 25:
            return await interaction.response.send_message( Res.trad(interaction=self.interaction, str="too_many_fields_error"), ephemeral=True )
        modal = ModalInput(title=Res.trad(interaction=self.interaction, str="add_field_modal_title"))
        modal.add_item( TextInput( label=Res.trad(interaction=self.interaction, str="field_name_input_label"), placeholder=Res.trad(interaction=self.interaction, str="field_name_input_placeholder"), max_length=255, ) )
        modal.add_item( TextInput(label=Res.trad(interaction=self.interaction, str="field_value_input_label"), max_length=2000, style=TextStyle.paragraph) )
        modal.add_item( TextInput( label=Res.trad(interaction=self.interaction, str="inline_input_label"), default="True", max_length=5, placeholder=Res.trad(interaction=self.interaction, str="inline_input_placeholder"), )
        )
        await interaction.response.send_modal(modal)
        await modal.wait()
        try:
            inline = False
            if str(modal.children[2]).lower() == "True" or str(modal.children[2]).lower() == "true":
                inline = True
            elif str(modal.children[2]).lower() == "False" or str(modal.children[2]).lower() == "false":
                inline = False
            else:
                raise Exception("Entrada booleana inválida.")
        except:
            await interaction.followup.send(
                Res.trad(interaction=self.interaction, str="invalid_boolean_error"),
                ephemeral=True,
            )
        else:
            self.embed.add_field(
                name=str(modal.children[0]), value=str(modal.children[1]), inline=inline
            )

    async def remove_field(self, interaction: Interaction) -> None:
        if not self.embed.fields:
            return await interaction.response.send_message(Res.trad(interaction=self.interaction, str="no_fields_to_remove_error"), ephemeral=True)
        field_options = list()
        for index, field in enumerate(self.embed.fields):
            field_options.append(
                SelectOption(
                    label=str(field.name)[0:30],
                    value=str(index),
                    emoji="🗑️"
                )
            )
        select = PromptDeSelecao(
            interaction=interaction,
            placeholder_str="remove_field_placeholder",
            options=field_options,
            max_values=len(field_options),
            ephemeral=True
        )
        await interaction.response.send_message(view=select, ephemeral=True)
        await select.wait()
        
        if vals := select.values:
            for value in sorted([int(v) for v in vals], reverse=True):
                self.embed.remove_field(value)