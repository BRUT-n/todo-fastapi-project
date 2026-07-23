# import time
# from datetime import timedelta

# import jwt
# from freezegun import freeze_time
# from src.auth.utils import encode_jwt_token, hash_password, validate_password
# from src.config import settings


# def test_hash_password():
#     """
#     Проверка что хеш не равен исходному паролю.
#     Проверка разности паролей (из-за использование соли).
#     Проверка что пароль захеширован в виде байтов.
#     """
#     test_password = "secret_string"
#     hashed_test_password_1 = hash_password(test_password)
#     hashed_test_password_2 = hash_password(test_password)

#     assert hashed_test_password_1 != test_password
#     assert hashed_test_password_1 != hashed_test_password_2
#     assert isinstance(hashed_test_password_1, bytes)

# def test_validate_password():
#     """
#     Проверка пароля по хешу.
#     Верный пароль соответствует существующему хешу.
#     Неверный пароль не валиден по хешу.
#     """
#     correct_password = "secret_password"
#     wrong_password = "not_secret_password"
#     correct_hash = hash_password(correct_password)

#     assert validate_password(correct_password, correct_hash) is True
#     assert validate_password(wrong_password, correct_hash) is False

# def test_encode_jwt_without_expire_time():
#     """
#     Проверка работоспособности кодирования словаря в JWT.
#     Проверка полезной нагрузки в токене БЕЗ времени действия токена.
#     Проверяется по типу "ключ: значение" и так же тип данных токена str.
#     """
#     payload = {
#         "sub": "mail@test.com",
#         "name": "Name",
#         "user_id": 1
#     }

#     token = encode_jwt_token(payload=payload)
#     decoded_token = jwt.decode(token, options={"verify_signature": False})

#     assert isinstance(token, str)
#     assert decoded_token["sub"] == "mail@test.com"
#     assert decoded_token["name"] == "Name"
#     assert decoded_token["user_id"] == 1

# @freeze_time("2026-07-13 12:00:00")
# def test_encode_jwt_and_expire_minutes():
#     """
#     Проверка валидности JWT по времени действия из настроек глобальных переменных.
#     Полученное из токена время истечения сравнивается с замороженным временем к которому
#     прибавляется (минуты * 60) в формате timestamp.
#     """
#     payload = {
#         "sub" : "test"
#     }

#     token = encode_jwt_token(payload=payload)
#     decoded_jwt = jwt.decode(token, options={"verify_signature": False})
#     expire_time_from_token = decoded_jwt.get("exp")

#     assert expire_time_from_token is not None

#     expected_expire_time = time.time() + (settings.auth.ACCESS_TOKEN_EXPIRE_MINUTES * 60)

#     assert expire_time_from_token == expected_expire_time

# @freeze_time("2026-07-13 12:00:00")
# def test_encode_jwt_and_expire_time_delta():
#     """
#     Проверка валидности JWT по времени действия из переданного аргумента.
#     Полученное из токена время сравнивается с текущим замороженным временем к которому
#     добавлено время из формата timedelta приведенное к секндам.
#     """
#     payload = {
#         "sub": "test"
#     }

#     delta = timedelta(minutes=1)
#     token = encode_jwt_token(payload=payload, expire_time_delta=delta)
#     decoded_jwt = jwt.decode(token, options={"verify_signature": False})
#     expire_time_from_token = decoded_jwt.get("exp")

#     assert expire_time_from_token is not None

#     expected_expire_time = time.time() + (delta.total_seconds())

#     assert expire_time_from_token == expected_expire_time
