from rDFA import *
from Improviser import *
from random import random




class CI:
    def __init__(self,  l:float, r:float, e:float, H:DFA, m=0, n = math.inf, S:DFA = None) -> None:
        assert m <= n, f"Length bounds are not allowed, should be m <= n"
        assert l <= r, f"Randomness requirement can not be sufficed, should be lambda <= rho"
        assert r > 0, f"rho > 0"
        self.soft_constraint = not (S is None or e==1) 
        self.rho = r
        self.epsilon = e
        self.l = l
        #Add lower bound
        self.I =  H if  m==0 else intersection(H, DFA(  [('q_'+str(i), 'q_'+str(i+1),c)for i in range(m) for c in H.alphabet] + [('q_'+str(m),'q_'+str(m),c) for c in H.alphabet],['q_'+str(m)])) 
        self.A = S 
        #Add upper bound
        if n != math.inf:
            self.I = intersection( self.I, DFA([ ('q_'+str(i), 'q_'+str(i+1),c)for i in range(n) for c in H.alphabet ], ['q_'+str(i) for i in range(n+1)]) )
        if self.soft_constraint:
            if self.I.size() == math.inf:
                assert l ==0.0, f"Problem is not feasible"
                assert CI(m=m,n=n,l=l, r=r/(1-e), H=self.A, e=1).isfeasible, f"Problem is not feasible"
            else:
                assert ((1-e)/r <= self.A.size()), f"Problem is not feasible"
                if l!=0:
                    assert (1/l >= self.I.size() and 1/r <= self.I.size()), f"Problem is not feasible"
                    assert (self.I.size()-self.A.size() <= e/l), f"Problem is not feasible" 
                else:
                    assert (1/r <= self.I.size()), f"Problem is not feasible" 
            self.A = intersection(self.I, S)            
        else:
            if self.I.size() == math.inf:
                assert l ==0.0, f"Problem is not feasible"
            else:
                if l!=0:
                    assert (1/l >= self.I.size() and 1/r <= self.I.size()), f"Problem is not feasible" 
                else:
                    assert (1/r <= self.I.size()), f"Problem is not feasible" 
        
        self.isfeasible = True
        
        

    def allinf(self, dfa: DFA, state: str) -> bool:
        b = True
        for e in [e for (s,e,c) in dfa.transitions if s==state]:
            b = b and (dfa.size(initial_state= e) == math.inf)
        return b

    def allfin(self, dfa: DFA, state: str) -> bool:
        b = True
        for e in [e for (s,e,c) in dfa.transitions if s==state]:
            b = b and (dfa.size(initial_state= e) != math.inf)
        return b


    def _generateImproviserTransitions(self, DFAtransitions: List = [], final_states: List = [], initial_state: str = 'q_0', rho: float = None, epsilon: float = None) -> List:
        if epsilon is None:
            epsilon = self.epsilon
        if rho is None:
            rho = self.rho
        dfa = DFA(transitions=DFAtransitions,final_states=final_states,initial_state=initial_state)
        t=[]
        if not dfa.size(initial_state=initial_state) == math.inf:
            for (s,e,c) in dfa.transitions: 
                if e in dfa.non_trivial_states and not dfa.size(initial_state=s) == 0:
                    t.append((s,e,c, float(dfa.size(initial_state=e))/float(dfa.size(initial_state=s))))
        else:
            for state in dfa.states:
                relevant_transitions = [(s,e,c) for (s,e,c) in dfa.transitions if s == state and e in dfa.non_trivial_states] 
                if self.allinf(dfa, state) or self.allfin(dfa, state) or self.rho >= 1/len(relevant_transitions):
                    for (s,e,c) in relevant_transitions:
                        t.append((s,e,c, 1/len(relevant_transitions))) 
                else:
                    pspace = 0
                    for (s,e,c) in [x for x in relevant_transitions if dfa.size(initial_state = x[1]) != math.inf]:
                        t.append((s,e,c,rho))
                        pspace += rho
                    for (s,e,c) in [x for x in relevant_transitions if dfa.size(initial_state = x[1]) == math.inf]:
                        t.append((s,e,c, (1-pspace)/len([x for x in relevant_transitions if dfa.size(initial_state = x[1]) == math.inf])))  
        return t


    def getImproviser(self) -> Improviser:
        ##INFINITE CASE
        if self.I.size() == math.inf:
            if self.soft_constraint:
                
                t = [] #List of all transitions in new Improviser
                intersec = intersection(self.I, self.A)
                diff = intersection(self.I, complement(self.A))
                for state in intersec.final:
                    t.append(("i"+state, "FINAL",""))
                for state in diff.final:
                    t.append(("d"+state, "FINAL", ""))
                for (start, end, char) in intersec.transitions:
                    t.append(('i'+start,'i'+end, char))
                for (start, end, char) in diff.transitions:
                    t.append(('d'+start,'d'+end, char))
                
                t.append(('q_0', 'i'+intersec.initial_state, ''))
                t.append(('q_0', 'd'+diff.initial_state, ''))                
                if diff.size() == math.inf:
                    intersectionImproviserTransitions = self._generateImproviserTransitions(DFAtransitions = [x for x in t if x[0][0]=='i'],final_states=["FINAL"],initial_state='i'+intersec.initial_state,rho= self.rho/(1-self.epsilon))
                    differenceImproviserTransitions = self._generateImproviserTransitions(DFAtransitions = [x for x in t if x[0][0]=='d'],final_states=["FINAL"],initial_state='d'+diff.initial_state,rho=self.rho/self.epsilon)    
                    return Improviser(transitions=intersectionImproviserTransitions+differenceImproviserTransitions + [('q_0','i'+intersec.initial_state,'',1-self.epsilon), ('q_0','d'+diff.initial_state,'',self.epsilon) ], final_state=["FINAL"])
                elif diff.size()*self.rho >= self.epsilon:
                    intersectionImproviserTransitions = self._generateImproviserTransitions(DFAtransitions = [x for x in t if x[0][0]=='i'],final_states=["FINAL"],initial_state='i'+intersec.initial_state,rho= self.rho/(1-self.epsilon))
                    differenceImproviserTransitions = [] if self.epsilon <= 0 else self._generateImproviserTransitions(DFAtransitions = [x for x in t if x[0][0]=='d'],final_states=["FINAL"],initial_state='d'+diff.initial_state,rho=self.rho/self.epsilon) 
                    return Improviser(transitions=intersectionImproviserTransitions+differenceImproviserTransitions + [('q_0','i'+intersec.initial_state,'',1-self.epsilon), ('q_0','d'+diff.initial_state,'',self.epsilon) ], final_state=["FINAL"])
                else:
                    intersectionImproviserTransitions = self._generateImproviserTransitions(DFAtransitions = [x for x in t if x[0][0]=='i'],final_states=["FINAL"],initial_state='i'+intersec.initial_state,rho= self.rho/(1-diff.size()*self.rho))
                    differenceImproviserTransitions = self._generateImproviserTransitions(DFAtransitions = [x for x in t if x[0][0]=='d'],final_states=["FINAL"],initial_state='d'+diff.initial_state,rho=self.rho/self.epsilon) 
                    return Improviser(transitions=intersectionImproviserTransitions+differenceImproviserTransitions + [('q_0','i'+intersec.initial_state,'',1-self.rho*diff.size()), ('q_0','d'+diff.initial_state,'',self.rho*diff.size()) ], final_state="FINAL")
                
            else:
                t = []
                for s in self.I.final:
                    t.append((s, "FINAL", ''))
                t+= self.I.transitions
                d = self._generateImproviserTransitions(DFAtransitions=t,final_states=["FINAL"],initial_state=self.I.initial_state)
                return Improviser(transitions = d, final_state=["FINAL"], initial_state= self.I.initial_state)
        
        #FINITE CASE
        else:
            if self.soft_constraint:
                t = [] #List of all transitions in new Improviser
                intersec = intersection(self.I, self.A)
                diff = intersection(self.I, complement(self.A))
                for state in intersec.final:
                    t.append(('i'+state, "FINAL", ''))
                for state in diff.final:
                    t.append(('d'+state, "FINAL", ''))
                for (start, end, char) in intersec.transitions:
                    t.append(('i'+start,'i'+end, char))
                for (start, end, char) in diff.transitions:
                    t.append(('d'+start,'d'+end, char))
                
                t.append(('q_0', 'i'+intersec.initial_state, ''))
                t.append(('q_0', 'd'+diff.initial_state, '')) 
                eopt = max(1-self.rho*intersec.size(), self.l*diff.size())
                intersectionImproviserTransitions = self._generateImproviserTransitions(DFAtransitions = [x for x in t if x[0][0]=='i'],final_states=["FINAL"],initial_state='i'+intersec.initial_state,rho= self.rho/(1-diff.size()*self.rho))
                differenceImproviserTransitions = [] if self.epsilon <=0 else self._generateImproviserTransitions(DFAtransitions = [x for x in t if x[0][0]=='d'],final_states=["FINAL"],initial_state='d'+diff.initial_state,rho=self.rho/self.epsilon) 
                return Improviser(transitions=intersectionImproviserTransitions+differenceImproviserTransitions + [('q_0','i'+intersec.initial_state,'',1-eopt), ('q_0','d'+diff.initial_state,'',eopt) ], final_state="FINAL")
            else:
                t = self._generateImproviserTransitions(DFAtransitions=self.I.transitions, final_states=self.I.final)
                return Improviser(t, final_state = self.I.final, initial_state=self.I.initial_state)