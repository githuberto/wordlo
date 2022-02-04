def main():
  with open("10k_common.txt", "r") as f:
    for w in map(lambda w: w.strip(), (w for w in f.readlines())):
      if len(w) == 5:
        print(w)

if __name__ == "__main__":
  main()
