from firebase import db
import discord
import random
import datetime

guildIDs = [901345738380939304]
logChannel = 908443147787444295
adminRole = 905093231342137424

class LevelUpProcess():

    def __init__(self, userID, author: discord.Member):
        self.userID = userID
        self.playerData = db.collection('user-cards').document(str(self.userID)).get().to_dict()
        self.author = author

    async def checkForLevelUp(self):

        level = self.playerData['Level']
        xp = self.playerData['XP']

        if 5 * (level**2) + (50 * level) + 100 - xp <= 10:
            self.playerData["Level"] += 1 
            self.playerData["XP"] = 0
            self.playerData["Rolls"] += 3
            embed = discord.Embed(title="You levelled up!", description=f"You are now Level `{self.playerData['Level']}`. You also have 3 new rolls!")
            

            db.collection("user-cards").document(str(self.userID)).set(self.playerData)

            await self.author.send(embed = embed)
        else:
            self.playerData["XP"] += 10  
            document = db.collection("user-cards").document(str(self.userID))
            document.set(self.playerData)

class RollProcess():

    def __init__(self, author: discord.Member, numberOfRolls,ctx):
        self.author = author
        self.nr = numberOfRolls
        self.ctx = ctx
        self.playerData = db.collection('user-cards').document(str(self.author.id)).get().to_dict()

    async def returnChance(self, denominator, numerator=1):
        return random.randint(numerator,denominator)

    async def oneRoll(self):

        if self.playerData["Rolls"] <= 0:
            await self.ctx.send("You do not have enough rolls.")
            return None, None
        
        if self.playerData["rollsSoFar"]%5==0:
            chosenCardName, chosenCardImage = random.choice(list(db.collection("Cards").document("Cards").get().to_dict()["Uncommon"].items()))
            chosenCardName = "Uncommon " + chosenCardName
            colour = 0x4ba1c2

        else:
            if await self.returnChance(400) == 1:
                chosenCardName, chosenCardImage = random.choice(list(db.collection("Cards").document("Cards").get().to_dict()["Secret Rare"].items()))
                chosenCardName = "Secret Rare " + chosenCardName
                colour = 0xab5236
            
            elif await self.returnChance(50) == 1:
                chosenCardName, chosenCardImage = random.choice(list(db.collection("Cards").document("Cards").get().to_dict()["Ultra Rare"].items()))
                chosenCardName = "Ultra Rare " + chosenCardName
                colour = 0xae543c

            elif await self.returnChance(15) == 1:
                chosenCardName, chosenCardImage = random.choice(list(db.collection("Cards").document("Cards").get().to_dict()["Rare"].items()))
                chosenCardName = "Rare " + chosenCardName
                colour = 0xf0ff6e

            elif await self.returnChance(10) == 1:
                chosenCardName, chosenCardImage = random.choice(list(db.collection("Cards").document("Cards").get().to_dict()["Uncommon"].items()))
                chosenCardName = "Uncommon " + chosenCardName
                colour = 0x4ba1c2

            else:
                chosenCardName, chosenCardImage = random.choice(list(db.collection("Cards").document("Cards").get().to_dict()["Common"].items()))
                chosenCardName = "Common " + chosenCardName
                colour = 0xa7a7a7

        self.playerData["rollsSoFar"] += 1
        self.playerData["Cards"].append({chosenCardName: chosenCardImage})
        self.playerData["Rolls"] -= 1
        db.collection("user-cards").document(str(self.author.id)).set(self.playerData)

        return chosenCardName, chosenCardImage, colour

    async def logRoll(self, name, colour):

        channel = self.author.guild.get_channel(logChannel)
        embed = discord.Embed(title="Card Rolled", description=f"{self.author.mention} has rolled a {name}.",timestamp=datetime.datetime.now(), colour=colour)
        embed.set_author(name=self.author.display_name,icon_url=self.author.avatar_url)
        embed.set_footer(text=self.author.id)
        await channel.send(embed=embed)

    async def process(self):
        if self.nr > 10 or self.nr < 1:
            await self.ctx.send("You can only roll between 1 and 10 rolls per go.", hidden=True)
            return
        await self.ctx.send("Check your DMs!", hidden=True)
        for i in range(0, self.nr):
            name, image, colour = await self.oneRoll()
            if name == None:
                return
            embed = discord.Embed(title=name,colour=colour)
            embed.set_image(url=image)
            await self.ctx.author.send(embed=embed)
            print(f"{self.author.display_name} rolled a {name}.")
            await self.logRoll(name, colour)

class MakeAccount():

    def __init__(self, user):
        self.user = user

    async def makeAccount(self):
        doc = db.collection("user-cards").document(str(self.user.id)).get().to_dict()
        if doc == None:
            db.collection("user-cards").document(str(self.user.id)).set({"Cards":[],"Level":1,"Rolls": 0, "XP": 0, "rollsSoFar": 0})

