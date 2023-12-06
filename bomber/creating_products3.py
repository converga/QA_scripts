import requests
import json
import uuid

# Changing parameters:
counter = 1  # Product number alias
namespace = 'billing-4'  # Namespace
product_number = 4  # Number of products to create

# set up url for creating the product
url = f'https://admin-{namespace}.testms-test.lognex.ru/api/tarifflego/1.0/product'
headers = {'Content-Type': 'application/json'}

# set data to activating request
data_activate = {
    "status": "ACTIVE"
}
json_activate = json.dumps(data_activate)

for product in range(product_number):
    with open('bomber\product_sample.json', encoding='utf-8') as product_data:
        sub_data = json.load(product_data)
        sub_data['name'] = str(f'Test_product_{counter}')

    for tariff in sub_data["tariffs"]:
        tariff["id"] = str(uuid.uuid4())

    # Remove blocks based on product number
    product_type = counter % 4
    name_prefix = ""
    if product_type == 1:  # like in the json
        pass
    elif product_type == 2:  # no 'trial'
        del sub_data['trial']
        name_prefix = "_NoTrial"
    elif product_type == 3:  # no 'free'
        del sub_data['free']
        name_prefix = "_NoFree"
    elif product_type == 0:  # no 'free' and no 'trial'
        del sub_data['free']
        del sub_data['trial']
        name_prefix = "_NoFree_NoTrial"

    # Add prefix to product name
    sub_data['name'] =  sub_data['name'] + name_prefix

    # Assigning Free and Trial to a product, if exist
    if 'free' in sub_data:
        free_tariff = next((tariff for tariff in sub_data["tariffs"] if tariff["name"]["en"] == "Free"), None)
        if free_tariff:
            sub_data['free']['tariffId'] = free_tariff["id"]
    if 'trial' in sub_data:
        trial_tariff = next((tariff for tariff in sub_data["tariffs"] if tariff["name"]["en"] == "Trial"), None)
        if trial_tariff:
            sub_data['trial']['tariffId'] = trial_tariff["id"]

    # convert the modified data back to json encoded to utf-8 and with no ascii
    json_data = json.dumps(sub_data, ensure_ascii=False, indent=4).encode('utf-8')

    # make a POST request to the specified URL with the json data
    response = requests.post(url, json_data, headers=headers)

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
            counter += 1
        else:
            print(f'Request failed with status code {response_activate.status_code}')

    else:
        print(f'Failed, {response}')
