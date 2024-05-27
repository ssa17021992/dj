import json

import requests


class FacebookError(Exception):
    """Facebook error."""

    def __init__(self, message=None, response=None):
        self.message = message
        self.response = response


class FacebookClient:
    """Facebook client."""

    user_agent = "Facebook/1.0"

    def __init__(self, access_token, version="3.3"):
        self.version = version
        self.access_token = access_token

    def endpoint(self, path):
        return f"https://graph.facebook.com/v{self.version}/{path}"

    @property
    def headers(self):
        return {
            "Content-Type": "application/json",
            "User-Agent": self.user_agent,
        }

    def request(self, method, url, data=None, headers=None, **kwargs):
        http_headers = self.headers
        http_headers.update(headers or {})

        try:
            response = requests.request(
                method,
                url,
                data=(data and json.dumps(data)),
                headers=http_headers,
                **kwargs,
            )
        except requests.exceptions.ConnectionError:
            raise FacebookError("Connection error")

        if response.status_code == 401:
            raise FacebookError("Unauthorized", response)

        if response.status_code == 403:
            raise FacebookError("Access denied", response)

        if response.status_code == 422:
            raise FacebookError("Unprocessed entity", response)

        if response.status_code == 499:
            raise FacebookError("Unknown error", response)

        if not 200 <= response.status_code < 300:
            raise FacebookError("Client error", response)

        return response.json()

    def get(self, path, headers=None):
        return self.request("GET", self.endpoint(path), headers=headers)

    def me(self, headers=None):
        path = (
            f"me?access_token={self.access_token}&fields="
            f"id,name,first_name,middle_name,last_name,email,birthday"
        )
        return self.get(path, headers=headers)
