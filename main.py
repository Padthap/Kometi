import discord, json, random, urllib.request, os, asyncio, aiohttp, datetime
from discord.ext import commands
from webserver import keep_alive


bot = commands.Bot(command_prefix=commands.when_mentioned_or('.')) 
bot.remove_command("help")
cogs = ["events.on_message",
        "events.music"]      
bot.snipes = {}
headers = {
  'Authorization': os.getenv("token")
}

@bot.event
async def on_ready():
	print(f"The {bot.user} is ready!")
	for cog in cogs:
		try:
			bot.load_extension(cog)
			print(f"{cog} was loaded.")
		except Exception as e:
			print(e)


@bot.event
async def on_command_error(ctx, error):
	if isinstance(error, commands.CheckFailure):
		embed = discord.Embed(title="❌ You Don\'t Have The Permission To Use That Command!", color=discord.Color.red())
		await ctx.send(embed=embed)
	elif isinstance(error, commands.MissingRequiredArgument):
		embed = discord.Embed(title="❌ You Did Not Gave All Required Arguments.", color=discord.Color.red())
		await ctx.send(embed=embed)
	elif isinstance(error, commands.BadArgument):
		embed = discord.Embed(title="❌ Give The Values Properly.", color=discord.Color.red())
		await ctx.send(embed=embed)
    


@bot.event
async def on_message_delete(message):
  bot.snipes[message.channel.id] = message

@bot.command()  
async def snipe(ctx, *, channel: discord.TextChannel = None):
  channel = channel or ctx.channel
  try:
    msg = bot.snipes[channel.id]
  except KeyError:
    return await ctx.send('Nothing to snipe!')
  # one liner, dont complain
  await ctx.send(embed=discord.Embed(description=f"`{msg.content}`", color=random.randint(0, 0xffffff)).set_author(name=str(msg.author), icon_url=str(msg.author.avatar_url)))
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    embed = discord.Embed(
        title=f"{member} has been banned.", colour=random.randint(0, 0xffffff))
    embed.add_field(name="Reason:", value=f"{reason}", inline=False)
    embed.add_field(name="Banned by:", value=f"{ctx.author}", inline=False)
    await ctx.send(embed=embed)
    # await member.create_dm()
    # await member.dm_channel.send(f"You have been banned from {ctx.guild}, by {ctx.author}")

@bot.command()
async def mute(ctx, member: discord.Member, *, reason=None):
    role_muted = discord.utils.get(ctx.guild.roles, name='Mute')
    await member.add_roles(role_muted)
    embed=discord.Embed(title=f"{member} has been muted.", colour=random.randint(0, 0xffffff))
    embed.add_field(name="Reason:", value=f"{reason}", inline=False)
    embed.add_field(name="Muted by:", value=f"{ctx.author}", inline=False)
    await ctx.send(embed=embed)
    await member.create_dm()
    await member.dm_channel.send(f"You have been muted in {ctx.guild}, by {ctx.author}")
@bot.command()
async def unmute(ctx, member: discord.Member):
    mutedRole = discord.utils.get(ctx.guild.roles, name="Muted")
 
    await member.remove_roles(mutedRole)
    embed=discord.Embed(title=f"{member} has been muted", colour=random.randint(0, 0xffffff))
    embed.add_field(name="Unmute by:", value=f"{ctx.author}", inline=False)
    await ctx.send(embed=embed)
    await member.create_dm()
    await member.dm_channel.send(f"You have been unmuted in {ctx.guild}, by {ctx.author} you can now caat there")

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    embed = discord.Embed(
        title=f"{member} has been kicked.", colour=random.randint(0, 0xffffff))
    embed.add_field(name="Reason", value=f"{reason}", inline=False)
    embed.add_field(name="Kicked by", value=f"{ctx.author}", inline=False)
    await ctx.channel.send(embed=embed)

@bot.command()
@commands.has_permissions(kick_members=True)
async def warn(ctx, member: discord.Member, *, reason=None):
    embed = discord.Embed(
        title=f"{member} has been warned.", colour=random.randint(0, 0xffffff))
    embed.add_field(name="Reason:", value=f"{reason}", inline=False)
    embed.add_field(name="Warn by:", value=f"{ctx.author}", inline=False)
    embed.set_footer(text=f"Requested by:{ctx.author.display_name}") 
    await ctx.channel.send(embed=embed)
    await member.create_dm()
    await member.dm_channel.send(f"You have been warned in {ctx.guild} for {reason}, by {ctx.author}")

