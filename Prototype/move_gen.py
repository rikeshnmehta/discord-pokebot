a_file = open("moves.txt")
file_contents = a_file.read()
moves = file_contents.splitlines()

scenarios = open("scenarios.txt", "a")
for move in moves:
    sentence = "Enemy POKEMON uses " + move + "\n"
    scenarios.write(sentence)

scenarios.close()
