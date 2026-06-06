import random

alphabet, rules, variables = [], {}, []
sections = {}

def reset_globals():
    alphabet.clear(), rules.clear(), variables.clear(), sections.clear()

def get_sections():
    for section in sections:
        print(f'{section}:')
        print(f'{sections[section]}\n')

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

    if section == 'VARIABLES':
        string = strip_comment(f.readline())
        while string != "\\":
            if string not in variables:
                variables.append(string)

            string = strip_comment(f.readline())
        sections["VARIABLES"] = variables

    if section == 'RULES':
        string = strip_comment(f.readline())
        while string != "\\":
            var, rule = string.split('=')

            if var in variables:
                if var not in rules.keys():
                    rules[var] = []

                if rule not in rules[var]:
                    rules[var].append(rule)

            string = strip_comment(f.readline())
        sections["RULES"] = rules

def parse(file_name):
    reset_globals()
    with open(file_name,'r') as f:
        line = strip_comment(f.readline())     # Reads the first line
        while line != 'END':                    # Checks if "line" has reached the end of the DFA
            if line == '/':                     # If a new section started:
                section = strip_comment(f.readline())  # - gets section name
                section_handler(section,f)        # - passes it to the parser
            line = strip_comment(f.readline())         # Reads next line

def generate_word(var):
    pos = random.randint(0, len(rules[var]) - 1)    # Generates a random rule from rules[var]
    return rules[var][pos]

def replace_vars(base, sep = ''):   # Replaces all variables in base with a random rule, separated by sep
    result = ''
    for char in base:
        if char in variables:
            result += generate_word(char) + sep
        else:
            result += char
    return result

def check_vars(sentence):   # Checks if there are still unreplaced variables in the sentence
    for char in sentence:
        if char in variables:
            return True
    return False

def generate_sentence(sep = '', max_steps = 1000):  # Generates a full sentence randomly using the rules
    base = generate_word(variables[0])
    sent = replace_vars(base,sep)
    steps = 0
    while check_vars(sent):
        if steps > max_steps:
            raise RecursionError("Too many substitutions!") # Safeguard against infinite recursion
        sent = replace_vars(sent, sep)
        steps += 1
    if sep and sent.endswith(sep):
        sent = sent[0:len(sent)-1]
    return sent