@bot.command(aliases=['clear', 'delete'])
@commands.has_guild_permissions(manage_messages=True)
async def purge(ctx, amount=5):
    await ctx.message.delete()
    await ctx.channel.purge(limit=amount)
    await ctx.send(f"***{amount} Message(s) has been deleted!***", delete_after=5)
@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, member):
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split('#')
    for ban_entry in banned_users:
        user = ban_entry.user
        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            embed = discord.Embed(
                title=f"{user} has been Unbanned",
                colour=random.randint(0, 0xffffff))
            embed.add_footer(f'Requested by {ctx.author.name}', url=ctx.author.avatar_url)
            await ctx.channel.send(embed=embed)
            await ctx.send(f"{user} be like:-\nhttps://tenor.com/view/unbanned-gif-18044894")
@bot.command() 
@commands.has_permissions(manage_channels=True)
async def nuke(ctx, channel: discord.TextChannel = None):
    if channel == None: 
        nuke_channel = ctx.channel
        new_channel = await nuke_channel.clone(reason="Has been Nuked!")
        await nuke_channel.delete()
        await new_channel.send("<:panda:814763561141665822> Nuked this channel.\n https://i.ibb.co/vQNwM9S/nuked-min.gif !")
        await ctx.send("Nuked the Channel sucessfully!")
 
    nuke_channel = discord.utils.get(ctx.guild.channels, name=channel.name)
 
    if nuke_channel is not None:
        new_channel = await nuke_channel.clone(reason="Has been Nuked!")
        await nuke_channel.delete()
        await new_channel.send("<:panda:814763561141665822> Nuked this channel.\n https://i.ibb.co/vQNwM9S/nuked-min.gif !")
        await ctx.send("Nuked the Channel sucessfully!")
"""Meme Command"""
@bot.command()
async def meme(ctx):
  
  url = "https://meme-api.herokuapp.com/gimme/dankmemes"
 
  response = urllib.request.urlopen(url)
  data = json.loads(response.read())
  img_title = data['title']
  img_url = data['url']
  embed = discord.Embed(title=img_title
  ,url=img_url,color=random.randint(0, 0xffffff))
  embed.set_image(url=img_url)
  await ctx.send(embed=embed)
  
"""Joke Command"""
@bot.command()
async def joke(ctx):
  url = "https://official-joke-api.appspot.com/random_joke"
  response = urllib.request.urlopen(url) 
  data = json.loads(response.read())
  punchline = data['punchline']
  text = data['setup']
  embed = discord.Embed(title=f"Joke 😂😂\n{text}",description=f"{punchline}",color=random.randint(0, 0xffffff))
  await ctx.send(embed=embed)
  
"""Coinflip command"""
@bot.command()
async def coinflip(ctx,arg1):
	arg1 = arg1.lower()
	results = random.choice(["heads","tails"])
	results = results.lower()
	if arg1 not in ["heads","tails"]:
		 await ctx.send("choose between heads or tails only.")
	elif arg1 != results:
		msg = await ctx.send("Flipping the coin.")
		await asyncio.sleep(1)
		await msg.edit(content="Flipping the coin..")
		await asyncio.sleep(1)
		await msg.edit(content="Flipping the coin...")
		await asyncio.sleep(2)
		await msg.edit(content=f"And its {results}!")
		await asyncio.sleep(1)
		await msg.edit(content=f"And its {results}!\nYou chose {arg1}.\nYou Lost. :(")
	elif arg1 == results:
		msg = await ctx.send("Flipping the coin.")
		await asyncio.sleep(1)
		await msg.edit(content="Flipping the coin..")
		await asyncio.sleep(1)
		await msg.edit(content="Flipping the coin...")
		await asyncio.sleep(2)
		await msg.edit(content=f"And its {arg1}!")
		await asyncio.sleep(1)
		await msg.edit(content=f"And its {arg1}!\n\nYou Won! :)")

