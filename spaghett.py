import discord
import os
import yt_dlp #pip install --upgrade yt-dlp
from dotenv import load_dotenv
import asyncio # To Do for 

def run_bot():
    load_dotenv()
    TOKEN = os.getenv('discord_token')
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    queues = {}
    voice_clients = {}
    currently_playing = {}
    current_volume = 0.25  # Default volume
    new_volume = 0.5
    loop_flags = {}  # Tracks whether loop is active for a guild
    cookie_path = r"./cookies.firefox-private.txt"
    yt_dl_options = {
        "format": "bestaudio/best",
        "cookiefile": cookie_path
    }
    ytdl = yt_dlp.YoutubeDL(yt_dl_options)
    timeout = 300
    


    def get_ffmpeg_options(volume):
        return {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -loglevel debug',
            'options': f'-vn -filter:a "volume={volume}"'
        }

    def add_to_queue(guild_id, url):
        if guild_id not in queues:
            queues[guild_id] = []
        queues[guild_id].append(url)

    def play_next_in_queue(guild_id):
        if guild_id in loop_flags and loop_flags[guild_id]:
            # Loop the current song
            song_url = currently_playing[guild_id]
            try:
                seek_options = get_ffmpeg_options(current_volume)
                player = discord.FFmpegOpusAudio(song_url, **seek_options)
                voice_clients[guild_id].play(player, after=lambda e: play_next_in_queue(guild_id))
            except Exception as e:
                print(f"Error looping song: {e}")
        elif guild_id in queues and queues[guild_id]:
            # Play the next song in the queue
            next_song = queues[guild_id].pop(0)
            currently_playing[guild_id] = next_song

            try:
                seek_options = get_ffmpeg_options(current_volume)
                player = discord.FFmpegOpusAudio(next_song, **seek_options)
                voice_clients[guild_id].play(player, after=lambda e: play_next_in_queue(guild_id))
            except Exception as e:
                print(f"Error playing next in queue: {e}")

    @client.event
    async def on_ready():
        print(f'{client.user} is now jamming')

    # @client.command
    # async def disconnect_after_timeout(voice_client, timeout):
    #    await asyncio.sleep(timeout)  
         

    @client.event
    async def on_message(message):
        nonlocal current_volume

        if message.content.lower().startswith("!play"):
            try:
                if not message.author.voice:
                    await message.channel.send("You need to be in a voice channel to play music!")
                    return

                if message.guild.id not in voice_clients or not voice_clients[message.guild.id].is_connected():
                    voice_client = await message.author.voice.channel.connect()
                    voice_clients[message.guild.id] = voice_client

                url = message.content.split()[1]

                try:
                    data = ytdl.extract_info(url, download=False)
                    song_url = data["url"]
                except Exception as e:
                    await message.channel.send(f"Failed to process the URL: {e}")
                    return

                if voice_clients[message.guild.id].is_playing():
                    add_to_queue(message.guild.id, song_url)
                    await message.channel.send("Added to queue. Bau mal lieber einen du Otto!")
                else:
                    currently_playing[message.guild.id] = song_url
                    player = discord.FFmpegOpusAudio(song_url, **get_ffmpeg_options(current_volume))
                    voice_clients[message.guild.id].play(player, after=lambda e: play_next_in_queue(message.guild.id))
                    await message.channel.send(f"The video {url} will be played")
                    return
            except Exception as e:
                print(f"Error in !play command: {e}")

        if message.content.lower().startswith("!pause"):
            try:
                voice_clients[message.guild.id].pause()
                await message.channel.send("Mach den Lahmacun in den Ofen rein, bis glei")
            except Exception as e:
                print(f"Error in !pause command: {e}")

        if message.content.lower().startswith("!resume"):
            try:
                voice_clients[message.guild.id].resume()
                await message.channel.send("Lahmacun ist fertig")
            except Exception as e:
                print(f"Error in !resume command: {e}")

        if message.content.lower().startswith("!stop"):
            try:
                voice_clients[message.guild.id].stop()
                await voice_clients[message.guild.id].disconnect()
                currently_playing.pop(message.guild.id, None)
                queues.pop(message.guild.id, None)
                loop_flags.pop(message.guild.id, None)
                await message.channel.send("Bis glei")
            except Exception as e:
                print(f"Error in !stop command: {e}")

        if message.content.lower().startswith("!loop"):
            try:
                guild_id = message.guild.id
                if guild_id not in loop_flags or not loop_flags[guild_id]:
                    loop_flags[guild_id] = True
                    await message.channel.send("Looping the current song.")
                else:
                    loop_flags[guild_id] = False
                    await message.channel.send("Stopped looping.")
            except Exception as e:
                print(f"Error in !loop command: {e}")

        if message.content.lower().startswith("!skip"):
            try:
                guild_id = message.guild.id
                if guild_id in loop_flags:
                    loop_flags[guild_id] = False  # Disable loop if active
                voice_clients[guild_id].stop()
                await message.channel.send("Skipped to the next song.")
            except Exception as e:
                print(f"Error in !skip command: {e}")

        if message.content.lower().startswith("!volume"):
            try:
                # Parse the new volume from the command
                new_volume = float(message.content.split()[1])
                if 0.0 <= new_volume <= 2.0:
                    current_volume = new_volume
                    guild_id = message.guild.id

                    # If something is playing, update the volume live
                    if guild_id in voice_clients and voice_clients[guild_id].is_playing():
                        currently_playing_song = currently_playing.get(guild_id)
                        if currently_playing_song:
                            voice_clients[guild_id].stop()
                            player = discord.FFmpegOpusAudio(
                                currently_playing_song,
                                **get_ffmpeg_options(current_volume)
                            )
                            voice_clients[guild_id].play(player, after=lambda e: play_next_in_queue(guild_id))

                    await message.channel.send(f"Die Lautstärke wurde auf {current_volume * 100:.0f}% geändert.")
                else:
                    await message.channel.send("Lautstärke muss zwischen 0.0 und 2.0 liegen!")
            except (IndexError, ValueError):
                await message.channel.send("Die Lautstärke muss zwischen 0.0 und 2.0 liegen!")
            except Exception as e:
                print(f"Error in !volume command: {e}")

        if message.content.lower().startswith("!seek"):
            try:
                # Get the seconds to seek from the message
                seconds = int(message.content.split()[1])

                # Check if a song is currently playing
                if message.guild.id not in currently_playing:
                    await message.channel.send("No song is currently playing.")
                    return

                # Stop the current player
                voice_clients[message.guild.id].stop()

                # Recreate the FFmpeg audio stream with the seek option for the current song
                song = currently_playing[message.guild.id]

                # Validate and extract info for the current song
                try:
                    data = ytdl.extract_info(song, download=False)
                    song_url = data["url"]
                except Exception as e:
                    await message.channel.send(f"Failed to process the song for seeking: {e}")
                    return

                seek_options = get_ffmpeg_options(current_volume)
                seek_options['before_options'] += f' -ss {seconds}'

                player = discord.FFmpegOpusAudio(song_url, **seek_options)

                voice_clients[message.guild.id].play(player)
            except Exception as e:
                print(e)



    client.run(TOKEN)

run_bot()

 