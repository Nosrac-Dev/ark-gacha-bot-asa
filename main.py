import discord
from discord.ext import commands
from typing import Callable
import asyncio
import logs.botoptions as botoptions
import pyautogui
import settings
import json
import time
import logs.discordbot as discordbot
import bot.stations as stations
import task_manager
import win32gui
import win32con
import sys
import pygetwindow as gw
import logs.gachalogs as gachalogs
import logging as logstuff
from ASA.player import console


intents = discord.Intents.default()
pyautogui.FAILSAFE = False
bot = commands.Bot(command_prefix=settings.command_prefix, intents=intents)

running_tasks = []

def load_json(json_file:str):
    try:
        with open(json_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []  

def save_json(json_file:str,data):
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=4)

async def send_new_logs():
    log_channel = bot.get_channel(settings.log_channel_gacha)
    last_position = 0
    
    while True:
        with open("logs/logs.txt", 'r') as file:
            file.seek(last_position)
            new_logs = file.read()
            if new_logs:
                if gachalogs.logging_level >= logstuff.ERROR:
                    await log_channel.send(f"<@576182444592463892>\n New logs:\n```{new_logs}```")
                else:    
                    await log_channel.send(f"New logs:\n```{new_logs}```")
                last_position = file.tell()
        await asyncio.sleep(5)

@bot.tree.command(name="add_gacha", description="add a new gacha station to the data")
async def add_gacha(interaction: discord.Interaction, name: str, teleporter: str, resource_type: str ,direction: str):
    data = load_json("json_files/gacha.json")

    for entry in data:
        if entry["name"] == name:
            await interaction.response.send_message(f"a gacha station with the name '{name}' already exists", ephemeral=True)
            return
        
    new_entry = {
        "name": name,
        "teleporter": teleporter,
        "resource_type": resource_type,
        "side" : direction
    }
    data.append(new_entry)

    save_json("json_files/gacha.json",data)

    await interaction.response.send_message(f"added new gacha station: {name}")

@bot.tree.command(name="list_gacha", description="list all gacha stations")
async def list_gacha(interaction: discord.Interaction):

    data = load_json("json_files/gacha.json")
    if not data:
        await interaction.response.send_message("no gacha stations found", ephemeral=True)
        return


    response = "gacha Stations:\n"
    for entry in data:
        response += f"- **{entry['name']}**: teleporter `{entry['teleporter']}`, resource `{entry['resource_type']} gacha on the `{entry['side']}` side `\n"

    await interaction.response.send_message(response)


@bot.tree.command(name="add_pego", description="add a new pego station to the data")
async def add_pego(interaction: discord.Interaction, name: str, teleporter: str, delay: int):
    data = load_json("json_files/pego.json")

    for entry in data:
        if entry["name"] == name:
            await interaction.response.send_message(f"a pego station with the name '{name}' already exists", ephemeral=True)
            return
        
    new_entry = {
        "name": name,
        "teleporter": teleporter,
        "delay": delay
    }
    data.append(new_entry)

    save_json("json_files/pego.json",data)

    await interaction.response.send_message(f"added new pego station: {name}")

@bot.tree.command(name="list_pego", description="list all pego stations")
async def list_pego(interaction: discord.Interaction):

    data = load_json("json_files/pego.json")
    if not data:
        await interaction.response.send_message("no pego stations found", ephemeral=True)
        return


    response = "pego Stations:\n"
    for entry in data:
        response += f"- **{entry['name']}**: teleporter `{entry['teleporter']}`, delay `{entry['delay']}`\n"

    await interaction.response.send_message(response)

@bot.tree.command(name="pause", description="sends the bot back to render bed for X amount of seconds")
async def reset(interaction: discord.Interaction,time:int):
    task = task_manager.scheduler
    pause_task = stations.pause(time)
    task.add_task(pause_task)
    await interaction.response.send_message(f"pause task added will now pause for {time} seconds once the next task finishes")
    
async def embed_send(queue_type):
    log_channel = 0
    if queue_type == "active_queue":
        log_channel = bot.get_channel(settings.log_active_queue)
    else:
        log_channel = bot.get_channel(settings.log_wait_queue)
    while True:
        embed_msg = await discordbot.embed_create(queue_type)
        await log_channel.purge()
        await log_channel.send(embed = embed_msg)
        await asyncio.sleep(30)

