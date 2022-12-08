import requests
import json
from threading import Thread

# Изменяемые параметры:

namespace = 6  # Неймспейс
ticket_number = 10  # Количество заявок на 1 поток


# Запрос на регистрацию
url = f'https://subzero-billing-{namespace}.testms-test.lognex.ru/api/clinton/1.0/ticket'
headers = {'Content-Type': 'application/json'}


# Функция для бомбардировки запросами в clinton, ничего менять не нужно
def bomber():
    counter1 = 0
    counter2 = 0
    with open('json1.json', 'r') as json1:
        sub_data = json.load(json1)
        for i in range(ticket_number):
            counter1 += 1
            response = requests.post(url, data=json.dumps(sub_data), headers=headers)
            #return response

    with open('json2.json', 'r') as json2:
        sub_data = json.load(json2)
        for j in range(ticket_number):
            counter2 += 1
            response_2 = requests.post(url, data=json.dumps(sub_data), headers=headers)
            #return response_2

    print('------------------------------------------------')
    print('итого, создано заявок:', counter1+counter2)


# Потоки
thread1 = Thread(target=bomber)
thread2 = Thread(target=bomber)
thread3 = Thread(target=bomber)
thread4 = Thread(target=bomber)
thread5 = Thread(target=bomber)
thread6 = Thread(target=bomber)
thread7 = Thread(target=bomber)
thread8 = Thread(target=bomber)
thread9 = Thread(target=bomber)
thread10 = Thread(target=bomber)
thread11 = Thread(target=bomber)
thread12 = Thread(target=bomber)
thread13 = Thread(target=bomber)
thread14 = Thread(target=bomber)
thread15 = Thread(target=bomber)
thread16 = Thread(target=bomber)
thread17 = Thread(target=bomber)
thread18 = Thread(target=bomber)
thread19 = Thread(target=bomber)
thread20 = Thread(target=bomber)


def start_threads():
    thread1.start()
    thread2.start()
    thread3.start()
    thread4.start()
    thread5.start()
    thread6.start()
    thread7.start()
    thread8.start()
    thread9.start()
    thread10.start()
    thread11.start()
    thread12.start()
    thread13.start()
    thread14.start()
    thread15.start()
    thread16.start()
    thread17.start()
    thread18.start()
    thread19.start()
    thread20.start()


def stop_threads():
    thread1.join()
    thread2.join()
    thread3.join()
    thread4.join()
    thread5.join()
    thread6.join()
    thread7.join()
    thread8.join()
    thread9.join()
    thread10.join()
    thread11.join()
    thread12.join()
    thread13.join()
    thread14.join()
    thread15.join()
    thread16.join()
    thread17.join()
    thread18.join()
    thread19.join()
    thread20.join()


start_threads()
stop_threads()
