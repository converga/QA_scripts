import requests
import json
import sqlalchemy
import time
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

# Изменяемые параметры:

con = sqlalchemy.create_engine('postgresql://postgres:@127.0.0.1:8181/lognex')

namespace = 5  # Неймспейс
ticket_number = 80  # Количество заявок на 1 поток
thread_number = 10  # Количество потоков
prolongation_flag = False  # Для кейсов с автопролонгацией. True - включена, False - не будут

# Запрос
url = f'https://subzero-billing-{namespace}.testms-test.lognex.ru/api/clinton/1.0/ticket'
headers = {'Content-Type': 'application/json'}


# Функция для запроса к базе
def sql_go(request):
    return pd.read_sql(sqlalchemy.text(request), con)


#  Формирование списка продуктов с его тарифами:

sql_product = '''
            select name as "Название_продукта", internal_id as "ID_продукта", trialtariff_id as "ID_триального_тарифа"
from billing.productversion
where name ILIKE 'Test_product_%'
limit 5 '''  # Ограничение количества продуктов

#  Формирование списка аккаунтов:

product_list = sql_go(sql_product)
account_list = sql_go('''select id from billing.billingaccount WHERE company LIKE 'test%'
limit 1 ''')  # Ограничение количества аккаунтов


def bomber_many_products():
    print('bomber start')

    counter = 0

    with requests.Session():
        with open('json1.json', 'r') as json1:
            sub_data = json.load(json1)
            sub_data['subscribeTo']['tariff']['id'] = prolongation_flag

            for i in range(ticket_number):
                for index, row in account_list.iterrows():
                    sub_data['accountId'] = str(row['id'])

                    for index, row in product_list.iterrows():
                        sub_data['subscribeTo']['product']['id'] = str(product_list.loc[index, 'ID_продукта'])
                        sub_data['subscribeTo']['tariff']['id'] = str(product_list.loc[index, 'ID_триального_тарифа'])

                        counter += 1

                        response = requests.post(url, data=json.dumps(sub_data), headers=headers)

                        if response.ok:
                            print()
                            print(f'Заявка для {row} создана', '\n')
                            print('------------------------------------------------')
                        else:
                            print(f'Заявка для {row} НЕ создана' + str(response))

        print('------------------------------------------------')
        print('------------------------------------------------')
        print(f'||| Итого, создано заявок: {counter} |||')


# Пуск потоков:

start = time.time()  # точка отсчета времени
with ThreadPoolExecutor(max_workers=thread_number) as executor:
    # Запуск потоков
    results = [executor.submit(bomber_many_products) for _ in range(thread_number)]

end = time.time() - start  # конец отчета времени
print('All threads have completed')
print(f'Выполнялось: {end}с')
