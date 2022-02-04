import nltk
import enchant
# nltk.download('averaged_perceptron_tagger') 
# nltk.download('wordnet') 
# nltk.download('omw-1.4') 
# nltk.download('names') 


def filter_method():
  with open("10k_common.txt", "r") as f:
    words = [w.strip() for w in f.readlines()]

  print("Tagging all words...")
  d = {word: pos for word, pos in nltk.pos_tag(nltk.corpus.wordnet.words())}
  print("Finished.")

  safe_words = []
  for w in words:
    if w not in d and w.title() in d:
      print(f"Proper noun: {w}")
    else:
      safe_words.append(w)

  print(safe_words)
  return safe_words


def removal_method():
  with open("10k_common.txt", "r") as f:
    words = {w.strip().title() for w in f.readlines()}

  with open("proper_nouns.txt", "r") as f:
    proper_nouns = {w.strip() for w in f.readlines()}

  for w in nltk.corpus.names.words("male.txt"):
    proper_nouns.add(w)

  for w in nltk.corpus.names.words("female.txt"):
    proper_nouns.add(w)

  print("Laura" in proper_nouns)


  dictionary = {w for w in nltk.corpus.words.words()}
  for w in words.intersection(proper_nouns):
      print(f"Removing {w}")
      words.remove(w)

  checker = enchant.Dict("en_US")
  for w in {w for w in words}:
    if not w or (w.lower() not in dictionary and not checker.check(w.lower())):
      print(f"Removing {w}")
      words.remove(w)

  return words



def main():
  # filter_method()
  print("\n".join(removal_method()))



if __name__ == "__main__":
  main()
