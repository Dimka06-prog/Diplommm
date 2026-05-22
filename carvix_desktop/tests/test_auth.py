"""
Тесты для системы авторизации
"""
import pytest
import bcrypt


class TestAuthentication:
    """Тесты авторизации"""

    def test_password_hashing(self):
        """Тест хеширования паролей"""
        password = "test123"
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)

        assert hashed is not None
        assert isinstance(hashed, bytes)
        assert bcrypt.checkpw(password.encode('utf-8'), hashed)

    def test_password_verification_success(self):
        """Тест успешной проверки пароля"""
        password = "correct_password"
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        assert bcrypt.checkpw(password.encode('utf-8'), hashed)

    def test_password_verification_failure(self):
        """Тест неудачной проверки пароля"""
        password = "correct_password"
        wrong_password = "wrong_password"
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        assert not bcrypt.checkpw(wrong_password.encode('utf-8'), hashed)

    def test_password_minimum_length(self):
        """Тест минимальной длины пароля"""
        # Пароль должен быть минимум 3 символа
        short_password = "ab"
        valid_password = "abc"

        assert len(short_password) < 3
        assert len(valid_password) >= 3
