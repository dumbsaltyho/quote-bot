from PIL import Image, ImageFont, ImageDraw 
import requests
from io import BytesIO
import discord
from discord import app_commands
from discord.ext import commands
from uwuipy import Uwuipy
from datetime import datetime, timezone
from imagetext_py import *
import random
import d_token

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
        get_avatar = requests.get(user.avatar)
    except requests.exceptions.MissingSchema:
        av_number = random.randrange(0, 6)
        get_avatar = requests.get(f"https://cdn.discordapp.com/embed/avatars/{av_number}.png")
    avatar = Image.open(BytesIO(get_avatar.content))
    return avatar

def generate_image(interaction, user, message: str, _uwu: bool = False, time_since: str = "now"):
    FontDB.SetDefaultEmojiOptions(EmojiOptions(parse_discord_emojis=True))
    FontDB.LoadFromPath("Light", "./Roboto-Light.ttf")
    FontDB.LoadFromPath("BoldItalic", "./Roboto-BoldItalic.ttf")
    font_light = FontDB.Query("Light")
    font_bold_italic = FontDB.Query("BoldItalic")

    message = message[:200]
    if _uwu == True:
        uwu = Uwuipy(None, 0.1, 0, 0, 1, False)
        message = uwu.uwuify(message)

    nickname = f'- {user.display_name}'
    username = f'@{user.name}'

    if isinstance(interaction.channel, discord.DMChannel):
        channel = 'direct messages'
    else:
        channel = f'#{interaction.channel.name}'

    cv = Canvas(1024, 512, (0,0,0,255))
    white = Paint.Color((255, 255, 255, 255))
    grey = Paint.Color((127, 127, 127, 255))
    message_font_size = 31
    m_width = 460
    x_pos = 752
    y_pos = 240
    message_width, message_height = text_size_multiline(text_wrap(text = message, width = m_width, size = message_font_size, font = font_light, draw_emojis = True), size = message_font_size, font = font_light, draw_emojis = True)
    draw_text_wrapped(
        canvas=cv,
        text = message,
        x = x_pos,
        y = y_pos,
        ax = 0.5, ay = 0.5,
        size = message_font_size,
        width = m_width,
        font = font_light,
        fill = white,
        align = TextAlign.Center,
        draw_emojis = True
    )
    draw_text_wrapped(
        canvas=cv,
        text = f"{nickname}",
        x = x_pos,
        y = (y_pos + (message_height / 2) + 32),
        ax = 0.5, ay = 0.5,
        size = 21,
        width = m_width,
        font = font_bold_italic,
        fill = white,
        align = TextAlign.Center,
        draw_emojis = True
    )
    draw_text_wrapped(
        canvas=cv,
        text = f"{username} in {channel}, {time_since}",
        x = x_pos,
        y = (y_pos + (message_height / 2) + 56),
        ax = 0.5, ay = 0.5,
        size = 19,
        width = m_width,
        font = font_light,
        fill = grey,
        align = TextAlign.Center,
        draw_emojis = True
    )

    im: Image.Image = cv.to_image()
    avatar = get_avatar(user)
    avatar_shadow = Image.open(r'avatar-shadow.png')
    im.paste(avatar.resize((512,512)), (0,0))
    im.paste(avatar_shadow, (0,0), avatar_shadow)

    return im

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@tree.command(name="quote", description="generate a quote from a reply, or with options!")
@app_commands.describe(user="the user to generate the quote from")
@app_commands.describe(message="the message to generate the quote from")
@app_commands.describe(uwu="uwuify the message?")
async def quote(interaction: discord.Interaction, user: discord.User, message: str, uwu: bool = False):
    gen_image = generate_image(interaction, user, message, uwu)
    
    with BytesIO() as image_binary:
        gen_image.save(image_binary, 'PNG')
        image_binary.seek(0)
        await interaction.response.send_message(file=discord.File(fp=image_binary,filename="quote.png"))

def app_base(interaction, message, uwu):
    user = message.author
    delta =  datetime.now(timezone.utc) - message.created_at
    if delta.days == 1:
        time_since = f'{delta.days} day ago'
    elif delta.days <= 1:
        time_since = f'less than 1 day ago'
    else:
        time_since = f'{delta.days} days ago'
    
    if (len(message.attachments) >= 1) and (len(message.content) <= 0):
        message = message.attachments[0].filename
    else:
        message = message.content
    
    gen_image = generate_image(interaction, user, message, uwu, time_since)

    return gen_image

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@tree.context_menu(name="Auto quote")
async def quote_app(interaction: discord.Interaction, message: discord.Message):
    gen_image = app_base(interaction, message, False)
    
    with BytesIO() as image_binary:
        gen_image.save(image_binary, 'PNG')
        image_binary.seek(0)
        await interaction.response.send_message(file=discord.File(fp=image_binary, filename="quote.png"))

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@tree.context_menu(name="Auto Quote uwu")
async def uwu_quote_app(interaction: discord.Interaction, message: discord.Message):
    gen_image = app_base(interaction, message, True)
    
    with BytesIO() as image_binary:
        gen_image.save(image_binary, 'PNG')
        image_binary.seek(0)
        await interaction.response.send_message(file=discord.File(fp=image_binary, filename="quote.png"))

client.run(token)