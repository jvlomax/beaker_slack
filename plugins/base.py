from abc import ABCMeta, abstractmethod, abstractproperty


class Plugin(metaclass=ABCMeta):

    @property
    @abstractmethod
    def commands(self):
        return []



    @abstractmethod
    def message_recieved(self, command, message):
        pass
