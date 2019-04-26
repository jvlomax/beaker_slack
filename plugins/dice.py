from plugins.base import Plugin
from random import randint
import re


class Dice(Plugin):
    commands = ["roll"]

    def message_recieved(self, command, message=""): # pylint:disable=unused-argument
        if message is None or message == "":
            return "Please enter a dnd style dice notiation, eg. 2d6"
        if not re.match(r"\d{,4}[D,d]\d{,4}$", message):
            return "Invalid dice format"
        num_dice, eyes = message.split("d")
        total = 0
        try:
            if int(num_dice) > 1000:
                raise ValueError
            if int(eyes) > 1000:
                raise ValueError
            for x in range(0, int(num_dice)):
                total += randint(1, int(eyes))
            return str(total)

        except Exception:
            return "That is not a valid number. only ints between 0 and 1000 are valid"

    def help(self):
        return "_n_d_y_. Roll _n_ dices each with _y_ eyes"
