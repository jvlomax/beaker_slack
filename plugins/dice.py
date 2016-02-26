from plugins.base import Plugin
from random import randint


class Dice(Plugin):
    commands = ["roll"]

    def message_recieved(self, command, message):
        num_dice, eyes = message.split("d")
        total = 0
        for x in range(0, int(eyes)):
            total += randint(1, int(eyes))

        return total

