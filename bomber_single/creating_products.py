import requests
import json
import uuid

# Changing parameters:
counter = 1
namespace = 'billing-4'
product_number = 6

# set up url for creating the product
url = f'https://admin-{namespace}.testms-test.lognex.ru/api/tarifflego/1.0/product'
headers = {'Content-Type': 'application/json'}

# set data to activating request
data_activate = {
    "status": "ACTIVE"
}
json_activate = json.dumps(data_activate)

free_id = None
trial_id = None
for product in range(product_number):
    with open('product_sample.json', encoding='utf-8') as product_data:
        sub_data = json.load(product_data)
        sub_data['name'] = str(f'Test_product_{counter}')

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
    counter += 1

    # check the status code of the response
    if response.ok:
        print('Success')
        response_data = response.json()
        product_id = response_data.get("id")
        url2 = f'https://admin-{namespace}.testms-test.lognex.ru/api/tarifflego/1.0/product/{product_id}/version/1/status'

        response_activate = requests.put(url2, json_activate, headers=headers)
        if response_activate.status_code == 204:
            print(f'Product{counter} successfully activated!')
            print('------------------------------------------')
        else:
            print(f'Request failed with status code {response_activate.status_code}')

    else:
        print(f'Failed, {response}')