import itertools


def main():
  words = []
  with open("fiver_words.txt", "r") as input_file:
      words = ((i, l.strip()) for i, l in enumerate(input_file.readlines()))

  start = int(input("Start at word #? "))
  words = itertools.dropwhile(lambda t: t[0] < start, words)

  with open("common_words.txt", "a") as output_file:
    for i, w in words:
      print(f"{i:4}: {w}")
      r = "x"
      while r not in " ":
        r = input("Keep? (enter) Delete? (space): ")
      if r == "":
        output_file.write(w+"\n")
        output_file.flush()


if __name__ == "__main__":
  main()
