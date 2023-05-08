import itertools
from collections import Counter
from datetime import datetime
import uuid
import tempfile
from graphviz import Digraph

class Consts():
    EPSILON = "$"

def find_permutation(state_list, current_state):
    for state in state_list:
        if Counter(current_state) == Counter(state):
            return state
    return current_state

def get_epsilon_closure(nfa, dfa_states, state):
    closure_states = []
    state_stack = [state]
    while len(state_stack) > 0:
        current_state = state_stack.pop(0)
        closure_states.append(current_state)
        alphabet = Consts.EPSILON
        if nfa["transition_function"][current_state][alphabet] not in closure_states:
            state_stack.extend(nfa["transition_function"][current_state][alphabet])
    closure_states = tuple(set(closure_states))
    return find_permutation(dfa_states, closure_states)

def nfa_to_dfa(nfa):
    dfa = {}
    
    dfa["states"] = ["phi"]
    for r in range(1, len(nfa["states"])+1):
        dfa["states"].extend(itertools.combinations(nfa["states"], r))
    
    # calculate epsilon closure of all states of nfa
    epsilon_closure = {}
    for state in nfa["states"]:
        epsilon_closure[state] = get_epsilon_closure(nfa, dfa["states"], state)
    dfa["initial_state"] =  epsilon_closure[nfa["initial_state"]]
    
    dfa["final_states"] = []
    for state in dfa["states"]:
        if state != "phi":
            for nfa_state in state:
                if nfa_state in nfa["final_states"]:
                    dfa["final_states"].append(state)
                    break

    # dfa["alphabets"] = ["a", "b"]
    dfa["alphabets"] = list(filter(lambda x:x!=Consts.EPSILON, nfa["alphabets"]))

    dfa["transition_function"]= {}
    counter = 0
    for state in dfa["states"]:
        #if counter%100 == 0: print(counter,"z",len(dfa["states"]))
        counter += 1
        dfa["transition_function"][state] = {}   
        for alphabet in dfa["alphabets"]:
            if state == "phi":
                dfa["transition_function"][state][alphabet] = state
            else:
                transition_states = []
                if len(state) == 1:
                    nfa_state = state[0]
                    next_nfa_states = nfa["transition_function"][nfa_state][alphabet]
                    for next_nfa_state in next_nfa_states:
                        transition_states.extend(epsilon_closure[next_nfa_state])
                else:
                    for nfa_state in state:
                        nfa_state = tuple([nfa_state])
                        if dfa["transition_function"][nfa_state][alphabet] != "phi":
                            transition_states.extend(dfa["transition_function"][nfa_state][alphabet])
                transition_states = tuple(set(transition_states))

                if len(transition_states) == 0:
                    dfa["transition_function"][state][alphabet] = "phi"
                else:
                    # find permutation of transition states in states
                    dfa["transition_function"][state][alphabet] = find_permutation(dfa["states"], transition_states)

    state_stack = [dfa["initial_state"]]
    dfa["reachable_states"] = []
    while len(state_stack) > 0:
        current_state = state_stack.pop(0)
        if current_state not in dfa["reachable_states"]:
            dfa["reachable_states"].append(current_state)
        for alphabet in dfa["alphabets"]:
            next_state = dfa["transition_function"][current_state][alphabet]
            if next_state not in dfa["reachable_states"]:
                state_stack.append(next_state)
                
    dfa["final_reachable_states"] = list(set(dfa["final_states"]) & set(dfa["reachable_states"]))

    return dfa

