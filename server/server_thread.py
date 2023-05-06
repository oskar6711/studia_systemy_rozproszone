import threading
from users_database import users
from utils import generate_account_number


class ServerThread(threading.Thread):

    def __init__(self, client_address, client_socket):
        threading.Thread.__init__(self)
        self.client_socket = client_socket
        self.client_address = client_address

    def get_balance(self, username):
        return users[username]['balance']

    def set_balance(self, username, new_balance):
        users[username]['balance'] = new_balance

    def withdraw_money(self, username, amount):
        balance = self.get_balance(username)
        self.set_balance(username, str(int(balance) - int(amount)))

    def deposit_money(self, username, amount):
        balance = self.get_balance(username)
        self.set_balance(username, str(int(balance) + int(amount)))

    def transfer_money(self, source_username, amount, target_username):
        source_balance = int(self.get_balance(source_username)) - int(amount)
        target_balance = int(self.get_balance(target_username)) + int(amount)
        self.set_balance(source_username, str(source_balance))
        self.set_balance(target_username, str(target_balance))

    def admin_add_user(self, username, password, name, surname, pesel):
        new_user = {
            'password': password,
            'name': name,
            'surname': surname,
            'pesel': pesel,
            'account_number': generate_account_number(),
            'balance': '0'
        }
        users[username] = new_user

    def admin_modify_user(self, target_username, new_name, new_surname, new_pesel):
        if new_name:
            users[target_username]['name'] = new_name
        if new_surname:
            users[target_username]['surname'] = new_surname
        if new_pesel:
            users[target_username]['pesel'] = new_pesel

    def run(self):
        logged_in = False
        is_admin = False
        username = ''
        client_message = ''
        thread_name = super().getName()

        print(
            f'{thread_name} | Polaczono z klientem: {self.client_address[0]}:{self.client_address[1]}')

        while not logged_in:
            while not username:
                self.client_socket.send(
                    bytes(f'Podaj nazwe uzytkownika:', 'utf-8'))
                data = self.client_socket.recv(2048)
                tmp_username = data.decode()
                if tmp_username in users:
                    username = tmp_username
                    break

            while True:
                self.client_socket.send(
                    bytes(f'Podaj haslo:', 'utf-8'))
                data = self.client_socket.recv(2048)
                tmp_password = data.decode()

                if users[username]['password'] == tmp_password:
                    logged_in = True
                    if username == 'admin':
                        is_admin = True
                        self.client_socket.send(
                            bytes(f'Zalogowano jako Admin, co chcesz teraz zrobic? (nowy | modyfikuj | wyjdz)', 'utf-8'))
                    else:
                        self.client_socket.send(
                            bytes(f'Zalogowano jako {username}, co chcesz teraz zrobic? (saldo | wyplata | wplata | przelew | wyjdz)', 'utf-8'))
                    break

        while True:
            data = self.client_socket.recv(2048)
            client_message = data.decode()
            msg_to_client = ''
            print(f'{thread_name} | Odczytana wiadomosc od klienta: {client_message}')

            if client_message == 'saldo':
                user_balance = self.get_balance(username)
                print(
                    f'{thread_name} | Balans uzytkownika {username} to {user_balance}')
                msg_to_client = f'Twoje saldo wynosi: {user_balance}'

            elif client_message == 'wyplata':
                amount = 0
                cancelled = False
                user_balance = self.get_balance(username)
                self.client_socket.send(
                    bytes(f'Ile chcesz wyplacic? Jezeli chcesz wrocic, wpisz "powrot"', 'utf-8'))
                while True:
                    data = self.client_socket.recv(2048)
                    tmp_amount = data.decode()
                    if tmp_amount == 'powrot':
                        cancelled = True
                        msg_to_client = 'Anulowano'
                        break
                    elif int(tmp_amount) > 0 and int(user_balance) - int(tmp_amount) >= 0:
                        amount = tmp_amount
                        break
                    self.client_socket.send(
                        bytes(f'Nieprawidlowa kwota, sprobuj jeszcze raz lub jezeli chcesz wrocic, wpisz "powrot"', 'utf-8'))

                if not cancelled:
                    self.withdraw_money(username, amount)
                    print(
                        f'{thread_name} | Wyplacono {amount} uzytkownikowi {username}')
                    msg_to_client = f'Wyplacono {amount} zl'

            elif client_message == 'wplata':
                amount = 0
                cancelled = False
                user_balance = self.get_balance(username)
                self.client_socket.send(
                    bytes(f'Ile chcesz wplacic? Jezeli chcesz wrocic, wpisz "powrot"', 'utf-8'))
                while True:
                    data = self.client_socket.recv(2048)
                    tmp_amount = data.decode()
                    if tmp_amount == 'powrot':
                        cancelled = True
                        msg_to_client = 'Anulowano'
                        break
                    elif int(tmp_amount) > 0:
                        amount = tmp_amount
                        break
                    self.client_socket.send(
                        bytes(f'Nieprawidlowa kwota, sprobuj jeszcze raz lub jezeli chcesz wrocic, wpisz "powrot"', 'utf-8'))

                if not cancelled:
                    self.deposit_money(username, amount)
                    print(
                        f'{thread_name} | Uzytkownik {username} wplacil {amount}')
                    msg_to_client = f'Wplaciles {amount}'

            elif client_message == 'przelew':
                amount = 0
                cancelled = False
                source_user_balance = self.get_balance(username)
                target_username = ''

                self.client_socket.send(
                    bytes(f'Ile pieniedzy chcesz przelac? Jezeli chcesz wrocic, wpisz "powrot"', 'utf-8'))
                while True:
                    data = self.client_socket.recv(2048)
                    tmp_amount = data.decode()
                    if tmp_amount == 'powrot':
                        cancelled = True
                        msg_to_client = 'Anulowano'
                        break
                    elif int(tmp_amount) > 0 and int(source_user_balance) - int(tmp_amount) >= 0:
                        amount = tmp_amount
                        break
                    self.client_socket.send(
                        bytes(f'Nieprawidlowa kwota, sprobuj jeszcze raz lub jezeli chcesz wrocic, wpisz "powrot"', 'utf-8'))

                if not cancelled:
                    self.client_socket.send(
                        bytes(f'Komu chcesz przelac pieniadze - {amount} zl (podaj nazwe uzytkownika)? Jezeli chcesz wrocic, wpisz "powrot"', 'utf-8'))
                    while True:
                        data = self.client_socket.recv(2048)
                        tmp_target_username = data.decode()
                        if tmp_target_username == 'powrot':
                            cancelled = True
                            msg_to_client = 'Anulowano'
                            break
                        elif tmp_target_username in users and tmp_target_username != 'admin':
                            target_username = tmp_target_username
                            break
                        self.client_socket.send(
                            bytes(f'Uzytkownik nie istnieje, sprobuj jeszcze raz lub jezeli chcesz wrocic, wpisz "powrot"', 'utf-8'))

                if not cancelled:
                    self.transfer_money(username, amount, target_username)
                    print(
                        f'{thread_name} | Uzytkownik {username} przelal {amount} zl do uzytkownika {target_username}')
                    msg_to_client = f'Przelales {amount} zl do uzytkownika {target_username}'

            elif client_message == 'nowy':
                if is_admin:
                    new_username = ''
                    new_password = ''
                    new_name = ''
                    new_surname = ''
                    new_pesel = ''
                    cancelled = False

                    self.client_socket.send(
                        bytes(f'Podaj nazwe nowego uzytkownika lub jezeli chcesz wrocic, wpisz "powrot"', 'utf-8'))
                    new_username_data = self.client_socket.recv(2048)
                    tmp_new_username = new_username_data.decode()
                    if tmp_new_username == 'powrot':
                        cancelled = True
                        msg_to_client = 'Anulowano'
                    else:
                        new_username = tmp_new_username

                    if not cancelled:
                        self.client_socket.send(
                            bytes(f'Podaj haslo dla nowego uzytkownika lub jezeli chcesz wrocic, wpisz "powrot"', 'utf-8'))
                        new_password_data = self.client_socket.recv(2048)
                        tmp_new_password = new_password_data.decode()
                        if tmp_new_password == 'powrot':
                            cancelled = True
                            msg_to_client = 'Anulowano'
                        else:
                            new_password = tmp_new_password

                    if not cancelled:
                        self.client_socket.send(
                            bytes(f'Podaj imie nowego uzytkownika lub jezeli chcesz wrocic, wpisz "powrot"', 'utf-8'))
                        new_name_data = self.client_socket.recv(2048)
                        tmp_new_name = new_name_data.decode()
                        if tmp_new_name == 'powrot':
                            cancelled = True
                            msg_to_client = 'Anulowano'
                        else:
                            new_name = tmp_new_name

                    if not cancelled:
                        self.client_socket.send(
                            bytes(f'Podaj nazwisko nowego uzytkownika lub jezeli chcesz wrocic, wpisz "powrot"', 'utf-8'))
                        new_surname_data = self.client_socket.recv(2048)
                        tmp_new_surname = new_surname_data.decode()
                        if tmp_new_surname == 'powrot':
                            cancelled = True
                            msg_to_client = 'Anulowano'
                        else:
                            new_surname = tmp_new_surname

                    if not cancelled:
                        self.client_socket.send(
                            bytes(f'Podaj pesel nowego uzytkownika lub jezeli chcesz wrocic, wpisz "powrot"', 'utf-8'))
                        new_pesel_data = self.client_socket.recv(2048)
                        tmp_new_pesel = new_pesel_data.decode()
                        if tmp_new_pesel == 'powrot':
                            cancelled = True
                            msg_to_client = 'Anulowano'
                        else:
                            new_pesel = tmp_new_pesel

                    if not cancelled:
                        self.admin_add_user(
                            new_username, new_password, new_name, new_surname, new_pesel)
                        print(f'{thread_name} | Admin dodal nowego uzytkownika')
                        msg_to_client = 'Dodano nowego uzytkownika'
                else:
                    msg_to_client = 'Nie jestes zalogowany jako admin!'

            elif client_message == 'modyfikuj':
                if is_admin:
                    user_to_modify = ''
                    modified_name = ''
                    modified_surname = ''
                    modified_pesel = ''
                    cancelled = False

                    self.client_socket.send(
                        bytes(f'Jakiego uzytkownika chcesz zmodyfikowac (podaj nazwe uzytkownika)? Jezeli chcesz wrocic, wpisz "powrot"', 'utf-8'))
                    while True:
                        data = self.client_socket.recv(2048)
                        tmp_user_to_modify = data.decode()
                        if tmp_user_to_modify == 'powrot':
                            cancelled = True
                            msg_to_client = 'Anulowano'
                            break
                        elif tmp_user_to_modify in users:
                            user_to_modify = tmp_user_to_modify
                            break
                        self.client_socket.send(
                            bytes(f'Podany uzytkownik nie istnieje, sprobuj jeszcze raz lub jezeli chcesz wrocic, wpisz "powrot"', 'utf-8'))

                    self.client_socket.send(
                        bytes(f'Podaj nowe imie lub jezeli chcesz pominac, wpisz "pomin"', 'utf-8'))
                    modified_name_data = self.client_socket.recv(2048)
                    tmp_modified_name = modified_name_data.decode()
                    if tmp_user_to_modify != 'pomin':
                        modified_name = tmp_modified_name
                    else:
                        modified_name = users[user_to_modify]['name']

                    self.client_socket.send(
                        bytes(f'Podaj nowe nazwisko lub jezeli chcesz pominac, wpisz "pomin"', 'utf-8'))
                    modified_surname_data = self.client_socket.recv(2048)
                    tmp_modified_surname = modified_surname_data.decode()
                    if tmp_modified_surname != 'pomin':
                        modified_surname = tmp_modified_surname
                    else:
                        modified_surname = users[user_to_modify]['surname']

                    self.client_socket.send(
                        bytes(f'Podaj nowy pesel lub jezeli chcesz pominac, wpisz "pomin"', 'utf-8'))
                    modified_pesel_data = self.client_socket.recv(2048)
                    tmp_modified_pesel = modified_pesel_data.decode()
                    if tmp_modified_pesel != 'pomin':
                        modified_pesel = tmp_modified_pesel
                    else:
                        modified_pesel = users[user_to_modify]['pesel']

                    self.admin_modify_user(
                        user_to_modify, modified_name, modified_surname, modified_pesel)
                    print(
                        f'{thread_name} | Admin zmodyfikowal dane uzytkownika {user_to_modify}')
                    msg_to_client = f'Zmieniono dane uzytkownika {user_to_modify}'
                else:
                    msg_to_client = 'Nie jestes zalogowany jako admin!'

            elif client_message == 'wyjdz' or client_message == '':
                break

            if msg_to_client:
                if is_admin:
                    self.client_socket.send(
                        bytes(f'{msg_to_client}, co chcesz teraz zrobic? (nowy | modyfikuj | wyjdz)', 'utf-8'))
                else:
                    self.client_socket.send(
                        bytes(f'{msg_to_client}, co chcesz teraz zrobic? (saldo | wyplata | wplata | przelew | wyjdz)', 'utf-8'))
            else:
                self.client_socket.send(
                    bytes(f'Komenda nie istnieje, wybierz jedna z: saldo | wyplata | wplata | przelew | wyjdz', 'utf-8'))

            msg_to_client = ''

        print(
            f'{thread_name} | Klient {self.client_address[0]}:{self.client_address[1]} rozlaczony.')
