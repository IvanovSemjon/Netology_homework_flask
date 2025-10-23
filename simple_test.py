import requests
import base64
import time
import os


# Простой тест без pytest
def test_basic_functionality():
    # Удаляем старую БД
    if os.path.exists("bulletin_board.db"):
        os.remove("bulletin_board.db")

    base_url = "http://127.0.0.1:5000"

    # Тест 1: Создание пользователя
    response = requests.post(
        f"{base_url}/users", json={"email": "test@example.com", "password": "test123"}
    )
    print(f"Create user: {response.status_code}")
    assert response.status_code == 200

    # Тест 2: Создание объявления без авторизации (должно быть 401)
    response = requests.post(
        f"{base_url}/ads", json={"title": "Test", "text": "Test description"}
    )
    print(f"Create ad without auth: {response.status_code}")
    assert response.status_code == 401

    # Тест 3: Создание объявления с авторизацией
    credentials = base64.b64encode(b"test@example.com:test123").decode()
    headers = {"Authorization": f"Basic {credentials}"}

    response = requests.post(
        f"{base_url}/ads",
        json={"title": "Test Ad", "text": "Test description"},
        headers=headers,
    )
    print(f"Create ad with auth: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.text}")
    assert response.status_code == 200

    print("All tests passed!")


if __name__ == "__main__":
    test_basic_functionality()
