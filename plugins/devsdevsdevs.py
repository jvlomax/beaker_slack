from plugins.base import Plugin


class DevsDevsDevs(Plugin):
    commands = ["devsdevsdevs"]

    def message_recieved(self, command, message=""): # pylint:disable=unused-argument
        return ":ballmer: :ballmer: :ballmer:"

    def help(self):
        return "Summon the devs!"