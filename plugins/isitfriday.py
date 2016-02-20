from plugins.base import Plugin
from datetime import date

class IsItFriday(Plugin):
    commands = ["isitfriday"]

    def message_recieved(self, command, message):
        data = {}
        if date.isoweekday(date.today()) == 5:
            data["username"] = "Rebecca Black"
            data["image"] = "http://www.johnstonefitness.com/wp-content/uploads/2011/04/Rebecca-Black-Wallpapers.png"
            data["text"] = "Yes it is friday. We so excited"

        else:
            data["text"] = "No, it is not friday"
        return data

