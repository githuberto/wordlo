from nltk.corpus import words

lower_words = (w for w in words.words() if w.islower())
fiver_words = (w for w in lower_words if len(w) == 5)
for w in fiver_words:
  print(w)
