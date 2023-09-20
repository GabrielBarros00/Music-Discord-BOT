import sqlite3


class DatabaseController:
    def __init__(self) -> None:
        self.conn: sqlite3.Connection = sqlite3.connect("configs.db", check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor: sqlite3.Cursor = self.conn.cursor()
        self.create_tables()
    
    def create_tables(self) -> None:
        self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS guilds 
                                (
                                    guild_id INTEGER PRIMARY KEY,
                                    auto_shuffle INTEGER,
                                    prefix TEXT,
                                    volume INTEGER,
                                    auto_queue INTEGER
                                )"""
                            )
    
    def create_guild(self, guild_id: int, auto_shuffle: bool=False, prefix: str ="<", volume: int =15, auto_queue: bool =False):
        self.cursor.execute("""
                            INSERT INTO guilds 
                                VALUES(?, ?, ?, ?, ?)""", 
                                (int(guild_id),
                                0 if not auto_shuffle else 1,
                                str(prefix),
                                int(volume),
                                0 if not auto_queue else 1
                                )
                            )
        self.conn.commit()
    
    def update_values(self, guild_id:int, **columns) -> None:
        sql = f"UPDATE guilds SET "
        all_items = columns.items()
        for index, column in enumerate(all_items):
            sql += f"{column[0]} = '{int(column[1]) if isinstance(column[1], bool) else column[1]}'"
            if not index == len(all_items) - 1:
                sql += ", "
            else:
                sql += " "
        sql += f"where guild_id = '{guild_id}'"
        self.cursor.execute(sql)
        self.conn.commit()
    
    def get_values(self, guild_id:int, *columns) -> dict:
        sql = f"SELECT {', '.join(columns)} FROM guilds WHERE guild_id = '{guild_id}'"
        data = self.cursor.execute(sql).fetchone()
        return dict(data) if data else data

    def delete_guild(self, guild_id: int) -> None:
        self.cursor.execute(
            "DELETE FROM guild_int WHERE name = ?",
            (int(guild_id),)
        )

database_manager = DatabaseController()
