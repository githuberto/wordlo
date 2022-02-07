from util import Game, WordBasket, Counter


def game_tests():
  game = Game("house", 1)
  print(f"Game word: {game.secret()}")
  print(f"Game won?: {game.won()}")
  print(f"Game lost?: {game.lost()}")

  result = game.run_turn("abcde")
  print(f"run_turn() return value: {result}")
  print(f"Game won?: {game.won()}")
  print(f"Game lost?: {game.lost()}")

  printout = game.print_board()
  print(f"print_board() output:\n{printout}")


def word_basket_tests():
  wb = WordBasket("10k_fivers.txt")
  print(wb.next_word())
  print(wb.next_word())
  print(wb.next_word())
  print(wb.next_word())
  print(wb.next_word())
  print(wb.next_word())


def counter_tests():
  c = Counter("test_count.txt")
  print(c.next_number())
  print(c.next_number())
  print(c.next_number())
  print(c.next_number())


def main():
  game_tests()
  word_basket_tests()
  counter_tests()


if __name__ == "__main__":
  main()
