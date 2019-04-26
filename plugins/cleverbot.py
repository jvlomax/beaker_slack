from plugins.base import Plugin
from cleverbot import Cleverbot, CleverbotError


class CelverBot(Plugin):
    commands = ["cb, cleverbot"]
    cb = Cleverbot('CC8u7_mY5Xlp6_KAONSqlvaSoOw', timeout=60)

    def message_recieved(self, command, message=""): # pylint:disable=unused-argument
        data = {}
        try:
            data["text"] = self.cb.say(message) or "No response"
        except CleverbotError as error:
            data["text"] = "Error connecting to clevebot: {}".format(error)
        return data