"""Cat Command"""
@bot.command()
async def cat(ctx):
	url = "https://api.thecatapi.com/v1/images/search"
	response = urllib.request.urlopen(url)
	data = json.loads(response.read())
	img_url = data[0]['url']
	embed = discord.Embed(title="Meow Meow 🐱",url=img_url,color=random.randint(0, 0xffffff))
	embed.set_image(url=img_url)
	await ctx.send(embed=embed)

"""Dog Command"""
@bot.command()
async def dog(ctx):
	url = "https://api.thedogapi.com/v1/images/search"
	response = urllib.request.urlopen(url)
	data = json.loads(response.read())
	img_url = data[0]['url']
	embed = discord.Embed(title="bhow bhow 🐶", url=img_url,color=random.randint(0, 0xffffff))
	embed.set_image(url=img_url)
	await ctx.send(embed=embed)
@bot.command()
async def bal(ctx, member:discord.Member=None):
  if member==None:
    await open_account(ctx.author)
    users = await get_bank_data()
    user=ctx.author
    wallet_amt = users[str(user.id)]["wallet"]
    bank_amt = users[str(user.id)]["bank"]
    embed=discord.Embed(title=f"{user.name}\'s balance:", colour=discord.Color.green())
    embed.add_field(name="Wallet:", value=wallet_amt, inline=False)
    embed.add_field(name="Bank:", value=bank_amt, inline=False)
    await ctx.send(embed=embed)
  else:
    await open_account(member)
    users = await get_bank_data()
    user=member
    wallet_amt = users[str(user.id)]["wallet"]
    bank_amt = users[str(user.id)]["bank"]
    embed=discord.Embed(title=f"{user.name}\'s balance:", colour=discord.Color.green())
    embed.add_field(name="Wallet:", value=wallet_amt, inline=False)
    embed.add_field(name="Bank:", value=bank_amt, inline=False)
    await ctx.send(embed=embed)


@bot.command()
async def withdraw(ctx, amount=None):
  await  open_account(ctx.author)
  if amount==None:
    await ctx.send("Beep boop!, Enter amount to withdraw")
    return
  bal=await update_bank(ctx.author)
  amount=int(amount)
  if amount>bal[1]:
    await ctx.send("You don't have that much money!")
    return
  if amount<0:
    await ctx.send("Amount must be positive!")
    return
  await update_bank(ctx.author, amount)
  await update_bank(ctx.author,-1*amount,"bank")
  await ctx.send(f"you withdrew ${amount}")

@bot.command()
async def dep(ctx, amount=None):
  await open_account(ctx.author)
  if amount==None:
    await ctx.send("Beep boop!, Enter amount to dep")
    return
  bal=await update_bank(ctx.author)
  amount=int(amount)
  if amount>bal[0]:
    await ctx.send("You don't have that much money!")
    return
  if amount<0:
    await ctx.send("Amount must be positive!")
    return
  await update_bank(ctx.author,-1*amount)
  await update_bank(ctx.author,amount,"bank")
  await ctx.send(f"you diposited ${amount}")

@bot.command()
async def pay(ctx, member:discord.Member, amount=None):
  await open_account(ctx.author)
  await open_account(member)
  if amount==None:
    await ctx.send("Beep boop!, Enter amount to send\nthe formate is -send <member> <amount> ")
    return
  bal=await update_bank(ctx.author)
  amount=int(amount)
  if amount>bal[0]:
    await ctx.send("You don't have that much money!")
    return
  if amount<0:
    await ctx.send("Amount must be positive!")
    return
  await update_bank(ctx.author,-1*amount,"wallet")
  await update_bank(member,amount,"bank")
  await ctx.send(f"you gave ${amount} to {member}")

async def open_account(user):
  with open("bank.json","r") as f:
    users = await get_bank_data()

  if str(user.id) in users:
      return False
  else:
      users[str(user.id)] = {}
      users[str(user.id)]["wallet"] = 0
      users[str(user.id)]["bank"] = 0

  with open("bank.json", "w") as f:
      json.dump(users, f)
  return True

async def get_bank_data():
    with open("bank.json", "r") as f:
        users = json.load(f)
    return users

