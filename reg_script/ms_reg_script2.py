import requests
import argparse
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("-namespace", help="namespace target, for example: billing-1", required=True)
parser.add_argument("-name", default="test", help="name prefix of accounts, for example: test", required=True)
parser.add_argument("-number", default=10, help="number of accounts", type=int, required=False)
parser.add_argument("-threads", default=4, help="number of threads", type=int, required=False)

args = parser.parse_args()


def emails_list_generator(name, n):
    """ Generates list of emails based on the given prefix and number. """
    return [f"{name}{i}@mail.ru" for i in range(n)]


def register_account(email, progress):
    """ Function to register an account using the API. """
    url = f'https://api-{args.namespace}.testms-test.lognex.ru/api/remap/1.2/register'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {'email': email}
    response = requests.post(url, headers=headers, data=data)
    progress.update(1)  # Update the progress bar after each registration attempt
    return response.ok


def process_batch(emails, progress):
    """ Process a batch of emails for registration. """
    return sum(register_account(email, progress) for email in emails)


emails_list = emails_list_generator(args.name, args.number)

# Determine the size of each batch:
batch_size = int(np.ceil(len(emails_list) / args.threads))
batches = [emails_list[i:i + batch_size] for i in range(0, len(emails_list), batch_size)]

# Create a global progress bar
total_progress = tqdm(total=len(emails_list), desc='Total Progress', position=0)

with ThreadPoolExecutor(max_workers=args.threads) as executor:
    # Pass the same progress bar reference to all threads
    results = list(executor.map(lambda batch: process_batch(batch, total_progress), batches))

total_success = sum(results)
total_progress.close()

print('------------------------------------------------')
print(f'Total registered: {total_success} out of {len(emails_list)}')
