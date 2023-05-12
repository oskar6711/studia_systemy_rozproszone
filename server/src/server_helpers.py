import json
import random


class ServerHelpers:

    def __init__(self, socket, username, users_data):
        self.socket = socket
        self.username = username
        self.users_data = users_data

    def save_users_data(self, path_to_database='./data/users_data.json'):
        with open(path_to_database, 'w') as db:
            json.dump(self.users_data, db)

    def load_users_data(self, path_to_database='./data/users_data.json'):
        with open(path_to_database) as db:
            self.users_data = json.load(db)

    def generate_account_number(self):
        acc_number = str(random.randint(10**14, 10**15 - 1))
        existing_acc_numbers = [
            self.users_data[user]['account_number'] for user in self.users_data.keys() if user != 'admin']
        while acc_number in existing_acc_numbers:
            acc_number = str(random.randint(10**14, 10**15 - 1))
        return acc_number

    def _handle_received_data(self):
        received_data = self.socket.recv(2048)
        decoded_data = received_data.decode()
        if decoded_data == 'powrot' or decoded_data == 'pomin':
            return False
        return decoded_data

    def _handle_amount_data(self):
        while True:
            data = self._handle_received_data()
            if not data:
                return False
            try:
                data = int(data)
                return data
            except ValueError:
                self._send_message(
                    'Kwota nie moze byc tekstem, sprobuj jeszcze raz lub jezeli chcesz wrocic, wpisz "powrot"')

    def _send_message(self, message):
        self.socket.send(bytes(message, 'utf-8'))

    def _set_balance(self, username, new_balance):
        self.users_data[username]['balance'] = str(new_balance)

    def get_balance(self, username):
        return self.users_data[username]['balance']

    def withdraw(self):
        amount = 0
        user_balance = self.get_balance(self.username)
        self._send_message(
            'Ile chcesz wyplacic? Jezeli chcesz wrocic, wpisz "powrot"')
        while True:
            data = self._handle_amount_data()
            if data:
                if int(data) > 0 and int(user_balance) - int(data) >= 0:
                    amount = data
                    new_balance = int(user_balance) - int(amount)
                    self._set_balance(self.username, new_balance)
                    return amount
                self._send_message(
                    'Nieprawidlowa kwota, sprobuj jeszcze raz lub jezeli chcesz wrocic, wpisz "powrot"')
            else:
                return False

    def deposit(self):
        amount = 0
        user_balance = self.get_balance(self.username)
        self._send_message(
            'Ile chcesz wplacic? Jezeli chcesz wrocic, wpisz "powrot"')
        while True:
            data = self._handle_amount_data()
            if data:
                if int(data) > 0:
                    amount = data
                    new_balance = int(user_balance) + int(amount)
                    self._set_balance(self.username, new_balance)
                    return amount
                self._send_message(
                    'Nieprawidlowa kwota, sprobuj jeszcze raz lub jezeli chcesz wrocic, wpisz "powrot"')
            else:
                return False

    def _get_transfer_amount(self):
        amount = 0
        source_user_balance = self.get_balance(self.username)

        self._send_message(
            f'Ile pieniedzy chcesz przelac? Jezeli chcesz wrocic, wpisz "powrot"')
        while True:
            data = self._handle_amount_data()
            if data:
                if int(data) > 0 and int(source_user_balance) - int(data) >= 0:
                    amount = data
                    return amount
                self._send_message(
                    'Nieprawidlowa kwota, sprobuj jeszcze raz lub jezeli chcesz wrocic, wpisz "powrot"')
            else:
                return False

    def _get_transfer_data(self):
        target_username = ''
        amount = self._get_transfer_amount()
        if amount:
            self._send_message(
                f'Komu chcesz przelac pieniadze - {amount} zl (podaj nazwe uzytkownika)? Jezeli chcesz wrocic, wpisz "powrot"')
            while True:
                data = self._handle_received_data()
                if data:
                    if data != self.username:
                        if data in self.users_data and data != 'admin':
                            target_username = data
                            return [amount, target_username]
                        self._send_message(
                            'Uzytkownik nie istnieje, sprobuj jeszcze raz lub jezeli chcesz wrocic, wpisz "powrot"')
                    else:
                        self._send_message(
                            'Nie mozesz przelac pieniedzy do siebie, sprobuj jeszcze raz lub jezeli chcesz wrocic, wpisz "powrot"')
                else:
                    return False
        return False

    def transfer(self):
        transfer_data = self._get_transfer_data()
        if transfer_data:
            amount = transfer_data[0]
            target = transfer_data[1]
            source_user_balance = self.get_balance(self.username)
            target_user_balance = self.get_balance(target)
            new_source_user_balance = int(source_user_balance) - int(amount)
            new_target_user_balance = int(target_user_balance) + int(amount)
            self._set_balance(self.username, new_source_user_balance)
            self._set_balance(target, new_target_user_balance)
            return [amount, target]
        else:
            return False

    def _set_property(self, property_to_set):
        """Function designed to set new user properites (username, password, name, surname, pesel)"""
        msg = ''

        if property_to_set == 'username':
            msg = 'Podaj nazwe uzytkownika lub jezeli chcesz wrocic, wpisz "powrot"'
        elif property_to_set == 'password':
            msg = 'Podaj haslo uzytkownika lub jezeli chcesz wrocic, wpisz "powrot"'
        elif property_to_set == 'name':
            msg = 'Podaj imie uzytkownika lub jezeli chcesz wrocic, wpisz "powrot"'
        elif property_to_set == 'surname':
            msg = 'Podaj nazwisko uzytkownika lub jezeli chcesz wrocic, wpisz "powrot"'
        elif property_to_set == 'pesel':
            msg = 'Podaj pesel uzytkownika lub jezeli chcesz wrocic, wpisz "powrot"'

        self._send_message(msg)
        data = self._handle_received_data()
        return data

    def create_user(self):
        username = self._set_property('username')
        if not username:
            return False
        password = self._set_property('password')
        if not password:
            return False
        name = self._set_property('name')
        if not name:
            return False
        surname = self._set_property('surname')
        if not surname:
            return False
        pesel = self._set_property('pesel')
        if not pesel:
            return False
        new_user = {
            'password': password,
            'name': name,
            'surname': surname,
            'pesel': pesel,
            'account_number': self.generate_account_number(),
            'balance': '0'
        }
        self.users_data[username] = new_user
        return True

    def _modify_property(self, property_to_modify):
        """Function designed to modify existing user properites (name, surname, pesel)"""
        msg = ''

        if property_to_modify == 'name':
            msg = 'Podaj nowe imie uzytkownika lub jezeli chcesz pominac, wpisz "pomin"'
        elif property_to_modify == 'surname':
            msg = 'Podaj nowe nazwisko uzytkownika lub jezeli chcesz pominac, wpisz "pomin"'
        elif property_to_modify == 'pesel':
            msg = 'Podaj nowy pesel uzytkownika lub jezeli chcesz pominac, wpisz "pomin"'
        else:
            raise AttributeError

        self._send_message(msg)
        data = self._handle_received_data()
        return data

    def _get_user_to_modify(self):
        self._send_message(
            'Jakiego uzytkownika chcesz zmodyfikowac (podaj nazwe uzytkownika)? Jezeli chcesz wrocic, wpisz "powrot"')
        while True:
            data = self._handle_received_data()
            if data:
                if data in self.users_data:
                    user_to_modify = data
                    return user_to_modify
                self._send_message(
                    'Podany uzytkownik nie istnieje, sprobuj jeszcze raz lub jezeli chcesz wrocic, wpisz "powrot"')
            else:
                return False

    def modify_user(self):
        changed = False
        user_to_modify = self._get_user_to_modify()
        if user_to_modify:
            new_name = self._modify_property('name')
            if new_name:
                self.users_data[user_to_modify]['name'] = new_name
                changed = True
            new_surname = self._modify_property('surname')
            if new_surname:
                self.users_data[user_to_modify]['surname'] = new_surname
                changed = True
            new_pesel = self._modify_property('pesel')
            if new_pesel:
                self.users_data[user_to_modify]['pesel'] = new_pesel
                changed = True
            return [user_to_modify, changed]
        return False

    def send_message_to_client(self, message, is_admin):
        if message:
            if is_admin:
                self._send_message(
                    f'{message}, co chcesz teraz zrobic? (nowy | modyfikuj | wyjdz)')
            else:
                self._send_message(
                    f'{message}, co chcesz teraz zrobic? (saldo | wyplata | wplata | przelew | wyjdz)')
        else:
            self._send_message(
                f'Komenda nie istnieje, wybierz jedna z: saldo | wyplata | wplata | przelew | wyjdz')
