from plugins.base import Plugin
import requests


class Chucknorris(Plugin):
    commands = ["chucknorris"]

    def message_recieved(self, command, message=""): # pylint:disable=unused-argument
        response = requests.get("https://api.chucknorris.io/jokes/random").json().get("value", "No joke found")
        return response

    def help(self):
        return "Show how awesome Chuck Norris is."

    def __str__(self):
        return "Chucknorris generator"