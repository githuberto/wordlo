import argparse
import sqlite3 as sl


class DbWrapper:
  def __init__(self, database):
    self.database = database
    self.con = sl.connect(database)

  def execute(self, sql, values=()):
    """
    Executes and commits a query on the database.

    sql - the SQL query to be executed
    values - an optional iterable of values for qmark substitution

    Returns: Any rows retrieved by the query or None.
    """
    with self.con:
      cur = self.con.cursor()
      if values:
        # print(f"Executing '{sql}' with values {values}")
        cur.execute(sql, values)
      else:
        # print(f"Executing '{sql}'")
        cur.execute(sql)
      return cur.fetchall()

  def create_table(self, table, columns):
    """
    Adds a table to the database.

    table - the name of the table to be created
    columns - an iterable of columns, e.g., ("text NAME PRIMARY KEY", "count INTEGER")
    """
    sql = f"CREATE TABLE {table} ({', '.join(columns)});"
    with self.con:
      return self.execute(sql)

  def insert(self, table, values):
    """
    Inserts a row containing values into the specified table.

    table - the name of the target table
    values - an iterable of values, e.g., ("MCOA", "2021-04-26 20:00:00", "DND")
    """
    sql = f"""
      INSERT INTO {table} VALUES({",".join(["?"]*len(values))})
    """
    self.execute(sql, values)

  def select(self, table, columns, key=None):
    """
    Selects the provided columns from the specified table.

    table - the name of the target table
    columns - a column or iterable of columns
    key - an optional key/value pair for select

    Returns: A list of rows in tuple form.
    """
    sql = f"SELECT {', '.join(columns)} FROM {table}"
    if key:
      sql += f"\nWHERE {key[0]} = {key[1]}"
    sql += ";"
    return self.execute(sql)

  def update(self, table, selector, columns):
    """
    Updates the provided columns for the provided user.

    table - the name of the target table
    key - the key of the row to be updated
    columns - a column or iterable of columns

    Returns: A list of rows in tuple form.
    """
    sql = f"""
    UPDATE {table}
    SET {", ".join(str(c[0]) + " = ?" for c in columns)}
    WHERE {selector[0]} = {selector[1]};
    """
    self.execute(sql, tuple(c[1] for c in columns))


def generate_tables(db):
  db.create_table("stats", ("user_id INTEGER PRIMARY KEY NOT NULL",
                            "total_games INTEGER NOT NULL",
                            "wins INTEGER NOT NULL",
                            "losses INTEGER NOT NULL",
                            "wins_1 INTEGER NOT NULL",
                            "wins_2 INTEGER NOT NULL",
                            "wins_3 INTEGER NOT NULL",
                            "wins_4 INTEGER NOT NULL",
                            "wins_5 INTEGER NOT NULL",
                            "wins_6 INTEGER NOT NULL"))
  db.create_table("game_count", ("guild_id INTEGER PRIMARY KEY NOT NULL",
                                 "count INTEGER NOT NULL"))


def test_update(db):
  db.update("stats", ("user_id", 1), (("wins", 99), ("losses", 2)))


def test_insert(db):
  db.insert("stats", (2, 3, 4, 5, 6, 7, 8, 9, 10, 11))
  db.insert("game_count", (69, 1))

def fix_count(db):
  db.update("game_count", ("guild_id", 696458628131061821), (("count", 280),))

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("--database", help="The path to the database.")
  parser.add_argument("--generate_tables", help="Generates a table in the database.", action="store_true")
  parser.add_argument("--test_update", help="Tests an update on the db.", action="store_true")
  parser.add_argument("--test_insert", help="Tests an insert on the db.", action="store_true")
  args = parser.parse_args()

  if not args.database:
    print("Missing required field: --database.")
    return

  db = DbWrapper(args.database)
  fix_count(db)
  return

  if args.generate_tables:
    generate_tables(db)

  if args.test_update:
    test_update(db)

  if args.test_insert:
    test_insert(db)


if __name__ == "__main__":
  main()
