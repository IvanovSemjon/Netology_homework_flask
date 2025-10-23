import requests
import base64
import subprocess
import time


class TestAPI:
    @classmethod
    def setup_class(cls):
        # Запускаем сервер в фоне
        cls.server_process = subprocess.Popen(['python', 'server.py'])
        time.sleep(2)  # Ждем запуска сервера
        cls.base_url = "http://127.0.0.1:5000"

    @classmethod
    def teardown_class(cls):
        # Останавливаем сервер
        cls.server_process.terminate()
        cls.server_process.wait()

    def test_create_user(self):
        response = requests.post(
            f"{self.base_url}/users",
            json={"email": "test@example.com", "password": "test123"}
        )
        assert response.status_code == 200
        assert "id" in response.json()

    def test_create_ad_without_auth(self):
        response = requests.post(
            f"{self.base_url}/ads",
            json={"title": "Test", "text": "Test description"}
        )
        assert response.status_code == 401

    def test_create_ad_with_auth(self):
        # Создаем пользователя
        requests.post(
            f"{self.base_url}/users",
            json={"email": "user2@example.com", "password": "pass123"}
        )

        # Авторизация
        credentials = base64.b64encode(b"user2@example.com:pass123")
        headers = {"Authorization": f"Basic {credentials.decode('utf-8')}"}

        response = requests.post(
            f"{self.base_url}/ads",
            json={"title": "Test Ad", "text": "Test description"},
            headers=headers
        )
        assert response.status_code == 200
        assert "id" in response.json()

    def test_get_ad(self):
        response = requests.get(f"{self.base_url}/ads/1")
        assert response.status_code in [200, 404]  # Может не существовать

    def test_update_ad_wrong_owner(self):
        # Создаем двух пользователей
        requests.post(
            f"{self.base_url}/users",
            json={"email": "owner@example.com", "password": "pass123"}
        )
        requests.post(
            f"{self.base_url}/users",
            json={"email": "other@example.com", "password": "pass123"}
        )

        # Создаем объявление от первого пользователя
        owner_creds = base64.b64encode(b"owner@example.com:pass123")
        owner_headers = {"Authorization": f"Basic {owner_creds.decode()}"}

        create_response = requests.post(
            f"{self.base_url}/ads",
            json={"title": "Owner Ad", "text": "Owner description"},
            headers=owner_headers
        )
        ad_id = create_response.json()["id"]

        # Пытаемся изменить от другого пользователя
        other_creds = base64.b64encode(b"other@example.com:pass123")
        other_headers = {"Authorization": f"Basic {other_creds.decode()}"}

        response = requests.patch(
            f"{self.base_url}/ads/{ad_id}",
            json={"title": "Hacked"},
            headers=other_headers
        )
        assert response.status_code == 403
