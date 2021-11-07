import glob
import discord
import random
from discord.ext import commands
import markovify

HEALTH_MAX = 100
HEALTH_MIN = 50
ATTITUDE = 0.15  # From 0 to 1
TEXT_TO_SPEECH = False
TOKEN = "OTA0ODg1MTkyODkwNjc5MzA2.YYCCAQ.uCQKjwsAyWNZq1xQQHsQZFbl9sM"

bot = commands.Bot(command_prefix="!")


def moveset_generator():
    moveset = []
    with open("media/text/moves.txt") as m:
        moves = m.readlines()
    for move in range(4):
        moveset.append(moves[int(random.random() * 679)])
    return moveset


# Pokemon class with Name, health and moveset
class Pokemon:
    def __init__(self, name=""):
        self.name = name
        self.max_hp = HEALTH_MIN + int(random.random() * (HEALTH_MAX - HEALTH_MIN))
        self.hp = 0
        self.moveset = moveset_generator()
        self.potion_count = 3
        self.ready = False


user_pokemon = Pokemon()
enemy_pokemon = Pokemon()


def battle_end_dialogue(result):
    if result == "win":
        user_pokemon.ready = False
        with open("media/text/enemy_lose_battle.txt") as r:
            enemy_lose_battle_text = r.read()
        post_battle_model = markovify.Text(enemy_lose_battle_text)
        return (
            "\nYour "
            + user_pokemon.name[:-1]
            + " used "
            + random.choice(user_pokemon.moveset)[:-1]
            + ' and won the the battle!\n"'
            + post_battle_model.make_sentence()
            + '"\n\n Use generate to play again.'
        )
    else:
        user_pokemon.ready = False
        with open("media/text/enemy_win_battle.txt") as r:
            enemy_win_battle_text = r.read()
        post_battle_model = markovify.Text(enemy_win_battle_text)
        return (
            "\nEnemy "
            + enemy_pokemon.name[:-1]
            + " used "
            + random.choice(enemy_pokemon.moveset)[:-1]
            + ' and won the battle!\n"'
            + post_battle_model.make_sentence()
            + '"\n\n Use generate to play again.'
        )


# Parse Pokemon names and before battle txt into single string
with open("media/text/pokemon_names.txt") as f:
    text = f.readlines()

with open("media/text/before_battle.txt") as r:
    before_battle_text = r.read()
message_model = markovify.Text(before_battle_text)

# Override markovify preprocessing to allow for single word generation
class PokemonText(markovify.Text):
    def word_split(self, sentence):
        return list(sentence)

    def word_join(Self, characters):
        return "".join(characters)


name_model = PokemonText(text)


@bot.command(
    name="generate", help="Responds with a pokemon game scenario with a fakemon."
)
async def scenario_response(ctx):
    if random.random() <= ATTITUDE:
        await ctx.send(file=discord.File("media/attitudes/no.gif"))
        await ctx.send("No, I don't think I will.", tts=TEXT_TO_SPEECH)
    else:
        user_pokemon.max_hp = HEALTH_MIN + int(
            random.random() * (HEALTH_MAX - HEALTH_MIN)
        )
        user_pokemon.hp = user_pokemon.max_hp
        user_pokemon.moveset = moveset_generator()
        user_pokemon.ready = True

        enemy_pokemon.max_hp = HEALTH_MIN + int(
            random.random() * (HEALTH_MAX - HEALTH_MIN)
        )
        enemy_pokemon.hp = enemy_pokemon.max_hp
        enemy_pokemon.moveset = moveset_generator()
        enemy_pokemon.ready = True
        await ctx.send(file=discord.File(random.choice(glob.glob("media/sprites/*"))))
        # Markov chain generate new original pokemon name
        user_pokemon.name = name_model.make_short_sentence(10)
        enemy_pokemon.name = name_model.make_short_sentence(10)
        response = (
            '"'
            + message_model.make_sentence()
            + '"'
            + "\n\nMy fakemon is called "
            + enemy_pokemon.name[:-1]
            + " and has "
            + str(enemy_pokemon.hp)
            + " health points."
            + "\n\nYour fakemon is called "
            + user_pokemon.name[:-1]
            + " and has "
            + str(user_pokemon.hp)
            + " health points."
            + "\n\nYou have "
            + str(user_pokemon.potion_count)
            + " potions. Use them with the potion command."
        )
        await ctx.send(response, tts=TEXT_TO_SPEECH)


