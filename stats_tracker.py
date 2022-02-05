import db


class StatsTracker:
  def __init__(self, db):
    self.db = db

  def store_stats(self, user_id, turn):
    cols = ["total_games", "wins", "losses", "wins_1", "wins_2", "wins_3", "wins_4", "wins_5", "wins_6"]
    res = self.db.select("stats", (cols), ("user_id", user_id))
    if not res:
      self.db.insert("stats", (user_id, 0, 0, 0, 0, 0, 0, 0, 0, 0))
      res = self.db.select("stats", (cols), ("user_id", user_id))

    row_map = {k: v for k, v in zip(cols, res[0])}
    row_map["total_games"] += 1
    if turn > 0:
      row_map["wins"] += 1
      row_map[f"wins_{turn}"] += 1
    else:
      row_map["losses"] += 1

    self.db.update("stats", ("user_id", user_id), (row_map.items()))

  def get_stats(self, user_id):
    cols = ["total_games", "wins", "losses", "wins_1", "wins_2", "wins_3", "wins_4", "wins_5", "wins_6"]
    res = self.db.select("stats", (cols), ("user_id", user_id))
    if not res:
      raise KeyError(f"No stats for user id {user_id}!")
    row_map = {k: v for k, v in zip(cols, res[0])}

    return row_map


  def next_number(self, guild_id):
    rows = self.db.select("game_count", (("count"),), ("guild_id", guild_id))
    if not rows:
      self.db.insert("game_count", (guild_id, 0))
      rows = self.db.select("game_count", (("count"),), ("guild_id", guild_id))
    num = rows[0][0] + 1
    self.db.update("game_count", ("guild_id", guild_id), (("count", num),))
    return num


if __name__ == "__main__":
  s = StatsTracker(db.DbWrapper("test.db"))
  print(s.next_number(1))
  print(s.next_number(1))
  print(s.next_number(13))
  print(s.next_number(13))
  print(s.next_number(1))
