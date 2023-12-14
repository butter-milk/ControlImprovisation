from random import random
from typing import List

class Improviser:
    #Transitions [(s,e,c,p)] (start, end, character, probability)
    def __init__(self, transitions: List, final_state: List, initial_state: str = 'q_0') -> None:
        self.transitions = transitions
        self.final = final_state
        self.initial_state = initial_state
        self.pos = initial_state    
        pass

    def generate(self, word: str = '') -> str:

        while True:
            
            edgesspace = sum([p for (s,e,c,p) in self.transitions if s == self.pos and not p==0])
            totalspace = float(1) - edgesspace
            prob = random()
            if prob <= totalspace:
                self.pos = self.initial_state
                return word

            for t in [ (e,c,p) for (s,e,c,p) in self.transitions if s == self.pos and not p==0]:
                if prob <= totalspace + t[2]:
                    
                    self.pos = t[0]
                    word = word + t[1]
                    break
                totalspace += t[2]
            
              

    def sample(self, no = 1) -> list():
        print(self.final)
        return [self.generate() for _ in range(no)]