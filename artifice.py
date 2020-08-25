import subprocess

import discord

from initiative import Initiative

TOKEN = ""

def fetch_token():
    tokfile = open("TOKEN.txt")
    tok = tokfile.read()
    tokfile.close()
    return tok

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
            '!init start (or begin) : start the initiative tracker\n'
            '!init end : clear the initiative tracker\n'
            '!init add <name> <bonus> <option> : add someone to initiative with a certain bonus\n'
            '    the optional parameter can be "adv" or "dis" to give them advantage\n'
            '    or disadvantage on the roll, or a number to specify what they roll\n'
            '!init remove <name> : removes someone from initiative\n'
            '!init next : advances the initiative tracker and tags the next player\n'
            )

    def print_init(self, channel):
        return str(self.trackers[channel])
            
    def in_init(self, channel):
        return (channel in self.trackers and self.trackers[channel] != None)

    async def process_init(self, init_command, channel, author):
        error = False

        if init_command[1] == "start" or init_command[1] == "begin":
            if self.in_init(channel):
                await channel.send("Already in initiative!")
            else:
                self.trackers[channel] = Initiative()
                await channel.send("Initiative begun!" + 
                        " Use !init add <name> <bonus> <options> to roll initiative.")
                self.init_msg[channel] = await channel.send(self.print_init(channel))
                await self.init_msg[channel].pin()

        elif init_command[1] == "add":
            if self.in_init(channel):
                adv = 0
                roll = None
                surprise = 0

                if is_number(init_command[2]):
                    await channel.send('Invalid argument, use !init add <name> <bonus> <options> to roll')
                    error = True

                if not is_number(init_command[3]):
                    await channel.send('Invalid argument, use !init add <name> <bonus> <options> to roll')
                    error = True

                if len(init_command) >= 5:
                    if init_command[4] == "adv":
                        adv = 1
                    elif init_command[4] == "dis":
                        adv = -1
                    elif init_command[4] == "surprise":
                        surprise = 1
                    elif init_command[4] == "lost":
                        surprise = -1
                    elif is_number(init_command[4]):
                        roll = int(init_command[4])
                    else:
                        await channel.send('Invalid argument, use !init add <name> <bonus> <options> to roll')
                        error = True
                    if len(init_command) == 6:
                        if init_command[5] == "adv":
                            adv = 1
                        elif init_command[5] == "dis":
                            adv = -1
                        elif init_command[5] == "surprise":
                            surprise = 1
                        elif init_command[5] == "lost":
                            surprise = -1
                        elif is_number(init_command[5]):
                            roll = int(init_command[5])
                        else:
                            await channel.send('Invalid argument, use !init add <name> <bonus> <options> to roll')
                            error = True
                
                if not error:
                    self.trackers[channel].add(init_command[2], int(init_command[3]), 
                            id=author, roll=roll, adv=adv, surprise=surprise)
                    await self.init_msg[channel].edit(content=self.print_init(channel))
            else:
                await channel.send("Not in initiative")

        elif init_command[1] == "remove":
            if self.in_init(channel):
                self.trackers[channel].remove(init_command[2])
                await self.init_msg[channel].edit(content=self.print_init(channel))
            else: 
                await channel.send("Not in intiative")

        elif init_command[1] == "end":
            if self.in_init(channel):
                self.trackers[channel] = None
                await self.init_msg[channel].unpin()
                await channel.send("Initiative ended")
            else:
                await channel.send("Not in intiative")

        elif init_command[1] == "next":
            if self.in_init(channel):
                tracker = self.trackers[channel]
                entity = tracker.next()
                member = entity.id
                name = entity.name
                await self.init_msg[channel].edit(content=self.print_init(channel))
                mention = member.mention
                await channel.send("Up next: " + name + " " + mention)
            else: 
                await channel.send("Not in initiative")
        
        else: 
            await channel.send('Invalid command, call \'!help\' for more information')

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
                roll = roll_dice(user_roll)
                await message.channel.send(message.author.display_name + 
                        " rolled " + user_roll + ": " + str(roll))

            elif message.content == '!re':
                if message.author.id in self.past_rolls:
                    user_roll = self.past_rolls[message.author.id]
                    roll = roll_dice(user_roll)
                    await message.channel.send(message.author.display_name + 
                            " rolled " + user_roll + ": " + str(roll))
                else:
                    await message.channel.send("No past roll on record!")

            elif message.content.split(" ")[0] == "!init":
                init_command = message.content.split(" ")
                await self.process_init(init_command, message.channel, message.author)
                
TOKEN = fetch_token()
client = ArtificeClient()
client.run(TOKEN)
