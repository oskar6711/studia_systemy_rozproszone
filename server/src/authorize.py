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