@bot.command(
    name="attack",
    help="After generating a scenario, this will execute one round of attacks.",
)
async def scenario_response(ctx):
    if user_pokemon.ready:
        user_move = random.choice(user_pokemon.moveset)
        enemy_move = random.choice(enemy_pokemon.moveset)
        user_damage = int(random.random() * 50)
        enemy_damage = int(random.random() * 50)
        if random.random() <= 0.2:
            user_damage += 50
            await ctx.send("CRITICAL HIT!", tts=TEXT_TO_SPEECH)

        user_miss = random.random() <= 0.15
        enemy_miss = random.random() <= 0.2

        if user_miss:
            response = (
                "Your fakemon, "
                + user_pokemon.name[:-1]
                + ", used "
                + user_move[:-1]
                + " but missed.\n"
            )
            user_damage = 0
        else:
            response = (
                "Your fakemon, "
                + user_pokemon.name[:-1]
                + ", used "
                + user_move[:-1]
                + " and did "
                + str(user_damage)
                + " damage.\n"
            )
        await ctx.send(response, tts=TEXT_TO_SPEECH)

        if enemy_miss:
            response = (
                "Enemy fakemon, "
                + enemy_pokemon.name[:-1]
                + ", used "
                + enemy_move[:-1]
                + " but missed.\n"
            )
            enemy_damage = 0
        else:
            response = (
                "Enemy fakemon, "
                + enemy_pokemon.name[:-1]
                + ", used "
                + enemy_move[:-1]
                + " and did "
                + str(enemy_damage)
                + " damage.\n"
            )
        await ctx.send(response, tts=TEXT_TO_SPEECH)

        user_pokemon.hp -= enemy_damage
        enemy_pokemon.hp -= user_damage

        if user_pokemon.hp <= 0:
            response = battle_end_dialogue(result="lose")
        elif enemy_pokemon.hp <= 0:
            response = battle_end_dialogue(result="win")
        else:
            response = (
                "Your fakemon, "
                + user_pokemon.name[:-1]
                + ", has "
                + str(user_pokemon.hp)
                + " health points left.\n"
                + "Enemy fakemon, "
                + enemy_pokemon.name[:-1]
                + ", has "
                + str(enemy_pokemon.hp)
                + " health points left.\n"
            )
        await ctx.send(response, tts=TEXT_TO_SPEECH)
    else:
        await ctx.send(
            "Run generate to create a new scenario first.", tts=TEXT_TO_SPEECH
        )


@bot.command(
    name="potion",
    help="After generating a scenario, this will use one potion to heal your fakemon by 20 health points.",
)
async def potion_use(ctx):
    if user_pokemon.ready:
        new_hp = user_pokemon.hp + 20
        if new_hp > user_pokemon.max_hp:
            user_pokemon.hp = user_pokemon.max_hp
        else:
            user_pokemon.hp = new_hp

        response = (
            "You used a potion.\n"
            + user_pokemon.name[:-1]
            + " now has "
            + str(user_pokemon.hp)
            + " health points.\n"
        )
        await ctx.send(response, tts=TEXT_TO_SPEECH)

        enemy_move = random.choice(enemy_pokemon.moveset)
        if random.random() <= 1.2:
            # Attack missed
            response = (
                "Enemy fakemon, "
                + enemy_pokemon.name[:-1]
                + ", used "
                + enemy_move[:-1]
                + " but missed.\n"
            )
            await ctx.send(response, tts=TEXT_TO_SPEECH)
        else:
            enemy_damage = int(random.random() * 50)
            user_pokemon.hp -= enemy_damage

            if user_pokemon.hp <= 0:
                response = battle_end_dialogue(result="lose")
            else:
                response = (
                    "Enemy fakemon, "
                    + enemy_pokemon.name[:-1]
                    + ", used "
                    + enemy_move[:-1]
                    + " and did "
                    + str(enemy_damage)
                    + " damage.\n\n"
                    + "Your fakemon, "
                    + user_pokemon.name[:-1]
                    + ", has "
                    + str(user_pokemon.hp)
                    + " health points left.\n"
                    + "Enemy fakemon, "
                    + enemy_pokemon.name[:-1]
                    + ", has "
                    + str(enemy_pokemon.hp)
                    + " health points left.\n"
                )
            await ctx.send(response, tts=TEXT_TO_SPEECH)
    else:
        await ctx.send(
            "Run generate to create a new scenario first.", tts=TEXT_TO_SPEECH
        )


bot.run(TOKEN)