def dfa_to_efficient_dfa(dfa):
    table = {}
    new_table = {}
    for state in dfa["reachable_states"]:
        table[state] = {}
        new_table[state] = {}
        for again_state in dfa["reachable_states"]:
            table[state][again_state] = 0
            new_table[state][again_state] = 0
            
    # populate final, non final pairs
    for state in dfa["reachable_states"]:
        if state not in dfa["final_reachable_states"]:
            for again_state in dfa["final_reachable_states"]:
                table[state][again_state] = 1
                new_table[state][again_state] = 1
                table[again_state][state] = 1
                new_table[again_state][state] = 1

    while True:
        for state_1 in dfa["reachable_states"]:
            for state_2 in dfa["reachable_states"]:
                for alphabet in dfa["alphabets"]:
                    # transition for an alphabet
                    if new_table[state_1][state_2] == 0:
                        next_state_1 = dfa["transition_function"][state_1][alphabet]
                        next_state_2 = dfa["transition_function"][state_2][alphabet]
                        new_table[state_1][state_2] = table[next_state_1][next_state_2]
                        new_table[state_2][state_1] = table[next_state_1][next_state_2]
                    else:
                        break

        changed = False
        # check if something changed or not
        for state_1 in dfa["reachable_states"]:
            for state_2 in dfa["reachable_states"]:
                if new_table[state_1][state_2] == 1 and table[state_1][state_2] == 0:
                    table[state_1][state_2] = new_table[state_1][state_2]
                    changed = True
        if not changed:
            break
    
    # implementing union find to merge
    parent = {}
    for state in dfa["reachable_states"]:
        # parent[state] = state
        parent[state] = {"value": state, "states": [state]}

    def get_parent(current_state, all=False):
        parent_state = parent[current_state]
        while parent_state["value"] != current_state:
            current_state = parent_state["value"]
            parent_state = parent[current_state]
        if all:
            return parent_state
        else:
            return tuple(parent_state["states"])

    for state_1 in dfa["reachable_states"]:
        for state_2 in dfa["reachable_states"]:
            if state_1 != state_2 and table[state_1][state_2] == 0:
                # merge state 1 and 2
                parent_state_1 = get_parent(state_1, all=True)
                parent_state_2 = get_parent(state_2, all=True)
                parent[parent_state_2["value"]]["value"] = parent_state_1["value"]
                parent[parent_state_1["value"]]["states"] = list(set(parent_state_1["states"]) | set(parent_state_2["states"]))

    # now we can create our new dfa
    new_dfa = {}
    new_dfa["states"] = list(set([get_parent(state) for state in dfa["reachable_states"]]))
    new_dfa["initial_state"] = get_parent(dfa["initial_state"])
    new_dfa["final_states"] = list(set([get_parent(state) for state in dfa["final_reachable_states"]]))
    # new_dfa["alphabets"] = ["a", "b"]
    new_dfa["alphabets"] = dfa["alphabets"]

    new_dfa["transition_function"]= {}
    for state in new_dfa["states"]:
        new_dfa["transition_function"][state] = {}
        for alphabet in new_dfa["alphabets"]:
            new_dfa["transition_function"][state][alphabet] = get_parent(dfa["transition_function"][state[0]][alphabet])

    # extras
    new_dfa["reachable_states"]  = new_dfa["states"]
    new_dfa["final_reachable_states"]  = new_dfa["final_states"]
    return new_dfa


priority = {'*': 3, '?': 2, '+': 1}

def is_alphabet(c):
    return c not in priority.keys() and c not in ['(', ')']

def add_concat_symbol(reg_exp):
    '''
    Replace 'and' operation with ? symbol
    '''
    new_reg_exp = ""
    for current_char in reg_exp:
        if(len(new_reg_exp)>0):
            prev_char = new_reg_exp[len(new_reg_exp)-1]
            if (prev_char == ')' or is_alphabet(prev_char) or prev_char == '*') and (current_char == '('  or is_alphabet(current_char)):
                new_reg_exp += "?"
        new_reg_exp += current_char
    return new_reg_exp

def regex_to_postfix(reg_exp):
    postfix_exp=""
    operator_stack = []

    reg_exp = add_concat_symbol(reg_exp)
    
    # shunting yard algorithm
    for current_char in reg_exp:
        if is_alphabet(current_char):
            postfix_exp += current_char
        elif current_char == '(':
            operator_stack.append(current_char)
        elif current_char == ')':
            top = operator_stack.pop()
            while top != '(':
                postfix_exp += top
                top = operator_stack.pop()
        else:
            if len(operator_stack) == 0:
                operator_stack.append(current_char)
            else:
                top = operator_stack[len(operator_stack)-1]
                while top!='(' and priority[top] >= priority[current_char]:
                    postfix_exp += top 
                    operator_stack.pop()
                    if len(operator_stack) > 0:
                        top = operator_stack[len(operator_stack)-1]
                    else:
                        break
                operator_stack.append(current_char)
    while len(operator_stack) != 0:
        postfix_exp += operator_stack.pop()

    return postfix_exp

