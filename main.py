import dfa  # Contains the parser for the DFA.txt file

dfa.parse(input('Input DFA file: '))
with open(input('Input file name: '),'r') as input_file:
    dfa.test(input_file.read())          # Reads the string to be checked


