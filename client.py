import requests
import base64

# Создаем пользователя
user_response = requests.post(
    "http://127.0.0.1:5000/users",
    json={"email": "user@example.com", "password": "password123"},
)
print(f"Create user: {user_response.status_code}")
print(user_response.json())

# Авторизация через Basic Auth
credentials = base64.b64encode(b"user@example.com:password123").decode("utf-8")
headers = {"Authorization": f"Basic {credentials}"}

# 1. Создаем объявление (только авторизованный пользователь)
create_response = requests.post(
    "http://127.0.0.1:5000/ads",
    json={"title": "Продам велосипед", "text": "Горный велосипед в отличном состоянии"},
    headers=headers,
)
print(f"Create: {create_response.status_code}")
print(create_response.json())

# 2. Получаем объявление по ID (без авторизации)
get_response = requests.get("http://127.0.0.1:5000/ads/1")
print(f"Get: {get_response.status_code}")
print(get_response.json())

# 3. Корректируем объявление (только владелец)
update_response = requests.patch(
    "http://127.0.0.1:5000/ads/1",
    json={
        "title": "Продам велосипед СРОЧНО",
        "text": "Горный велосипед в отличном состоянии. Торг уместен!",
    },
    headers=headers,
)
print(f"Update: {update_response.status_code}")
print(update_response.json())

# 4. Удаляем объявление (только владелец)
delete_response = requests.delete("http://127.0.0.1:5000/ads/1", headers=headers)
print(f"Delete: {delete_response.status_code}")
print(delete_response.json())
