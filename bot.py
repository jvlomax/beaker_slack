import os
import sys
from datetime import date
from slackclient import SlackClient


class Bot:
    def __init__(self, token, name="beaker"):
        self.token = token
        self.name = name

    def connect(self):
        sc = SlackClient(self.token)
        if sc.rtm_connect():
            while 1:
                for message in sc.rtm_read():
                    print(message)
                    try:
                        split = message["text"].split(" ")
                    except KeyError:
                        pass
                    else:
                        if split[0][0] == "@":
                            command = split[0][1:]
                            if command == "isitfriday":
                                if date.isoweekday(date.today()) == 5:
                                    text = "Yes it is friday. We so excited"
                                    # sc.rtm_send_message(message["channel"], "Yes it is friday. We so excited")
                                else:
                                    text = "No, it is not friday"
                                    # sc.rtm_send_message(message["channel"], "No, it is not friday")
                                sc.api_call("chat.postMessage", channel=message["channel"], as_user=False, text=text, username="Beaker")
if __name__ == "__main__":
    environ_token = os.environ.get("SLACK_API_TOKEN")
    arg_token = None
    if len(sys.argv) > 1:
        arg_token = sys.argv[1]

    if arg_token is not None:
        bot = Bot(arg_token)
        bot.connect()
    elif environ_token is not None:
        bot = Bot(environ_token)
        bot.connect()
    else:
        print("Please supply a slack API token either as an arg or as env variable")