import math 
from typing import List



#You only have to give non-trivial transitions, others are automatically send to a sink state. 
#None of the states can be named 'sink'
class DFA:
    
    # transitions: [(start_state, end_state, char)]
    # final: [state]
    # state: of type char, initial state is ALWAYS 'q_0'
    # alphabet: all characters which can be used
    def __init__(self, transitions: List, final_states:List, initial_state:str = 'q_0') -> None:
        self.transitions = transitions
        self.initial_state = initial_state
        self.states = list(set(x[0] for x in transitions)) + ['sink']
        self.alphabet = list(set(x[2] for x in transitions))
        self.transitions += [('sink','sink', char) for char in self.alphabet]
        
        for state in self.states:
            for char in self.alphabet:
                if [x for x in self.transitions if x[0] == state and x[2] == char] == []:
                    self.transitions += [(state,'sink', char)]
        self.final = final_states
        self.pos = initial_state
        

        #All states which have a path to a final state
        def non_trivial(states: List, transitions: List, final: List, non_trivial_states: List=[x for x in self.final]):
            i=0
            for x in [(s,e,c) for (s,e,c) in self.transitions if e in non_trivial_states and s not in non_trivial_states]:
                i+=1
                non_trivial_states.append(x[0])
            if not i:
                return non_trivial_states
            return non_trivial(states=self.states, transitions = self.transitions, final = final,non_trivial_states= non_trivial_states)
        self.non_trivial_states = non_trivial(self.states, self.transitions, self.final)

        pass
    


    def move(self, transition: tuple) -> None:
        self.pos = transition[1]
        

    def size(self, visited: List = [], initial_state: str = None) -> int:
        if initial_state is None:
            initial_state = self.initial_state
        self.pos = initial_state
        size = int((initial_state in self.final))
        for (s,e,c) in [(s,e,c) for (s,e,c) in self.transitions if (s==initial_state and e in self.non_trivial_states)]:
            if s in visited:
                return math.inf
            size += self.size(visited= visited+[s], initial_state=e)
            
        return size
            
        

    def membership(self, word: List, state: str = 'q_0') -> bool:
        if len(word) == 0:
            return (state in self.final)
        nstate = [e for (s,e,c) in self.transitions if s==state and c == word[0]]
        return nstate != [] and self.membership(word[1:],state=nstate[0])
        

def complement(dfa: DFA) -> DFA:
    return DFA( transitions=dfa.transitions, final_states=list(set(s for (s,e,t) in dfa.transitions if s not in dfa.final)))
    
def intersection(dfa1: DFA, dfa2: DFA) -> DFA:
    final = [x+y for x in dfa1.final for y in dfa2.final]
    newtranstitions = []
    for (s1,e1,c) in dfa1.transitions:
        for (s2,e2) in [(x,y) for (x,y,z) in dfa2.transitions if c==z]:
                newtranstitions.append((s1+s2,e1+e2,c)) 
    return DFA(transitions=newtranstitions, final_states=final, initial_state=dfa1.initial_state+dfa2.initial_state)

def union(dfa1: DFA, dfa2: DFA) -> DFA:
    return complement(intersection(complement(dfa1),complement(dfa2)))


