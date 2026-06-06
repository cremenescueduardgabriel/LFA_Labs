import pda  # Contains the parser for the PDA.txt file

pda.parse(input('Input PDA file: '))
with open(input('Input file name: '),'r') as input_file:
    pda.test(input_file.read())          # Reads the string to be checked


