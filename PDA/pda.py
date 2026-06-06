alphabet, states, final, start, gamma = [], [], [], [], []  # Stores SIGMA, STATES, FINAL, START, GAMMA from the PDA file
transitions = {}  # Nested dict: transitions[state][symbol][to_pop]
sections = {}  # Stores each section's raw data for debugging via get_sections()
stack = []  # Global stack used by the old delta() function (kept for backward compatibility)

def reset_globals():
    alphabet.clear(), states.clear(), final.clear(), start.clear(), gamma.clear(), transitions.clear(), stack.clear()
    sections.clear()

def strip_comment(line):
    # Removes /* */ block comments and # line comments from a line.
    # Returns the cleaned, stripped string.

    in_multiline = [False]  # Using list for mutability inside nested scope
    result = []
    i = 0
    while i < len(line):
        if not in_multiline[0] and i + 1 < len(line) and line[i:i + 2] == '/*':
            in_multiline[0] = True  # Entered a block comment
            i += 2
        elif in_multiline[0] and i + 1 < len(line) and line[i:i + 2] == '*/':
            in_multiline[0] = False  # Exited a block comment
            i += 2
        elif not in_multiline[0]:
            if line[i] == '#':
                break  # Line comment: stop here, discard the rest
            result.append(line[i])  # Normal character: keep it
            i += 1
        else:
            i += 1  # Inside a block comment: skip
    return ''.join(result).strip()


def section_handler(section, f):
    # Parses a section from the PDA file and stores the data in the global lists/dicts.
    # Each section reads lines until it hits the closing backslash.

    if section == 'SIGMA':
        # Reads the input alphabet symbols
        symbol = strip_comment(f.readline())
        while symbol != "\\":  # Backslash marks the end of the section
            if symbol:
                alphabet.append(symbol)
            symbol = strip_comment(f.readline())
        sections["SIGMA"] = alphabet

    if section == 'GAMMA':
        # Reads the stack alphabet symbols
        symbol = strip_comment(f.readline())
        while symbol != "\\":
            if symbol:
                gamma.append(symbol)
            symbol = strip_comment(f.readline())
        sections["GAMMA"] = gamma

    elif section == 'STATES':
        # Reads the list of state names
        state = strip_comment(f.readline())
        while state != '\\':
            if state:
                states.append(state)
            state = strip_comment(f.readline())
        sections["STATES"] = states

    elif section == 'FINAL':
        # Reads the accepting state(s)
        final_state = strip_comment(f.readline())
        while final_state != '\\':
            if final_state:
                final.append(final_state)
            final_state = strip_comment(f.readline())
        sections["FINAL"] = final

    elif section == 'DELTA':
        # Reads transition rules of the form: (state, symbol, pop){return (next_state, push)}
        transition = strip_comment(f.readline())
        while transition != '\\':
            transition = transition.split('{')

            # Parse the left side: (state, symbol, to_pop)
            state, symbol, to_pop = transition[0].strip('()').split(',')
            # Parse the right side: strip "return (...)" to get (next_state, push_values)
            values = transition[1].replace('return', '').strip()[:-1:1]
            values = values.strip('()').split(',')

            # Build the nested dictionary: transitions[state][symbol][to_pop]
            if state not in transitions:
                transitions[state] = {}
            if symbol not in transitions[state]:
                transitions[state][symbol] = {}
            transitions[state][symbol][to_pop] = tuple(values)

            transition = strip_comment(f.readline())  # Next transition rule
        sections["DELTA"] = transitions

    elif section == 'START':
        # Reads the initial state (only one, stored as a string)
        start.append(strip_comment(f.readline()))
        sections["START"] = start[0]


def delta(state, symbol, to_pop):  # Transition function (uses global stack)
    # Applies a transition rule using the global `stack`.
    # Reads/writes the global stack directly — only works when there's a single known execution path.
    state = str(state).strip('[\']')

    # Look up the rule in the parsed transitions table
    if state not in transitions:
        return None
    if symbol not in transitions[state]:
        return None
    if to_pop not in transitions[state][symbol]:
        return None

    # Pop from the global stack if required (to_pop != 'e')
    if to_pop != 'e':
        if not stack:
            return None
        if stack[-1] != to_pop:
            return None
        stack.pop()

    # Push result symbols onto the global stack (skipping 'e' = epsilon = no push)
    result = transitions[state][symbol][to_pop]
    next_state = result[0]
    for val in result[1:]:
        if val.strip() != 'e':
            stack.append(val.strip())

    return next_state


