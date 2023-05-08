import automata_lib

states = ["q0","qF"]
terminals = ["S110","S101","S011","U110","U101",
             "U011","D110","D101","D011","F110","F101","F011"]
transitions = []
transition_function = dict()

f = open("automataG.txt", "r")
#f = open("automataGprime.txt","r")

delta = f.readlines()
f.close()
transitions_list = []

for d in delta:
    dd = list(map(str,d[:-1].split(' ')))
    if dd[0] != "q0" and dd[0] != "qF":
        if dd[0] not in states:
            states.append(dd[0])
    if dd[2] != "q0" and dd[2] != "qF":
        if dd[2] not in states:
            states.append(dd[2])
    transitions_list.append((dd[0],dd[1],dd[2]))

for state in states:
    transition_function[state] = dict()
    transition_function[state]['$'] = []
    for term in terminals:
        transition_function[state][term] = []

for transition in transitions_list:
    if transition[0] in states:
        if transition[2] in states:
            transition_function[transition[0]][transition[1]].append(transition[2])

NFA2 = {
    "states": list(states),
    "initial_state": "q0",
    "final_states": ["qF"],
    "alphabets": ["$"] + list(terminals),
    "transition_function": transition_function
}
DFA2 = automata_lib.nfa_to_dfa(NFA2)
A_G = automata_lib.dfa_to_efficient_dfa(DFA2)



NFA1 = {
    "states": ["q0 q0","qS q0","qS q1","qU q0",
               "qU q1", "qD q0","qD q1","qF q0"],
    "initial_state": "q0 q0",
    "final_states": ["qF q0"],
    "alphabets": ["$","S110","S101","S011","U110","U101","U011",
                      "D110","D101","D011","F110","F101","F011"],
    "transition_function": {
        "q0 q0": {
            "$": [],
            "S110": ["qS q0"],
            "S101": ["qS q1"],
            "S011": ["qS q1"],
            "U110": [],
            "U101": [],
            "U011": [],
            "D110": [],
            "D101": [],
            "D011": [],
            "F110": [],
            "F101": [],
            "F011": []
        },
        "qS q0": {
            "$": [],
            "S110": [],
            "S101": [],
            "S011": [],
            "U110": [],
            "U101": [],
            "U011": ["qU q1"],
            "D110": [],
            "D101": [],
            "D011": ["qD q1"],
            "F110": [],
            "F101": [],
            "F011": ["qF q0"]
        },
        "qS q1": {
            "$": [],
            "S110": [],
            "S101": [],
            "S011": [],
            "U110": ["qU q0"],
            "U101": ["qU q1"],
            "U011": [],
            "D110": ["qD q0"],
            "D101": ["qD q1"],
            "D011": [],
            "F110": ["qF q0"],
            "F101": ["qF q0"],
            "F011": []
        },
        "qU q0": {
            "$": [],
            "S110": [],
            "S101": [],
            "S011": [],
            "U110": [],
            "U101": [],
            "U011": [],
            "D110": [],
            "D101": [],
            "D011": ["qS q1"],
            "F110": [],
            "F101": [],
            "F011": []
        },
        "qU q1": {
            "$": [],
            "S110": [],
            "S101": [],
            "S011": [],
            "U110": [],
            "U101": [],
            "U011": [],
            "D110": ["qS q0"],
            "D101": ["qS q1"],
            "D011": [],
            "F110": [],
            "F101": [],
            "F011": []
        },
        "qD q0": {
            "$": [],
            "S110": [],
            "S101": [],
            "S011": [],
            "U110": [],
            "U101": [],
            "U011": ["qS q1"],
            "D110": [],
            "D101": [],
            "D011": [],
            "F110": [],
            "F101": [],
            "F011": []
        },
        "qD q1": {
            "$": [],
            "S110": [],
            "S101": [],
            "S011": [],
            "U110": ["qS q0"],
            "U101": ["qS q1"],
            "U011": [],
            "D110": [],
            "D101": [],
            "D011": [],
            "F110": [],
            "F101": [],
            "F011": []
        },
        "qF q0": {
            "$": [],
            "S110": [],
            "S101": [],
            "S011": [],
            "U110": [],
            "U101": [],
            "U011": [],
            "D110": [],
            "D101": [],
            "D011": [],
            "F110": [],
            "F101": [],
            "F011": []
        }
    },
    "reachable_states": ["$","q0 q0","qS q0","qF q0", "qS q1", "qU q1", "qD q1"],
    "final_reachable_states": ["qF q0"]
}
DFA1 = automata_lib.nfa_to_dfa(NFA1)
A_R = automata_lib.dfa_to_efficient_dfa(DFA1)


intersection_accepting_states = set()
intersection_transitions = []

for state1 in A_R["states"]:
    for state2 in A_G["states"]:
        if state1 in A_R["final_states"] and state2 not in A_G["final_states"]:
            intersection_accepting_states.add((state1,state2))
        for term in A_R["alphabets"]:
            nextstate1 = A_R["transition_function"][state1][term]
            nextstate2 = A_G["transition_function"][state2][term]
            intersection_transitions.append(((state1,state2),term,(nextstate1,nextstate2)))
            
reachable = {(A_R["initial_state"],A_G["initial_state"])}
query = [((A_R["initial_state"],A_G["initial_state"]),"")]

success = True

while len(query) > 0:
    state, word = query.pop()
    for transition in intersection_transitions:
        if transition[0] == state and transition[2] not in reachable:
            if transition[2] in intersection_accepting_states:
                print("L(A_R) is not subset of L(A_G), word", word, "is in L(A_R) but not in L(A_G)")
                success = False
            reachable.add(transition[2])
            query.append((transition[2],word + transition[1]))

if success:
    print("L(A_R) is subset of L(A_G)")
