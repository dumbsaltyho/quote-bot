from PIL import Image, ImageFont, ImageDraw 
import textwrap
import requests
from io import BytesIO
import discord
from discord import app_commands
from discord.ext import commands
from uwuipy import uwuipy

intents = discord.Intents.default()
intents.message_content = True
intents.dm_messages = True
client = discord.Client(intents=intents, activity=discord.CustomActivity(name="neinheart my beloved"))
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    await tree.sync()
    print('ready !')

def get_avatar(user):
    try:
        get_avatar = requests.get(user.avatar.url)
    except AttributeError:
        get_avatar = requests.get("https://cdn.discordapp.com/embed/avatars/0.png")
    avatar = Image.open(BytesIO(get_avatar.content))

    return avatar

def generate_image(interaction, user, message: str, _uwu: bool = False):
    font_message = ImageFont.truetype(r'Urbanist-Light.ttf', 24)
    font_nickname = ImageFont.truetype(r'Urbanist-BoldItalic.ttf', 18)
    font_username = ImageFont.truetype(r'Urbanist-ExtraLight.ttf', 16)
    font_bottom_text = ImageFont.truetype(r'Urbanist-LightItalic.ttf', 14)
    
    base_image = Image.new('RGB', (1024, 512), (0,0,0,0))
    draw = ImageDraw.Draw(base_image)
    
    avatar = get_avatar(user)
    avatar_shadow = Image.open(r'avatar-shadow.png')

    if _uwu == True:
        uwu = uwuipy(None, 0.1, 0, 0, 1, False)
        message = uwu.uwuify(message)

    message = textwrap.wrap(message[:200], width=37)
    message = '\n'.join(message)

    nickname = f'- {user.display_name}'
    username = f'@{user.name}'

    if isinstance(interaction.channel, discord.DMChannel):
        channel = '#wouldn\'t you like to know, weather boy?'
    else:
        channel = f'#{interaction.channel.name}'

    text_box = draw.multiline_textbbox((0,0), message, font_message)
    qh = (256 + ((text_box[3]) / 2) + 24)

    draw.multiline_text(((768), 256), message, fill="white", font=font_message, align="center", anchor='mm') 
    draw.text(((768),(qh)), nickname, fill="white", font=font_nickname, align="center", anchor='mm')
    draw.text(((768),(qh+24)), f'{username} in {channel}', fill="grey", font=font_username, align="center", anchor='mm')
    base_image.paste(avatar.resize((512,512)), (0,0))
    base_image.paste(avatar_shadow, (0,0), avatar_shadow)

    return base_image

@tree.command(name="quote", description="generate a quote from a reply, or with options!")
@app_commands.describe(user="the user to generate the quote from")
@app_commands.describe(message="the message to generate the quote from")
@app_commands.describe(uwu="uwuify the message?")
async def quote(interaction: discord.Interaction, user: discord.User, message: str = "", uwu: bool = False):
    gen_image = generate_image(interaction, user, message, uwu)
    
    with BytesIO() as image_binary:
        gen_image.save(image_binary, 'PNG')
        image_binary.seek(0)
        await interaction.response.send_message(file=discord.File(fp=image_binary,filename="quote.png"))
    return

@tree.context_menu(name="Quote")
async def quote_app(interaction: discord.Interaction, message: discord.Message):
    user = message.author
    
    if (len(message.attachments) >= 1) and (len(message.content) <= 0):
        message = message.attachments[0].filename
    else:
        message = message.content
    
    gen_image = generate_image(interaction, user, message)
    
    with BytesIO() as image_binary:
        gen_image.save(image_binary, 'PNG')
        image_binary.seek(0)
        await interaction.response.send_message(file=discord.File(fp=image_binary, filename="quote.png"))

@tree.command()
@commands.is_owner()
async def goodbye(interaction: discord.Interaction):
    await interaction.response.send_message("shutting down, see u soon !")
    await client.close()

client.run("token")