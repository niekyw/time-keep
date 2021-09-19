import sqlite3

tasks_database = './databases/tasks.db'

def create_databases():
    conn = sqlite3.connect(tasks_database)
    conn.execute("PRAGMA foreign_keys = 1")
    cur = conn.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS tasks
    (indx          int(8),
    User            text,
    Notes           text,
    Start_Time      datetime,
    End_Time        datetime,
    Category        text,
    FOREIGN KEY (Category) REFERENCES categories (Category))''')

    cur.execute('''CREATE TABLE IF NOT EXISTS categories
    (User   text,
    Category text)''')
    conn.commit()


if __name__ == '__main__':
    create_databases()