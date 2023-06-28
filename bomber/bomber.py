import requests
import json
import sqlalchemy
import time
import pandas as pd
import argparse
from concurrent.futures import ThreadPoolExecutor

# параметры запуска:
def arg_parse():
    parser = argparse.ArgumentParser(description='subzero ticket trigger')
    parser.add_argument('-namespace', type=str, help='Target k8s namespace. Example: billing-1')
    parser.add_argument('-ticket_count', default=1, type=int, help='Count of subzero tickets to create')
    parser.add_argument('-t', '--threads', default=5, type=int,
                        help='The number of threads to create load')
    parser.add_argument('-prolong', default = True, type = bool)
    return parser.parse_args()


con = sqlalchemy.create_engine(
    'postgresql://postgres:@127.0.0.1:8181/lognex')  # Соединение к бд. Требуется проброс портов

args = arg_parse()

# namespace = 'billing-1'  # Неймспейс
#ticket_number = 1  # Количество заявок на 1 поток
#thread_number = 10  # Количество потоков
#prolongation_flag = False  # Для кейсов с автопролонгацией. True - включена, False - выключена

# Запрос
url = f'https://subzero-{args.namespace}.testms-test.lognex.ru/api/clinton/1.0/ticket'
headers = {'Content-Type': 'application/json'}


# Функция для запроса к базе
def sql_go(request):
    return pd.read_sql(sqlalchemy.text(request), con)


#  Формирование списка продуктов с его тарифами:

sql_product = '''
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
limit 10 '''  # Ограничение количества продуктов !!!
#  Формирование списка аккаунтов:

product_list = sql_go(sql_product)
account_list = sql_go('''select id from billing.billingaccount WHERE company LIKE 'test%'
limit 10 ''')  # Ограничение количества аккаунтов !!!


def bomber_many_products():
    

    print('bomber start')

    counter = 0

    with requests.Session():
        with open('bomber\json1.json', 'r') as json1:
            sub_data = json.load(json1)
            sub_data['subscribeTo']['autoprolongate'] = args.prolong

            for i in range(argparse.ticket_count):
                for index, row in account_list.iterrows():
                    sub_data['accountId'] = str(row['id'])

                    for index, row in product_list.iterrows():
                        sub_data['subscribeTo']['product']['id'] = str(product_list.loc[index, 'ID_продукта'])
                        sub_data['subscribeTo']['tariff']['id'] = str(product_list.loc[index, 'ID_платного_тарифа'])  # Вставить тариф из запроса, Платный или Бесплатный

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
with ThreadPoolExecutor(max_workers=args.threads) as executor:
    # Запуск потоков
    results = [executor.submit(bomber_many_products) for _ in range(args.threads)]

end = time.time() - start  # конец отчета времени
print('Все потоки отработали')
print(f'Выполнялось: {end}с')
