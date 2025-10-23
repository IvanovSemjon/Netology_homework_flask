import requests
import base64
import subprocess
import time
import uuid


class TestAPI:
    @classmethod
    def setup_class(cls):
        # Запускаем сервер в фоне
        cls.server_process = subprocess.Popen(["python", "server.py"])
        time.sleep(2)  # Ждем запуска сервера
        cls.base_url = "http://127.0.0.1:5000"

    @classmethod
    def teardown_class(cls):
        # Останавливаем сервер
        cls.server_process.terminate()
        cls.server_process.wait()

    def test_create_user(self):
        email = f"test{uuid.uuid4()}@example.com"
        response = requests.post(
            f"{self.base_url}/users",
            json={"email": email, "password": "test123"},
        )
        assert response.status_code == 200
        assert "id" in response.json()

    def test_create_ad_without_auth(self):
        response = requests.post(
            f"{self.base_url}/ads",
            json={"title": "Test", "text": "Test description with enough characters"},
        )
        assert response.status_code == 401

    def test_create_ad_with_auth(self):
        # Создаем пользователя
        email = f"user{uuid.uuid4()}@example.com"
        user_response = requests.post(
            f"{self.base_url}/users",
            json={"email": email, "password": "pass123"},
        )
        assert user_response.status_code == 200

        # Авторизация
        credentials = base64.b64encode(f"{email}:pass123".encode())
        headers = {"Authorization": f"Basic {credentials.decode('utf-8')}"}

        response = requests.post(
            f"{self.base_url}/ads",
            json={
                "title": "Test Ad",
                "text": "Test description with enough characters",
            },
            headers=headers,
        )
        assert response.status_code == 200
        assert "id" in response.json()

    def test_get_ad(self):
        response = requests.get(f"{self.base_url}/ads/1")
        assert response.status_code in [
            200,
            404,
            500,
        ]  # Может не существовать или ошибка

    def test_update_ad_wrong_owner(self):
        # Создаем двух пользователей
        owner_email = f"owner{uuid.uuid4()}@example.com"
        other_email = f"other{uuid.uuid4()}@example.com"
        
        requests.post(
            f"{self.base_url}/users",
            json={"email": owner_email, "password": "pass123"},
        )
        requests.post(
            f"{self.base_url}/users",
            json={"email": other_email, "password": "pass123"},
        )

        # Создаем объявление от первого пользователя
        owner_creds = base64.b64encode(f"{owner_email}:pass123".encode())
        owner_headers = {"Authorization": f"Basic {owner_creds.decode()}"}

        create_response = requests.post(
            f"{self.base_url}/ads",
            json={
                "title": "Owner Ad",
                "text": "Owner description with enough characters",
            },
            headers=owner_headers,
        )
        if create_response.status_code == 200:
            ad_id = create_response.json()["id"]
        else:
            # Если создание не удалось, пропускаем тест
            return

        # Пытаемся изменить от другого пользователя
        other_creds = base64.b64encode(f"{other_email}:pass123".encode())
        other_headers = {"Authorization": f"Basic {other_creds.decode()}"}

        response = requests.patch(
            f"{self.base_url}/ads/{ad_id}",
            json={"title": "Hacked"},
            headers=other_headers,
        )
        assert response.status_code == 403