async def update_bank(user, change=0, mode="wallet"):
  users = await get_bank_data()
  users[str(user.id)][mode] += change
  with open("bank.json", "w") as f:
    json.dump(users, f)
    bala=[users[str(user.id)]["wallet"],users[str(user.id)]["bank"]]
  return bala


@bot.command()
@commands.cooldown(1, 30, commands.BucketType.user) 
async def beg(ctx):

    await open_account(ctx.author)
    users = await get_bank_data()
    user = ctx.author
    earnings = random.randrange(100)

    await ctx.send(f"Someone has donated ${earnings}")

    users[str(user.id)]["wallet"] += earnings
    
    with open("bank.json", "w") as f:
      json.dump(users, f)
    
@beg.error
async def beg_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        msg = 'This command is ratelimited, please try again in {:.0f}s'.format(error.retry_after)
        await ctx.send(msg)
    else:
        raise error

@bot.command(pass_context=True)
@commands.cooldown(1, 320, commands.BucketType.user) 
async def rob(ctx,member: discord.Member):
    await open_account(ctx.author)
    await open_account(member)
   
    bal = await update_bank(member)

    

    if bal[0]<100:
        await ctx.send("It's not worth it")
        return

    earnings = random.randrange(0, 99)
  

    await update_bank(ctx.author,earnings)
    await update_bank(member,-1*earnings)

    await ctx.send(f"you robbed and got {earnings} coins!")

@rob.error
async def rob_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        msg = 'This command is ratelimited, please try again in {:.0f}s'.format(error.retry_after)
        await ctx.send(msg)
    else:
        raise error

