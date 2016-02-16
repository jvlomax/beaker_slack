import os
import datetime
from importlib import import_module
from slackclient import SlackClient

from plugins.base import Plugin
import sys


class Bot:
    def __init__(self, token, name="beaker"):
        self.token = token
        self.name = name
        self.plugins = []

        self.tag = "@"

    def get_plugins(self):
        print(os.listdir("plugins"))
        modules = [file for file in os.listdir("plugins") if file.endswith(".py") and file != "base.py" and not file.startswith("__")]
        for module in modules:
            import_module("plugins." + module.split(".")[0])
        for subclass in Plugin.__subclasses__():
            print(subclass.__name__)
            self.plugins.append(subclass())

    def refresh_plugins(self):
        pass

    def connect(self):
        sc = SlackClient(self.token)
        if sc.rtm_connect():
            while 1:
                for message in sc.rtm_read():
                    if message.get("text") is None:
                        continue
                    if message["text"] == "" or message["text"] is None:
                        continue
                    print(message)
                    try:
                        split = message["text"].split(" ")
                    except KeyError:
                        pass
                    else:
                        if split[0][0] == self.tag:

                            command = split[0][1:]
                            for module in self.plugins:
                                if command in module.commands:
                                    data = module.message_recieved(command, " ".join(split[1:]))
                                    if isinstance(data, str):
                                        data = {"text": data}
                                    sc.api_call("chat.postMessage", channel=message["channel"], **data)
                                    break
                            else:
                                data = {}
                                if command == "whatdayisit":
                                    data["text"] = datetime.datetime.now().strftime('%A')
                                elif command == "say":
                                    data["text"] = " ".join(split[1:])
                                elif command == "summon":
                                    sc.api_call("chat.delete", channel=message["channel"], ts=message["ts"])
                                    data["text"] = "@" + " @".join(split[1:])
                                    data["username"] = "summoner"
                                    data["image"] = "http://seriousmovielover.com/wordpress/wp-content/uploads/2009/10/python2.jpg"
                                    data["as_user"] = False
                                if data != {}:
                                    sc.api_call("chat.postMessage", channel=message["channel"], **data)

    def run(self):
        self.get_plugins()
        print(self.plugins)
        self.connect()

if __name__ == "__main__":

    try:
        token = sys.argv[1]
    except IndexError:
        token = os.environ.get("SLACK_API_TOKEN")
    if token is not None:
        bot = Bot(token)
        bot.run()

    else:
        print("Please supply a slack API token either as an arg or as env variable")
