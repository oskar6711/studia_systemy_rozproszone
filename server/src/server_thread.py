import threading
import json
from server_helpers import ServerHelpers, authorize


class ServerThread(threading.Thread):

    def __init__(self, client_address, client_socket):
        threading.Thread.__init__(self)
        self.client_socket = client_socket
        self.client_address = client_address

    def run(self):
        client_message = ''
        thread_name = super().getName()

        print(
            f'{thread_name} | Polaczono z klientem: {self.client_address[0]}:{self.client_address[1]}')

        users = {}
        with open('./data/users_data.json') as db:
            users = json.load(db)

        username, is_admin = authorize(self.client_socket, users)
        helpers = ServerHelpers(self.client_socket, username, users)

        print(f'{thread_name} | Uzytkownik {username} zalogowal sie')

        while True:
            helpers.load_users_data()
            data = self.client_socket.recv(2048)
            client_message = data.decode()
            msg_to_client = ''
            print(f'{thread_name} | Odczytana wiadomosc od klienta: {client_message}')

            if client_message == 'saldo':
                user_balance = helpers.get_balance(username)
                msg_to_client = f'Twoje saldo wynosi: {user_balance}'
                print(
                    f'{thread_name} | Balans uzytkownika {username} to {user_balance}')
                helpers.save_users_data()

            elif client_message == 'wyplata':
                withdrawed_amount = helpers.withdraw()
                if withdrawed_amount:
                    print(
                        f'{thread_name} | Wyplacono {withdrawed_amount} uzytkownikowi {username}')
                    msg_to_client = f'Wyplacono {withdrawed_amount} zl'
                    helpers.save_users_data()
                else:
                    msg_to_client = 'Anulowano'

            elif client_message == 'wplata':
                deposit_amount = helpers.deposit()
                if deposit_amount:
                    print(
                        f'{thread_name} | Uzytkownik {username} wplacil {deposit_amount}')
                    msg_to_client = f'Wplacono {deposit_amount}'
                    helpers.save_users_data()
                else:
                    msg_to_client = 'Anulowano'

            elif client_message == 'przelew':
                transfer = helpers.transfer()
                if transfer:
                    amount = transfer[0]
                    target_username = transfer[1]
                    print(
                        f'{thread_name} | Uzytkownik {username} przelal {amount} zl do uzytkownika {target_username}')
                    msg_to_client = f'Przelales {amount} zl do uzytkownika {target_username}'
                    helpers.save_users_data()
                else:
                    msg_to_client = 'Anulowano'

            elif client_message == 'nowy':
                if is_admin:
                    new_user = helpers.create_user()
                    if new_user:
                        print(f'{thread_name} | Admin dodal nowego uzytkownika')
                        msg_to_client = 'Dodano nowego uzytkownika'
                        helpers.save_users_data()
                    else:
                        msg_to_client = 'Anulowano'
                else:
                    msg_to_client = 'Nie jestes zalogowany jako admin!'

            elif client_message == 'modyfikuj':
                if is_admin:
                    modified_user = helpers.modify_user()
                    if modified_user[1]:
                        print(
                            f'{thread_name} | Admin zmodyfikowal dane uzytkownika {modified_user[0]}')
                        msg_to_client = f'Zmieniono dane uzytkownika {modified_user[0]}'
                        helpers.save_users_data()
                    else:
                        msg_to_client = 'Nie zmieniono zadnych danych'
                else:
                    msg_to_client = 'Nie jestes zalogowany jako admin!'

            elif client_message == 'wyjdz' or client_message == '':
                break

            helpers.send_message_to_client(msg_to_client, is_admin)
            msg_to_client = ''

        print(
            f'{thread_name} | Klient {self.client_address[0]}:{self.client_address[1]} rozlaczony.')
