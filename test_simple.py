import pytest
import requests
import base64
import os
import subprocess
import time
import uuid


class TestSimpleAPI:
    @classmethod
    def setup_class(cls):
        # Используем уникальную БД для тестов
        cls.test_db = f"test_{uuid.uuid4().hex}.db"
        os.environ["DB_NAME"] = cls.test_db

        # Запускаем сервер с тестовой БД
        env = os.environ.copy()
        env["DB_NAME"] = cls.test_db
        cls.server_process = subprocess.Popen(["python", "server.py"], env=env)
        time.sleep(3)
        cls.base_url = "http://127.0.0.1:5000"

    @classmethod
    def teardown_class(cls):
        cls.server_process.terminate()
        cls.server_process.wait()
        # Удаляем тестовую БД
        if os.path.exists(cls.test_db):
            os.remove(cls.test_db)

    def test_create_user(self):
        response = requests.post(
            f"{self.base_url}/users",
            json={"email": "test@example.com", "password": "test123"},
        )
        assert response.status_code == 200

    def test_create_ad_without_auth(self):
        response = requests.post(
            f"{self.base_url}/ads", json={"title": "Test", "text": "Test description"}
        )
        assert response.status_code == 401

    def test_create_ad_with_auth(self):
        # Создаем пользователя
        requests.post(
            f"{self.base_url}/users",
            json={"email": "user@example.com", "password": "pass123"},
        )

        # Авторизация и создание объявления
        credentials = base64.b64encode(b"user@example.com:pass123").decode()
        headers = {"Authorization": f"Basic {credentials}"}

        response = requests.post(
            f"{self.base_url}/ads",
            json={"title": "Test Ad", "text": "Test description"},
            headers=headers,
        )
        assert response.status_code == 200
