import dfa
dfa.parse(input('Input game config file: '))

moves = input('Input movement: ')

state = dfa.start[0]
for symbol in moves:
    state = dfa.delta(state, symbol)

if state in dfa.final:
    print(f'You won! You will go to {state}.')
else:
    print('You lost...')
