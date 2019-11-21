import os

from plugins.base import Plugin
from cleverbot import Cleverbot, CleverbotError


class CelverBot(Plugin):
    commands = ["cb", "cleverbot"]
    cb = Cleverbot(os.environ.get("CLEVERBOT_API_TOKEN"), timeout=60)

    def message_recieved(self, command, message=""):    # pylint:disable=unused-argument
        data = {}
        try:
            data["text"] = self.cb.say(" ".join(message)[1:]) or "No response"
        except CleverbotError as error:
            data["text"] = "Error connecting to clevebot: {}".format(error)
        finally:
            return data

    def __str__(self):
        return "Cleverbot plugin"
