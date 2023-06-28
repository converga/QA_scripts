from sqlalchemy import create_engine
from time import sleep

engine = create_engine('mysql+pymsql://username:password@localhost/dbname', pool_size=20, max_overflow=0)
connections = []

try:
    for _ in range(20):  # assuming the pool size is 20
        connection = engine.connect()
        connections.append(connection)
        result = connection.execute('SELECT SLEEP(30)')
        print('Query executed')
    print('All connections used')
except:
    print('Reached connection pool limit')

# Don't forget to close the connections
finally:
    for connection in connections:
        connection.close()
