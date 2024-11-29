import sqlite3

connection = sqlite3.connect("reservations.db")

with open("schema.sql") as database_schema:
    connection.executescript(database_schema.read())

cursor = connection.cursor()

connection.commit()
connection.close