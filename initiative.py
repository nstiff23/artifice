"""
TODO
- add error checking
- import walter and replace roll functions
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
                f'roll = {self.roll}, id = {self.id})'
    
    def __init__(self):
        self.entities = []
        self.surprise = []
        self.lost = []
        self.curr = -1
        self.started = False

    def _get_names(self): return [e.name for e in self.entities]
    def _get_mods(self): return [e.mod for e in self.entities]
    def _get_rolls(self): return [e.roll for e in self.entities]
    def _get_ids(self): return [e.id for e in self.entities]

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
                if roll == 1:
                    if surprise > 0: surprise = 0 #surprise + nat 1 = cancel
                    else: surprise = -1

            roll += mod #add mod to roll after checking natural surprise/loss

            newE = self.Entity(name, mod, roll, id)
            self.entities.append(newE)
        else:
            newE = self.Entity(name, mod, roll, id)
            self.entities.append(newE)
            
        if surprise > 0: self.surprise.append(newE)
        if surprise < 0: self.lost.append(newE)

        self.entities.sort(key=lambda e : (e.roll, e.mod), reverse=True) # sort by roll then mod
        
        if self.started and roll > self.entities[self.curr].roll: self.curr += 1

    def remove(self, name): 
        idx = -1
        for i in range(len(self.entities)):
            if self.entities[i].name == name: idx = i; break
        
        if name in self.surprise: self.surprise.remove(self.entities[idx])
        if name in self.lost: self.lost.remove(self.entities[idx])

        return self.entities.pop(idx).name

    def view(self): return self.curr, self.entities

    def next(self):
        self.started = True 

        self.curr += 1
        if self.surprise: # go through surprise list here
            out = self.surprise[self.curr]
            self.surprise.pop(self.curr)
            if not self.surprise: self.curr = -1    
            return out.name        
            
        out = self.entities[self.curr]
        if out in self.lost: 
            self.lost.remove(out)
            return self.next()

        if self.curr == len(self.entities) - 1: self.curr = -1

        return out.name

    def __repr__(self):
        return f'{self.curr}' + '\n' + '\n'.join([repr(e) for e in self.entities])

if __name__ == '__main__':
    tracker = Initiative()

    tracker.add('Tristan', 5)
    tracker.add('Nathan', 1)
    tracker.add('Tyler', 1)
    tracker.add('Jeff', -3)
    tracker.add('George', -1)
    
    print(tracker.next())
    print(tracker)
    print(tracker.next())
    print(tracker)

    tracker.add('b1', 0)
    tracker.add('b2', 0)
    tracker.add('b3', 0)
    tracker.add('b4', 0)
    tracker.add('b5', 0)
    tracker.add('b6', 0)
    
    print(tracker.next())
    print(tracker)
    print(tracker.next())
    print(tracker)
    
    """for i in range(10):
        print(tracker.next())
        if i == 0: print(tracker) """
    