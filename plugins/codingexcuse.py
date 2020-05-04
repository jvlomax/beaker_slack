import requests
from plugins.base import Plugin


class CodingExcuse(Plugin):
    commands = ["codingexcuse", "excuse"]

    def message_recieved(self, command, message=""): # pylint:disable=unused-argument
        return requests.get("http://whatthecommit.com/index.txt").content
