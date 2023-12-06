import requests
import json
import sqlalchemy
import time
import pandas as pd
import argparse
from concurrent.futures import ThreadPoolExecutor

# параметры запуска:

parser = argparse.ArgumentParser()
parser.add_argument("-namespace", help="namespace target", required=True)
parser.add_argument("-ticket_number", default=1, help="number of tickets per thread", type=int, required=True)
parser.add_argument("-thread_number", default=1, help="number of threads", type=int, required=True)
parser.add_argument("-product_number", default=10, help="maximum number of products to create tickets for", 
                    type=int, required=True)
parser.add_argument("-company", default='test', help = "company name", type=str)
parser.add_argument("-company_number", default=100, help = "company number limit", 
                    type=int, required=False)
parser.add_argument("-prolongation", default=True, help = "prolongation flag", 
                    type=bool, required=False)


args = parser.parse_args()

# Соединение к бд. Требуется проброс портов
con = sqlalchemy.create_engine(
    'postgresql://postgres:@127.0.0.1:8181/lognex')

#  todo: 
# 3b339e7f-eb56-40ee-9d36-79af20d578f8	USER	{"en": "User", "ru": "Пользовательская"}
# 83aa62a3-f20c-4052-9bea-3674fa6076fd	ADMIN	{"en": "Admin", "ru": "Административная"}
# 80557aeb-5e89-484a-8e4c-cf3b8f9dc858	PARTNER	{"en": "Partner", "ru": "Партнерская"}
# 13f9e97b-8c11-409f-8ec2-2b4ec0830ce7	VENDOR	{"en": "Vendor", "ru": "Вендорская"}
# 74ba2cfc-d4ee-4a63-a16f-2cf920c829c7	VENDOR_TEST	{"en": "Vendor test", "ru": "Вендорская тестирование"}
# f3c7ccc8-df4e-11ed-b5ea-0242ac120002	SYSTEM	{"en": "System", "ru": "Системная"}  

namespace = args.namespace  # Неймспейс
ticket_number = args.ticket_number  # Количество заявок на 1 поток
thread_number = args.thread_number  # Количество потоков
prolongation_flag = args.prolongation  # Для кейсов с автопролонгацией
product_number = args.product_number
company = args.company


# Запрос
url = f'https://subzero-{namespace}.testms-test.lognex.ru/api/clinton/1.0/ticket'
headers = {'Content-Type': 'application/json'}


# Функция для запроса к базе
def sql_go(request):
    return pd.read_sql(sqlalchemy.text(request), con)


#  Формирование списка продуктов с его тарифами:

sql_product = f'''
            WITH paid_tariffs AS (
  SELECT *
  FROM billing.tariffversion
  WHERE price = 1000
)
SELECT pv.name AS "Название_продукта", 
       pv.internal_id AS "ID_продукта", 
       pv.trialtariff_id AS "ID_триального_тарифа",
       paid_tariffs.internal_id AS "ID_платного_тарифа"
FROM billing.productversion pv
LEFT JOIN billing.tariff t ON pv.internal_id = t.product_id
inner JOIN paid_tariffs ON paid_tariffs.internal_id = t.id
WHERE pv.name ILIKE 'Test_product_%'
limit {product_number} '''  # Ограничение количества продуктов

#  Формирование списка аккаунтов:
product_list = sql_go(sql_product)
account_list = sql_go(f'''select id from billing.billingaccount WHERE company LIKE '{company}%' 
                      limit {args.company_number} ''')  # Ограничение аккаунтов


def bomber_many_products():
    

    print('bomber start')

    counter = 0

    with requests.Session():
        with open('bomber\json1.json', 'r') as json1:
            sub_data = json.load(json1)
            sub_data['subscribeTo']['autoprolongate'] = prolongation_flag

            for i in range(ticket_number):
                for index, row in account_list.iterrows():
                    sub_data['accountId'] = str(row['id'])

                    for index, row in product_list.iterrows():
                        sub_data['subscribeTo']['product']['id'] = str(product_list.loc[index, 'ID_продукта'])
                        sub_data['subscribeTo']['tariff']['id'] = str(product_list.loc[index, 'ID_платного_тарифа'])

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
print('Все потоки отработали')
print(f'Выполнялось: {end}с')

# Пример:
# python bomber\bomber.py -namespace billing-1 -ticket_number 1  -thread_number 1 -product_number 1 -company test3