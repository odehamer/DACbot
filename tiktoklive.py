from TikTokLive import TikTokLiveClient
from TikTokLive.client.logger import LogLevel
from TikTokLive.events import ConnectEvent, CommentEvent, GiftEvent
from gtts import gTTS
import time
import os
import platform

streamer_username = "sergioramoscr_" #change to desired streamer
min_coins = 1 #minimum coins required to trigger TTS

gifters = []

client: TikTokLiveClient = TikTokLiveClient(
    unique_id="@" + streamer_username
)

@client.on(ConnectEvent)
async def on_connect(event: ConnectEvent):
    print(f"Connected to @{event.unique_id}!", flush=True)
    client.logger.info(f"Connected to @{event.unique_id}!")

@client.on(CommentEvent)
async def on_comment(event: CommentEvent):
    username = event.user.username
    print(f"Checking comment from {username}", flush=True)
    if username in gifters:
        comment_text = event.comment
        print(f"New comment by {event.user.nickname}: {comment_text}", flush=True)

        # use gTTS to speak the comment
        tts = gTTS(text=comment_text, lang='en', slow=False)
        tts.save("temp_comment.mp3")
        
        # Cross-platform audio playback
        if platform.system() == "Darwin":  # macOS
            os.system("afplay -v 3 temp_comment.mp3")
        elif platform.system() == "Windows":
            os.system("powershell -c (New-Object Media.SoundPlayer 'temp_comment.mp3').PlaySync()")
        else:  # Linux
            os.system("ffplay -nodisp -autoexit temp_comment.mp3")
        
        os.remove("temp_comment.mp3")

        gifters.remove(username)
    elif "tts" in event.comment.lower() and (username == "odehamer" or username == streamer_username): #manual TTS trigger, chat "tts <username>" to add someone to TTS
        print(f"{event.comment.lower().strip('tts ').strip()} manually added to TTS", flush=True)
        gifters.append(event.comment.lower().strip("tts ").strip())


@client.on(GiftEvent)
async def on_gift(event: GiftEvent):
    print(event.gift.diamond_count)
    if event.gift.diamond_count * 2 >= min_coins: # according to google 1 diamond = 2 coins   
        print(f"{event.user.nickname} added to TTS via gift", flush=True)
        gifters.append(event.user.username)

client.add_listener(ConnectEvent, on_connect)
client.add_listener(CommentEvent, on_comment)

if __name__ == "__main__":
    running = True

    while running: #sometimes takes a few tries to connect
        try:
            client.run()
            running = False
        except Exception as e: 
            print(f"Error: {e}", flush=True)
            print("Trying to connect to client again in 10 seconds, make sure username is correct. This may take a few minutes", flush=True)
            time.sleep(10)