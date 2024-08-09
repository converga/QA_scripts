import requests
import json
import pandas as pd
import sqlalchemy
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import argparse

# Параметры запуска
parser = argparse.ArgumentParser()
parser.add_argument("-namespace", help="namespace target", required=True)
parser.add_argument("-thread_number", default=10, help="number of threads", type=int, required=False)
parser.add_argument("-product_number", default=10, help="maximum number of products to create tickets for", type=int,
                    required=True)
parser.add_argument("-company", default='test', help="company name", type=str)
parser.add_argument("-company_number", default=100, help="company number limit", type=int, required=False)
args = parser.parse_args()

# Соединение к БД
con = sqlalchemy.create_engine('postgresql://postgres:@127.0.0.1:8181/lognex')

# Формирование списка продуктов и аккаунтов
product_list = pd.read_sql(sqlalchemy.text(f'''
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
    INNER JOIN paid_tariffs ON paid_tariffs.internal_id = t.id
    WHERE pv.name ILIKE 'Test_product_%'
    LIMIT {args.product_number}
'''), con)
account_list = pd.read_sql(sqlalchemy.text(f'''
    SELECT id
    FROM billing.billingaccount
    WHERE company LIKE '{args.company}%'
    LIMIT {args.company_number}
'''), con)


# Функция обработки батча
def process_batch(batch, progress):
    session = requests.Session()
    url = f'https://subzero-{args.namespace}.testms-test.lognex.ru/api/clinton/1.0/ticket'
    headers = {'Content-Type': 'application/json'}
    local_success = 0
    with open('bomber/json2_cancel.json', 'r') as json1:
        sub_data = json.load(json1)
        for account_id, product_id in batch:
            sub_data['accountId'] = str(account_id)
            sub_data['unsubscribeFrom']['product']['id'] = str(product_id.ID_продукта)
            sub_data['unsubscribeFrom']['tariff']['id'] = str(product_id.ID_платного_тарифа)
            response = session.post(url, json=sub_data, headers=headers)
            progress.update(1)
            if response.ok:
                local_success += 1
            else:
                error_msg = f"Ошибка {response.status_code} для аккаунта {account_id} - {response.text}"
                tqdm.write(error_msg)
    return local_success


# Создание и распределение батчей
total_requests = len(account_list) * len(product_list)
batches = [(account.id, product) for account in account_list.itertuples() for product in
           product_list.itertuples(index=False)]
batched_work = [batches[i::args.thread_number] for i in range(args.thread_number)]

# Инициализация общего прогресс-бара
progress_bar = tqdm(total=total_requests, desc='Общий прогресс')

# Запуск многопоточной обработки
with ThreadPoolExecutor(max_workers=args.thread_number) as executor:
    futures = [executor.submit(process_batch, batch, progress_bar) for batch in batched_work]
    results = [future.result() for future in as_completed(futures)]

progress_bar.close()

# Подведение итогов
total_success = sum(results)
print(f'Всего сброшено подписок: {total_success} из {total_requests}')