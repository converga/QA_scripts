import requests
import json
import uuid
import argparse

# Command line arguments
parser = argparse.ArgumentParser(description='Product registration script')
parser.add_argument('--namespace', type=str, help='Namespace')
parser.add_argument('--product_number', type=int, help='Number of products to create')
parser.add_argument('--product_name', type=str, help='Name of the product')
args = parser.parse_args()

# set up url for creating the product
url = f'https://admin-{args.namespace}.testms-test.lognex.ru/api/tarifflego/1.0/product'
headers = {'Content-Type': 'application/json'}

# set data to activating request
data_activate = {
    "status": "ACTIVE"
}
json_activate = json.dumps(data_activate)

counter = 1
free_id = None
trial_id = None
for product in range(args.product_number):
    with open('bomber\product_sample.json', encoding='utf-8') as product_data:
        sub_data = json.load(product_data)
        sub_data['name'] = args.product_name + f'{counter}'

    for tariff in sub_data["tariffs"]:
        if tariff["name"]["en"] == "Free":
            free_id = str(uuid.uuid4())
            tariff["id"] = free_id
        elif tariff["name"]["en"] == "Trial":
            trial_id = str(uuid.uuid4())
            tariff["id"] = trial_id
        else:
            tariff["id"] = str(uuid.uuid4())

    # Assigning Free and Trial to a product
    sub_data['trial']['tariffId'] = trial_id
    sub_data['free']['tariffId'] = free_id

    # convert the modified data back to json encoded to utf-8 and with no ascii
    json_data = json.dumps(sub_data, ensure_ascii=False, indent=4).encode('utf-8')

    # make a POST request to the specified URL with the json data
    response = requests.post(url, json_data, headers=headers)

    # check the status code of the response
    if response.ok:
        print('Success')
        response_data = response.json()
        product_id = response_data.get("id")
        url2 = f'https://admin-{args.namespace}.testms-test.lognex.ru/api/tarifflego/1.0/product/{product_id}/version/1/status'

        response_activate = requests.put(url2, json_activate, headers=headers)
        if response_activate.status_code == 204:
            print(f'Product{counter} successfully activated!')
            print('------------------------------------------')
            counter += 1
        else:
            print(f'Request failed with status code {response_activate.status_code}')

    else:
        print(f'Failed, {response}')

# to run the script: 
# python creating_products2.py --namespace billing-1 --product_number 3 --product_name "test_product"  
