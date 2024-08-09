import requests
import json
import sqlalchemy
import time
import pandas as pd
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# параметры запуска
parser = argparse.ArgumentParser()
parser.add_argument("-namespace", help="namespace target", required=True)
parser.add_argument("-ticket_number", default=1, help="number of tickets per thread", type=int, required=True)
parser.add_argument("-thread_number", default=1, help="number of threads", type=int, required=True)
parser.add_argument("-product_number", default=10, help="maximum number of products to create tickets for", type=int,
                    required=True)
parser.add_argument("-company", default='test', help="company name", type=str)
parser.add_argument("-company_number", default=100, help="company number limit", type=int, required=False)
parser.add_argument("-prolongation", default=True, help="prolongation flag", type=bool, required=False)
parser.add_argument("-source", default="ADMIN", choices=["USER", "ADMIN", "PARTNER", "VENDOR", "VENDOR_TEST"],
                    required=False, help="Source type for ticket creation")
parser.add_argument("-upgrade_flag", default=False, type=bool, required=False, help="simple ticket or upgrade_ticket?")

args = parser.parse_args()

# Идентификаторы для разных типов источников
source_ids = {
    "USER": "3b339e7f-eb56-40ee-9d36-79af20d578f8",
    "ADMIN": "83aa62a3-f20c-4052-9bea-3674fa6076fd",
    "PARTNER": "80557aeb-5e89-484a-8e4c-cf3b8f9dc858",
    "VENDOR": "13f9e97b-8c11-409f-8ec2-2b4ec0830ce7",
    "VENDOR_TEST": "74ba2cfc-d4ee-4a63-a16f-2cf920c829c7"
}

# Соединение к БД
con = sqlalchemy.create_engine('postgresql://postgres:@127.0.0.1:8181/lognex')

namespace = args.namespace
ticket_number = args.ticket_number
thread_number = args.thread_number
prolongation_flag = args.prolongation
product_number = args.product_number
company = args.company
source = args.source
upgrade_flag = args.upgrade_flag

tariff_price = 0

if upgrade_flag:
    tariff_price = 6000

url = f'https://subzero-{namespace}.testms-test.lognex.ru/api/clinton/1.0/ticket'
headers = {'Content-Type': 'application/json'}

successful_requests = 0


def sql_go(request):
    """Функция для запроса к базе данных"""
    return pd.read_sql(sqlalchemy.text(request), con)


sql_product = f'''
            WITH paid_tariffs AS (
  SELECT *
  FROM billing.tariffversion
  WHERE price = {tariff_price}
)
SELECT pv.name AS "Название_продукта", 
       pv.internal_id AS "ID_продукта", 
       pv.trialtariff_id AS "ID_триального_тарифа",
       paid_tariffs.internal_id AS "ID_платного_тарифа"
FROM billing.productversion pv
LEFT JOIN billing.tariff t ON pv.internal_id = t.product_id
INNER JOIN paid_tariffs ON paid_tariffs.internal_id = t.id
WHERE pv.name ILIKE 'Test_product_%'
LIMIT {product_number}
'''

product_list = sql_go(sql_product)
account_list = sql_go(f'''SELECT id FROM billing.billingaccount WHERE company LIKE '{company}%' 
                      LIMIT {args.company_number}''')


def bomber_many_products():
    """Функция для создания заявок"""
    global successful_requests
    with requests.Session() as session:
        with open('bomber/json1.json', 'r') as json1:
            sub_data = json.load(json1)
            sub_data['subscribeTo']['autoprolongate'] = prolongation_flag
            sub_data['source']['type']['id'] = source_ids[source]
            sub_data['subscribeTo']['period']['fromCurrentSubscription'] = upgrade_flag
            if upgrade_flag:
                sub_data['subscribeTo']['period']['value'] = 12
                sub_data['sum']['declared'] = 6000
                sub_data['comment'] = "апгрейд"
            else:
                pass

            local_success = 0
            total_requests = ticket_number * len(account_list) * len(product_list)
            progress_bar = tqdm(total=total_requests, desc='Обработка заявок')

            for _ in range(ticket_number):
                for index, account in account_list.iterrows():
                    sub_data['accountId'] = str(account['id'])
                    for index, product in product_list.iterrows():
                        sub_data['subscribeTo']['product']['id'] = str(product['ID_продукта'])
                        sub_data['subscribeTo']['tariff']['id'] = str(product['ID_платного_тарифа'])
                        response = session.post(url, data=json.dumps(sub_data), headers=headers)
                        if response.ok:
                            local_success += 1
                        else:
                            error_msg = f"Ошибка {response.status_code} для аккаунта {account['id']} - {response.text}"
                            tqdm.write(error_msg)
                        progress_bar.update(1)  # Обновляем прогресс-бар после каждого запроса
            successful_requests += local_success
            progress_bar.close()
            return local_success


start = time.time()
with ThreadPoolExecutor(max_workers=thread_number) as executor:
    futures = [executor.submit(bomber_many_products) for _ in range(thread_number)]
    for future in as_completed(futures):
        print(f'Успешно создано заявок в потоке: {future.result()}')

end = time.time() - start

print(f'Всего успешно создано заявок: {successful_requests}')
print(f'Выполнялось: {end:.2f} с')
