import http

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend

User = get_user_model()


class CustomBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        payload = {"username": username, "password": password}
        response = requests.post(
            settings.AUTH_API_LOGIN_URL,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=payload,
        )
        if response.status_code != http.HTTPStatus.OK:
            return None
        tokens = response.json()
        response = requests.get(
            settings.AUTH_API_USER_DATA_URL,
            headers={
                "accept": "application/json",
                "Authorization": f"Bearer {tokens["access_token"]}",
            },
        )
        if response.status_code != http.HTTPStatus.OK:
            return None
        user_data = response.json()
        try:
            user, created = User.objects.get_or_create(
                login=user_data["login"],
            )
            user.login = user_data.get("login")
            user.email = user_data.get("email")
            user.first_name = user_data.get("first_name")
            user.last_name = user_data.get("last_name")
            user.is_admin = False
            if ("superuser" == user.login) or (
                "content_admin" in user_data.get("roles")
            ):
                user.is_admin = True
            user.save()
        except Exception:
            return None

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
