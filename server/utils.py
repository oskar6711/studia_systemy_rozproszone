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
    users_data = []
    with open('users_database.txt', 'r') as file:
        for line in file:
            line = line.strip()
            users_data.append(line)
    return users_data


def set_users_data():
    users_data = get_users_data()
    with open('./users_database.txt', 'w') as file:
        for line in users_data:
            file.write(line + '\n')


print(get_users_data())