helpforuc=discord.Embed(title="Useful Commands",description="<> : required\n[] : optional\n**avatar [@member]** : shows your/member\'s avatar\n**serverinfo** : gives you info of any server\n**userinfo [@member]** : gives user\'s info",color=random.randint(0,0xffffff))
helpforeco = discord.Embed(title="economy Commands",description="<> : required\n[] : optional\n**bal** : shows your balance\n**beg** : gives your random money\n**pay** <member> <amount>: gives amount mentioned to the member\n**dep** <amount> : diposits amout mentioned in bank\n**withdraw** <amount> : withdraws amout mentioned in wallet",color=random.randint(0,0xffffff))
helpforuti = discord.Embed(title="utility Commands",description="**info** : Info about developer and bot\n**website** : gives you kometi\'s website link\n**invite** : sends bot\'s invite link and help server\'s link",color=random.randint(0,0xffffff))
helpforeco = discord.Embed(title="economy Commands",description="<> : required\n[] : optional\n**bal** : shows your balance\n**beg** : gives your random money\n**pay** <member> <amount>: gives amount mentioned to the member\n**dep** <amount> : diposits amout mentioned in bank\n**withdraw** <amount> : withdraws amout mentioned in wallet",color=random.randint(0,0xffffff))
helpformsg = discord.Embed(title="Messages Related Commands",description="All Fields are required\n**purge** <amount> : purges the chat\n**nuke** <#channel> : nukes a channel",color=random.randint(0,0xffffff))
helpfornsfw = discord.Embed(title="NSFW Related Commands",description="All Fields are required\n**porn** : Sends random porn gif\n**hentai** : Sends random hentai image\n**pussy** : Sends random pussy image\n**4k** : Sends random 4k image\n**ass** : Sends random ass image\n**boobs** : Sends random boobs image",color=random.randint(0,0xffffff))
helpfornsfw.set_footer(text="api used: https://nekobot.xyz/api/")
helpforfun = discord.Embed(title="Fun Commands",description="All Fields are required\n**meme** : shows a random meme\n**joke** : shows a random joke\n**dog** : shows a random dog pic\n**cat** : shows a random cat pic\n**coinflip** <heads/tails> : heads or tails game",color=random.randint(0,0xffffff))
helpforga = discord.Embed(title="Giveaway Commands",description="All Fields are required\n**gstart <mins> <prize>** : starts giveaway\n**giveaway ||give answer of all ques||** : starts giveaway in mentioned channel\n**reroll** : rerolls giveaway winner",color=random.randint(0,0xffffff))
helpformusic = discord.Embed(title="Music Commands",description="<> : required\n[] : optional\n**summon** [#channel] : makes the bot join a vc\n**leave** : makes the bot leave the joined vc\n**play** <song/url> : plays the given song\n**pause** : pauses the current song\n**resume** : resumes the paused song\n**stop** : stops the current playing song\n**skip** skips the current song\n**queue** : shows the current queue\n**shuffle** : shuffles the queue\n**now** : shows the current playing song\n**remove** : remove a song from the queue\n**loop** : loops the current song",color=random.randint(0,0xffffff))
helpformod = discord.Embed(title="Moderation Commands",description="<> : required\n[] : optional\n**kick** <@member> [reason] : kicks a member\n**ban** <@member> [reason] : bans a member\n**unban** <user#tag> : unbans a user\nlock [channel] : makes normal perms people unable to send message in mentioned channel lock [channel] : unlocks locked channel",color=random.randint(0,0xffffff))
emfornor=discord.Embed(title="kometi\'s commands", description="here are the catageory for kometi\'s commands", colour=random.randrange(0, 0xffffff))
emfornor.add_field(name="Messages💬", value="commands related to message")
emfornor.add_field(name="Moderation‼️", value="commands related to moderation")
emfornor.add_field(name="Music🎵", value="commands related to music")
emfornor.add_field(name="Economy💸", value="commands related to economy")
emfornor.add_field(name="Fun😁", value="commands related to fun")
emfornor.add_field(name="giveaway🎉", value="commands related to giveaway")
emfornor.add_field(name="utility👷", value="commands related to utility")
emfornor.add_field(name="NSFW🔞", value="command related to NSFW")
emfornor.add_field(name="Useful commands🧭", value="Some useful commands .help commands for more help")
emfornor.set_footer(text="for more indept help try .help {catageory}")
@bot.command()
async def help(ctx, arg1=None):
  if ctx.channel.is_nsfw():
    if arg1==None:
      emfornor.set_thumbnail(url=ctx.author.avatar_url)
      await ctx.send(embed=emfornor)
    elif arg1=="moderation":
      await ctx.send(embed=helpformod)
    elif arg1=="music":
      await ctx.send(embed=helpformusic)
    elif arg1=="fun":
      await ctx.send(embed=helpforfun)
    elif arg1=="message":
      await ctx.send(embed=helpformsg)
    elif arg1=="economy":
      await ctx.send(embed=helpforeco)
    elif arg1=="utility":
      await ctx.send(embed=helpforuti)
    elif arg1=="giveaway":
      await ctx.send(embed=helpforga)
    elif arg1=="nsfw":
      await ctx.send(embed=helpfornsfw)
    elif arg1=="commands":
      await ctx.send(embed=helpforuc)
    else:
      await ctx.send(f"you better use `fun`, `music`, `moderation`,`utility`,`economy`, `giveaway` or `message`, `commands` for useful commands in place of `{arg1}` and you can also use `nsfw` but in nsfw channel like this.")
  else:
    if arg1==None:
      emfornor.set_thumbnail(url=ctx.author.avatar_url)
      await ctx.send(embed=emfornor)
    elif arg1=="moderation":
      await ctx.send(embed=helpformod)
    elif arg1=="music":
      await ctx.send(embed=helpformusic)
    elif arg1=="fun":
      await ctx.send(embed=helpforfun)
    elif arg1=="message":
      await ctx.send(embed=helpformsg)
    elif arg1=="economy":
      await ctx.send(embed=helpforeco)
    elif arg1=="giveaway":
      await ctx.send(embed=helpforga)
    elif arg1=="utility":
      await ctx.send(embed=helpforuti)
    elif arg1=="commands":
      await ctx.send(embed=helpforuc)
    else:
      await ctx.send(f"you better use `fun`, `music`, `moderation`,`utility`,`economy` or `message`, `commands` for useful commands in place of  in place of `{arg1}` and you can also use `nsfw` but in nsfw channel")
 
