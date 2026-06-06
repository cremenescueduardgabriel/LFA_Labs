alphabet, states, final, start = [], [], [], []  # Initialized as lists for appending in the handler
transitions = {}  # Initialized as dictionary for ease of access in the "delta" function
sections = {}

def reset_globals():
    alphabet.clear(), states.clear(), final.clear(), start.clear(), transitions.clear()
    sections.clear()

def strip_comment(line):
    in_multiline = [False]
    result = []
    i = 0
    while i < len(line):
        if not in_multiline[0] and i + 1 < len(line) and line[i:i+2] == '/*':
            in_multiline[0] = True
            i += 2
        elif in_multiline[0] and i + 1 < len(line) and line[i:i+2] == '*/':
            in_multiline[0] = False
            i += 2
        elif not in_multiline[0]:
            if line[i] == '#':
                break
            result.append(line[i])
            i += 1
        else:
            i += 1
    return ''.join(result).strip()

def section_handler(section,f):
    if section == 'SIGMA':
        symbol = strip_comment(f.readline())
        while symbol != "\\":                   # Checks if the section has ended
            if symbol:
                alphabet.append(symbol)             # Appends the given symbols to the alphabet
            symbol = strip_comment(f.readline())
        sections["SIGMA"] = alphabet

    elif section == 'STATES':
        state = strip_comment(f.readline())
        while state != '\\':                    # Checks if the section has ended
            if state:
                states.append(state)                # Appends the given state to the states list
            state = strip_comment(f.readline())
        sections["STATES"] = states

    elif section == 'FINAL':
        final_state = strip_comment(f.readline())
        while final_state != '\\':              # Checks if the section has ended
            if final_state:
                final.append(final_state)           # Appends the given final state to the final list
            final_state = strip_comment(f.readline())
        sections["FINAL"] = final

    elif section == 'DELTA':
        transition = strip_comment(f.readline())       # Reads the transition string
        while transition != '\\':               # Checks if the section has ended
            transition = transition.split('{')  # Splits the transition string into two for the next steps

            state, symbol = transition[0].strip('()').split(',')        # Extracts the state and symbol from the first half
            values = transition[1].replace('return','').strip()[:-1:1]   # Extracts the return values from the second half
            values = values.strip('()').split(',')   # Splits comma-separated values into a list

            if state not in transitions:
                transitions[state] = {}             # Builds a dictionary for every state

            if symbol not in transitions[state]:
                transitions[state][symbol] = values      # Assigns return values for the transition
            else:
                for v in values:
                    if v not in transitions[state][symbol]:
                        transitions[state][symbol].append(v)

            transition = strip_comment(f.readline())       # Reads the next transition string
        sections["DELTA"] = transitions

    elif section == 'START':
        start.append(strip_comment(f.readline()))          # Reads the unique starting state
        sections["START"] = start[0]

def delta(state,symbol):              # Transition function
    state = str(state)
    if state in transitions and symbol in transitions[state]:
        return transitions[state][symbol]
    return []

def epsilon_closure(states_list):
    closure = set(states_list)
    stack = list(states_list)
    while stack:
        state = stack.pop()
        eps_transitions = delta(state, 'e')
        for s in eps_transitions:
            if s not in closure:
                closure.add(s)
                stack.append(s)
    return list(closure)

def test(string):
    string = string.strip()
    for symbol in string:               # Checks if the string is valid
        if symbol not in alphabet:
            raise ValueError(f"Invalid symbol: {symbol}!")


    start_state = start[0] if isinstance(start, list) else start
    current_states = epsilon_closure([start_state])

    for symbol in string:
        next_states = []
        for state in current_states:
            next_states.extend(delta(state, symbol))
        current_states = epsilon_closure(next_states)

    for state in current_states:
        if state in final:
            print("Accepted")
            return

    print("Rejected")

def get_sections():
    for section in sections:
        print(f'{section}:')
        print(f'{sections[section]}\n')

def parse(file_name):
    reset_globals()
    with open(file_name,'r') as f:
        line = strip_comment(f.readline())     # Reads the first line
        while line != 'END':                    # Checks if "line" has reached the end of the NFA
            if line == '/':                     # If a new section started:
                section = strip_comment(f.readline())  # - gets section name
                section_handler(section,f)        # - passes it to the parser
            line = strip_comment(f.readline())         # Reads next line
    if start[0] not in states:
        raise ValueError(f"Start state '{start[0]}' not in states list")
    for s in final:
        if s not in states:
            raise ValueError(f"Final state '{s}' not in states list")