from PIL import Image, ImageFont, ImageDraw 
from imagetext_py import *
import requests
from io import BytesIO
import discord
from discord import app_commands
from discord.ext import commands
from uwuipy import uwuipy
from datetime import datetime, timezone

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

def generate_image(interaction, user, message: str, _uwu: bool = False, time_since: str = "now"):
    FontDB.SetDefaultEmojiOptions(EmojiOptions(parse_discord_emojis=True))
    FontDB.LoadFromPath("UrbanistLight", "/home/stel/stinkymel-quote-bot/Urbanist-Light.ttf")
    FontDB.LoadFromPath("UrbanistBoldItalic", "/home/stel/stinkymel-quote-bot/Urbanist-BoldItalic.ttf")
    FontDB.LoadFromPath("UrbanistExtraLight", "/home/stel/stinkymel-quote-bot/Urbanist-ExtraLight.ttf")
    font_message = FontDB.Query("UrbanistLight")
    font_nickname = FontDB.Query("UrbanistBoldItalic")
    font_username = FontDB.Query("UrbanistExtraLight")

    message = message[:200]
    if _uwu == True:
        uwu = uwuipy(None, 0.1, 0, 0, 1, False)
        message = uwu.uwuify(message)

    nickname = f'- {user.display_name}'
    username = f'@{user.name}'

    if isinstance(interaction.channel, discord.DMChannel):
        channel = '#wouldn\'t you like to know, weather boy?'
    else:
        channel = f'#{interaction.channel.name}'

    cv = Canvas(1024, 512, (0,0,0,255))
    white = Paint.Color((255, 255, 255, 255))
    grey = Paint.Color((127, 127, 127, 255))
    message_width, message_height = text_size_multiline(text_wrap(text = message, width = 448, size = 28, font = font_message, draw_emojis = True), size = 24, font = font_message, draw_emojis = True)
    draw_text_wrapped(
        canvas=cv,
        text = message,
        x = 768,
        y = 256,
        ax = 0.5, ay = 0.5,
        size = 28,
        width = 448,
        font = font_message,
        fill = white,
        align = TextAlign.Center,
        draw_emojis = True
    )
    draw_text_wrapped(
        canvas=cv,
        text = f"{nickname}",
        x = 768,
        y = (256 + (message_height / 2) + 32),
        ax = 0.5, ay = 0.5,
        size = 18,
        width = 448,
        font = font_nickname,
        fill = white,
        align = TextAlign.Center,
        draw_emojis = True
    )
    draw_text_wrapped(
        canvas=cv,
        text = f"{username} in {channel}, {time_since}",
        x = 768,
        y = (256 + (message_height / 2) + 48),
        ax = 0.5, ay = 0.5,
        size = 16,
        width = 448,
        font = font_username,
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
    time_since = f'{delta.days} days ago'
    
    if (len(message.attachments) >= 1) and (len(message.content) <= 0):
        message = message.attachments[0].filename
    else:
        message = message.content
    
    gen_image = generate_image(interaction, user, message, uwu, time_since)

    return gen_image

@tree.context_menu(name="Auto quote")
async def quote_app(interaction: discord.Interaction, message: discord.Message):
    gen_image = app_base(interaction, message, False)
    
    with BytesIO() as image_binary:
        gen_image.save(image_binary, 'PNG')
        image_binary.seek(0)
        await interaction.response.send_message(file=discord.File(fp=image_binary, filename="quote.png"))

@tree.context_menu(name="Auto Quote uwu")
async def uwu_quote_app(interaction: discord.Interaction, message: discord.Message):
    gen_image = app_base(interaction, message, True)
    
    with BytesIO() as image_binary:
        gen_image.save(image_binary, 'PNG')
        image_binary.seek(0)
        await interaction.response.send_message(file=discord.File(fp=image_binary, filename="quote.png"))

client.run("token")