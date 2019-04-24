#! /usr/bin/python3
from apscheduler.schedulers.background import BackgroundScheduler
import requests

import os
import datetime
from importlib import import_module, reload, invalidate_caches
from slackclient import SlackClient
import sys
import plugins.base
import cleverbot


class Bot:
    def __init__(self, token, name="beaker"):
        self.token = token
        self.name = name
        self.plugins = []
        self.module_objects = []
        self.tag = "@"
        self.sc = SlackClient(self.token)
        self.get_plugins()
        self.cb = cleverbot.Cleverbot('CC8u7_mY5Xlp6_KAONSqlvaSoOw', timeout=60)


    def get_plugins(self, reload_modules=False):
        modules = [file for file in os.listdir("plugins") if file.endswith(".py") and file != "base.py" and not file.startswith("__")]
        if not reload_modules:
            for module in modules:
                self.module_objects.append(import_module("plugins." + module.split(".")[0]))
        else:
            reload(plugins.base)
            new_modules = []
            for module in self.module_objects:
                new_module = reload(module)
                new_modules.append(new_module)
            self.module_objects.clear()
            self.module_objects = new_modules
            self.plugins.clear()

            invalidate_caches()
        print(plugins.base.Plugin.__subclasses__())
        for subclass in plugins.base.Plugin.__subclasses__():

            self.plugins.append(subclass())
        print("module objects: {}".format(self.module_objects))
        print("plugins: {}".format(self.plugins))

    def connect(self):
        if self.sc.rtm_connect(auto_reconnect=True):
            while 1:
                for message in self.sc.rtm_read():
                    if message.get("user", "") == "U2MQJU56V" or message.get("bot_id", "") == "B2MQ86EK0":
                        continue
                    if message.get("text") is None:
                        continue
                    if message["text"] == "" or message["text"] is None:
                        continue
                    #if float(message["ts"]) < time.time():
                    #    print("old message, ignoring")
                    #    continue
                    print(message)
                    try:
                        split = message["text"].split(" ")
                    except KeyError:
                        pass
                    else:
                       is_ok = True
                       try:
                           x = split[0][0]
                       except IndexError:
                           is_ok = False
                       if is_ok and split[0][0] == self.tag:
                            command = split[0][1:]
                            params = " ".join(split[1:])
                            if command == "help":
                                if params:
                                    for module in self.plugins:
                                        if params in module.commands:
                                            data = module.help()
                                            if isinstance(data, str):
                                                data = {"text": data}
                                            self.sc.api_call("chat.postMessage", channel=message["channel"], **data)
                                            break
                                    # Module not found
                                    else:
                                        data = {"text": "could not find module {}".format(params)}
                                        self.sc.api_call("chat.postMessage", channel=message["channel"], **data)
                                        break
                                # No params, general beaker help
                                else:
                                    data = {"text": "Beaker bot help. You're on your own for now, Ain't nobody got time for writing help"}
                                    self.sc.api_call("chat.postMessage", channel=message["channel"], **data)
                            # Find the correct module to call
                            for module in self.plugins:
                                if command in module.commands:
                                    print(dir(module))
                                    data = module.message_recieved(command, " ".join(split[1:]) or "")
                                    # If plugins returns string, we need to make it into dictionary
                                    if isinstance(data, str):
                                        data = {"text": data}
                                    # Add default data if not already defined by the plugin
                                    if "name" not in data:
                                        data["name"] = self.name
                                    if "as_user" not in data:
                                        data["as_user"] = True
                                    """
                                    if "icon_url" not in data:
                                        data["icon_url"] = ""
                                    """
                                    self.sc.api_call("chat.postMessage", channel=message["channel"], **data)
                                    break
                            else:
                                data = {}
                                if command == "whatdayisit":
                                    data["text"] = datetime.datetime.now().strftime('%A')
                                elif command == "say":
                                    data["text"] = " ".join(split[1:])
                                elif command == "summon":
                                    self.sc.api_call("chat.delete", channel=message["channel"], ts=message["ts"])
                                    data["text"] = "@" + " @".join(split[1:])
                                    data["username"] = "summoner"
                                    data["icon_url"] = "http://seriousmovielover.com/wordpress/wp-content/uploads/2009/10/python2.jpg"
                                    data["as_user"] = False
                                elif command == "commands":
                                    available_commands = ""
                                    commands = []
                                    for module in self.plugins:
                                        commands.extend([c for c in module.commands])
                                        available_commands += "{}, ".format(" ,".join(module.commands))
                                    commands.extend(["help", "say", "whatdayisit"])
                                    help_message = "Available commands: {}".format(", ".join(sorted(commands))) if len(available_commands) > 0 else "No commands available"
                                    data["text"] = help_message
                                elif command == "refresh":
                                    self.get_plugins(True)
                                    data["text"] = "successfully refreshed plugins"
                                elif command == "cb":
                                    try:
                                        print("Cleverbot")
                                        data["text"] = self.cb.say(" ".join(split[1:])) or "No response"
                                        print("data recieved: {}".format(data))
                                    except cleverbot.CleverbotError as error:
                                        print("cleverbot error {}".format(error))
                                        data["text"] = "Error connecting to clevebot: {}".format(error)
                                if data != {}:
                                    if "name" not in data:
                                        data["name"] = self.name
                                    if "as_user" not in data:
                                        data["as_user"] = True
                                    self.sc.api_call("chat.postMessage", channel=message["channel"], **data)

    def run(self):
        self.connect()

if __name__ == "__main__":

    if len(sys.argv) > 1:
        token = sys.argv[1]
    else:
        print("else")
        token = os.environ.get("SLACK_API_TOKEN")
    if token is not None:
        bot = Bot(token)
        bot.run()

    else:
        print("Please supply a slack API token either as an arg or as env variable")
