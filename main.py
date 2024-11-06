import asyncio
import discord
from discord import *
from discord.ext import commands
from discord.ui import *
from actions import loading,error
import logging

logging.basicConfig(level=logging.DEBUG, format="[%(asctime)s %(levelname)s] %(filename)s %(message)s", filename="./log.log")

console = logging.StreamHandler()
console.setLevel(logging.INFO)

formatter = logging.Formatter("[%(asctime)s %(levelname)s] %(message)s",datefmt="%Y-%m-%d %H:%M:%S")
console.setFormatter(formatter)

logging.getLogger('').addHandler(console)

logger = logging.getLogger(__name__)

import json
import os
import sys
import psutil
import time

config = {}
with open("./config.json","r",encoding="UTF-8") as c:
    config = json.load(c)

intents = Intents.all()
bot = commands.Bot(command_prefix="k.",intents=intents)
bot.remove_command("help")

loaded = []
all_ext = []

def check_admin(interaction:Interaction):
    return str(interaction.user.id) in config["admin"]

@bot.event
async def on_ready():
    logger.info("syncing slash")
    await bot.tree.sync()
    logger.info("bot ready")

@bot.tree.error
async def on_command_error(interaction:Interaction,event_method):
    error_msg=str(event_method)
    embed=discord.Embed(title="Error",description=f"Catch From{interaction.user}\nAt {time.ctime(time.time())}")
    embed.add_field(name=error_msg,value="** **")
    admins = bot.get_user(949607058993455104)
    await admins.send(embed=embed)
    await interaction.edit_original_response(embed=error.get_error(error_msg))

@bot.tree.command(name="status",description="Check the status of the bot")
async def status(interaction:Interaction):
    await interaction.response.send_message(embed=loading.get_loading())
    embed = Embed(title="Status",color=0xff5500)
    embed.add_field(name=f"🐍Python",value=sys.version)
    embed.add_field(name=f"🤔Discord.py",value=discord.__version__,inline=True)
    embed.add_field(name=f"✨CPU",value=psutil.cpu_percent(0.1),inline=True)
    embed.add_field(name=f"✨RAM",value=str(psutil.virtual_memory()[2])+"%",inline=False)
    embed.add_field(name=f"====Modules====",value="** **",inline=False)
    for i in all_ext:
        status = "🟩" if i in loaded else "🟥"
        status_text = "已載入" if i in loaded else "未載入"
        embed.add_field(name=f"{status} {i}",value=status_text,inline=True)
    await interaction.edit_original_response(embed=embed)

@bot.tree.command(name="load",description="load")
@app_commands.describe(extension="模組")
@app_commands.check(check_admin)
async def load(interaction:Interaction, extension:str):
    await interaction.response.defer()
    await bot.load_extension(f'cmds.{extension}')
    if extension not in loaded:
        loaded.append(extension)
    await bot.tree.sync()
    await interaction.followup.send(f'loaded {extension} done.')
    
@bot.tree.command(name="unload",description="unload")
@app_commands.describe(extension="模組")
@app_commands.check(check_admin)
async def unload(interaction:Interaction, extension:str):
    await interaction.response.defer()
    await bot.unload_extension(f'cmds.{extension}')
    if extension in loaded:
        loaded.remove(extension)
    await bot.tree.sync()
    await interaction.followup.send(f'unloaded {extension} done.')

@bot.tree.command(name="reload",description="reload")
@app_commands.describe(extension="模組")
@app_commands.check(check_admin)
async def reload(interaction:Interaction, extension:str):
    await interaction.response.defer()
    await bot.reload_extension(f'cmds.{extension}')
    await bot.tree.sync()
    await interaction.followup.send(f'reloaded {extension} done.')

async def load_extensions():
    for Filename in os.listdir('./cmds'):
        if Filename.endswith('.py'):
                logger.info(f"loading {Filename}")
                await bot.load_extension(f'cmds.{Filename[:-3]}')
                all_ext.append(Filename[:-3])
                loaded.append(Filename[:-3])
                logger.info("done")
    logger.info("setting up...")

async def main():
    async with bot:
        await load_extensions()
        await bot.start(config['TOKEN'])

if __name__ == "__main__":
    os.system("title " + "Work Bot v2")
    asyncio.run(main())
    