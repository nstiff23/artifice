# artifice
**Authors:** Nathan Stiff and Tyler Hoffman
 
Initiative tracker Discord bot for Dungeons and Dragons 5th edition.

The initiative tracker backend and interface with the Discord API are written in Python; dice roller is a parser implementing a CFG and is written in C++. All code is (mostly) tested. Let us know about any bugs -- this code is in active development!

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