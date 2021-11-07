import markovify

with open("before_battle.txt") as f:
    text = f.read()

text_model = markovify.Text(text)

print(text_model.make_sentence())
