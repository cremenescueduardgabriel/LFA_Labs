import nfa  # Contains the parser for the NFA.txt file

nfa.parse(input('Input NFA file: '))
with open(input('Input file name: '),'r') as input_file:
    nfa.test(input_file.read())          # Reads the string to be checked


