from abc import ABCMeta, abstractmethod


class Plugin(metaclass=ABCMeta):

    @property
    @abstractmethod
    def commands(self):
        return []

    @abstractmethod
    def message_recieved(self, command, message):
        pass

    def help(self):
        return "This module has not implemented a help method"