class GiveRolls():

    def __init__(self,user,nr, ctx):
        self.user = user
        self.nr = nr
        self.playerData = db.collection('user-cards').document(str(self.user.id)).get().to_dict()
        self.ctx = ctx

    async def giveRolls(self):
        self.playerData["Rolls"] += self.nr
        db.collection("user-cards").document(str(self.user.id)).set(self.playerData)
        await self.ctx.send(f"Gave {self.user.display_name} `{self.nr}` rolls.", hidden=True)
        
class viewInfo():

    def __init__(self,ctx, user):
        self.ctx = ctx
        self.user: discord.Member = user
        self.playerData = db.collection('user-cards').document(str(self.user.id)).get().to_dict()
    
    async def getCards(self):

        return self.playerData["Cards"]
    
    async def sortCards(self):

        cards: list = await self.getCards()

        sortedDict = {}
        
        for card in cards:
            
            if list(card.keys())[0] not in sortedDict.keys():

                sortedDict[list(card.keys())[0]] = {"url": list(card.values())[0], "amount":1}

            else:

                sortedDict[list(card.keys())[0]]["amount"] += 1

        string = ""

        for key, value in sortedDict.items():

            string += f"• **{key}** ({value['amount']})\n"

        if string == "":
            return "*Empty*"

        return string

    async def sendEmbed(self):

        cardsString = await self.sortCards()

        maxXP = 5 * (self.playerData["Level"]**2) + (50 * self.playerData["Level"]) + 100

        embed = discord.Embed()
        embed.add_field(name="Level", value=self.playerData["Level"])
        embed.add_field(name="XP", value=f'{self.playerData["XP"]}/{maxXP}')
        embed.add_field(name="Rolls",value=self.playerData["Rolls"])
        embed.add_field(name=f"Cards ({len(self.playerData['Cards'])})", value=cardsString, inline=False)
        embed.set_author(name=self.user.display_name,icon_url=self.user.avatar_url)

        await self.ctx.send(embed=embed, hidden=True)
            


class CardManipulation():

    def __init__(self, ctx, rarity, name):
        self.ctx = ctx
        self.rarity = rarity
        self.name = name
        self.cardsDict = db.collection("Cards").document("Cards").get().to_dict()

    async def addCard(self, image):

        self.cardsDict[self.rarity][self.name] = image
        db.collection("Cards").document("Cards").set(self.cardsDict)

        colours = {
            "Common": 0xa7a7a7,
            "Uncommon": 0x4ba1c2,
            "Rare": 0xf0ff6e,
            "Ultra Rare": 0xae543c,
            "Secret Rare": 0xab5236
        }
        
        embed = discord.Embed(title=f"{self.rarity} {self.name} has been added to the system.", timestamp=datetime.datetime.now(), colour=colours[self.rarity])
        embed.set_image(url=image)
        embed.set_author(name=self.ctx.author.display_name,icon_url=self.ctx.author.avatar_url)
        channel = self.ctx.guild.get_channel(logChannel)
        await self.ctx.send(embed=embed,hidden=True)
        await channel.send(embed=embed)

    async def removeCard(self):

        if self.name in self.cardsDict[self.rarity].keys():

            colours = {
            "Common": 0xa7a7a7,
            "Uncommon": 0x4ba1c2,
            "Rare": 0xf0ff6e,
            "Ultra Rare": 0xae543c,
            "Secret Rare": 0xab5236
        }

            del self.cardsDict[self.rarity][self.name] 
            db.collection("Cards").document("Cards").set(self.cardsDict)
            embed = discord.Embed(title=f"{self.rarity} {self.name} has been removed from the system.", timestamp=datetime.datetime.now(), colour=colours[self.rarity])
            embed.set_author(name=self.ctx.author.display_name,icon_url=self.ctx.author.avatar_url)
            channel = self.ctx.guild.get_channel(logChannel)
            await self.ctx.send(embed=embed,hidden=True)
            await channel.send(embed=embed)

        else:

            await self.ctx.send("That card does not exist.", hidden=True)

class removeFromPlayer():

    def __init__(self, ctx, user, rarity, name):
        self.ctx = ctx
        self.user = user
        self.rarity = rarity
        self.name: discord.Member = name
        self.playerData = db.collection('user-cards').document(str(self.user.id)).get().to_dict()

    async def removeCard(self):
        count = 0
        for card in self.playerData["Cards"]:
            if list(card.keys())[0] == f"{self.rarity} {self.name}":
                self.playerData["Cards"].pop(count)
                db.collection("user-cards").document(str(self.user.id)).set(self.playerData)
                await self.ctx.send(f"Removed {self.rarity} {self.name} from {self.ctx.author.mention}.", hidden=True)
                return
            count += 1
        await self.ctx.send(f"Could not find that card in the player's inventory.", hidden=True)
                




