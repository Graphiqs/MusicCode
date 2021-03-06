import discord
from discord.ext import commands
import asyncio
import requests, bs4
import os
import time
import youtube_dl
import inspect
import datetime
from discord import opus

start_time = time.time()

client = commands.Bot(command_prefix=("m."))
songs = asyncio.Queue()
play_next_song = asyncio.Event()
client.remove_command("help")

players = {}
queues = {}

def check_queue(id):
	if queues[id] != []:
		player = queues[id].pop(0)
		players[id] = player
		player.start()

@client.event 
async def on_ready():
	print('Logged in as')
	print("User name:", client.user.name)
	print("User id:", client.user.id)
	print('---------------')
	
async def audio_player_task():
    while True:
        play_next_song.clear()
        current = await songs.get()
        current.start()
        await play_next_song.wait()


def toggle_next():
    client.loop.call_soon_threadsafe(play_next_song.set)


@client.command(pass_context=True)
async def plays(ctx, url):
	if not client.is_voice_connected(ctx.message.server):
		voice = await client.join_voice_channel(ctx.message.author.voice_channel)
	else:
		voice = client.voice_client_in(ctx.message.server)
		
		player = await voice.create_ytdl_player(url, after=toggle_next)
		await songs.put(player)

@client.command(pass_context=True, no_pm=True)
async def ping(ctx):
    pingtime = time.time()
    pingms = await client.say("Pinging...")
    ping = (time.time() - pingtime) * 1000
    await client.edit_message(pingms, "Pong! :ping_pong: ping time is `%dms`" % ping)
	
	
	
	
    
@client.command(name="join", pass_context=True, no_pm=True)
async def _join(ctx):
    user = ctx.message.author
    channel = ctx.message.author.voice.voice_channel
    await client.join_voice_channel(channel)
    embed = discord.Embed(colour=user.colour)
    embed.add_field(name="Successfully connected to voice channel:", value=channel)
    await client.say(embed=embed)
	
@client.command(name="leave", pass_context=True, no_pm=True)
async def _leave(ctx):
    user = ctx.message.author
    server = ctx.message.server
    channel = ctx.message.author.voice.voice_channel
    voice_client = client.voice_client_in(server)
    await voice_client.disconnect()
    embed = discord.Embed(colour=user.colour)
    embed.add_field(name="Successfully disconnected from:", value=channel)
    await client.say(embed=embed)

@client.command(pass_context=True)
async def pause(ctx):
    user = ctx.message.author
    id = ctx.message.server.id
    players[id].pause()
    embed = discord.Embed(colour=user.colour)
    embed.add_field(name="Player Paused", value=f"Requested by {ctx.message.author.name}")
    await client.say(embed=embed)

@client.command(pass_context=True)
async def skip(ctx):
    user = ctx.message.author
    id = ctx.message.server.id
    players[id].stop()
    embed = discord.Embed(colour=user.colour)
    embed.add_field(name="Player Skipped", value=f"Requested by {ctx.message.author.name}")
    await client.say(embed=embed)
	
@client.command(name="play", pass_context=True)
async def _play(ctx, *, name):
	author = ctx.message.author
	name = ctx.message.content.replace("m.play ", '')
	fullcontent = ('http://www.youtube.com/results?search_query=' + name)
	text = requests.get(fullcontent).text
	soup = bs4.BeautifulSoup(text, 'html.parser')
	img = soup.find_all('img')
	div = [ d for d in soup.find_all('div') if d.has_attr('class') and 'yt-lockup-dismissable' in d['class']]
	a = [ x for x in div[0].find_all('a') if x.has_attr('title') ]
	title = (a[0]['title'])
	a0 = [ x for x in div[0].find_all('a') if x.has_attr('title') ][0]
	url = ('http://www.youtube.com'+a0['href'])
	server = ctx.message.server
	voice_client = client.voice_client_in(server)
	player = await voice_client.create_ytdl_player(url, after=lambda: check_queue(server.id))
	players[server.id] = player
	print("User: {} From Server: {} is playing {}".format(author, server, title))
	player.start()
	embed = discord.Embed(description="**__Song Play By MUZICAL DOCTORB__**")
	embed.set_thumbnail(url="https://i.pinimg.com/originals/03/2b/08/032b0870b9053a191b67dc8c3f340345.gif")
	embed.add_field(name="Now Playing", value=title)
	await client.say(embed=embed)
	
