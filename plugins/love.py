from plugins.base import Plugin


class WhatIsLove(Plugin):
    commands = ["whatislove"]

    def message_recieved(self, command, message=""): # pylint:disable=unused-argument
        return "BABY DON'T HURT ME, DON'T HURT ME, NO MOREEE!"
