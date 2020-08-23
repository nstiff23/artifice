import os
import subprocess
import socket

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

class InitMember:
    user = None
    name = ""
    init = 0

    def __init__(self, user, name, init):
        self.user = user
        self.name = name
        self.init = init

    def get_init(self):
        return self.init

class InitTracker:
    tracker = []
    init_counter = 0

    def add(self, name, user, init):
        member = InitMember(user, name, init)
        self.tracker.append(member)
        self.tracker.sort(key=InitMember.get_init)

    def remove(self, name):
        for i in range(0, len(self.tracker)):
            member = self.tracker[i]
            if member.name == name:
                self.tracker.pop(i)
                break

    def clear(self):
        self.tracker = []

    def print_init(self):
        msg = "Initiative:\n"
        for member in self.tracker:
            msg += " " + str(member.init) + " " + member.name + "\n"
        return msg

    def next(self):
        member = self.tracker[self.init_counter]
        self.init_counter += 1
        if self.init_counter >= len(self.tracker):
            self.init_counter = 0;
        return member

class ArtificeClient(discord.Client):
    sleeping = False
    focused = False
    channel = 0
    past_rolls = {}

    tracker = InitTracker()

    init_msg = None
    in_init = False

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

    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')

    async def on_message(self, message):
        if message.author == self.user:
            return
        
        if message.content:
            elif message.content == '!help':
                await message.author.create_dm()
                await message.author.dm_channel.send(self.helpmsg)
            elif message.content.split(" ")[0] == '!roll':
                user_roll = message.content[6:]
                self.past_rolls[message.author.id] = user_roll
                roll = self.roll_dice(user_roll)
                await message.channel.send(message.author.display_name + " rolled " + user_roll + ": " + str(roll))
            elif message.content == '!re':
                if message.author.id in self.past_rolls:
                    user_roll = self.past_rolls[message.author.id]
                    roll = self.roll_dice(user_roll)
                    await message.channel.send(message.author.display_name + " rolled " + user_roll + ": " + str(roll))
                else:
                    await message.channel.send("No past roll on record!")
            elif message.content.split(" ")[0] == "!init":
                init_command = message.content.split(" ")
                if init_command[1] == "start" or init_command[1] == "begin":
                    if self.in_init:
                        await message.channel.send("Already in initiative!")
                    else:
                        self.tracker.clear()
                        await message.channel.send("Initiative begun! Use !init add <bonus> to roll initiative.")
                        self.init_msg = await message.channel.send(self.tracker.print_init())
                        await self.init_msg.pin()
                        self.in_init = True
                elif init_command[1] == "add":
                    if self.in_init:
                        init_roll = self.roll_dice("1d20+("+init_command[3]+")")
                        self.tracker.add(init_command[2], message.author, init_roll)
                        await self.init_msg.edit(content=self.tracker.print_init())
                    else:
                        await message.channel.send("Not in initiative")
                elif init_command[1] == "remove":
                    if self.in_init:
                        self.tracker.remove(init_command[2])
                        await self.init_msg.edit(content=self.tracker.print_init())
                    else: 
                        await message.channel.send("Not in intiative")
                elif init_command[1] == "end":
                    if self.in_init:
                        self.tracker.clear()
                        await self.init_msg.unpin()
                        await message.channel.send("Initiative ended")
                        self.in_init = False
                    else:
                        await message.channel.send("Not in intiative")
                elif init_command[1] == "next":
                    if self.in_init:
                        member = self.tracker.next()
                        mention = member.user.mention
                        await message.channel.send("Up next: " + member.name + " " + mention)
                    else: 
                        await message.channel.send("Not in initiative")

client = ArtificeClient()
client.run(TOKEN)
