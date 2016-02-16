from plugins.base import Plugin


class IsItFriday(Plugin):
    commands = ["isitfriday"]

    def message_recieved(self, command, message):
        return ""