@client.command(pass_context=True)
async def queue(ctx, *, name):
	name = ctx.message.content.replace("m.queue ", '')
	fullcontent = ('http://www.youtube.com/results?search_query=' + name)
	text = requests.get(fullcontent).text
	soup = bs4.BeautifulSoup(text, 'html.parser')
	img = soup.find_all('img')
	div = [ d for d in soup.find_all('div') if d.has_attr('class') and 'yt-lockup-dismissable' in d['class']]
	a = [ x for x in div[0].find_all('a') if x.has_attr('title') ]
	title = (a[0]['title'])
	a0 = [ x for x in div[0].find_all('a') if x.has_attr('title') ][0]
	url = ('http://www.youtube.com'+a0['href'])
	server = ctx.message.server
	voice_client = client.voice_client_in(server)
	player = await voice_client.create_ytdl_player(url, after=lambda: check_queue(server.id))
	
	if server.id in queues:
		queues[server.id].append(player)
	else:
		queues[server.id] = [player]
	embed = discord.Embed(description="**__Song Play By MUZICAL DOCTORB__**")
	embed.add_field(name="Video queued", value=title)
	await client.say(embed=embed)

@client.command(pass_context=True)
async def resume(ctx):
    user = ctx.message.author
    id = ctx.message.server.id
    players[id].resume()
    embed = discord.Embed(colour=user.colour)
    embed.add_field(name="Player Resumed", value=f"Requested by {ctx.message.author.name}")
    await client.say(embed=embed)
	
@client.command()
async def stats():
	servers = list(client.servers)
	current_time = time.time()
	difference = int(round(current_time - start_time))
	text = str(datetime.timedelta(seconds=difference))
	embed = discord.Embed(title="Servers:", description=f"{str(len(servers))}", color=0xFFFF)
	embed.add_field(name="Users:", value=f"{str(len(set(client.get_all_members())))}")
	embed.add_field(name="Uptime:", value=f"{text}")
	await client.say(embed=embed)
	
@client.command(pass_context=True)
async def support(ctx):
	user = ctx.message.author
	servers = list(client.servers)
	embed = discord.Embed(color=user.colour)
	embed.add_field(name="Support server", value=f"[Link](https://discord.gg/Eagbjbj)")
	embed.set_thumbnail(url="https://cdn.discordapp.com/icons/455508238784266263/689f34285d678398783054b161168bd5.jpg")
	await client.say(embed=embed)
	

	
@client.command()
async def invite():
  	"""Bot Invite"""
  	await client.say("📧Check DMs For Information✅")
  	await client.whisper("Add me with this link {}".format(discord.utils.oauth_url(client.user.id)))	
	
	
	
@client.command(pass_context=True)
async def help(ctx):
	user = ctx.message.author
	embed = discord.Embed(colour=user.colour)
	embed.add_field(name="Music commands:", value="m.play | m.join | m.leave | m.pause | m.resume | m.skip | m.queue", inline=True)
	embed.add_field(name="Credits:", value="m.credits")
	embed.add_field(name="Other commands:", value="m.ping | m.support | m.stats | m.invite")
	await client.say(embed=embed)

@client.command(no_pm=True)
async def credits():
	"""credits who helped me"""
	await client.say('Imran helped me with this music bot')
	
def user_is_me(ctx):
	return ctx.message.author.id == "455500545587675156"

@client.command(name='eval', pass_context=True)
@commands.check(user_is_me)
async def _eval(ctx, *, command):
    res = eval(command)
    if inspect.isawaitable(res):
        await client.say(await res)
    else:
    	await client.delete_message(ctx.message)
    	await client.say(res)
        
@_eval.error
async def eval_error(error, ctx):
	if isinstance(error, discord.ext.commands.errors.CheckFailure):
		text = "Sorry {}, You can't use this command only the bot owner can do this.".format(ctx.message.author.mention)
		await client.send_message(ctx.message.channel, text)
		
client.loop.create_task(audio_player_task())
client.run(os.environ['BOT_TOKEN'])
