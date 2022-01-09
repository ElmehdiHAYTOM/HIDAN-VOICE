import discord
import asyncio
from discord.ext import commands
import traceback
import os
import validators
import pymongo


class Check(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.myclient = pymongo.MongoClient("mongodb+srv://HIDAN:622623766Q358442@hidanbot.cd8yb.mongodb.net")
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
                        guildSetting=self.db["guildSettings"].find_one({"guildID":guildID})
                        name = f"{member.name}'s channel"
                        if guildSetting is None:
                            limit = 0
                        else:
                            limit = guildSetting["channelLimit"]
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


def setup(bot):
    bot.add_cog(Check(bot))
