from utils import generate_account_number


class ServerHelpers:

    def __init__(self, socket, username, users_data):
        self.socket = socket
        self.username = username
        self.users_data = users_data

    def _send_message(self, message):
        self.socket.send(bytes(message, 'utf-8'))

    def _set_balance(self, username, new_balance):
        self.users_data[username]['balance'] = new_balance

    def get_balance(self, username):
        return self.users_data[username]['balance']

    def withdraw(self):
        amount = 0
        user_balance = self.get_balance(self.username)
        self._send_message(
            'Ile chcesz wyplacic? Jezeli chcesz wrocic, wpisz "powrot"')
        while True:
            data = self.socket.recv(2048)
            tmp_amount = data.decode()
            if tmp_amount == 'powrot':
                return False
            elif int(tmp_amount) > 0 and int(user_balance) - int(tmp_amount) >= 0:
                amount = tmp_amount
                new_balance = int(user_balance) - int(amount)
                self._set_balance(self.username, new_balance)
                return amount
            self._send_message(
                'Nieprawidlowa kwota, sprobuj jeszcze raz lub jezeli chcesz wrocic, wpisz "powrot"')

    def deposit(self):
        amount = 0
        user_balance = self.get_balance(self.username)
        self._send_message(
            'Ile chcesz wplacic? Jezeli chcesz wrocic, wpisz "powrot"')
        while True:
            data = self.socket.recv(2048)
            tmp_amount = data.decode()
            if tmp_amount == 'powrot':
                return False
            elif int(tmp_amount) > 0:
                amount = tmp_amount
                new_balance = int(user_balance) + int(amount)
                self._set_balance(self.username, new_balance)
                return amount
            self._send_message(
                'Nieprawidlowa kwota, sprobuj jeszcze raz lub jezeli chcesz wrocic, wpisz "powrot"')

    def _get_transfer_amount(self):
        amount = 0
        source_user_balance = self.get_balance(self.username)

        self._send_message(
            f'Ile pieniedzy chcesz przelac? Jezeli chcesz wrocic, wpisz "powrot"')
        while True:
            data = self.socket.recv(2048)
            tmp_amount = data.decode()
            if tmp_amount == 'powrot':
                return False
            elif int(tmp_amount) > 0 and int(source_user_balance) - int(tmp_amount) >= 0:
                amount = tmp_amount
                return amount
            self._send_message(
                'Nieprawidlowa kwota, sprobuj jeszcze raz lub jezeli chcesz wrocic, wpisz "powrot"')

    def _get_transfer_data(self):
        target_username = ''
        amount = self._get_transfer_amount()
        if amount:
            self._send_message(
                f'Komu chcesz przelac pieniadze - {amount} zl (podaj nazwe uzytkownika)? Jezeli chcesz wrocic, wpisz "powrot"')
            while True:
                data = self.socket.recv(2048)
                tmp_target_username = data.decode()
                if tmp_target_username == 'powrot':
                    return False
                elif tmp_target_username in self.users_data and tmp_target_username != 'admin':
                    target_username = tmp_target_username
                    return [amount, target_username]
                self._send_message(
                    'Uzytkownik nie istnieje, sprobuj jeszcze raz lub jezeli chcesz wrocic, wpisz "powrot"')
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
        """Function designed to set user properites (username, password, name, surname, pesel)"""
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
        else:
            raise AttributeError

        self._send_message(msg)
        data = self.socket.recv(2048)
        property = data.decode()
        if property == 'powrot':
            return False
        return property

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
            'account_number': generate_account_number(),
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
        data = self.socket.recv(2048)
        property = data.decode()
        if property == 'pomin':
            return False
        return property

    def _get_user_to_modify(self):
        self._send_message(
            'Jakiego uzytkownika chcesz zmodyfikowac (podaj nazwe uzytkownika)? Jezeli chcesz wrocic, wpisz "powrot"')
        while True:
            data = self.socket.recv(2048)
            tmp_user_to_modify = data.decode()
            if tmp_user_to_modify == 'powrot':
                return False
            elif tmp_user_to_modify in self.users_data:
                user_to_modify = tmp_user_to_modify
                return user_to_modify
            self._send_message(
                'Podany uzytkownik nie istnieje, sprobuj jeszcze raz lub jezeli chcesz wrocic, wpisz "powrot"')

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


def authorize(socket, users_data):
    user = ['', False]

    while True:
        socket.send(
            bytes(f'Podaj nazwe uzytkownika:', 'utf-8'))
        while True:
            data = socket.recv(2048)
            tmp_username = data.decode()
            if tmp_username in users_data:
                user[0] = tmp_username
                break
            else:
                socket.send(
                    bytes(f'Podany uzytkownik nie istnieje, sprobuj jeszcze raz:', 'utf-8'))

        socket.send(
            bytes(f'Podaj haslo:', 'utf-8'))
        while True:
            data = socket.recv(2048)
            tmp_password = data.decode()

            if users_data[user[0]]['password'] == tmp_password:
                if user[0] == 'admin':
                    user[1] = True
                    socket.send(
                        bytes(f'Zalogowano jako Admin, co chcesz teraz zrobic? (nowy | modyfikuj | wyjdz)', 'utf-8'))
                else:
                    socket.send(
                        bytes(f'Zalogowano jako {user[0]}, co chcesz teraz zrobic? (saldo | wyplata | wplata | przelew | wyjdz)', 'utf-8'))
                break
            else:
                socket.send(
                    bytes(f'Bledne haslo, sprobuj jeszcze raz:', 'utf-8'))
        return user
