from plugins.base import Plugin
import os
import json
import atexit


class Define(Plugin):
    commands = ["define"]

    def __init__(self):

        if not os.path.exists(os.path.join("plugins", "define")):
            os.makedirs(os.path.join("plugins", "define"))

        if not os.path.exists(os.path.join("plugins", "define", "definitions.json")):
            mode = "w+"
        else:
            mode = "r"
        with open(os.path.join("plugins", "define", "definitions.json"), mode) as fp:
            try:
                self.definitions = json.load(fp)
            except Exception:
                self.definitions = {}
                print("error parsing json file")
        atexit.register(self.write_definitions)

    def message_recieved(self, command, message=""): # pylint:disable=unused-argument
        if message == "help":
            return self.help()

        # Only one token in message, get definition
        if len(message.split(" - ")) == 1:

            if message.split(" ")[0] == "clear":
                return self.clear_definition(" ".join(message.split(" ")[1:]))

            if message.upper() in self.definitions:
                item = self.definitions[message.upper()]
                if isinstance(item, list):
                    return "Found {} entries for {}:\n* {}".format(
                        len(self.definitions[message.upper()]),
                        message,
                        "\n* ".join(item for item in self.definitions[message.upper()])
                    )
                else:
                    return self.definitions[message.upper()]
            else:
                return "Definition not found"

            return self.definitions.get(message.upper(), "Definition not found")

        elif len(message.split(" - ")) > 1:
            # create definition
            word = message.split(" - ")[0]
            definition = message.split(" - ")[1]
            if word.upper() in self.definitions:
                prev_def = self.definitions[word.upper()]
                if isinstance(prev_def, list):
                    self.definitions[word.upper()].append(definition)
                else:
                    new_def = [prev_def, definition]
                    self.definitions[word.upper()] = new_def

            else:
                self.definitions[message.split(" - ")[0].upper()] = message.split(" - ")[1]
            self.write_definitions()
            return message.split(" - ")[0] + " written to dictionary"
        else:
            return "I don't know what you mean"

    def write_definitions(self):
        if not os.path.exists("plugins/define"):
            os.makedirs(os.join("plugins", "define"))
        with open(os.path.join("plugins", "define", "definitions.json"), "w+") as fp:
            json.dump(self.definitions, fp)

    def clear_definition(self, definition):
        try:
            del (self.definitions[definition.upper()])
            return "{} deleted".format(definition)
        except Exception:
            return "Item not found"

    def help(self):
        return "* You can look up a definition by just entering the name eg. @define YHR\n" \
               "* You can add an entry by entering after the name, seperating with hyphen. eg. @define YHR - Yellow Hook Reef\n" \
               "* You can clear entries by using the clear command, eg. @define clear YHR"

    def __str__(self):
        return "Plugin for word definitions"
