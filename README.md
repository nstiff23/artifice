# artifice
**Authors:** Nathan Stiff and Tyler Hoffman
 
Artifice is an initiative tracker Discord bot for Dungeons and Dragons 5th edition. The bot includes a dice roller, which can run complex arithmetic to handle different types of dice, modifiers, resistances, different damage types, buffs and debuffs all with a minimum of hassle. Artifice also has a built-in initiative tracker, which can make initiative rolls with advantage or disadvantage, insert a character at a predetermined spot in the initiative, and give characters a surprise round or a delayed entry. We've tried our best to cover any concievable situation and edge case that the D&D 5th edition rules allow for.

The initiative tracker backend and interface with the Discord API are Python; dice roller is a parser implementing a CFG in C++. All code is (mostly) tested. Let us know about any bugs!

The bot requires `ffmpeg` and the Python libraries `discord`, `ytp-dl` and `PyNaCl`. To set up the bot, put your Discord bot token in a file called `TOKEN.txt`, and then run `python3 artifice.py` -- once Artifice is running, you'll be able to add it to your server using Discord's tools. Note: this code has only been tested on Linux machines.

# Commands:
- `!help` : displays this message
- `!roll` : roll some dice
    - format: 4d6h3: roll 4d6, keep the 3 highest
    - can also add, subtract, divide and multiply in PMDAS order
    - ex: `!roll 4d6+(3d10/2-1)-1d4+2d5`
    - use adv and dis to roll with advantage or disadvantage, respectively
- `!re` : repeat your most recent roll
- `!init` : controls the initiative tracker
- `!init start` (or `!init begin`) : start the initiative tracker
- `!init end` : clear the initiative tracker
- `!init add <name> <bonus> <option>` : add someone to initiative with a certain bonus
    - optional parameter can be "adv" or "dis" to give them advantage or disadvantage on the roll, or a number to specify what they roll exactly
- `!init remove <name>` : removes someone from initiative
- `!init next` : advances the initiative tracker and tags the next player
