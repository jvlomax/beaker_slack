from plugins.base import Plugin


class TestClass(Plugin):
    commands = ["test"]

    def message_recieved(self, command, message):
        pass


if __name__ == "__main__":
    t = TestClass()