def delta_pure(state, symbol, to_pop, current_stack):
    # Like delta() but does not touch the global `stack` variable.
    # Takes a stack snapshot and returns (next_state, new_stack) or (None, None).
    # Needed because nondeterministic paths can have different stacks simultaneously;
    # each path works on its own copy without interfering with others.

    state = str(state).strip('[\']')
    # Look up the rule (same lookup as delta(), but doesn't touch global stack)
    if state not in transitions:
        return None, None
    if symbol not in transitions[state]:
        return None, None
    if to_pop not in transitions[state][symbol]:
        return None, None

    # Work on a copy of the caller's stack so the original is preserved
    new_stack = current_stack[:]
    if to_pop != 'e':
        if not new_stack:
            return None, None
        if new_stack[-1] != to_pop:
            return None, None
        new_stack.pop()

    # Push result symbols onto the local copy (skipping 'e')
    result = transitions[state][symbol][to_pop]
    next_state = result[0]
    for val in result[1:]:
        if val.strip() != 'e':
            new_stack.append(val.strip())
    return next_state, new_stack


def epsilon_closure_configs(configs):
    # Epsilon closure over (state, stack) configurations.
    # Starting from the given configs, follows all epsilon transitions
    # (rules with 'e' as the input symbol) and collects every reachable
    # (state, stack) pair.  Each config keeps its own stack copy so
    # nondeterministic branches don't interfere.

    result = list(configs)
    worklist = list(configs)
    while worklist:
        state, stack_snapshot = worklist.pop()
        if state in transitions and 'e' in transitions[state]:
            # For each epsilon rule from this state...
            for to_pop in transitions[state]['e']:
                next_state, new_stack = delta_pure(state, 'e', to_pop, stack_snapshot)
                if next_state is not None:
                    new_config = (next_state, new_stack)
                    if new_config not in result:
                        result.append(new_config)
                        worklist.append(new_config)
    return result


def epsilon_closure(states_list):
    # Epsilon closure over states only (uses global stack).
    # Explores epsilon transitions but backs up/restores the global stack
    # after each attempt.  Kept for backward compatibility.

    closure_states = set(states_list)
    worklist = list(states_list)
    while worklist:
        state = worklist.pop()
        if state not in transitions or 'e' not in transitions[state]:
            continue
        for to_pop in transitions[state]['e']:
            stack_backup = stack[:]
            next_state = delta(state, 'e', to_pop)
            if next_state is not None and next_state not in closure_states:
                closure_states.add(next_state)
                worklist.append(next_state)
            stack.clear()
            stack.extend(stack_backup)
    return list(closure_states)


def test(string):
    # Simulates the PDA on the input string.
    # Uses (state, stack) configuration tracking so nondeterministic branches are explored independently.
    # Accepts if any path ends in a final state after consuming all input.

    # Validate input symbols against the alphabet
    string = string.strip()
    for symbol in string:
        if symbol not in alphabet:
            print(f"Invalid symbol: {symbol}!")
            exit(1)

    # Start in the initial state with an empty stack, then follow
    # epsilon transitions to reach the initial configuration set
    start_state = start[0] if isinstance(start, list) else start
    configs = epsilon_closure_configs([(start_state, [])])

    # Process each input symbol one at a time
    for symbol in string:
        next_configs = []
        # For each current (state, stack) configuration, try all matching rules
        for state, stack_snapshot in configs:
            if state in transitions and symbol in transitions[state]:
                for to_pop in transitions[state][symbol]:
                    next_state, new_stack = delta_pure(state, symbol, to_pop, stack_snapshot)
                    if next_state is not None:
                        next_configs.append((next_state, new_stack))
        # Follow epsilon transitions from the newly reached configs
        configs = epsilon_closure_configs(next_configs)

    # Accept if any live configuration is in a final state
    for state, _ in configs:
        if state in final:
            print("Accepted")
            return
    print("Rejected")


def get_sections():
    # Prints all parsed sections for debugging
    for section in sections:
        print(f'{section}:')
        print(f'{sections[section]}\n')


def parse(file_name):
    # Reads a PDA specification file and populates the global data structures.
    # Format: sections start with '/' on its own line, followed by a section name,
    # followed by data lines, ending with '\' on its own line.
    # The file ends with 'END'.
    reset_globals()
    with open(file_name, 'r') as f:
        # Read the first line (should be '/' to start the first section)
        line = strip_comment(f.readline())
        while line != 'END':  # 'END' marks the end of the PDA file
            if line == '/':  # A forward slash starts a new section
                section = strip_comment(f.readline())  # Read the section name
                section_handler(section, f)  # Parse all lines in this section
            line = strip_comment(f.readline())  # Read the next line