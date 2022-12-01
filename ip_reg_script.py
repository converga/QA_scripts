import requests

# Список айпишников из https://lognex.atlassian.net/wiki/spaces/SPC1/pages/3814228396/-+IpInfo+dadata+geoplugin
ip_list = ['95.24.50.58',
           '37.145.40.212',
           '178.187.3.208',
           '212.34.121.245',
           '95.24.50.37',
           '92.246.141.255',
           '31.148.205.9',
           '5.137.104.150',
           '83.234.158.25',
           '95.31.190.41',
           '109.163.216.177',
           '109.170.69.122',
           '85.103.40.151',
           '185.107.81.152',
           '217.138.194.124',
           '195.54.178.39',
           '165.231.253.250',
           '5.248.131.255',
           '194.242.103.154',
           '109.110.84.153',
           '194.38.2.27',
           '37.79.92.107',
           '195.245.103.117',
           '151.249.174.104',
           '31.148.211.27',
           '46.20.203.50',
           '94.240.24.91',
           '207.180.230.92',
           '178.141.122.9',
           '178.176.113.4',
           '92.255.238.124',
           '94.25.181.116'
           ]


def ip_reg(namespace, company_name):
    url = f'https://online-{namespace}.testms-test.lognex.ru/registration'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    counter = 0

    for ip in ip_list:
        email = str(company_name) + str(counter) + '@' + 'mail.ru'
        data = {
            'email': email,
            'ipSource': ip,
        }
        response = requests.post(url, headers=headers, data=data)
        if response.ok:
            counter += 1
            # response=json.loads(response.text)
            print(f'account №{counter} with ip {ip} successfully registered')
        else:
            print('Registry failed!' + str(response))
    print('------------------------------------------------')
    print(f'итого, зарегистрировано: {counter} аккаунтов из', len(ip_list))


# Пуск скрипта
# 1ый параметр: неймспейс, 2ой - название компании для формирования email
ip_reg('billing-4', 'dadata_last')
