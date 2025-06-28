import pandas as pd
import psycopg2
#import requests
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# connection to existing db in postgresql
# connection = psycopg2.connect(
#                                 host = "localhost",
#                                 port = 5432,
#                                 user = "postgres",
#                                 password = "jegan",
#                                 database = "postgres" )

# connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

# # creating phonepe db
# cursor = connection.cursor()
# cursor.execute("create database Phonepe_pulse_db")
# cursor.close()
# connection.close()

# connect to phonepe db
connection = psycopg2.connect(
                              host = "localhost",
                                port = 5432,
                                user = "postgres",
                                database = "phonepe_pulse_db",
                                password = "jegan" )

# table creation
connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

cursor = connection.cursor()
# cursor.execute("DROP TABLE IF EXISTS top_user")
cursor.execute("""create table if not exists map_transaction (state TEXT,
        year INT,
        quater INT,
        transaction_area TEXT,
        transaction_count BIGINT,
        transaction_amount BIGINT)""")

df = pd.read_csv("Map_transaction.csv")
for index, row in df.iterrows():
    cursor.execute("""
        INSERT INTO map_transaction (state, year, quater, transaction_area, transaction_count, transaction_amount)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        row['State'],
        row['Year'],
        row['Quater'],
        row['Transaction_area'],
        row['Transaction_count'],
        row['Transaction_amount']
    ))

connection.commit()
cursor.close()
print("Map_transaction table created succesfully")