def get_alphabet_nfa(character, alphabets):
    nfa = {}
    nfa["states"] = [uuid.uuid4(), uuid.uuid4()]
    nfa["initial_state"] = nfa["states"][0]
    nfa["final_states"] = [nfa["states"][1]]
    nfa["alphabets"] = alphabets
    nfa["transition_function"]= {}
    for state in nfa["states"]:
        nfa["transition_function"][state] = {}
        for alphabet in nfa["alphabets"]:
            nfa["transition_function"][state][alphabet] = []
    nfa["transition_function"][nfa["initial_state"]][character] = nfa["final_states"] 
    return nfa

def concat_nfa(nfa1, nfa2):
    nfa = {}

    nfa["states"] = []
    nfa["states"].extend(nfa1["states"])
    nfa["states"].extend(nfa2["states"])

    nfa["initial_state"] = nfa1["initial_state"]
    nfa["final_states"] = nfa2["final_states"]
    nfa["alphabets"] = list(set(nfa1["alphabets"]) | set(nfa2["alphabets"]))

    nfa["transition_function"]= {}
    for state in nfa["states"]:
        if state in nfa1["states"]:
            nfa["transition_function"][state] = nfa1["transition_function"][state]
        elif state in nfa2["states"]:
            nfa["transition_function"][state] = nfa2["transition_function"][state]

    # connect final states of nfa1 with start state of nfa2 using epsilon transition
    for state in nfa1["final_states"]:
        nfa["transition_function"][state][Consts.EPSILON].append(nfa2["initial_state"])

    return nfa

def union_nfa(nfa1, nfa2):
    nfa = {}

    nfa["states"] = [uuid.uuid4()]
    nfa["states"].extend(nfa1["states"])
    nfa["states"].extend(nfa2["states"])

    nfa["initial_state"] = nfa["states"][0]
    nfa["final_states"] = []
    nfa["final_states"].extend(nfa1["final_states"])
    nfa["final_states"].extend(nfa2["final_states"])
    nfa["alphabets"] = list(set(nfa1["alphabets"]) | set(nfa2["alphabets"]))

    nfa["transition_function"]= {}
    for state in nfa["states"]:
        if state in nfa1["states"]:
            nfa["transition_function"][state] = nfa1["transition_function"][state]
        elif state in nfa2["states"]:
            nfa["transition_function"][state] = nfa2["transition_function"][state]
        else:
            nfa["transition_function"][state] = {}
            for alphabet in nfa["alphabets"]:
                nfa["transition_function"][state][alphabet] = []
    
    # connecting start state to start state of nfa 1 and nfa 2 through epsilon move
    nfa["transition_function"][nfa["initial_state"]][Consts.EPSILON].extend([nfa1["initial_state"], nfa2["initial_state"]])
    return nfa

def cleene_star_nfa(nfa1):
    nfa = {}

    nfa["states"] = [uuid.uuid4()]
    nfa["states"].extend(nfa1["states"])
    nfa["states"].append(uuid.uuid4())

    nfa["initial_state"] = nfa["states"][0]
    nfa["final_states"] = [nfa["states"][  len(nfa["states"])-1 ]]
    nfa["alphabets"] =  nfa1["alphabets"]
    
    nfa["transition_function"]= {}
    for state in nfa["states"]:
        if state in nfa1["states"]:
            nfa["transition_function"][state] = nfa1["transition_function"][state]
        else:
            nfa["transition_function"][state] = {}
            for alphabet in nfa["alphabets"]:
                nfa["transition_function"][state][alphabet] = []

    # connecting start state to start state of nfa 1 through epsilon move
    nfa["transition_function"][nfa["initial_state"]][Consts.EPSILON].append(nfa1["initial_state"])

    for final_state in nfa1["final_states"]:
        # connecting final states of nfa1 to start state of nfa1 through epsilon move
        nfa["transition_function"][final_state][Consts.EPSILON].append(nfa1["initial_state"])
        # connecting final states of nfa1 to final states of nfa through epsilon move
        nfa["transition_function"][final_state][Consts.EPSILON].extend(nfa["final_states"])

    # connecting start state to final state of nfa through epsilon move
    nfa["transition_function"][nfa["initial_state"]][Consts.EPSILON].extend(nfa["final_states"])
    return nfa
    