@bot.tree.command()
async def start(interaction: discord.Interaction):
    global running_tasks
    logchn = bot.get_channel(settings.log_channel_gacha) 
    if logchn:
        await logchn.send(f'bot starting up now')
        await logchn.send(f"<@576182444592463892> Starting Now!")
    # resetting log files
    with open("logs/logs.txt", 'w') as file:
        file.write(f"")
    running_tasks.append(bot.loop.create_task(send_new_logs()))
    
    
    await interaction.response.send_message(f"starting up bot now you have 5 seconds before start")
    time.sleep(5)
    running_tasks.append(asyncio.create_task(botoptions.task_manager_start()))
    running_tasks.append(bot.loop.create_task(embed_send("active_queue")))
    running_tasks.append(bot.loop.create_task(embed_send("waiting_queue")))
    
@bot.tree.command()
async def shutdown(interaction: discord.Interaction):
    await interaction.response.send_message("Shutting down script...")
    print("Shutting down script...")
    cmd_windows = [win for win in gw.getAllWindows() if "cmd" in win.title.lower() or "command prompt" in win.title.lower() or "system32" in win.title.lower()]

    if cmd_windows:
        cmd_window = cmd_windows[0]  
        hwnd = cmd_window._hWnd  

        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE) 
        win32gui.SetForegroundWindow(hwnd)  
        time.sleep(1)         
        win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
        print("Shutting down...")
        sys.exit() 
    else:
        print("No CMD window found.")

@bot.tree.command(name="lag_factor", description="changes the sleep_constant value in settings.py") #Command to adjust the sleep_constant value in settings.py to account for lag Nosrac 5/28
async def lag_factor(interaction: discord.Interaction, factor:float):
    settings.sleep_constant = factor
    await interaction.response.send_message(f"sleep_constant has been set to {settings.sleep_constant} the bot will now run {settings.sleep_constant*100}% slower than base speed")

@bot.tree.command(name="logging", description="Changes the logging level of the bot (DEBUG, INFO, WARNING, ERROR, CRITICAL)") #Command to adjust the logging level of the bot by changing the logging_level variable in gachalogs file Nosrac 5/29
async def logging(interaction: discord.Interaction, level:str):
    level = level.upper()
    if level in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
        gachalogs.logging_level = logstuff.getLevelName(level)
    else:
        gachalogs.logging_level = logstuff.getLevelName("INFO")
        #gachalogs.logging_level = 20
    logstuff.getLogger("Gacha").setLevel(gachalogs.logging_level)
    await interaction.response.send_message(f"Logging_level has been set to {logstuff.getLevelName(gachalogs.logging_level)}" )

@bot.tree.command(name="log_reset", description="resets the loggint task") #Nos 5/3 
async def log_reset(interaction: discord.Interaction):
    global running_tasks
    logchn = bot.get_channel(settings.log_channel_gacha) 
    if logchn:
        await logchn.send(f'Logs are resetting')
    
    # resetting log files
    with open("logs/logs.txt", 'w') as file:
        file.write(f"")
    running_tasks.pop(1) #Removes the first Item from the running_task array (send_new_logs)
    running_tasks.insert(1, bot.loop.create_task(send_new_logs())) #Starts a new (send_new_logs) and adds it to the first slot of the running_task array

    await interaction.response.send_message(f"Logs should be fixed now")
    await logchn.send(f"{running_tasks}") 
#    running_tasks.append(bot.loop.create_task(embed_send("active_queue"))) #saved incase active or waiting cues need to be resetzzzzzzz
#    running_tasks.append(bot.loop.create_task(embed_send("waiting_queue")))@bot.tree.command(name="berry", description="Flag bot to refill iguanadon berries") #Bitbucket Command to change berry_station global variable to true 

@bot.tree.command(name="berry", description="Flag to refill Berries") #Bitbucket 
async def berry(interaction: discord.Interaction, refill:bool):
    stations.berry_station = refill
    await interaction.response.send_message(f"berry_station has been set to {stations.berry_station}")

@bot.tree.command(name="reconnect", description="Reconnect to server. Helpful if items did not render in") #Bitbucket 
async def reconnect(interaction: discord.Interaction, confirm:bool):
    await interaction.response.send_message(f"Resetting connection to server")
    console.console_write("reconnect")
    time.sleep(60) # takes a while for the reonnect to actually go into action





@bot.event
async def on_ready():
    await bot.tree.sync()
    
    logchn = bot.get_channel(settings.log_channel_gacha) 
    if logchn:
        await logchn.send(f'bot ready to start')
    print (f'logged in as {bot.user}')

api_key = settings.discord_api_key

if __name__ =="__main__":
    if len(settings.discord_api_key) < 4:
        print("you need to have a valid discord API key for the bot to run")
        print("please follow the instructions in the discord server to get your api key")
        exit()
    bot.run(api_key)