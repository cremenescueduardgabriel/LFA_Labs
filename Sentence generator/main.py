import gen
gen.parse('gen.txt')
sent = gen.generate_sentence(' ')
print(sent)
gen.parse('gen2.txt')
sent = gen.generate_sentence()
print(sent)
