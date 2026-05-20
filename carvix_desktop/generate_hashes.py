import bcrypt

# Простые пароли для всех ролей (3 символа)
passwords = {
    'dis': '123',
    'dri': '123',
    'mec': '123',
    'adm': '123'
}

for role, password in passwords.items():
    # Генерируем хеш пароля
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    print(f"{role}: {hashed.decode('utf-8')}")