@bot.command(aliases=["server"])
async def serverinfo(ctx):

  embed = discord.Embed(
      title=f"{ctx.guild.name}\'s Server Information",
      color=random.randint(0, 0xffffff)
    )
  embed.set_thumbnail(url=ctx.guild.icon_url)
  embed.add_field(name="Server ID", value=f"{ctx.guild.id}", inline=False)
  embed.add_field(name="Region", value=f"{ctx.guild.region}", inline=False)
  embed.add_field(name="Member Count", value=f"{ctx.guild.member_count}", inline=False)

  await ctx.send(embed=embed)


@bot.command(aliases=["ava"])
async def avatar(ctx, member: discord.Member = None):
  if member==None:
    embed = discord.Embed(colour=random.randint(0, 0xffffff),timestamp=ctx.message.created_at, title=f"{ctx.author.name}\'s Avatar") 
    embed.set_image(url=ctx.author.avatar_url)
    await ctx.send(embed=embed)
  else:
    embed = discord.Embed(colour=random.randint(0, 0xffffff),timestamp=ctx.message.created_at, title=f"{member.name}\'s avatar") 
    embed.set_image(url=member.avatar_url)
    await ctx.send(embed=embed)

@bot.command(aliases=["whois"])
async def userinfo(ctx, member: discord.Member = None):
    if not member:  # if member is no mentioned
        member = ctx.message.author  # set member as the author
    roles = [role for role in member.roles]
    embed = discord.Embed(colour=random.randint(0, 0xffffff), timestamp=ctx.message.created_at,
                          title=f"User Info - {member}")
    embed.set_thumbnail(url=member.avatar_url)
    embed.set_footer(text=f"Requested by {ctx.author}")

    embed.add_field(name="ID:", value=member.id, inline=False)
    embed.add_field(name="Name:", value=member.name, inline=False)
    embed.add_field(name="Name in server:", value=member.display_name, inline=False)

    embed.add_field(name="Created Account On:", value=member.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"), inline=False)
    embed.add_field(name="Joined Server On:", value=member.joined_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"), inline=False)
   
    embed.add_field(name="Roles:", value=" ".join([role.mention for role in roles]), inline=False)
    embed.add_field(name="Highest Role:", value=member.top_role.mention, inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def pussy(ctx): 
  if ctx.channel.is_nsfw():
    async with aiohttp.ClientSession() as cs:
      async with cs.get('https://nekobot.xyz/api/image?type=pussy') as r:
        res = await r.json()  # returns dict
        url=res['message']
        em=discord.Embed(title="Pussy", colour=random.randint(0, 0xffffff))
        em.set_image(url=url)
        em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=em)
  else:
    await ctx.send("`not in nsfw channel.` :angry: ")
@bot.command()
async def hentai(ctx): 
  if ctx.channel.is_nsfw():
    async with aiohttp.ClientSession() as cs:
      async with cs.get('https://nekobot.xyz/api/image?type=hentai') as r:
        res = await r.json()  # returns dict
        url=res['message']
        em=discord.Embed(title="Hentai💦", colour=random.randint(0, 0xffffff))
        em.set_image(url=url)
        em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=em)
  else:
    await ctx.send("`not in nsfw channel.` :angry: ")
@bot.command()
async def ass(ctx): 
  if ctx.channel.is_nsfw():
    async with aiohttp.ClientSession() as cs:
      async with cs.get('https://nekobot.xyz/api/image?type=ass') as r:
        res = await r.json()  # returns dict
        url=res['message']
        em=discord.Embed(title="Ass🍑", colour=random.randint(0, 0xffffff))
        em.set_image(url=url)
        em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=em)
  else:
    await ctx.send("`not in nsfw channel.` :angry: ")
@bot.command()
async def porn(ctx): 
  if ctx.channel.is_nsfw():
    async with aiohttp.ClientSession() as cs:
      async with cs.get('https://nekobot.xyz/api/image?type=pgif') as r:
        res = await r.json()  # returns dict
        url=res['message']
        em=discord.Embed(title="Porn gif⬇️", colour=random.randint(0, 0xffffff))
        em.set_image(url=url)
        em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=em)
  else:
    await ctx.send("`not in nsfw channel.` :angry: ")
