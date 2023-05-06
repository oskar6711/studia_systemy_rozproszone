import random
from users_data import users


def generate_account_number():
    rnd_number = str(random.randint(10**14, 10**15 - 1))
    account_numbers = []
    for user in users:
        account_numbers.append(users.get(user).get('account_number'))
    while rnd_number not in account_numbers:
        rnd_number = str(random.randint(10**14, 10**15 - 1))
    return rnd_number


def get_users_data():
    pass


def set_users_data():
    pass
