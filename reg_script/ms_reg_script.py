import requests
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-namespace", help="namespace target, for example: billing-1", required=True)
parser.add_argument("-name", default="test", help="name prefix of accountsm for example: test", required=True)
parser.add_argument("-number", default=10,  help="number of accounts", type = int, required=False)

args = parser.parse_args()


def emails_list_generator(name, n):
    emails = []
    for i in range(n):
        result = name + str(i) + '@' + 'mail.ru'
        emails.append(result)
    return emails


emails_list = emails_list_generator(args.name, args.number)
#len(emails_list)

#namespace = 'billing-2'  # Неймспейс

url = f'https://online-{args.namespace}.testms-test.lognex.ru/api/remap/1.2/register'
headers = {'Content-Type': 'application/x-www-form-urlencoded'}

counter = 0
for email in emails_list:
    data = {
        'email': email
    }
    response = requests.post(url, headers=headers, data=data)
    if response.ok:
        counter += 1
        # response=json.loads(response.text)
        print(f'account №{counter} successfully registered')
    else:
        print('Registry failed!' + str(response))
print('------------------------------------------------')
print(f'итого, зарегистрировано: {counter} из', len(emails_list))
