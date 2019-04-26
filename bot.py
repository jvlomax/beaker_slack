#! /usr/bin/python3
import argparse
import datetime
from importlib import import_module, reload, invalidate_caches
import os
import sys

from slackclient import SlackClient

import plugins.base


# TODO: Drop `if self.verbose` and use logging like a sane person
class Bot:
    def __init__(self, token, name="beaker", verbose=False):
        self.token = token
        self.name = name
        self.plugins = []
        self.module_objects = []
        self.tag = "@"
        self.verbose = verbose
        self.sc = SlackClient(self.token)
        self.get_plugins()

    def get_plugins(self, reload_modules=False):
        modules = [file for file in os.listdir("plugins") if file.endswith(".py")
                   and file != "base.py"
                   and not file.startswith("__")]
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
        if self.verbose:
            print(plugins.base.Plugin.__subclasses__())
        for subclass in plugins.base.Plugin.__subclasses__():

            self.plugins.append(subclass())
        if self.verbose:
            print("module objects: {}".format(self.module_objects))
            print("plugins: {}".format(self.plugins))

    def help(self, params):
        # No params, general beaker help
        if not params:
            return {"text": "Beaker bot help. You're on your own for now, Ain't nobody got time for writing help"}
        for module in self.plugins:
            if params in module.commands:
                return module.help()
        # Module not found
        else:
            return {"text": "could not find module {}".format(params)}

    def call_plugin(self, command, params=""):
        for plugin in self.plugins:
            if command in plugin.commands:
                data = plugin.message_recieved(plugin, params)
                return data

    def show_commands(self):
        commands = []
        for module in self.plugins:
            commands.extend([c for c in module.commands])
        # TODO: These internal commands should be defined on the class object
        commands.extend(["help", "say", "whatdayisit"])
        help_message = "Available commands: {}".format(", ".join(sorted(commands))) \
            if commands else "No commands available"
        return {"text": help_message}

    def handle_message(self, message):
        # Ignore messages from the bot itself
        # TODO: find a better way of storing the bot id and username
        if message.get("user", "") == "U2MQJU56V" or message.get("bot_id", "") == "B2MQ86EK0":
            return
        if not message.get("text"):
            return
        if self.verbose:
            print(message)

        # The first character for the first word should be our call tag. If not us, return
        if message[0] != self.tag:
            return
        # Split message into individual words
        split = message["text"].split(" ")
        # The command is the word that follows the tag
        command = split[0][1:]
        # The params to the command are any words that follow the command
        params = " ".join(split[1:])
        data = {}
        # First look for the command in our internal handlers
        if command == "help":
            data = self.help(params)
        elif command == "whatdayisit":
            data["text"] = datetime.datetime.now().strftime('%A')
        elif command == "say":
            data["text"] = " ".join(split[1:])
        elif command == "summon":
            # TODO: find a neater way to allow a method to delete a message so we can put this somewhere else
            self.sc.api_call("chat.delete", channel=message["channel"], ts=message["ts"])
            data["text"] = "@" + " @".join(split[1:])
            data["username"] = "summoner"
            data["icon_url"] = "http://seriousmovielover.com/wordpress/wp-content/uploads/2009/10/python2.jpg"
            data["as_user"] = False
        elif command == "commands":
            data = self.show_commands()
        elif command == "refresh":
            self.get_plugins(True)
            data["text"] = "successfully refreshed plugins"
        # Not found in internal commands, look for plugin to call
        else:
            data = self.call_plugin(command, params)

        if isinstance(data, str):
            data = {"text": data}
        data.setdefault("name", self.name)
        data.setdefault("as_user", True)
        if data:
            self.sc.api_call("chat.postMessage", channel=message["channel"], **data)

    def connect(self):
        if self.sc.rtm_connect(auto_reconnect=True):
            while 1:
                for message in self.sc.rtm_read():
                    self.handle_message(message)

    def run(self):
        self.connect()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Beaker Bot for slack")
    parser.add_argument("-v", "--verbose", help="Print verbose messages")
    parser.add_argument("--name", help="The name to use for the bot", default="Beaker")
    parser.add_argument("--token", help="slack token to use for slack slackclient")
    args = parser.parse_args()
    token = args.token or os.environ.get("SLACK_API_TOKEN")
    if not token:
        print("Please supply a slack API token either as an arg or as env variable")
        sys.exit()

    bot = Bot(token, name=args.name, verbose=args.verbose)
    bot.run()
