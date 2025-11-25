import discord
from discord.ext import commands, tasks
import logging
from dotenv import load_dotenv
import os
from TikTokLive import TikTokLiveClient
from TikTokLive.client.logger import LogLevel
from TikTokLive.events import LiveEndEvent

load_dotenv()
token = os.getenv("DISCORD_TOKEN")
channel_id = int(os.getenv("DISCORD_CHANNEL_ID", "0"))  # Add this to your .env

print(f"Loaded Discord Token: {token}", flush=True)

client: TikTokLiveClient = TikTokLiveClient(
    unique_id="@dralphachad" #channel to monitor
)

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}', flush=True)
    check_live.start()
    print(f"Started check_live task on {client.unique_id}", flush=True)

@tasks.loop(minutes=1)
async def check_live():
    channel = bot.get_channel(channel_id)
    if not channel:
        return 
    
    if await client.is_live():
        await channel.send(f"@everyone DAC just went live! Tune in now!")
        check_live_ended.start()
        check_live.stop()

@tasks.loop(minutes=1)
async def check_live_ended():
    channel = bot.get_channel(channel_id)
    if not channel:
        return 
    
    if not await client.is_live():
        await channel.send(f"DAC ended stream, thanks for watching!")
        check_live.start()
        check_live_ended.stop()

bot.run(token, log_handler=handler, log_level=logging.DEBUG)