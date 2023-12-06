import requests
import sqlalchemy
import time
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

con = sqlalchemy.create_engine(
    'postgresql://postgres:@127.0.0.1:8181/lognex')

namespace = 'billing-5'  # Неймспейс
thread_number = 20  # Количество потоков

# Функция для запроса к базе
def sql_go(request):
    return pd.read_sql(sqlalchemy.text(request), con)

#  Формирование списка продуктов с его тарифами:

sql_product = '''
SELECT 
       pv.internal_id AS "ID_продукта"
FROM billing.productversion pv
WHERE pv.name ILIKE 'Test_product_%'
limit 10 '''  # Ограничение количества продуктов !!!
#  Формирование списка аккаунтов:

product_list = sql_go(sql_product)


def bomber_report_get():
    print('bomber_report starts')

    counter = 0

    with requests.Session():
        for index, row in product_list.iterrows():
        # for product in (product_list):
            product = str(product_list.loc[index, 'ID_продукта'])
            
            # Запрос
            url = f'https://admin-{namespace}.testms-test.lognex.ru/api/bones/1.0/product/{product}/vendorrevenue?periodStartMoment=2023-03-01T00%3A00%3A00%2B03%3A00&periodEndMoment=2023-05-05T00%3A00%3A00%2B03%3A00'
            headers = {'Content-Type': 'application/json'}
            
            response = requests.get(url, headers=headers)

            if response.ok:
                print()
                print(f'Для {product}, ', response.text,  '\n')
                print('------------------------------------------------')
            else:
                print(f'Для {product}, Ошибка' + str(response))
            counter += 1

    print('------------------------------------------------')
    print('------------------------------------------------')
    print(f'||| Итого, выполнено запросов в потоке: {counter} |||')


# Пуск потоков:

start = time.time()  # точка отсчета времени
with ThreadPoolExecutor(max_workers=thread_number) as executor:
    # Запуск потоков
    results = [executor.submit(bomber_report_get) for _ in range(thread_number)]

end = time.time() - start  # конец отчета времени
print('Все потоки отработали')
print(f'Выполнялось: {end}с')

