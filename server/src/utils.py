import random
import json

users = {}
with open('./data/users_data.json') as db:
    users = json.load(db)


def generate_account_number():
    rnd_number = str(random.randint(10**14, 10**15 - 1))
    account_numbers = []
    for user in users:
        account_numbers.append(users.get(user).get('account_number'))
    while rnd_number not in account_numbers:
        rnd_number = str(random.randint(10**14, 10**15 - 1))
    return rnd_number
