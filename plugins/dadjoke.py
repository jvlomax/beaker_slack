import requests
from plugins.base import Plugin


class Dadjoke(Plugin):
    commands = ["dadjoke", "dad"]

    def message_recieved(self, command, message=""):
        response = requests.get("https://icanhazdadjoke.com/", headers={"Accept": "text/plain"})
        return response.text
