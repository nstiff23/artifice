"""
TODO
- add error checking
"""
import random

class Initiative:
    class Entity:
        def __init__(self, name, mod, roll, id):
            self.name = name
            self.mod = mod
            self.roll = roll
            self.id = id
        
        def __repr__(self):
            return f'Entity(name = {self.name}, mod = {self.mod}, ' + \
                f'roll = {self.roll}, id = {self.id}'

        def __str__(self):
            out = ""
            if self.roll < 10:
                out += "0" + str(self.roll)
            else:
                out += str(self.roll)

            out += " "

            out += self.name
            return out
    
    def __init__(self):
        self.entities = []
        self.surprise = []
        self.lost = []
        self.curr = -1
        self.started = False

    def __str__(self):
        out = "```\n"
        if len(self.surprise) > 0:
            out += "SURPRISE\n==========\n"
            for i in range(0,len(self.surprise)):
                out += self.print_entity(self.surprise[i])
        out += "INITIATIVE\n==========\n"
        for i in range(0,len(self.entities)):
            bold = (self.curr == i)
            out += self.print_entity(self.entities[i], current=bold)
        if len(self.lost) > 0:
            out += "LOST\n==========\n"
            for i in range(0,len(self.lost)):
                out += self.print_entity(self.lost[i])

        out += "```"
        return out

    def _get_names(self): return [e.name for e in self.entities]
    def _get_mods(self): return [e.mod for e in self.entities]
    def _get_rolls(self): return [e.roll for e in self.entities]
    def _get_ids(self): return [e.id for e in self.entities]

    def print_entity(self, entity, current=False):
        out = ""
        if current:
            out += ">"
        else:
            out += " "

        out += str(entity)
        out += '\n'
        return out

    def add(self, name, mod, roll=None, id=None, adv=0, surprise=0): 
        # roll: if number, roll is a manually-specified roll
        #       if None, mod is an initiative modifier (do the roll)

        # Add to regular initiative
        if roll is None: 
            if adv != 0:
                r1 = random.randint(1, 20)
                r2 = random.randint(1, 20)
                
                if adv > 0: roll = max(r1, r2)
                if adv < 0: roll = min(r1, r2)
            else: roll = random.randint(1, 20)

            if not self.started:
                if roll == 20: 
                    if surprise < 0: surprise = 0 #lost + nat 20 = cancel
                    else: surprise = 1
                # bogus rule
                #if roll == 1:
                #    if surprise > 0: surprise = 0 #surprise + nat 1 = cancel
                #    else: surprise = -1

            roll += mod #add mod to roll after checking natural surprise/loss

            newE = self.Entity(name, mod, roll, id)
            self.entities.append(newE)
        else:
            newE = self.Entity(name, mod, roll, id)
            self.entities.append(newE)

        if self.started: surprise = 0
            
        if surprise > 0: self.surprise.append(newE)
        if surprise < 0: self.lost.append(newE)

        if self.started and roll > self.entities[self.curr].roll: self.curr += 1

        self.entities.sort(key=lambda e : (e.roll, e.mod), reverse=True) # sort by roll then mod

    def remove(self, name): 
        idx = -1
        for i in range(len(self.entities)):
            if self.entities[i].name == name: idx = i; break
        
        if self.entities[idx] in self.surprise: self.surprise.remove(self.entities[idx])
        if self.entities[idx] in self.lost: self.lost.remove(self.entities[idx])

        return self.entities.pop(idx).name

    def view(self): return self.curr, self.entities

    def next(self):
        self.started = True 

        self.curr += 1
        if self.surprise: # go through surprise list here
            out = self.surprise.pop(self.curr)
            if not self.surprise: self.curr = -1    
            return out        
            
        out = self.entities[self.curr]
        if out in self.lost: 
            self.lost.remove(out)
            return self.next()

        if self.curr == len(self.entities) - 1: self.curr = -1

        return out

    def __repr__(self):
        return f'{self.curr}' + '\n' + '\n'.join([repr(e) for e in self.entities])

if __name__ == '__main__':
    tracker = Initiative()

    tracker.add('Silver', 3)
    tracker.add('Mike', 3)
    tracker.add('Kiran', 3)
    tracker.add('Mecha', 2, surprise=1)
    tracker.add('slowpoke', 2, roll=2)
    
    tracker.next()
    print(tracker)
    tracker.next()
    print(tracker)
    
    tracker.next()
    print(tracker)
    tracker.next()
    print(tracker)
    
    print(tracker.next())
    print(tracker)
    print(tracker.next())
    print(tracker)
        
    print(tracker.next())
    print(tracker)
    print(tracker.next())
    print(tracker)
      
    print(tracker.next())
    print(tracker)
    print(tracker.next())
    print(tracker)
    