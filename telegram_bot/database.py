import sqlite3 

from typing import List, Tuple
from telegram_bot import config as cfg
from telegram_bot import exceptions as ex


class Planner:
    def __init__(self, db_name: str = cfg.DB_NAME) -> None:
        self.db_name = db_name 
        self._create_table()

    
    def _create_table(self):
        with sqlite3.connect(self.db_name) as conn:
            query = """
                CREATE TABLE IF NOT EXISTS planner(
                    userid INT,
                    plan TEXT
                )
            """
            conn.execute(query)

    
    def add(self, message):
        with sqlite3.connect(self.db_name) as conn:
            print("[ADD INTO planner]")
            conn.execute(
                "INSERT INTO planner VALUES (?, ?)",
                (message.chat.id, message.text)
            )
    

    def get_tasks(self, message):
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT plan FROM planner WHERE userid=?",
                (message.chat.id,),
            )
            tasks: List[Tuple[str]] = cur.fetchall()
            tasks: List[str] = list(chain.from_iterable(tasks))

            if len(tasks) == 0:
                raise ex.TaskNotExists
            
            return tasks


    def show(self, message):
        tasks = self.get_tasks(message=message)
        tasks = [f"{i + 1}. {task}" for i, task in enumerate(tasks)] 
        return "\n".join(tasks)


    def delete(self, message):
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute(
                "DELETE FROM planner WHERE userid=? AND plan=?",
                (message.chat.id, message.text),
            )
            conn.commit()

    def delete_all(self, message):
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute(
                "DELETE FROM planner WHERE userid=?",
                (message.chat.id,),
            )
            conn.commit()
 