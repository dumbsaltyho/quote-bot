from PIL import Image, ImageFont, ImageDraw 
import textwrap
import requests
from io import BytesIO
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='t.', intents=intents)

@client.event
async def on_ready():
    print('ready !')

@client.command()
async def quote(ctx):
    message = await ctx.fetch_message(ctx.message.reference.message_id)
    user = await client.fetch_user(message.author.id)

    base_image = Image.new('RGB', (1024, 512), (0,0,0,0))
    w, h = base_image.size
    qh = (h/2)
    draw = ImageDraw.Draw(base_image)
    font_message = ImageFont.truetype(r'Urbanist-Light.ttf', 24)
    font_nickname = ImageFont.truetype(r'Urbanist-BoldItalic.ttf', 18)
    font_username = ImageFont.truetype(r'Urbanist-ExtraLight.ttf', 16)
    font_bottom_text = ImageFont.truetype(r'Urbanist-LightItalic.ttf', 14)

    get_avatar = requests.get(user.avatar.url)
    avatar = Image.open(BytesIO(get_avatar.content))
    avatar_shadow = Image.open(r'avatar-shadow.png')

    if (len(message.attachments) >= 1) and (len(message.content) <= 0):
        message = message.attachments[0].filename
    else:
        if (len(message.content) >= 141) and (len(message.content) <= 160):
            qh = (h/2-8)
        elif (len(message.content) >= 161) and (len(message.content) <= 180):
            qh = (h/2-16)
        elif len(message.content) >= 181:
            qh = (h/2-16)
        else:
            pass
        message = textwrap.wrap(message.content[:200], width=37)
        message = '\n'.join(message)

    nickname = f'- {user.display_name}'
    username = f'@{user.name}'
    channel = f'#{ctx.channel.name}'
    draw.text(((w/2+256), qh), f'"{message}"', fill="white", font=font_message, align="center", anchor='mm') 
    draw.text(((w/2+256),(352)), nickname, fill="white", font=font_nickname, align="center", anchor='mm')
    draw.text(((w/2+256),(376)), f'{username} in {channel}', fill="grey", font=font_username, align="center", anchor='mm')
    draw.text(((w/2+256), 480), "reply to any text message with t.quote to make a quote", fill="white", font=font_bottom_text,align="center",anchor='mb')
    base_image.paste(avatar.resize((512,512)), (0,0))
    base_image.paste(avatar_shadow, (0,0), avatar_shadow)
    with BytesIO() as image_binary:
        base_image.save(image_binary, 'PNG')
        image_binary.seek(0)
        await ctx.send(file=discord.File(fp=image_binary,filename="image.png"))

client.run("token")