@bot.command(aliases=['4k'])
async def _4k(ctx): 
  if ctx.channel.is_nsfw():
    async with aiohttp.ClientSession() as cs:
      async with cs.get('https://nekobot.xyz/api/image?type=4k') as r:
        res = await r.json()  # returns dict
        url=res['message']
        em=discord.Embed(title="4k💦", colour=random.randint(0, 0xffffff))
        em.set_image(url=url)
        em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=em)
  else:
    await ctx.send("`not in nsfw channel.` :angry: ")



@bot.command()
async def boobs(ctx): 
  if ctx.channel.is_nsfw():
    async with aiohttp.ClientSession() as cs:
      async with cs.get('https://nekobot.xyz/api/image?type=boobs') as r:
        res = await r.json()  # returns dict
        url=res['message']
        em=discord.Embed(title="Oh boobs", colour=random.randint(0, 0xffffff))
        em.set_image(url=url)
        em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=em)
  else:
    await ctx.send("`not in nsfw channel.` :angry: ")

@bot.command()
async def nsfw(ctx):
  await ctx.send("Bro use `help nsfw` for help for nsfw or commands for nsfw ||in nsfw channel only||")

@bot.command()
async def invite(ctx):
    embed = discord.Embed(description="**Hey, looks like you are interested in adding me!**", colour=0x7289da)
    embed.set_author(name=bot.user.name, icon_url=bot.user.avatar_url)
    embed.add_field(name="Need Support?", value="[`Join my support server`](https://discord.gg/tdEkWra6ph)", inline=False)
    embed.add_field(name="Wanna invite me?", value=f"[`Invite me!`](https://discord.com/oauth2/authorize?client_id={bot.user.id}&scope=bot&permissions=8)", inline=False)
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(view_audit_log=True)
async def gstart(ctx, mins : int, * , prize: str):
    embed = discord.Embed(title = "Giveaway!", description = f"{prize}", color = ctx.author.color)

    end = datetime.datetime.utcnow() + datetime.timedelta(seconds = mins*60) 

    embed.add_field(name = "Ends At:", value = f"{end} UTC")
    embed.set_footer(text = f"Ends {mins} mintues from now!")

    my_msg = await ctx.send(embed = embed)


    await my_msg.add_reaction("🎉")


    await asyncio.sleep(mins*60)


    new_msg = await ctx.channel.fetch_message(my_msg.id)


    users = await new_msg.reactions[0].users().flatten()
    users.pop(users.index(bot.user))

    winner = random.choice(users)

    await ctx.send(f"Congratulations! {winner.mention} won {prize}!")

def convert(time):
    pos = ["s","m","h","d"]

    time_dict = {"s" : 1, "m" : 60, "h" : 3600 , "d" : 3600*24}

    unit = time[-1]

    if unit not in pos:
        return -1
    try:
        val = int(time[:-1])
    except:
        return -2


    return val * time_dict[unit]