def regex_to_nfa(reg_exp):
    postfix_exp = regex_to_postfix(reg_exp)
    
    nfa_stack = []
    alphabets = []
    for character in postfix_exp:
        if is_alphabet(character):
            if character not in alphabets:
                alphabets.append(character)
    if Consts.EPSILON not in alphabets:
        alphabets.append(Consts.EPSILON)
    for character in postfix_exp:
        if is_alphabet(character):
            nfa_stack.append(get_alphabet_nfa(character, alphabets))
        elif character == "?": # concat
            nfa2 = nfa_stack.pop()
            nfa1 = nfa_stack.pop()
            nfa_stack.append(concat_nfa(nfa1, nfa2))
        elif character == "+": # union
            nfa2 = nfa_stack.pop()
            nfa1 = nfa_stack.pop()
            nfa_stack.append(union_nfa(nfa1, nfa2))
        elif character == "*": # cleene star
            nfa1 = nfa_stack.pop()
            nfa_stack.append(cleene_star_nfa(nfa1))
    nfa = nfa_stack.pop()
    return nfa


def union_regex(a, b):

    def split_into_unique(string):
        i=0
        j=0
        brac = 0
        result = []
        for c in string:
            if c == "(":
                brac+=1
            elif c == ")":
                brac-=1
            if brac == 0:
                if c == "+":
                    result.append(string[i:j])
                    i = j+1
            j+=1
        result.append(string[i:j])
        result = list(set(result))
        if "" in result:
            result.remove("")
        return result
    
    split_a = split_into_unique(a)
    split_b = split_into_unique(b)

    merged = list(set(split_a) | set(split_b))
    return "+".join(merged)

def concat_regex(a, b):
    if a=="" or b=="":
        return ""
    elif a[len(a)-1]==Consts.EPSILON:
        return "{}{}".format(a[:-1], b)
    elif b[0]==Consts.EPSILON:
        return "{}{}".format(a, b[2:])
    else:
        return "{}{}".format(a, b)

def cleene_star_regex(a):
    if a == Consts.EPSILON:
        return Consts.EPSILON
    elif a == "":
        return Consts.EPSILON
    else:
        return "{}*".format(bracket(a))

def bracket(a):
    # if a in [Consts.EPSILON, "", "a", "b"]:
    if len(a) <= 1:
        return a
    else:
        return "({})".format(a)

