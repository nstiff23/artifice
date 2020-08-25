import os
import subprocess

import discord
from dotenv import load_dotenv

from initiative import Initiative

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

def roll_dice(user_roll):
    user_roll = user_roll.replace(" ","")
    if user_roll[:3] == "adv":
        res1 = subprocess.run(["./dice", user_roll[3:]], capture_output=True, text=True)
        res2 = subprocess.run(["./dice", user_roll[3:]], capture_output=True, text=True)
        return max(int(res1.stdout.strip()), int(res2.stdout.strip()))
    elif user_roll[:3] == "dis":
        res1 = subprocess.run(["./dice", user_roll[3:]], capture_output=True, text=True)
        res2 = subprocess.run(["./dice", user_roll[3:]], capture_output=True, text=True)
        return min(int(res1.stdout.strip()), int(res2.stdout.strip()))
    else:
        res = subprocess.run(["./dice", user_roll], capture_output=True, text=True) 
        return int(res.stdout.strip())

def is_number(string):
    try:
        int(string)
        return True
    except ValueError:
        return False

class ArtificeClient(discord.Client):
    trackers = {}
    init_msg = {}

    past_rolls = {}

    helpmsg = (
            '**Artifice**\n'
            'Commands:\n'
            '!help : displays this message\n'
            '!roll : roll some dice\n'
            '    format: 4d6h3: roll 4d6, keep the 3 highest\n'
            '    can also add, subtract, divide and multiply in PMDAS order\n'
            '    ex. 4d6+(3d10/2-1)-1d4+2d5\n'
            '    use adv and dis to roll with advantage or disadvantage, respectively\n'
            '!re : repeat your most recent roll\n'
            '!init : controls the initiative tracker\n'
            '!init start : start the initiative tracker\n'
            '!init end : clear the initiative tracker\n'
            '!init add <bonus> : add someone to initiative with a certain bonus\n'
            '!init remove <name> : removes someone from initiative'
            )

    @staticmethod
    def print_entity(self, entity, current=FALSE):
        out = ""
        if current:
            out += ">"
        else:
            out += " "

        roll = entity.roll
        if roll < 10:
            out += " " + str(roll)
        else:
            out += str(roll)

        name = entity.name[0:20]
        out += name

        if current:
            out += "**"
        out += '\n'
        return out

    @staticmethod
    def print_init(self, channel):
        out = "```\n"
        tracker = trackers[channel]

        curr, entities = tracker.view()
        surprise = tracker.surprise
        lost = tracker.lost

        if len(surprise) > 0:
            out += "SURPRISE\n========\n"
            for i in range(0,len(surprise)):
                out += self.print_entity(surprise[i])
        out += "INITIATIVE\n==========\n"
        for i in range(0,len(entities)):
            bold = (curr == i)
            out += self.print_entity(entities[i], current=bold)
        if len(lost) > 0:
            out += "LOST\n====\n"
            for i in range(0,len(lost)):
                out += self.print_entity(lost[i])

        out += "```"
    
    @staticmethod
    def in_init(self, channel):
        return channel in trackers

    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')

    async def on_message(self, message):
        if message.author == self.user:
            return
        
        if message.content:
            if message.content == '!help':
                await message.author.create_dm()
                await message.author.dm_channel.send(self.helpmsg)
            elif message.content.split(" ")[0] == '!roll':
                user_roll = message.content[6:]
                self.past_rolls[message.author.id] = user_roll
                roll = self.roll_dice(user_roll)
                await message.channel.send(message.author.display_name + 
                        " rolled " + user_roll + ": " + str(roll))

            elif message.content == '!re':
                if message.author.id in self.past_rolls:
                    user_roll = self.past_rolls[message.author.id]
                    roll = self.roll_dice(user_roll)
                    await message.channel.send(message.author.display_name + 
                            " rolled " + user_roll + ": " + str(roll))
                else:
                    await message.channel.send("No past roll on record!")

            elif message.content.split(" ")[0] == "!init":
                init_command = message.content.split(" ")
                if init_command[1] == "start" or init_command[1] == "begin":
                    if self.in_init(message.channel):
                        await message.channel.send("Already in initiative!")
                    else:
                        self.trackers[message.channel] = Initiative()
                        await message.channel.send("Initiative begun!" + 
                                " Use !init add <bonus> to roll initiative.")
                        self.init_msg[message.channel] = await message.channel.send(
                                self.print_init(message.channel))
                        await self.init_msg[message.channel].pin()

                elif init_command[1] == "add":
                    if self.in_init(message.channel):
                        adv = 0
                        if init_command[4] == "adv":
                            adv = 1
                        elif init_command[4] == "dis":
                            adv = -1
                        
                        if is_number(init_command[4]):
                            self.trackers[message.channel].add(init_command[2], int(init_command[3]),
                                    roll=int(init_command[4]), id=message.author)
                        else:
                            self.trackers[message.channel].add(init_command[2], int(init_command[3]),
                                    id=message.author)
                        await self.init_msg[message.channel].edit(
                                content=self.print_init(message.channel))
                    else:
                        await message.channel.send("Not in initiative")

                elif init_command[1] == "remove":
                    if self.in_init(message.channel):
                        self.trackers[message.channel].remove(init_command[2])
                        await self.init_msg.edit(content=self.print_init(message.channel))
                    else: 
                        await message.channel.send("Not in intiative")

                elif init_command[1] == "end":
                    if self.in_init(message.channel):
                        self.trackers[message.channel] = None
                        await self.init_msg.unpin()
                        await message.channel.send("Initiative ended")
                    else:
                        await message.channel.send("Not in intiative")

                elif init_command[1] == "next":
                    if self.in_init(message.channel):
                        member = self.trackers[message.channel].next()
                        mention = member.user.mention
                        await message.channel.send("Up next: " + member.name + " " + mention)
                    else: 
                        await message.channel.send("Not in initiative")

client = ArtificeClient()
client.run(TOKEN)
