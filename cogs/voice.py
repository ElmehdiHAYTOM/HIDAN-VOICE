import discord
import asyncio
from discord.ext import commands
import os
import pymongo


class voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.myclient = pymongo.MongoClient(os.environ["MONGO_URL"])
        self.db = self.myclient["voice"]

    def add(self,q,table):
        self.db[f"{table}"].insert_one(q)

    def delete(self,q,table):
        self.db[f"{table}"].delete_one(q)

    def update(self,q,nq,table):
        self.db[f"{table}"].update_one(q,{"$set":nq})


    def check(self,q,table):
        if self.db[table].find_one(q):
            return True
        else:
            return False



    def embed(self,member,msg,msgtype):
        color={
            "Error":0xE74C3C,
            "Success":0x2ECC71,

        }
        emojie={
            "Error":"❌",
            "Success":"✅",
        }

        
        embed = discord.Embed(
            description=emojie[msgtype]+" "+msg,
            color=color[msgtype],
            
        )
        embed.set_author(icon_url=member.avatar_url,name=member.name)
        
        #embed.add_field(name=emojie[msgtype],value=msg, inline=False)
        return embed


    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.errors.MemberNotFound):
            return  await ctx.send(embed=self.embed(ctx.author,"CAN'T FIND MEMBER","Error"))
        if isinstance(error,commands.errors.MissingRequiredArgument):
            return  await ctx.send(embed=self.embed(ctx.author,"Missing Required Argument : use .help","Error"))
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(embed=self.embed(ctx.author,f'This command is on cooldown, you can use it in {round(error.retry_after, 2)}',"Error"))
    

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        id = member.id
        guildID = member.guild.id
        voice=self.db["guild"].find_one({"guildID":guildID})
        if voice is None:
            pass
        else:
            voiceID = voice["voiceChannelID"]
            if after.channel:
                if after.channel.id == voiceID:
                    #cooldown=self.db["voiceChannel"].find_one({"userID":member.id})   to do : debug :)
                    #if cooldown is None:
                        
                    
                        voice=self.db["guild"].find_one({"guildID":guildID})["voiceCategoryID"]
                        setting =self.db["userSettings"].find_one({"userID":member.id})
                        guildSetting=self.db["guildSettings"].find_one({"guildID":guildID})
                        if setting is None:
                            name = f"{member.name}'s channel"
                            if guildSetting is None:
                                limit = 0
                            else:
                                limit = guildSetting["channelLimit"]
                        else:
                            if guildSetting is None:
                                name = setting["channelName"]
                                limit = setting["channelLimit"]
                            elif guildSetting is not None and setting["channelLimit"] == 0:
                                name = setting["channelName"]
                                limit = guildSetting["channelLimit"]
                            else:
                                name = setting["channelName"]
                                limit = setting["channelLimit"]
                        categoryID = voice
                        
                        category = self.bot.get_channel(categoryID)
                        channel2 = await member.guild.create_voice_channel(name,category=category)
                        channelID = channel2.id
                        await member.move_to(channel2)
                        await channel2.set_permissions(self.bot.user, connect=True,read_messages=True)
                        await channel2.edit(name= name, user_limit = limit,sync_permissions=1)
                        #await asyncio.sleep(1)
                        if not self.check({"userID":id},"voiceChannel"):
                            self.add({"userID":id,"voiceID":channelID},"voiceChannel")
                        else:
                            self.db["voiceChannel"].update_one({"userID":id,},{"$set":{"voiceID":channelID}})

                        def check(a,b,c):
                            return (len(channel2.members) == 0) and (len(channel2.voice_states) == 0)
                        #await asyncio.sleep(1)
                        await self.bot.wait_for('voice_state_update', check=check)
                        await channel2.delete()
                        
                    #else:  this for cooldown
                    
                        #await member.send(embed=self.embed(member,"Creating channels too quickly you've been put on a 15 second cooldown!","Error"))
                        #await asyncio.sleep(15) 
                        self.delete({"userID":id},"voiceChannel")









    @commands.group(aliases=["v"])
    async def voice(self, ctx):
        pass

    @voice.command()
    async def help(self, ctx):
        embed = discord.Embed(title="Help", description="",color=0x1ABC9C)
        embed.set_author(name=f"{ctx.guild.me.display_name}", icon_url=f"{ctx.guild.me.avatar_url}")

        embed.add_field(name=f'**Commands**', value=f'**Lock your channel by using the following command:**\n`.voice lock`\n\n'
                        f'**Unlock your channel by using the following command:**\n`.voice unlock`\n\n'
                        f'**Change your channel name by using the following command:**\n`.voice name <name>`\n**You can use this command only 2 times each 600 seconds**\n**Example:** `.voice name EU 5kd+`\n\n'
                        f'**Change your channel limit by using the following command:**\n`.voice limit number`\n**Example:** `.voice limit 2`\n\n'
                        f'**Give users permission to join by using the following command:**\n`.voice permit @person`\n**Example:** `.voice permit @HIDAN BOT#8888`\n\n'
                        f'**Claim ownership of channel once the owner has left:**\n`.voice claim`\n**Example:** `.voice claim`\n\n'
                        f'**Give ownership of channel to a member in the same voice:**\n`.voice transfer`\n**Example:** `.voice transfer @HIDAN BOT#8888`\n\n'

                        f'**Remove permission and the user from your channel using the following command:**\n`.voice reject @person`\n**Example:** `.voice reject @HIDAN BOT#8888`\n\n', inline='false')
        embed.set_footer(text='Bot developed by HIDAN BOT#8888')
        await ctx.channel.send(embed=embed)

    

    @voice.command()
    async def setup(self, ctx):
        guildID = ctx.guild.id
        id = ctx.author.id
        if ctx.author.id == ctx.guild.owner.id or ctx.author.id == 340096218707525645:
            def check(m):
                return m.author.id == ctx.author.id
            await ctx.channel.send(embed=self.embed(ctx.author,"**You have 60 seconds to answer each question!**","Success"))
            await ctx.channel.send(embed=self.embed(ctx.author,f"**Enter the name of the category you wish to create the channels in:(e.g Voice Channels)**","Success"))
            try:
                category = await self.bot.wait_for('message', check=check, timeout = 60.0)
            except asyncio.TimeoutError:
                await ctx.channel.send(embed=self.embed(ctx.author,'Took too long to answer!',"Error"))
            else:
                new_cat = await ctx.guild.create_category_channel(category.content)
                await ctx.channel.send(embed=self.embed(ctx.author,'**Enter the name of the voice channel: (e.g Join To Create)**',"Success"))
                try:
                    channel = await self.bot.wait_for('message', check=check, timeout = 60.0)
                except asyncio.TimeoutError:
                    await ctx.channel.send(embed=self.embed(ctx.author,'Took too long to answer!',"Error"))
                else:
                    await ctx.channel.send(embed=self.embed(ctx.author,f"**Enter server default role (id or enter \"everyone\")**","Success")) 
                    try:
                        default_role= await self.bot.wait_for('message', check=check, timeout = 60.0)

                    except asyncio.TimeoutError:
                        await ctx.channel.send(embed=self.embed(ctx.author,'Took too long to answer!',"Error"))
                    else:
                        default_role=default_role.content
                        if default_role == "everyone":
                            role = ctx.guild.default_role
                        else :
                            try:
                                role = ctx.guild.get_role(int(default_role))
                            except:
                                await ctx.channel.send(embed=self.embed(ctx.author,'Invalide role id!',"Error"))
                            else:
                                try:
                                    channel = await ctx.guild.create_voice_channel(channel.content, category=new_cat)
                                    voice=self.db["guild"].find_one({"guildID":guildID,"ownerID":id})
                                    if voice is None:
                                        self.add({"guildID":guildID,"ownerID":id,"voiceChannelID":channel.id,"voiceCategoryID":new_cat.id,"default_role":role},"guild")
                                    else:
                                        self.db["guild"].update_one({"guildID":guildID},{"$set":{"guildID":guildID,"ownerID":id,"voiceChannelID":channel.id,"voiceCategoryID":new_cat.id,"default_role":role.id}})
                                    await ctx.channel.send(embed=self.embed(ctx.author,"**You are all setup and ready to go!**\nYou can edit the permissions for the category and it's gonna sync to created rooms","Success"))
                                except:
                                    await ctx.channel.send(embed=self.embed(ctx.author,"You didn't enter the names properly.\nUse `.voice setup` again!","Error"))
        else:
            
            await ctx.channel.send(embed=self.embed(ctx.author,f"{ctx.author.mention} only the owner of the server can setup the bot!","Error"))
    @commands.command()
    async def setlimit(self, ctx, num):
        if num == None:
            raise commands.errors.MissingRequiredArgument
        if ctx.author.id == ctx.guild.owner.id or ctx.author.id == 340096218707525645:
            voice=self.db["guildSettings"].find_one({"guildID":ctx.guild.id})
            if voice is None:
                self.add({"guildID":ctx.guild.id,"channelName":f"'s channel","channelLimit":num},"guildSettings")
            else:
                self.db["guildSettings"].update_one({"guildID":ctx.guild.id},{"$set":{"channelLimit":num}})
            await ctx.send(embed=self.embed(ctx.author,"You have changed the default channel limit for your server!","Success"))
        else:
            await ctx.channel.send(embed=self.embed(ctx.author,f" only the owner of the server can setup the bot!","Error"))

    @setup.error
    async def info_error(self, ctx, error):
        print(error)

    @voice.command()
    async def lock(self, ctx):
        id = ctx.author.id
        voice=self.db["voiceChannel"].find_one({"userID":id})
        if voice is None:
            await ctx.channel.send(embed=self.embed(ctx.author,f"{ctx.author.mention} You don't own a channel.","Error"))
        else:
            if self.db["guild"].find_one({"guildID":ctx.guild.id}):
                role = self.db["guild"].find_one({"guildID":ctx.guild.id})["default_role"]
            else:
                return await ctx.send(embed=self.embed(ctx.author,"Bot not setted up!","Error"))
            role = ctx.guild.get_role(role)
            channelID = voice["voiceID"]
            channel = self.bot.get_channel(channelID)
            await channel.set_permissions(role, connect=False)
            await ctx.channel.send(embed=self.embed(ctx.author,f'{ctx.author.mention} Voice chat locked! 🔒',"Success"))

    @voice.command()
    async def transfer(self, ctx,member:discord.Member):
        if member == None:
            raise commands.errors.MissingRequiredArgument
        id = ctx.author.id
        voice=self.db["voiceChannel"].find_one({"userID":id})
        if voice is None:
            return await ctx.channel.send(embed=self.embed(ctx.author,f" You don't own a channel.","Error"))
        if member.id == id:
            return await ctx.channel.send(embed=self.embed(ctx.author,f" You are already the owner of the channel.","Error"))

        
        elif member not in ctx.author.voice.channel.members:
            return await ctx.channel.send(embed=self.embed(ctx.author,f" Member not in voice channel .","Error"))


        else:
            self.db["voiceChannel"].update_one({"userID":id},{"$set":{"userID":member.id}})
            return await ctx.channel.send(embed=self.embed(ctx.author,f' Channel Transfered to {member.mention} .',"Success"))


    @voice.command()
    async def unlock(self, ctx):
        id = ctx.author.id
        voice=self.db["voiceChannel"].find_one({"userID":id})
        if voice is None:
            return await ctx.channel.send(embed=self.embed(ctx.author,f"{ctx.author.mention} You don't own a channel.","Error"))
        else:
            if self.db["guild"].find_one({"guildID":ctx.guild.id}):
                role = self.db["guild"].find_one({"guildID":ctx.guild.id})["default_role"]
            else:
                return await ctx.send(embed=self.embed(ctx.author,"Bot not setted up!","Error"))
            role =ctx.guild.get_role(role)
            channelID = voice["voiceID"]
            channel = self.bot.get_channel(channelID)
            await channel.set_permissions(role, connect=True)
            await ctx.channel.send(embed=self.embed(ctx.author,f'{ctx.author.mention} Voice chat unlocked! 🔓',"Success"))

    @voice.command(aliases=["allow"])
    async def permit(self, ctx, member : discord.Member):
        if member == None:
            raise commands.errors.MissingRequiredArgument
        id = ctx.author.id
        voice=self.db["voiceChannel"].find_one({"userID":id})
        if voice is None:
            return await ctx.channel.send(embed=self.embed(ctx.author,f" You don't own a channel.","Error"))
        else:
            channelID = voice["voiceID"]
            channel = self.bot.get_channel(channelID)
            await channel.set_permissions(member, connect=True)
            await ctx.channel.send(embed=self.embed(ctx.author,f' You have permited {member.mention} to have access to the channel. ✅',"Success"))

    @voice.command(aliases=["deny"])
    async def reject(self, ctx, member : discord.Member):
        if member == None:
            raise commands.errors.MissingRequiredArgument
        id = ctx.author.id
        if id == member.id : 
            return await ctx.channel.send(embed=self.embed(ctx.author,f" You can't reject yourself","Error"))

        guildID = ctx.guild.id
        voice=self.db["voiceChannel"].find_one({"userID":id})
        if voice is None:
            await ctx.channel.send(embed=self.embed(ctx.author,f" You don't own a channel.","Error"))
        else:
            channelID = voice["voiceID"]
            channel = self.bot.get_channel(channelID)
            for members in channel.members:
                if members.id == member.id:
                    voice=self.db["guild"].find_one({"guildID":guildID})
                    channel2 = self.bot.get_channel(voice["voiceChannelID"])
                    await member.move_to(channel2)
                    
                    
            await channel.set_permissions(member, connect=False,read_messages=True)
            await ctx.channel.send(embed=self.embed(ctx.author,f' You have rejected {member.mention} from accessing the channel. ❌',"Success"))



    @voice.command()
    async def limit(self, ctx, limit):
        if limit == None:
            raise commands.errors.MissingRequiredArgument
        id = ctx.author.id
        voice=self.db["voiceChannel"].find_one({"userID":id})
        if voice is None:
            await ctx.channel.send(embed=self.embed(ctx.author,f" You don't own a channel.","Error"))
        else:
            channelID = voice["voiceID"]
            channel = self.bot.get_channel(channelID)
            await channel.edit(user_limit = limit)
            await ctx.channel.send(embed=self.embed(ctx.author,f' You have set the channel limit to be '+ '`{}`.'.format(limit),"Success"))
            voice =  self.db["userSettings"].find_one({"userID":id,})
            if voice is None:
                self.add({"userID":id,"channelName":f'{ctx.author.name}',"channelLimit":limit},"userSettings")
            else:
                self.db["userSettings"].update_one({"userID":id},{"$set":{"channelLimit":limit}})

    @voice.command()
    @commands.cooldown(2, 600, commands.BucketType.user)
    async def name(self, ctx,*, name):
        if name == None:
            raise commands.errors.MissingRequiredArgument
        id = ctx.author.id
        voiceid=ctx.author.voice.channel.id
        voice=self.db["voiceChannel"].find_one({"userID":id,"voiceID":voiceid})
        if voice is None:
            await ctx.channel.send(embed=self.embed(ctx.author,f" You don't own the channel.","Error"))
        else:
            channelID = voice["voiceID"]
            channel = self.bot.get_channel(channelID)
            await channel.edit(name = name)
            await ctx.channel.send(embed=self.embed(ctx.author,f' You have changed the channel name to '+ '`{}`'.format(name),"Success"))
            voice =  self.db["userSettings"].find_one({"userID":id,})
            if voice is None:
                self.add({"userID":id,"channelName":name,"channelLimit":0},"userSettings")
            else:
                self.db["userSettings"].update_one({"userID":id},{"$set":{"channelName":name}})


    @voice.command()
    async def claim(self, ctx):
        
        x = False
        channel = ctx.author.voice.channel
        if channel == None:
            await ctx.channel.send(embed=self.embed(ctx.author,f" you're not in a voice channel.","Error"))
        else:
            id = ctx.author.id
            voice=self.db["voiceChannel"].find_one({"voiceID":channel.id})
            if voice is None:
                if self.check({"voiceCategoryID":channel.category_id},"guild"):
                    self.add({"voiceID":channel.id,"userID":id},"voiceChannel")
                    await ctx.channel.send(embed=self.embed(ctx.author,f" You are now the owner of the channel!","Success"))
                else:
                    await ctx.channel.send(embed=self.embed(ctx.author,f" You can't own that channel!","Error"))
            else:
                for data in channel.members:
                    if data.id == voice["userID"]:
                        owner = ctx.guild.get_member(voice ["userID"])
                        if owner.id == ctx.author.id:
                             return await ctx.channel.send(embed=self.embed(ctx.author,f" You are already the owner of the channel. ","Error"))

                        await ctx.channel.send(embed=self.embed(ctx.author,f" This channel is already owned by {owner.mention}!","Error"))
                        x = True
                if x == False:
                    await ctx.channel.send(embed=self.embed(ctx.author,f" You are now the owner of the channel!","Success"))
                    self.db["voiceChannel"].update_one({"voiceID":channel.id},{"$set":{"userID":id}})



def setup(bot):
    bot.add_cog(voice(bot))
