import time
import argparse
import discord
import asyncio
import enchant
from wordlo_util import Game, WordBasket, Counter


WARNING_DELAY = 4
DELETE_DELAY = 1
CHECK_EMOJI = "✅"
BAN_EMOJI="🚫"
PENSIVE_EMOJI="😔"


class Wordlo(discord.Client):
  def __init__(self, intents, guild_name, channel_name, prefix, word_basket, dictionary, counter):
    super(Wordlo, self).__init__(intents=intents)
    self.players = {}
    self.prefix = prefix
    self.word_basket = word_basket
    self.dictionary = dictionary
    self.guild_name = guild_name
    self.channel_name = channel_name
    self.counter = counter

    self.guild = None
    self.channel = None

  async def on_ready(self):
    print("Initializing...")
    self.guild = discord.utils.get(self.guilds, name=self.guild_name)
    if not self.guild:
      print("Failed to find server {self.guild_name}!")
      await self.logout()
      return

    self.channel = discord.utils.get(self.guild.channels, name=self.channel_name)
    if not self.channel:
      print(f"Failed to find channel {self.channel_name} in server {self.guild_name}")
      await self.logout()
      return

    print(f"Running in {self.channel.name} on {self.guild.name} with prefix {self.prefix}.")

  async def help(self, message):
      help = f"""
                > Wordlo is a clone of the puzzle game Wordle. 
                > 
                > Commands:
                > `{self.prefix}wordlo` - Start a singleplayer game.
                > `{self.prefix}wordlo @otheruser @otherotheruser` - Start a co-op game.
                > `{self.prefix}<word>` - Guess a word in an active game. e.g., `&horse`.
                > `{self.prefix}quit` - Abort an active game.
                > `{self.prefix}help` - Display this help message.
                > 
                > You have 6 tries to discover the secret word. Each guess must be a 5 letter English word. The emojis that appear above your guess will give you hints about the secret word:
                > :thinking: - the letter below is not in the secret word.
                > :smile: - the letter below is in the secret word, but in a different position.
                > :heart_eyes: - the letter below in the same position in the secret word.
                > 
                > Guess the secret word within 6 tries to win!
                > 
                > Play the original game here: https://www.powerlanguage.co.uk/wordle/.
             """
      await message.reply(help)

  async def on_message(self, message):
    if not self.channel:
      return

    if message.guild.id != self.guild.id:
      return

    if message.channel.id != self.channel.id:
      return

    if message.content == f"{self.prefix}help":
      await self.help(message)
    elif message.content.startswith(self.prefix + "wordlo"):
      await self.new_game(message)
    elif message.content == f"{self.prefix}quit":
      await self.quit_game(message)
    elif message.content.startswith(self.prefix):
      await self.next_turn(message)

  async def new_game(self, message):
    users = {user for user in message.mentions}
    users.add(message.author)
    if (message.content != f"{self.prefix}wordlo"
      and not message.content.startswith(f"{self.prefix}wordlo ")):
      await self.warn_delete("Type `&help` to learn how to use Wordlo.", message, delay=5)
      return

    names = ", ".join(user.mention for user in users if user.id in self.players)
    if names:
      await self.warn_delete(f"An active game already exists for the following player(s): {names}! Type `{self.prefix}quit` to quit.", message)
      return

    secret_word = self.word_basket.next_word()
    game = Game(secret_word, self.counter.next_number(), users)

    board_message = await self.print_board(game, message, None)
    for user in users:
      self.players[user.id] = (game, board_message)
    await message.delete(delay=10)

  async def next_turn(self, message):
    aid = message.author.id

    if aid not in self.players:
      await self.warn_delete(
          f"To start a new game, type: `{self.prefix}`wordlo. Type `&help` for more information.",
          message)
      return

    word = message.content[1:].lower()
    if len(word) != 5:
      await self.warn_delete("Your word must be exactly 5 letters long!", message)
      return

    if not dictionary.check(word) and not self.word_basket.check(word):
      await self.warn_delete(f"Sorry, {word} is not in my dictionary.", message)
      return

    game, board_message = self.players[aid]

    await message.delete(delay=DELETE_DELAY)

    if not game.run_turn(word):
      for user in game.users:
        self.players.pop(user.id)
    await self.print_board(game, message, board_message)

  async def quit_game(self, message):
    if message.author.id not in self.players:
      await self.warn_delete("You don't have an active game!", message)
      return

    await self.warn_delete("Aborting your game...", message)
    game, board_message = self.players[message.author.id]
    for user in game.users:
      self.players.pop(user.id)
    await self.print_board(game, message, board_message, aborted=True)

  async def print_board(self, game, message, board_message, aborted=False):
    embed = discord.Embed(type="rich",
                          description=game.print_board(),
                          colour=discord.Colour.random())
    embed.set_author(name=f"Game #{game.game_number()}",
                     icon_url=str(message.author.avatar_url))
    if aborted:
      embed.set_footer(text=f"Game aborted. {PENSIVE_EMOJI}")
    elif game.won():
      embed.set_footer(text=f"YOU WIN!")
    elif game.lost():
      embed.set_footer(text=f"GAME OVER! The word was `{game.secret()}`.")
    else:
      text = ""
      if game.turns_left() == 1:
        text = "1 guess left!"
      else:
        text = f"{game.turns_left()} guesses left!"
      embed.set_footer(text=text)
    if board_message is None:
      return await message.channel.send(embed=embed)
    return await board_message.edit(embed=embed)

  async def warn_delete(self, warning, message, delay=WARNING_DELAY):
    await message.add_reaction(BAN_EMOJI)
    await message.reply(warning, delete_after=delay)
    await message.delete(delay=delay)


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument(
      "discord_token", help="The path to your Discord bot token.")
  parser.add_argument(
      "--guild", default="yobots", help="The guild the bot should be active in.")
  parser.add_argument(
      "--channel", default="general", help="The channel the bot should be active in.")
  parser.add_argument(
      "--prefix", default="!", help="The channel for bot readings.")
  parser.add_argument(
      "--word_basket", default="10k_fivers.txt", help="The basket of secret words.")
  parser.add_argument(
      "--counter_file", default="wordlo_count.txt",
      help="The file containing the number of games played.")
  args = parser.parse_args()

  with open(args.discord_token, "r") as token_file:
    discord_token = token_file.read().strip()

  word_basket = WordBasket(args.word_basket)

  dictionary = enchant.Dict("en_US")

  counter = Counter(args.counter_file)

  intents = discord.Intents.default()
  bot = Wordlo(intents, args.guild, args.channel, args.prefix, word_basket, dictionary, counter)
  bot.run(discord_token)
