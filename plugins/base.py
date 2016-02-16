from abc import ABCMeta, abstractmethod


class Plugin(metaclass=ABCMeta):
    commands = [""]


    @abstractmethod
    def message_recieved(self, command, message):
        pass
