import random


UNKNOWN_SQUARE = ":grey_question:"
PERFECT_SQUARE = ":heart_eyes:"
MATCHING_SQUARE = ":smile:"
EMPTY_SQUARE = ":thinking:"


def emojify(c):
  if c.isalpha():
    return ":regional_indicator_{}:".format(c)

  return ":blue_square:"


class Counter:
  def __init__(self, count_file):
    print(f"Using count file {count_file}.")
    self.count_file = count_file

  def next_number(self):
    with open(self.count_file, "r+t") as f:
      line = str(f.readline().strip())
      n = int(line)
      f.truncate(0)
      f.seek(0)
      f.write(str(n+1))
    return n


class WordBasket:
  def __init__(self, filename):
    self.words = []
    with open(filename, "r") as f:
      self.words = [l.strip() for l in f.readlines()]
    print(f"Successfully read words from {filename}.")

  def next_word(self, length):
    word = ""
    while len(word) != length:
      word = random.choice(self.words)
    return word

  def check(self, word):
    return word in self.words


class Board:
  def __init__(self, word_length, size):
    self.word_length = word_length
    self.current = 0
    self.words = [" " * word_length for _ in range(size)]

  def add_guess(self, guess):
    if self.full():
      raise IndexError(f"Can't insert \"{guess}\": Board is full!")

    if len(guess) != self.word_length:
      raise ValueError(f"Words must be exactly {self.word_length} letters long!")

    self.words[self.current] = guess
    self.current += 1

  def turn(self):
    return self.current

  def full(self):
    return self.current == len(self.words)

  def get_words(self):
    return self.words

  def turns_left(self):
    return len(self.words) - self.current


class Game:
  def __init__(self, secret_word, number, users, length):
    self.board = Board(length, 6)
    self.secret_word = secret_word
    self.number = number
    self.users = users
    self.has_won = False
    self.has_lost = False
    self.length = length

  def game_number(self):
    return self.number

  def run_turn(self, guess):
    self.board.add_guess(guess)

    if guess == self.secret_word:
      self.has_won = True
      return False
    elif self.board.full():
      self.has_lost = True
      return False

    return True

  def secret(self):
    return self.secret_word

  def won(self):
    return self.has_won

  def lost(self):
    return self.has_lost

  def turns_left(self):
    return self.board.turns_left()

  def get_colors(self, guess):
    if " " in guess:
      return [UNKNOWN_SQUARE for _ in guess]

    counts = {gc: self.secret_word.count(gc) for gc in guess}
    color_bar = [EMPTY_SQUARE for _ in guess]

    # Process perfect matches first.
    for i in range(len(guess)):
      if guess[i] == self.secret_word[i]:
        color_bar[i] = PERFECT_SQUARE
        counts[guess[i]] -= 1

    for i in range(len(guess)):
      if counts[guess[i]] > 0 and color_bar[i] == EMPTY_SQUARE:
        color_bar[i] = MATCHING_SQUARE
        counts[guess[i]] -= 1

    return color_bar

  def get_emojis(self, guess):
    color_bar = self.get_colors(guess)
    letter_bar = [emojify(gc) for gc in guess]

    result = f"{''.join(color_bar)}\n{''.join(letter_bar)}"
    return result

  def print_board(self):
    return "\n".join(self.get_emojis(w) for w in self.board.get_words())