def dfa_to_regex(dfa):
    L = {}

    # find dead states
    is_not_dead = {}

    def is_final(state, visited):
        if state in dfa["final_reachable_states"]:
            return True
        else:
            visited.append(state)
            for alphabet in dfa["alphabets"]:
                next_state = dfa["transition_function"][state][alphabet]
                if next_state not in visited:
                    if is_final(next_state, visited) == True:
                        return True
        return False

    for state in dfa["reachable_states"]:
        is_not_dead[state] = is_final(state, [])

    # make new start state
    gnfa = {}
    gnfa["initial_state"] = uuid.uuid4()
    gnfa["final_states"] =  [uuid.uuid4()]
    gnfa["initial_state"] = "P0"
    gnfa["final_states"] =  ["P1"]

    gnfa["states"] = [gnfa["initial_state"]]
    gnfa["states"].extend(dfa["reachable_states"])
    gnfa["states"].extend(gnfa["final_states"])

    gnfa["alphabets"] = list(set(dfa["alphabets"]) | set([Consts.EPSILON]))


    gnfa["transition_function"]= {}
    # attach initial state of gnfa to initial state of dfa with epsilon transition
    gnfa["transition_function"][gnfa["initial_state"]] = {Consts.EPSILON: dfa["initial_state"]}

    # append rest of the transitions of dfa to gnfa
    for state in dfa["reachable_states"]:
        gnfa["transition_function"][state] = {}
        for alphabet in dfa["alphabets"]:
            next_state = dfa["transition_function"][state][alphabet]
            # appending only those which are not reachable from themselves from 
            if is_not_dead[next_state]:
                gnfa["transition_function"][state][alphabet] = next_state

    # attach final states of dfs to final state of gnfa with epsilon transition
    for state in dfa["final_reachable_states"]:
        gnfa["transition_function"][state][Consts.EPSILON] = gnfa["final_states"][0]

    gnfa["transition_function"][gnfa["final_states"][0]] = {}


    for state_1 in gnfa["states"]:
        L[state_1] = {}
        for state_2 in gnfa["states"]:
            L[state_1][state_2] = []
        for alphabet, next_state in gnfa["transition_function"][state_1].items():
            L[state_1][next_state].append(alphabet)
    visited = []

    reachable_non_dead_states = filter(lambda x: is_not_dead[x], dfa["reachable_states"])

    # removing states one by one gnfa["states"]:
    for chosen_state in reachable_non_dead_states:
        # for cleene star

        string = ""
        for transition_string in L[chosen_state][chosen_state]:
            string = union_regex(string, transition_string)
        if string != "":
            string = cleene_star_regex(string)
            L[chosen_state][chosen_state] = [string]

            # for appending star with next values
            next_states =  list(gnfa["transition_function"][chosen_state].items())
            for alphabet, next_state in next_states:
                del gnfa["transition_function"][chosen_state][alphabet]
                if chosen_state != next_state:
                    for ind in range(len(L[chosen_state][next_state])):
                        L[chosen_state][next_state][ind] = concat_regex(string, L[chosen_state][next_state][ind])
                        gnfa["transition_function"][chosen_state][L[chosen_state][next_state][ind]] = next_state
                    
        # concatenating prev state of chosen state to next states of chosen state
        for prev_state in gnfa["states"]:
            if prev_state != chosen_state:
                prev_next_states = list(gnfa["transition_function"][prev_state].items())
                
                for alphabet, next_state in prev_next_states:
                    if next_state == chosen_state:
                        # connecting prev_state to next of chosen
                        all_new_strings = []
                        for chosen_state_alphabet, chosen_next_state in gnfa["transition_function"][chosen_state].items():
                            new_strings = []
                            for prev_to_chosen in L[prev_state][chosen_state]:
                                chosen_to_next = chosen_state_alphabet
                                string = concat_regex(prev_to_chosen, chosen_to_next)
                                gnfa["transition_function"][prev_state][string] = chosen_next_state
                                new_strings.append(string)
                                all_new_strings.append(string)

                            L[prev_state][chosen_next_state].extend(new_strings)
                        if alphabet not in all_new_strings:
                            del gnfa["transition_function"][prev_state][alphabet]
    regex = ""
    for transition_string in L[gnfa["initial_state"]][gnfa["final_states"][0]]:
        regex = union_regex(regex, transition_string)
    regex = bracket(regex)
    return regex


def draw_nfa(nfa, title=""):
    state_name = {}
    i = 0
    for state in nfa["states"]:
        state_name[state] = "q{}".format(i).translate(str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉"))
        i+=1

    g = Digraph()
    g.attr(rankdir='LR')

    if title == "":
        title = r'\n\nNFA'
    else:
        title = r'\n\nNFA : '+title
    g.attr(label=title, fontsize='30')

    # mark goal states
    g.attr('node', shape='doublecircle')
    for state in nfa['final_states']:
        g.node(state_name[state])

    # add an initial edge
    g.attr('node', shape='none')
    g.node("")
    
    g.attr('node', shape='circle')
    g.edge("", state_name[nfa["initial_state"]])

    for state in nfa["states"]:
        for character in nfa["transition_function"][state]:
            for transition_state in nfa["transition_function"][state][character]:
                g.edge(state_name[state], state_name[transition_state], label= character if character != Consts.EPSILON else "\u03B5")

    g.view(tempfile.mktemp('.gv'))  

def draw_dfa(dfa, title=""):
    state_name = {}
    i = 0
    for state in dfa["reachable_states"]:
        if state == "phi":
            state_name[state] = "\u03A6"
        else:
            state_name[state] = "q{}".format(i).translate(str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉"))
            i+=1

    g = Digraph()
    g.attr(rankdir='LR')

    if title == "":
        title = r'\n\nDFA'
    else:
        title = r'\n\nDFA : '+title
    g.attr(label=title, fontsize='30')

    # mark goal states
    g.attr('node', shape='doublecircle')
    for state in dfa["final_reachable_states"]:
        g.node(state_name[state])

    # add an initial edge
    g.attr('node', shape='none')
    g.node("")
    
    g.attr('node', shape='circle')
    g.edge("", state_name[dfa["initial_state"]])

    for state in dfa["reachable_states"]:
        for character in dfa["transition_function"][state].keys():
            transition_state = dfa["transition_function"][state][character]
            g.edge(state_name[state], state_name[transition_state], label= character)

    g.view(tempfile.mktemp('.gv'))
