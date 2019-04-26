import requests
from plugins.base import Plugin


class Commitmsg(Plugin):
    commands = ["whatthecommit", "commitmsg"]

    def message_recieved(self, command, message=""): # pylint:disable=unused-argument
        response = requests.get("http://whatthecommit.com/index.txt")
        return response.text