@bot.command()
@commands.has_permissions(view_audit_log=True)
async def giveaway(ctx):
    await ctx.send("Let's start with this giveaway! Answer these questions within 15 seconds!")

    questions = ["Which channel should it be hosted in?", 
                "What should be the duration of the giveaway? (s|m|h|d)",
                "What is the prize of the giveaway?"]

    answers = []

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel 

    for i in questions:
        await ctx.send(i)

        try:
            msg = await bot.wait_for('message', timeout=15.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send('You didn\'t answer in time, please be quicker next time!')
            return
        else:
            answers.append(msg.content)
        try:
          c_id = int(answers[0][2:-1])
        except:
          await ctx.send(f"You didn't mention a channel properly. Do it like this {ctx.channel.mention} next time.")
          return

    channel = bot.get_channel(c_id)

    time = convert(answers[1])
    if time == -1:
        await ctx.send("You didn't answer the time with a proper unit. Use (s|m|h|d) next time!")
        return
    elif time == -2:
        await ctx.send("The time must be an integer. Please enter an integer next time")
        return            

    prize = answers[2]

    await ctx.send(f"The Giveaway will be in {channel.mention} and will last {answers[1]}!")


    embed = discord.Embed(title = "Giveaway!", description = f"{prize}", color = ctx.author.color)

    embed.add_field(name = "Hosted by:", value = ctx.author.mention)

    embed.set_footer(text = f"Ends {answers[1]} from now!")

    my_msg = await channel.send(embed = embed)
    await my_msg.add_reaction("🎉")


    await asyncio.sleep(time)


    new_msg = await channel.fetch_message(my_msg.id)


    users = await new_msg.reactions[0].users().flatten()
    users.pop(users.index(bot.user))

    winner = random.choice(users)

    await channel.send(f"Congratulations! {winner.mention} won {prize}!")

@bot.command()
@commands.has_permissions(view_audit_log=True)
async def reroll(ctx, channel : discord.TextChannel, id_ : int):
    try:
        new_msg = await channel.fetch_message(id_)
    except:
        await ctx.send("The id was entered incorrectly.")
        return
    
    users = await new_msg.reactions[0].users().flatten()
    users.pop(users.index(bot.user))

    winner = random.choice(users)

    await channel.send(f"Congratulations! The new winner is {winner.mention}.!")   

@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx, channel : discord.TextChannel=None):
    if channel == None: 
      channel = ctx.channel
      overwrite = channel.overwrites_for(ctx.guild.default_role)
      overwrite.send_messages = False
      await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
      await ctx.send('Channel locked.')
      await channel.send(f"This channel has been locked by {ctx.author. mention}")
    else:
      channel = channel or ctx.channel
      overwrite = channel.overwrites_for(ctx.guild.default_role)
      overwrite.send_messages = False
      await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
      await ctx.send('Channel locked.')
      await channel.send(f"This channel has been locked by {ctx.author. mention}")

@bot.command() 
@commands.has_permissions(manage_channels=True)
async def unlock(ctx, channel : discord.TextChannel=None):
  if channel == None: 
    channel = ctx.channel
    overwrite = channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = True
    await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    await ctx.send('Channel unlocked.')
    await channel.send(f"This channel has been locked by {ctx.author. mention}")

  else:
    channel = channel or ctx.channel
    overwrite = channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = True
    await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    await ctx.send('Channel unlocked.')
    await channel.send(f"This channel has been locked by {ctx.author. mention}")

@bot.command()
async def info(ctx):
  em=discord.Embed(description=f"```py\nOwner/Dev : Padthap#2028\nIDE : https://repl.it\nlanguage made on : Python 9.1\nPing : {round(bot.latency * 1000)} ms```")
  await ctx.send(embed=em)

@bot.command(aliases=['web'])
async def website(ctx):
  em = discord.Embed(tittle="kometi's website",colour=random.randint(0, 0xffffff))
  em.add_field(name="Kometi website", value="[Click here](https://website.padthap.repl.co/)", inline=False)
  await ctx.send(embed=em)

@bot.command()
async def wasted(ctx, member: discord.Member = None):
  if member==None:
    embed = discord.Embed(colour=random.randint(0, 0xffffff),timestamp=ctx.message.created_at, title=f"{ctx.author.name}\'s wasted avatar") 
    embed.set_image(url=f"https://some-random-api.ml/canvas/wasted?avatar=https://cdn.discordapp.com/avatars/{ctx.author.id}/{ctx.author.avatar}.png")
    await ctx.send(embed=embed)
  else:
    embed = discord.Embed(colour=random.randint(0, 0xffffff),timestamp=ctx.message.created_at, title=f"{member.name}\'s wasted avatar") 
    embed.set_image(url=f"https://some-random-api.ml/canvas/wasted?avatar=https://cdn.discordapp.com/avatars/{member.id}/{member.avatar}.png")
    await ctx.send(embed=embed)
    
@bot.command()
async def lyrics(ctx,*, arg):
    async with aiohttp.ClientSession() as cs:
      async with cs.get(f'https://some-random-api.ml/lyrics?title={arg}') as r:
        res = await r.json()  # returns dict
        title=res['title']
        decs=res['lyrics']
        em=discord.Embed(title=title, description=decs, colour=random.randint(0, 0xffffff))
        em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=em)
@bot.command()
async def bigemoji(ctx, emoji: discord.Emoji):
  await ctx.send(f"{emoji.url}?size=256")


bot.load_extension("jishaku")
keep_alive()

bot.run(os.getenv("TOKEN"))