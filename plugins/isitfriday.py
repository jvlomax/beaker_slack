from plugins.base import Plugin
from datetime import date


class IsItFriday(Plugin):
    commands = ["isitfriday"]

    def message_recieved(self, command, message=""): # pylint:disable=unused-argument
        data = {}
        if date.isoweekday(date.today()) == 5:
            data["username"] = "Rebecca Black"
            data["icon_url"] = "http://www.johnstonefitness.com/wp-content/uploads/2011/04/Rebecca-Black-Wallpapers.png"
            data["as_user"] = False
            data["text"] = "Yes it is friday. We so excited"
        else:
            data["text"] = "No, it is not friday"
        return data
