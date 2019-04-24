import requests
from plugins.base import Plugin


class CodingExcuse(Plugin):
    commands = ["codingexcuse", "excuse"]

    def message_recieved(self, command, message=""):
        response = requests.get("http://codingexcuses.com/", headers={"Accept": "application/json"})
        return response.json()["excuse"]
