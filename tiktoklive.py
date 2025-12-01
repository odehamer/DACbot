from TikTokLive import TikTokLiveClient
from TikTokLive.client.logger import LogLevel
from TikTokLive.events import ConnectEvent, CommentEvent, GiftEvent
import subprocess

streamer_username = "kioyasme"

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
        subprocess.run(["say", comment_text])
        gifters.remove(username)
    elif "tts" in event.comment.lower() and (username == "odehamer" or username == streamer_username):
        print(f"{username} manually added to TTS", flush=True)
        gifters.append(username)


@client.on(GiftEvent)
async def on_gift(event: GiftEvent):
    print(f"{event.user.nickname} added to TTS via gift", flush=True)
    gifters.append(event.user.username)

client.add_listener(ConnectEvent, on_connect)
client.add_listener(CommentEvent, on_comment)

if __name__ == "__main__":
    try:
        client.run()
    except Exception as e:
        print(f"Error: {e}", flush=True)
        print("User either does not exist, or you have made too many API calls. Try again in a few minutes", flush=True)