"""
Модуль валидации данных
"""
import re


class ValidationError(Exception):
    """Исключение для ошибок валидации"""
    pass


class Validator:
    """Класс для валидации данных"""

    @staticmethod
    def validate_fio(fio: str) -> bool:
        """Валидация ФИО"""
        if not fio or not fio.strip():
            raise ValidationError("ФИО обязательно для заполнения")

        fio = fio.strip()
        # Проверка: минимум 2 слова, каждое начинается с заглавной буквы
        words = fio.split()
        if len(words) < 2:
            raise ValidationError("ФИО должно содержать минимум 2 слова (Фамилия Имя)")

        # Проверка, что каждое слово начинается с заглавной буквы
        for word in words:
            if not word[0].isupper():
                raise ValidationError("Каждое слово в ФИО должно начинаться с заглавной буквы")

        # Проверка на наличие только букв и пробелов
        if not re.match(r'^[А-Яа-яA-Za-z\s]+$', fio):
            raise ValidationError("ФИО должно содержать только буквы")

        return True

    @staticmethod
    def validate_login(login: str) -> bool:
        """Валидация логина"""
        if not login or not login.strip():
            raise ValidationError("Логин обязателен для заполнения")

        login = login.strip()
        if len(login) < 3:
            raise ValidationError("Логин должен быть минимум 3 символа")

        if len(login) > 50:
            raise ValidationError("Логин должен быть не более 50 символов")

        # Только латинские буквы, цифры и подчеркивание
        if not re.match(r'^[a-zA-Z0-9_]+$', login):
            raise ValidationError("Логин должен содержать только латинские буквы, цифры и подчеркивание")

        return True

    @staticmethod
    def validate_password(password: str) -> bool:
        """Валидация пароля"""
        if not password:
            raise ValidationError("Пароль обязателен для заполнения")

        if len(password) < 6:
            raise ValidationError("Пароль должен быть минимум 6 символов")

        if len(password) > 100:
            raise ValidationError("Пароль должен быть не более 100 символов")

        # Проверка на наличие хотя бы одной заглавной буквы
        if not re.search(r'[A-Z]', password):
            raise ValidationError("Пароль должен содержать минимум 1 заглавную букву")

        # Проверка на наличие хотя бы одной строчной буквы
        if not re.search(r'[a-z]', password):
            raise ValidationError("Пароль должен содержать минимум 1 строчную букву")

        # Проверка на наличие хотя бы одной цифры
        if not re.search(r'\d', password):
            raise ValidationError("Пароль должен содержать минимум 1 цифру")

        return True

    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Валидация телефона"""
        if not phone:
            return True  # Телефон не обязателен

        phone = phone.strip()
        # Проверка формата +7 (XXX) XXX-XX-XX или аналогичного
        if not re.match(r'^\+?[\d\s\-\(\)]+$', phone):
            raise ValidationError("Телефон должен содержать только цифры, пробелы, дефисы, скобки и плюс")

        # Удаляем все нецифровые символы
        digits = re.sub(r'[^\d]', '', phone)
        if len(digits) < 10 or len(digits) > 15:
            raise ValidationError("Телефон должен содержать от 10 до 15 цифр")

        return True

    @staticmethod
    def validate_license_number(license_number: str) -> bool:
        """Валидация номера водительской лицензии"""
        if not license_number:
            return True  # Лицензия не обязательна

        license_number = license_number.strip()
        if len(license_number) < 5:
            raise ValidationError("Номер лицензии должен быть минимум 5 символов")

        if len(license_number) > 20:
            raise ValidationError("Номер лицензии должен быть не более 20 символов")

        return True

    @staticmethod
    def validate_gos_nomer(gos_nomer: str) -> bool:
        """Валидация гос. номера"""
        if not gos_nomer or not gos_nomer.strip():
            raise ValidationError("Гос. номер обязателен для заполнения")

        gos_nomer = gos_nomer.strip()
        # Проверка формата: А123БВ777
        if not re.match(r'^[А-Яа-яA-Za-z]\d{3}[А-Яа-яA-Za-z]{2}\d{2,3}$', gos_nomer):
            raise ValidationError("Гос. номер должен быть в формате А123БВ777")

        return True

    @staticmethod
    def validate_vin(vin: str) -> bool:
        """Валидация VIN кода"""
        if not vin or not vin.strip():
            raise ValidationError("VIN обязателен для заполнения")

        vin = vin.strip()
        if len(vin) != 17:
            raise ValidationError("VIN должен быть ровно 17 символов")

        if not re.match(r'^[A-HJ-NPR-Z0-9]+$', vin, re.IGNORECASE):
            raise ValidationError("VIN должен содержать только заглавные буквы (кроме I, O, Q) и цифры")

        return True

    @staticmethod
    def validate_probeg(probeg: int) -> bool:
        """Валидация пробега"""
        if probeg < 0:
            raise ValidationError("Пробег не может быть отрицательным")

        if probeg > 10000000:
            raise ValidationError("Пробег не может превышать 10,000,000 км")

        return True

    @staticmethod
    def validate_amount(amount: float) -> bool:
        """Валидация суммы (например, штрафа)"""
        if amount < 0:
            raise ValidationError("Сумма не может быть отрицательной")

        if amount > 1000000:
            raise ValidationError("Сумма не может превышать 1,000,000")

        return True
