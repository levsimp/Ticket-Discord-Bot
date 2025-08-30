import discord
from discord.ext import commands
from discord import ui, ButtonStyle
import asyncio
import json
import os

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

DATA_FILE = "ticket_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

class TicketCreateView(ui.View):
    def __init__(self, button_name, category_name):
        super().__init__(timeout=None)
        self.category_name = category_name
        self.add_item(TicketButton(button_name, category_name))

class TicketButton(ui.Button):
    def __init__(self, button_name, category_name):
        super().__init__(label=button_name, style=ButtonStyle.primary, custom_id=f"ticket_{category_name}")
        self.category_name = category_name
    
    async def callback(self, interaction: discord.Interaction):
        category = discord.utils.get(interaction.guild.categories, name=self.category_name)
        if not category:
            category = await interaction.guild.create_category(self.category_name)
        
        for channel in category.channels:
            if isinstance(channel, discord.TextChannel) and channel.topic == str(interaction.user.id):
                await interaction.response.send_message(
                    "You already have an open ticket!", 
                    ephemeral=True
                )
                return
        
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        ticket_channel = await category.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            topic=str(interaction.user.id),
            overwrites=overwrites
        )
        
        await interaction.response.send_message(
            f"Your ticket has been created: {ticket_channel.mention}", 
            ephemeral=True
        )
        
        embed = discord.Embed(
            title="Support Ticket",
            description="Thank you for creating a ticket. Support staff will be with you shortly.\n\nUse `/close` to close this ticket.",
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Created by {interaction.user}")
        await ticket_channel.send(embed=embed, view=TicketCloseView())

class TicketCloseView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @ui.button(label="Close Ticket", style=ButtonStyle.danger, custom_id="close_ticket")
    async def close_ticket(self, button: ui.Button, interaction: discord.Interaction):
        if str(interaction.user.id) != interaction.channel.topic and not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message("Only the ticket creator or staff can close this ticket.", ephemeral=True)
            return
        
        confirm_embed = discord.Embed(
            title="Confirm Closure",
            description="Are you sure you want to close this ticket?",
            color=discord.Color.orange()
        )
        await interaction.response.send_message(embed=confirm_embed, view=ConfirmCloseView(), ephemeral=True)

class ConfirmCloseView(ui.View):
    def __init__(self):
        super().__init__(timeout=30)
    
    @ui.button(label="Confirm", style=ButtonStyle.danger)
    async def confirm(self, button: ui.Button, interaction: discord.Interaction):
        creator_id = interaction.channel.topic
        creator = interaction.guild.get_member(int(creator_id))
        
        transcript = []
        async for message in interaction.channel.history(limit=200, oldest_first=True):
            transcript.append(f"{message.author.name}: {message.content}")
        
        transcript_text = "\n".join(transcript)
        
        if creator:
            try:
                if len(transcript_text) > 1900:
                    chunks = [transcript_text[i:i+1900] for i in range(0, len(transcript_text), 1900)]
                    for chunk in chunks:
                        await creator.send(f"**Ticket Transcript**\n```{chunk}```")
                else:
                    await creator.send(f"**Ticket Transcript**\n```{transcript_text}```")
            except discord.Forbidden:
                pass
        
        await interaction.channel.delete()
    
    @ui.button(label="Cancel", style=ButtonStyle.secondary)
    async def cancel(self, button: ui.Button, interaction: discord.Interaction):
        await interaction.message.delete()
        await interaction.response.send_message("Ticket closure cancelled.", ephemeral=True)
    
    async def on_timeout(self):
        pass
@bot.slash_command(name="setup", description="Set up the ticket system")
@commands.has_permissions(administrator=True)
async def setup(
    ctx, 
    title: discord.Option(str, description="Title of the embed"),
    text: discord.Option(str, description="Text of the embed"),
    button_name: discord.Option(str, description="Name of the ticket button"),
    category: discord.Option(str, description="Name of the ticket category")
):
    embed = discord.Embed(title=title, description=text, color=discord.Color.blue())
    
    view = TicketCreateView(button_name, category)
    await ctx.send(embed=embed, view=view)
    
    data = load_data()
    guild_id = str(ctx.guild.id)
    
    if guild_id not in data:
        data[guild_id] = {}
    
    data[guild_id]["ticket_message"] = {
        "title": title,
        "text": text,
        "button_name": button_name,
        "category": category
    }
    
    save_data(data)
    
    await ctx.respond("Ticket system has been set up!", ephemeral=True)

@bot.slash_command(name="close", description="Close the current ticket")
async def close_ticket(ctx):
    if not isinstance(ctx.channel, discord.TextChannel) or not ctx.channel.topic:
        await ctx.respond("This command can only be used in ticket channels.", ephemeral=True)
        return
    
    if str(ctx.author.id) != ctx.channel.topic and not ctx.author.guild_permissions.manage_messages:
        await ctx.respond("Only the ticket creator or staff can close this ticket.", ephemeral=True)
        return
    
    creator_id = ctx.channel.topic
    creator = ctx.guild.get_member(int(creator_id))
    
    transcript = []
    async for message in ctx.channel.history(limit=200, oldest_first=True):
        transcript.append(f"{message.author.name}: {message.content}")
    
    transcript_text = "\n".join(transcript)
    
    if creator:
        try:
            if len(transcript_text) > 1900:
                chunks = [transcript_text[i:i+1900] for i in range(0, len(transcript_text), 1900)]
                for chunk in chunks:
                    await creator.send(f"**Ticket Transcript**\n```{chunk}```")
            else:
                await creator.send(f"**Ticket Transcript**\n```{transcript_text}```")
        except discord.Forbidden:
            pass
    
    await ctx.respond("Closing ticket...", ephemeral=True)
    await asyncio.sleep(1)
    await ctx.channel.delete()

@setup.error
async def setup_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.respond("You need administrator permissions to use this command.", ephemeral=True)

@bot.event
async def on_ready():
    print(f'{bot.user} has logged in!')
    
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="Tickets | Made by Lev (@_yw2)"
        )
    )
    data = load_data()
    for guild_id, guild_data in data.items():
        if "ticket_message" in guild_data:
            msg_data = guild_data["ticket_message"]
            bot.add_view(TicketCreateView(msg_data["button_name"], msg_data["category"]))

if __name__ == "__main__":
    bot.run("YOUR_BOT_TOKEN")
