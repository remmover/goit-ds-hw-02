import sqlite3
from faker import Faker
import random


def create_tables():
    conn = sqlite3.connect("tasks.sqlite")
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        fullname VARCHAR(100) NOT NULL,
                        email VARCHAR(100) UNIQUE NOT NULL
                    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS status (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name VARCHAR(50) UNIQUE NOT NULL
                    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title VARCHAR(100) NOT NULL,
                        description TEXT,
                        status_id INTEGER,
                        user_id INTEGER,
                        FOREIGN KEY (status_id) REFERENCES status(id),
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    )''')

    conn.commit()
    conn.close()


def seed_database():
    conn = sqlite3.connect("tasks.sqlite")
    cursor = conn.cursor()
    faker = Faker()

    # Insert statuses
    statuses = [('new',), ('in progress',), ('completed',)]
    cursor.executemany('INSERT OR IGNORE INTO status (name) VALUES (?)', statuses)

    # Insert users
    users = [(faker.name(), faker.email()) for _ in range(10)]
    cursor.executemany('INSERT INTO users (fullname, email) VALUES (?, ?)', users)

    # Fetch user and status IDs
    cursor.execute('SELECT id FROM users')
    user_ids = [row[0] for row in cursor.fetchall()]
    cursor.execute('SELECT id FROM status')
    status_ids = [row[0] for row in cursor.fetchall()]

    # Insert tasks
    tasks = [(faker.sentence(), faker.text(), random.choice(status_ids), random.choice(user_ids)) for _ in range(20)]
    cursor.executemany('INSERT INTO tasks (title, description, status_id, user_id) VALUES (?, ?, ?, ?)', tasks)

    conn.commit()
    conn.close()


def execute_queries():
    conn = sqlite3.connect("tasks.sqlite")
    cursor = conn.cursor()

    # 1. Get all tasks for a specific user
    user_id = 1
    cursor.execute('SELECT * FROM tasks WHERE user_id = ?', (user_id,))
    print("№ 1 Tasks for user_id=1:", cursor.fetchall())

    # 2. Get tasks with a specific status
    cursor.execute("SELECT * FROM tasks WHERE status_id = (SELECT id FROM status WHERE name='new')")
    print("№ 2 New tasks:", cursor.fetchall())

    # 3. Update task status
    cursor.execute("UPDATE tasks SET status_id = (SELECT id FROM status WHERE name='in progress') WHERE id = 1")
    conn.commit()

    # 4. Get users without tasks
    cursor.execute("SELECT * FROM users WHERE id NOT IN (SELECT DISTINCT user_id FROM tasks)")
    print("№ 4 Users without tasks:", cursor.fetchall())

    # 5. Add a new task for a specific user
    cursor.execute(
        "INSERT INTO tasks (title, description, status_id, user_id) VALUES ('New Task', 'Task description', 1, 1)")
    conn.commit()

    # 6. Get all tasks that are not completed
    cursor.execute("SELECT * FROM tasks WHERE status_id != (SELECT id FROM status WHERE name='completed')")
    print("№ 6 Incomplete tasks:", cursor.fetchall())

    # 7. Delete a specific task
    cursor.execute("DELETE FROM tasks WHERE id = 2")
    conn.commit()

    # 8. Find users by email pattern
    cursor.execute("SELECT * FROM users WHERE email LIKE '%@example.com'")
    print("№ 8 Users with @example.com emails:", cursor.fetchall())

    # 9. Update a user's name
    cursor.execute("UPDATE users SET fullname = 'Updated Name' WHERE id = 1")
    conn.commit()

    # 10. Get count of tasks per status
    cursor.execute(
        "SELECT status.name, COUNT(tasks.id) FROM tasks JOIN status ON tasks.status_id = status.id GROUP BY status.name")
    print("№ 10 Task count per status:", cursor.fetchall())

    # 11. Get tasks assigned to users with a specific email domain
    cursor.execute(
        "SELECT tasks.* FROM tasks JOIN users ON tasks.user_id = users.id WHERE users.email LIKE '%@example.com'")
    print("№ 11 Tasks for users with @example.com emails:", cursor.fetchall())

    # 12. Get tasks with no description
    cursor.execute("SELECT * FROM tasks WHERE description IS NULL OR description = ''")
    print("№ 12 Tasks without description:", cursor.fetchall())

    # 13. Get users and their tasks with status 'in progress'
    cursor.execute(
        "SELECT users.fullname, tasks.title FROM users JOIN tasks ON users.id = tasks.user_id JOIN status ON tasks.status_id = status.id WHERE status.name = 'in progress'")
    print("№ 13 Users with 'in progress' tasks:", cursor.fetchall())

    # 14. Get users and count of their tasks
    cursor.execute(
        "SELECT users.fullname, COUNT(tasks.id) FROM users LEFT JOIN tasks ON users.id = tasks.user_id GROUP BY users.id")
    print("№ 14 and their task count:", cursor.fetchall())

    conn.close()


if __name__ == "__main__":
    create_tables()
    seed_database()
    execute_queries()
