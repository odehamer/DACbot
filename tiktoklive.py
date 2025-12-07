"""
╔════════════════════════════════════════════════════════════════╗
║                    ⚙️  CONFIGURATION  ⚙️                        ║
║                 Only touch variables in this section           ║
╚════════════════════════════════════════════════════════════════╝
"""

streamer_username = "dralphachad" #change to desired streamer
min_coins = 1 #minimum coins required to trigger TTS
can_mods_tts = True # True to allow mods to use TTS without gifting, False to restrict to gifting only (make sure to capatalize True/False correctly)
tts_on_follow = True # True to enable TTS on follow, False to disable
random_accents = False # True to use random accents for TTS, False to use default US accent

"""
╔════════════════════════════════════════════════════════════════╗
║                      🚨  DANGER ZONE  🚨                        ║
║              Do NOT modify anything below this line            ║
╚════════════════════════════════════════════════════════════════╝
"""



from TikTokLive import TikTokLiveClient
from TikTokLive.client.logger import LogLevel
from TikTokLive.events import ConnectEvent, CommentEvent, GiftEvent, FollowEvent    
from gtts import gTTS
try:
    from playsound import playsound
except Exception:
    playsound = None
import time
import os
import platform
import subprocess
import random

gifters = []
followers = [] # stop duplicate follow TTS
diamond_count = 0  # Initialize diamond counter
tts_accents = ['com.au', 'co.uk', 'ca', 'us', 'ie', 'co.in', 'co.za', 'com.ng']  # Different accents for variety

client: TikTokLiveClient = TikTokLiveClient(
    unique_id="@" + streamer_username
)

@client.on(ConnectEvent)
async def on_connect(event: ConnectEvent):
    print(f"Connected to @{event.unique_id}!", flush=True)
    client.logger.info(f"Connected to @{event.unique_id}!")

@client.on(CommentEvent)
async def on_comment(event: CommentEvent):
    username = event.user_info.username
    is_mod = event.user_info.is_moderator
    #print(f"Checking comment from {username}, mod: {event.user_info.is_moderator}", flush=True)
    if username in gifters or (can_mods_tts and (username == streamer_username or username == "odehamer" or is_mod)): #check if user is allowed TTS
        comment_text = event.comment
        if (can_mods_tts and (username == streamer_username or username == "odehamer" or is_mod)):
            print(f"Reading mod {username}'s message: {comment_text}", flush=True)
        else:
            print(f"Reading {username}'s message ({gifters.count(username) - 1} tts messages remaining): {comment_text}", flush=True)

        # generate a random accent for variety
        accent = random.choice(tts_accents)

        # use gTTS to speak the comment
        tts = gTTS(text=comment_text, lang='en', tld=accent, slow=False)
        tts.save("temp_comment.mp3")
        
        # Cross-platform audio playback
        if platform.system() == "Darwin":  # macOS
            os.system("afplay -v 3 temp_comment.mp3")
        elif platform.system() == "Windows":
            # Windows: PowerShell SoundPlayer only accepts WAV. Prefer playsound if available.
            if playsound:
                try:
                    playsound("temp_comment.mp3")
                    played = True
                except Exception:
                    played = False
            else:
                played = False

            if not played:
                # Use PowerShell Start-Process with -Wait to play MP3 with the default associated player
                # This blocks until the external player exits (so it behaves like PlaySync).
                try:
                    subprocess.run([
                        "powershell",
                        "-NoProfile",
                        "-Command",
                        "Start-Process",
                        "-FilePath",
                        os.path.abspath("temp_comment.mp3"),
                        "-Wait"
                    ], check=False)
                except Exception:
                    # Final fallback: use start (may be asynchronous)
                    os.system(f'start "" "{os.path.abspath("temp_comment.mp3")}"')
        else:  # Linux
            os.system("ffplay -nodisp -autoexit temp_comment.mp3")
        
        os.remove("temp_comment.mp3")
        
        # After speaking, remove user from gifters list
        try: 
            gifters.remove(username)
        except ValueError:
            pass

    elif "tts" in event.comment.lower() and (username == "odehamer" or username == streamer_username): #manual TTS trigger, chat "tts <username>" to add someone to TTS
        print(f"{event.comment.lower().strip('tts ').strip()} manually added to TTS", flush=True)
        gifters.append(event.comment.lower().strip("tts ").strip())


@client.on(GiftEvent)
async def on_gift(event: GiftEvent):
    global diamond_count
    diamond_count += event.gift.diamond_count
    print(f"Estimated stream earnings: ${(diamond_count * 0.005):.2f}") # according to google 1 diamond = 0.005 USD
    if event.gift.diamond_count * 2 >= min_coins: # according to google 1 diamond = 2 coins   
        print(f"{event.user.username} added to TTS via gift", flush=True)
        gifters.append(event.user.username)

@client.on(FollowEvent)
async def on_follow(event: FollowEvent):
    if tts_on_follow and event.user.username not in followers:
        print(f"{event.user.username} was added to TTS via follow", flush=True)
        gifters.append(event.user.username)
        followers.append(event.user.username)


client.add_listener(ConnectEvent, on_connect)
client.add_listener(CommentEvent, on_comment)

if __name__ == "__main__":
    running = True

    if not random_accents:
        tts_accents = ['us']  # Override to only use US accent

    while running: #sometimes takes a few tries to connect
        try:
            client.run()
            running = False
        except Exception as e:
            #print(f"Error: {e}", flush=True)
            print("Connection failed, this may take a few tries. Make sure the username is correct, and the user is live", flush=True)
            time.sleep(5)

