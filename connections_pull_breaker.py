from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import threading
import time

engine = create_engine('mysql+pymsql://username:password@localhost/dbname', pool_size=5, max_overflow=0)
con = sqlalchemy.create_engine(
    'postgresql://postgres:@127.0.0.1:8181/lognex')  
Session = sessionmaker(bind=engine)

def execute_sleep(session, sleep_time):
    try:
        session.execute(text(f"SELECT SLEEP({sleep_time});"))
    except Exception as e:
        print("Error: ", str(e))
    finally:
        session.close()

threads = []
for i in range(6):  # 1 more than the pool_size
    session = Session()
    t = threading.Thread(target=execute_sleep, args=(session, 30))
    t.start()
    threads.append(t)
    time.sleep(1)  # delay a bit for better visibility of what's going on

for thread in threads:
    thread.join()
