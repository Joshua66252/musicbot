from disnake.ext import commands
from pedalboard import Pedalboard, Reverb, Compressor, PitchShift, Resample
from pedalboard.io import AudioFile
import time,pathlib,random,sys,os,disnake,pydub,requests
random.seed(time.time())
os.system("title Music bot")
botPrefix = "]["
_status = pathlib.Path('botFiles/statusBot').read_text()
validFiles = [".wma",".m4a",".mp3",".ogg",".wav",".flac"]
songPath = pathlib.Path(pathlib.Path('botFiles/musicBotMusicPath').read_text())
command_sync_flags = commands.CommandSyncFlags.all()
intents = disnake.Intents.all()
bot = commands.Bot(command_prefix=botPrefix,intents=intents,command_sync_flags=command_sync_flags)
@bot.event
async def on_ready():
	print(f"Logged in - {bot.user}")
	await bot.change_presence(status=disnake.Status.online, activity=disnake.Game(_status))
bot.remove_command('help')
async def playSong(songName,speed,interaction,alvin,reverb):
	voice = interaction.user.voice
	validSongList = [path.stem.lower() for path in songPath.iterdir() if path.suffix in validFiles]
	songListPlr = [path for path in songPath.iterdir() if path.suffix in validFiles]
	if songName.lower() in validSongList:
		song = songListPlr[validSongList.index(songName.lower())]
		vc = interaction.guild.voice_client
		if not vc:
			vc = await voice.channel.connect()
		if not vc.channel == voice.channel:
			await vc.move_to(voice.channel)
		if vc.is_playing():
			vc.stop()
		args = ""
		reverse = False
		if speed<0:
			speed = speed*-1
			reverse = True
		if speed<0.5:
			speed = 0.5
		if not alvin:
			args+=f'-af "atempo={speed}"'
			if reverse:
				args+=",areverse"
		else:
			args+='-af "atempo=1.25,asetrate=44100*2,aresample=44100"'
		if reverb:
			songNameFile = str(song).split("\\")
			songNameFile = songNameFile[len(songNameFile)-1]
			fileReverb = pathlib.Path(f'./botFiles/musicReverbed/{songNameFile}')
			if fileReverb.is_file():
				song = f'./botFiles/musicReverbed/{songNameFile}'
			else:
				board = Pedalboard([Reverb(room_size=0.5)])
				with AudioFile(str(song)) as f:
					with AudioFile(f'./botFiles/musicReverbed/{songNameFile}', 'w', f.samplerate, f.num_channels) as o:
						while f.tell() < f.frames:
							chunk = f.read(int(f.samplerate))
							effected = board(chunk, f.samplerate, reset=False)
							o.write(effected)
				song = f'./botFiles/musicReverbed/{songNameFile}'
		vc.play(disnake.FFmpegPCMAudio(song,options=args))
		return True
@bot.command(brief='Restarts the bot which updates the code')
async def updatecode(ctx):
	if not ctx.author.id == 904086010462343248: return
	await ctx.channel.send("Restarting")
	os.startfile(sys.argv[0])
	sys.exit()
@bot.command(brief=f'Changes the bot status ({botPrefix}changestatus "STATUS")')
async def changestatus(ctx,statusCmd):
	if not ctx.author.id == 904086010462343248 or not statusCmd: return
	with open("botFiles/statusBot", "w", encoding="utf-8") as file:
		file.write(statusCmd)
	await bot.change_presence(status=disnake.Status.online, activity=disnake.Game(statusCmd))
@bot.slash_command(description="Joins voice channel")
async def join(interaction):
	voice = interaction.user.voice
	if voice:
		await voice.channel.connect()
		await interaction.response.send_message("Bot joined vc")
	else:
		await interaction.response.send_message("You are not in a vc")
@bot.slash_command(description="Leaves voice channel")
async def leave(interaction):
	vc = interaction.guild.voice_client
	if vc:
		await vc.disconnect()
		await interaction.response.send_message("Bot left vc")
	else:
		await interaction.response.send_message("Bot is not in a vc")
@bot.slash_command(description="Plays a song")
async def play(interaction,song:str="random",speed:float=1,alvinized:bool=False,reverb:bool=False):
	if alvinized == True or speed == 0:
		speed = 1
	if song == "random":
		songList = [path.stem for path in songPath.iterdir() if path.suffix in validFiles]
		song = random.choice(songList)
	await interaction.response.send_message("Please wait")
	textToSend = f"Bot playing `{song}`"
	play = await playSong(song,speed,interaction,alvinized,reverb)
	if speed != 1:
		if speed <= 0.5:
			textToSend+=" `0.5x (Lowest possible with FFmpeg >:( )`"
		else:
			textToSend+=f" `{speed}x`"
	elif alvinized == True:
		textToSend+=" alvinized"
	if reverb:
		textToSend+=" with reverb"
	if play:
		await interaction.edit_original_response(textToSend)
	else:
		await interaction.edit_original_response("Invalid song")
@bot.slash_command(description="Stops playing song")
async def stop(interaction):
	vc = interaction.guild.voice_client
	if vc and vc.is_playing():
		await interaction.response.send_message("The bot will stop the current song.")
		vc.stop()
	else:
		await interaction.response.send_message("The bot is not in a vc or the bot is not playing anything")
@bot.slash_command(description="Lists songs")
async def list(interaction):
	await interaction.response.send_message("### **Song list: [eggland.space](http://eggland.space:4000/)**")
@bot.slash_command(description="Provides a bot invite link")
async def invite(interaction):
	await interaction.response.send_message("https://discord.com/api/oauth2/authorize?client_id="+str(bot.application_id)+"&permissions=8&scope=bot")
@bot.slash_command(description="Insults you")
async def insult(interaction):
	response0 = requests.get("https://evilinsult.com/generate_insult.php")
	await interaction.response.send_message(f"# {str(response0.content)[2:-1]}")
bot.run(pathlib.Path('botFiles/token').read_text())