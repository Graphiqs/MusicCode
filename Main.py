import discord
from discord.ext import commands
import asyncio
import requests, bs4
from itertools import cycle
import os
import time
import youtube_dl
from discord import opus

client = commands.Bot(command_prefix=("m."))
status = ["testing the bot", "m.help", "created by noobperson"]

async def change_status():
	await client.wait_until_ready()
	msgs = cycle(status)
	
	while not client.is_closed:
		current_status = next(msgs)
		await client.change_presence(game=discord.Game(name=current_status))
		await asyncio.sleep(4)

players = {}	

@client.event 
async def on_ready():
	print('Logged in as')
	print("User name:", client.user.name)
	print("User id:", client.user.id)
	print('---------------')
	
@client.event
async def on_message(message):
  if message.content == 'm.stop':
      serverid = message.server.id
      players[serverid].stop()
      await client.send_message(message.channel, "Player stopped")
  if message.content == 'm.pause':
      serverid = message.server.id
      players[serverid].pause()
      await client.send_message(message.channel, "Player paused")
  if message.content == 'm.resume':
      serverid = message.server.id
      players[serverid].resume()
      await client.send_message(message.channel, "Player resumed")
  if message.content.startswith('m.play '):
      author = message.author
      name = message.content.replace("m.play ", '')                 
      fullcontent = ('http://www.youtube.com/results?search_query=' + name)
      text = requests.get(fullcontent).text
      soup = bs4.BeautifulSoup(text, 'html.parser')
      img = soup.find_all('img')
      div = [ d for d in soup.find_all('div') if d.has_attr('class') and 'yt-lockup-dismissable' in d['class']]
      a = [ x for x in div[0].find_all('a') if x.has_attr('title') ]
      title = (a[0]['title'])
      a0 = [ x for x in div[0].find_all('a') if x.has_attr('title') ][0]
      url = ('http://www.youtube.com'+a0['href'])
      delmsg = await client.send_message(message.channel, 'Now Playing ** >> ' + title + '**')
      server = message.server
      voice_client = client.voice_client_in(server)
      player = await voice_client.create_ytdl_player(url)
      players[server.id] = player
      print("User: {} From Server: {} is playing {}".format(author, server, title))
      player.start()
  await client.process_commands(message)

@client.command(pass_context=True, no_pm=True)
async def ping(ctx):
    pingtime = time.time()
    pingms = await client.say("Pinging...")
    ping = (time.time() - pingtime) * 1000
    await client.edit_message(pingms, "Pong! :ping_pong: ping time is `%dms`" % ping)
	
@client.command(pass_context=True, no_pm=True, hidden=True)
async def playing(ctx):
    """Shows info about the currently played song."""

    state = get_voice_state(ctx.message.server)
    if state.current is None:
        await client.say('Not playing anything.')
    else:
        await client.say('Now playing {}'.format(state.current))
    
@client.command(pass_context=True)
async def join(ctx):
    channel = ctx.message.author.voice.voice_channel
    await client.join_voice_channel(channel)
    await client.say('Connected to voice channel: **[' + str(channel) + ']**')
	
@client.command(pass_context=True)
async def leave(ctx):
    server = ctx.message.server
    channel = ctx.message.author.voice.voice_channel
    voice_client = client.voice_client_in(server)
    if voice_client is None:
		await client.say(":exclamation: ***I am not in a voice channel***")
				 return
				 await voice_client.disconnect()
				 await client.say("Successfully disconnected from ***[{}]***".format(channel))

@client.command()
async def credits():
	"""credits who helped me"""
	await client.say('iHoverZz#2321 helped me with this music bot')
	
client.loop.create_task(change_status())
client.run(os.environ['BOT_TOKEN'])
