import markovify

with open("pokemon_names.txt") as f:
    text = f.readlines()


class PokemonText(markovify.Text):
    def word_split(self, sentence):
        return list(sentence)

    def word_join(Self, characters):
        return "".join(characters)


name_model = PokemonText(text)

for i in range(5):
    print(name_model.make_short_sentence(15))
