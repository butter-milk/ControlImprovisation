from rDFA import *
from CI import *


Hard_test = DFA(transitions= [('q_0','q_1','a'),('q_0', 'q_1', 'b'),('q_1', 'q_2', 'b'),('q_2','q_2','b')], final_states=['q_2','q_1'])
Soft_test = DFA(transitions= [('q_0','q_1','a'),('q_0', 'q_1', 'b'),('q_1', 'q_0', 'b'),('q_1','q_0','a')], final_states=['q_1'])
CI_test = CI(m=0,l=0,r=0.9,e=0,H=Hard_test, S=Soft_test)
Improviser_test = CI_test.getImproviser()
sample = Improviser_test.sample(100)
print(
    "max length of word generated: ", max(len(x) for x in sample), "\n",
    "number of unique words: ", len(set(sample)), "\n",
    "min length of word generated:", min([len(x) for x in sample])
)
print(set(sample))
