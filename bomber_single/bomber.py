import requests
import json
from concurrent.futures import ThreadPoolExecutor

# Изменяемые параметры:

namespace = 5  # Неймспейс
ticket_number = 1  # Количество заявок на 1 поток
num_threads = 20  # Количество потоков

# Запрос
url = f'https://subzero-billing-{namespace}.testms-test.lognex.ru/api/clinton/1.0/ticket'
headers = {'Content-Type': 'application/json'}


# Функция для бомбардировки запросами в clinton, ничего менять не нужно
def bomber():
    print('bomber start')

    counter1 = 0
    counter2 = 0

    with requests.Session() as s:
        with open('json1.json', 'r') as json1:
            sub_data = json.load(json1)
            for i in range(ticket_number):
                counter1 += 1
                with s.post(url, data=json.dumps(sub_data), headers=headers):
                    print('request 1 done', counter1)
            #return response

    print('bomber midway')

    with requests.Session() as s:
        with open('json2.json', 'r') as json2:
            sub_data = json.load(json2)
            for j in range(ticket_number):
                counter2 += 1
                with s.post(url, data=json.dumps(sub_data), headers=headers):
                    print('request 2 done', counter2)
            #return response_2

    print('------------------------------------------------')
    print('итого, создано заявок:', counter1+counter2)


# Создание пула потоков
with ThreadPoolExecutor(max_workers=num_threads) as executor:
    # Запуск потоков
    results = [executor.submit(bomber) for _ in range(num_threads)]

print('All threads have completed')
